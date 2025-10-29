from domain.google_storage_xlsx_reader import GoogleStorageXlsxReader
from domain.google_datascan_config import DataScanConfig
from adapters.google_storage_bucket import GoogleStorageBucket
from adapters.google_dataplex_insert import GoogleDataplexInsert
import logging


#Agregar import después de crear DataScan
class Orchestrator:
    """Clase encargada de orquestar el procesamiento de un archivo Excel que llega a un bucket."""

    def __init__(self, bucket_name: str, file_name: str):
        self.bucket_name = bucket_name
        self.file_name = file_name
        self.storage_bucket = GoogleStorageBucket(bucket_name, file_name)
        self.xlsx_reader = GoogleStorageXlsxReader(self.storage_bucket)

    def run(self):
        """
        Ejecuta toda la lógica:
        1. Lee el Excel.
        2. Convierte cada fila en un diccionario.
        3. Crea objetos DataScan.
        4. Inserta en Dataplex.
        """

        # Leer hoja "Calidad Basica" hasta encontrar fila vacía
        filas = self.xlsx_reader.read_calidad_basica(self.file_name)

        # Transformar cada fila en DataScan y enviar a Dataplex
        results = []
        inserters = {}
        for fila in filas:
            data_scan_obj = DataScanConfig.from_dict(fila)
            project_id = data_scan_obj.project

            if project_id not in inserters:
                inserters[project_id] = GoogleDataplexInsert(project_id=project_id, location = "us-central1")

            inserter = inserters[project_id]
            try:
                result = inserter.process(data_scan_obj)
            except Exception as e:
                logging.error(f"[Orchestrator] Error al insertar DataScan para proyecto {project_id}: {e}")
                result = None
            results.append(result)

        logging.info(f"[Orchestrator] Procesamiento completo para {self.file_name} de bucket {self.bucket_name}")
        return results