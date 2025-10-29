from google.cloud import storage
import logging

class GoogleStorageBucket:
    """Permite descargar archivos de un bucket y devolverlos como bytes"""

    def __init__(self, bucket_name: str, file_name: str):
        self.bucket_name = bucket_name
        self.file_name = file_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def download_file_as_bytes(self, file_name: str) -> bytes:
        """Descarga un archivo desde el bucket como bytes"""
        try:
            blob = self.bucket.blob(file_name)
            data = blob.download_as_bytes()
            return data
        except Exception as e:
            logging.error(f"[GoogleStorageBucket] Error al descargar '{file_name}': {e}")
            raise
