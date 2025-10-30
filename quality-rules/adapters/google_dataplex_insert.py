import logging
from datetime import datetime
from typing import Dict, Any
from google.cloud import dataplex_v1
from google.api_core.exceptions import GoogleAPIError
from domain.google_datascan_config import DataScanConfig
from adapters.google_bigquery_insert import BigQueryAdapter

class GoogleDataplexInsert:
    """Servicio encargado de construir y enviar DataScans a Google Dataplex."""
    def __init__(self, project_id: str, location: str = "us-central1"):
        """Inicializa el inserter con el proyecto y la region."""
        self.project_id, self.location = project_id, location
        self.client = dataplex_v1.DataScanServiceClient()

    def _scan_id(self, config: DataScanConfig) -> str:
        """Genera un ID único para el DataScan basado en la configuración."""
        cleaned_table = (config.table.replace("_", "-")[:42].strip("-").lower())
        fecha_scan = datetime.strptime(config.hora_registro, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d") # Formato fecha
        return "-".join([config.zone, cleaned_table, fecha_scan])

    def _display_name(self, config: DataScanConfig) -> str:
        """Genera un nombre legible para el DataScan."""
        fecha_scan = datetime.strptime(config.hora_registro, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d") # Formato fecha
        return f"{config.zone}-{config.table[:20]}-{fecha_scan}"

    def _column_completeness_template(self, column: str) -> Dict[str, Any]:
        """Genera una regla de completitud para una columna específica."""
        return {
            "non_null_expectation": {},
            "column": column,
            "dimension": "COMPLETENESS",
            "threshold": 1,
            "name": f"completitud-{column.replace('_', '-')}"
        }

    def _table_completeness_rule_list(self, config: DataScanConfig) -> list[Dict[str, Any]]:
        """Genera una lista de reglas de completitud para todas las columnas indicadas en la configuración."""
        return [self._column_completeness_template(col) for col in (config.columnas_completitud or [])]

    def _table_freshness_rule(self, config: DataScanConfig) -> Dict[str, Any]:
        """Genera una regla de frescura basada en la configuración."""
        return {
            "table_condition_expectation": {"sql_expression": config.regla_completitud},
            "dimension": "FRESHNESS",
            "column": config.columna_particion if config.columna_particion != "" else config.llaves[0],
            "name": "freshness-tabla"
        }

    def _table_uniqueness_rule(self, config: DataScanConfig) -> Dict[str, Any]:
        """Genera una regla de unicidad basada en las llaves indicadas en la configuración."""
        if not config.llaves:
            logging.warning("[GoogleDataplexInsert] No se especificaron llaves para unicidad")
            return {}
        surrogated_key_str = (",'|',").join(config.llaves)
        return {
            "table_condition_expectation": {
                "sql_expression": f"(count(1)>0) AND (COUNT(DISTINCT CONCAT({surrogated_key_str}))/(COUNT(1))=1)"
            },
            "dimension": "UNIQUENESS",
            "column": config.llaves[0],
            "name": "unicidad-llaves"
        }

    def _rule_list(self, config: DataScanConfig) -> list[Dict[str, Any]]:
        """Genera la lista completa de reglas basadas en la configuración."""
        rules = self._table_completeness_rule_list(config)
        if config.regla_completitud:
            rules.append(self._table_freshness_rule(config))
        if config.llaves:
            rules.append(self._table_uniqueness_rule(config))
        rules = [r for r in rules if r]
        if not rules:
            raise ValueError("[GoogleDataplexInsert] No se generaron reglas para el DataScan")
        return rules

    def build_scan(self, config: DataScanConfig) -> Dict[str, Any]:
        """Construye el payload de un DataScan en base a la configuración de dominio."""
        scan_id = self._scan_id(config)
        payload = {
            "name": f"projects/{self.project_id}/locations/{self.location}/dataScans/{scan_id}",
            "description": config.descripcion_scan,
            "labels": {
                "project": config.project,
                "zone": config.zone,
                "periodicidad": config.periodicidad,
                "tipo_creacion": "automatica"
            },
            "data": {
                "resource": f"//bigquery.googleapis.com/projects/{config.project}/datasets/{config.dataset}/tables/{config.table}",
            },
            "data_quality_spec": {
                "row_filter": config.filter_sentence,
                "rules": self._rule_list(config),
            },
            "execution_spec": {
                "trigger": {
                    "schedule": {"cron": config.schedule.strip()}
                }
            }
        }

        #Exportacion de resultados a BigQuery si aplica
        if config.result_table:
            partes = config.result_table.split('.')
            if len(partes)==3:
                proyecto, dataset, tabla = partes
                payload["data_quality_spec"]["post_scan_actions"] = {
                    "bigquery_export": {
                        "results_table": f"//bigquery.googleapis.com/projects/{proyecto}/datasets/{dataset}/tables/{tabla}"
                    }
                }
            else:
                logging.warning(f"[GoogleDataplexInsert] result_table mal formada: {config.result_table}")

        return payload

    def insert(self, scan_payload: Dict[str, Any], config: DataScanConfig) -> Dict[str, Any]:
        """Inserta el DataScan en Dataplex usando la API oficial. Retorna la respuesta del servicio."""
        scan_id = scan_payload['name'].split('/')[-1]
        bq_adapter = BigQueryAdapter(
            project_id="fif-df-data-governance",
            dataset="dataplex",
            table="data_scans_insert_logs",
            scan_id=scan_id
        )
        parent = f"projects/{self.project_id}/locations/{self.location}"
        logging.info(f"[GoogleDataplexInsert] Insertando DataScan: {scan_id} en {parent}")
        try:
            response = self.client.create_data_scan(parent=parent, data_scan=scan_payload, data_scan_id=scan_id)
            bq_adapter.insert_result("OK", config, scan_id)
        except GoogleAPIError as e:
            if e.code == 409:
                logging.warning(f"[GoogleDataplexInsert] DataScan {scan_id} ya existe en {parent}")
                bq_adapter.insert_result(f"Warning: {e}", config, scan_id)
            else:
                logging.error(f"[GoogleDataplexInsert] Error al insertar DataScan {scan_id} en {parent}: {e}")
                bq_adapter.insert_result(f"Error: {e}", config, scan_id)
                
    def process(self, config: DataScanConfig) -> Dict[str, Any]:
        """Construye e inserta un DataScan en una sola llamada."""
        scan_payload = self.build_scan(config)
        self.insert(scan_payload, config)
