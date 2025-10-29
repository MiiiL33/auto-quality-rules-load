from fastapi import FastAPI, Request
from google.cloud import storage
import google.auth
import requests
import base64
import json
import logging
from domain.health_route_logger import HealthRouteLoggerFilter
from application.orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO)

app = FastAPI()
storage_client = storage.Client()  # Usa la SA de Cloud Run

logging.getLogger("uvicorn.access").addFilter(HealthRouteLoggerFilter())

# --- Log inicial de la SA y proyecto ---
credentials, project_id = google.auth.default()
logging.info(f"[Startup] Proyecto detectado: {project_id}")

# Obteniendo SA a usar
METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email"
headers = {"Metadata-Flavor": "Google"}
try:
    response = requests.get(METADATA_URL, headers=headers, timeout=2)
    logging.info(f"[Startup] SA que corre Cloud Run: {response.text}")
except Exception as e:
    logging.warning(f"[Startup] No se pudo obtener la SA desde metadata: {e}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def read_root():
    return {"message": "Carga de reglas de calidad corriendo"}


@app.post("/pubsub")
async def pubsub_push(request: Request):
    body = await request.json()
    
    pubsub_message = body.get("message", {})
    data_base64 = pubsub_message.get("data")
    
    if not data_base64:
        raise ValueError("[Pub/Sub] Push recibido sin datos, revisar archivo")
    
    data_json = base64.b64decode(data_base64).decode("utf-8")
    message_data = json.loads(data_json)
    
    bucket_name = message_data["bucket"]
    file_name = message_data["name"]
    
    logging.info(f"[Pub/Sub] Archivo recibido: {file_name}; bucket: {bucket_name}")

    try:
        orchestrator = Orchestrator(bucket_name, file_name)
        result = orchestrator.run()
        return {"status": "Processed", "file": file_name, "details": result}

    except Exception as e:
        logging.error(f"[Pub/Sub] Error en Orchestrator para {file_name}: {e}")
        return {"status": "Error", "message": str(e)}

    
    return {"status": "Processed", "file": file_name}
