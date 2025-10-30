from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
import pytz

@dataclass
class DataScanConfig:
    """Entidad de dominio que representa la configuración de un DataScan."""
    zone: str
    project: str
    dataset: str
    table: str
    filter_sentence: Optional[str]
    schedule: str
    periodicidad: str
    query_size: Optional[str] = None
    llaves: Optional[List[str]] = None
    regla_completitud: Optional[str] = None
    columnas_completitud: Optional[List[str]] = None
    columna_particion: Optional[str] = None
    publicar_resultados: bool = True
    hora_registro: Optional[str] = field(init=False)
    result_table: Optional[str] = field(init=False)
    descripcion_scan: Optional[str] = None

    def __post_init__(self):
        chile_tz = pytz.timezone('America/Santiago')
        self.hora_registro = datetime.now(chile_tz).strftime("%Y-%m-%d %H:%M:%S")
        self.periodicidad = self.periodicidad.lower()
        self.result_table = (
            "quality-rules-load-poc.dataplex.data_quality_scans_results"
            if self.publicar_resultados
            else None
        )

    @classmethod
    def from_dict(cls, data: Dict) -> "DataScanConfig":
        """Crea una instancia de DataScanConfig a partir de un diccionario proveniente de la lectura del Excel."""
        
        # Se normalizan campos vacíos a None
        normalize = lambda x: x if x not in (None, "") else None

        # Convertir llaves y columnas_completitud en listas, normalizando partición
        llaves = [k.strip() for k in (normalize(data.get("llaves")) or "").split(",") if k.strip()]
        columnas_completitud = [k.strip() for k in (normalize(data.get("columnas_completitud")) or "").split(",") if k.strip()]
        columna_particion = (normalize(data.get("columna_particion")) or "").strip()
        publicar_resultados = str(data.get("publicar_resultados")).upper() == "S"
        descripcion_scan = ((normalize(data.get("descripcion_scan")) or "").strip() or f"Reglas de calidad para tabla {data.get('dataset')}.{data.get('table')}")


        return cls(
            zone = normalize(data.get("zone")),
            project = normalize(data.get("project")),
            dataset = normalize(data.get("dataset")),
            table = normalize(data.get("table")),
            filter_sentence = normalize(data.get("filter_sentence")),
            schedule = normalize(data.get("schedule")),
            periodicidad = normalize(data.get("periodicidad")),
            query_size = normalize(data.get("query_size")),
            llaves = llaves,
            regla_completitud = normalize(data.get("regla_completitud")),
            columnas_completitud = columnas_completitud,
            columna_particion = columna_particion,
            publicar_resultados = publicar_resultados,
            descripcion_scan = descripcion_scan
        )