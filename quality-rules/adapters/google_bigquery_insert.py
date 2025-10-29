import logging
from google.cloud import bigquery
from datetime import datetime
from dataclasses import asdict
from domain.google_datascan_config import DataScanConfig
import json

class BigQueryAdapter:
    """Encargado de insertar resultados de ejecución en BigQuery."""

    def __init__(self, project_id: str, dataset: str, table: str, scan_id: str):
        self.client = bigquery.Client(project=project_id)
        self.table_id = f"{project_id}.{dataset}.{table}"

    def insert_result(self, status: str, data_scan_obj: DataScanConfig, scan_id: str) -> None:
        """Inserta un registro y maneja cualquier error internamente para no romper el flujo."""
        row = {
            "scan_id": scan_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            **asdict(data_scan_obj),
        }

        # Convertir listas a JSON para preservar comas internas
        for key, value in row.items():
            if isinstance(value, list):
                row[key] = json.dumps(value)

        try:
            errors = self.client.insert_rows_json(self.table_id, [row])
            if errors:
                logging.error(f"[BigQueryAdapter] Error al insertar: {errors}")
        except Exception as e:
            logging.error(f"[BigQueryAdapter] Excepción al insertar en BigQuery: {e}")
