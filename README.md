
# Data Quality Rules Load

Esta herramienta automatiza la creación de reglas de calidad en Dataplex de manera semi automática, a partir de configuraciones definidas en una planilla en formato *.xlsx* (Excel o Google Sheets). 
Su objetivo es simplificar la gestión de reglas de calidad y mantener un registro claro de las ejecuciones.

---
		
## ¿Cómo funciona?

1. **Entrada (planilla en Cloud Storage)**  
   - El proceso parte desde una planilla cargada en un bucket de GCS por un Data Engineer
   - Cada fila del archivo representa una regla de calidad de un DataScan

2. **Orquestación (Cloud Run)**  
   - La aplicación está desplegada en Cloud Run, la cual lee la planilla desde la hoja **Calidad Basica**
   - La hoja puede tener de 1 a N tablas a las cuales se asignan reglas
   - A partir de cada regla, se genera el DataScan asociado a la tabla asociado a su proyecto respectivo

3. **Ejecución de reglas (Dataplex)**
   - Las reglas insertadas viven dentro del mismo proyecto que la tabla
   - La ejecución de la regla es parte de la configuración del DataScan, el proceso **NO** ejecuta las reglas, solo las inserta
   - Al ejecutarse el escaneo, Dataplex deja registro en tabla de BigQuery el resultado del escaneo¹

---

## ¿Qué beneficios trae esta aplicación?

- **Automatización**: no es necesario crear DataScans manualmente.  
- **Trazabilidad**: cada ejecución de DataScan queda registrada en BigQuery¹
- **Integración nativa**: se apoya en servicios de GCP (Cloud Run, Dataplex, BigQuery, GCS).  

---

## Flujo del proceso

1. Se sube la planilla al bucket
2. Cloud Run lo procesa y crea los DataScans.  
3. Dataplex ejecuta las reglas de calidad a la hora configurada.
4. Los resultados y logs quedan disponibles en BigQuery¹
5. Si se desea probar el DataScan de inmediato, se puede cambiar el schedule del DataScan insertado por **On Demand**, de esta manera se puede ejecutar el DataScan de forma manual. Luego de eso, se recomienda borrar el DataScan y subir nuevamente la planilla para dejar la configuración como se estableció originalmente
---

## Componentes que viven en el proceso
 - Cuenta de servicio dentro del proyecto: _quality-rules-load-exec@quality-rules-load-poc.iam.gserviceaccount.com_
	 - Roles: BigQuery Data Editor, BigQuery Job User, Dataplex DataScan Creator, Pub/Sub Subscriber, Storage Object Viewer.
	- Bucket: *quality-rules-bucket*
- Tópico y Suscripcion Pub/Sub²: quality-rules-load-topic: quality-rules-load-subscription
- Cloud Run donde se ejecuta el core del proceso: *quality-rules-load-cr* ³
## Descripción técnica del proceso
La  **suscripción**  correspondiente envía el mensaje vía  _push_  a  **Cloud Run**, que recibe esos datos, localiza el archivo en el bucket y lo procesa.

Dentro de Cloud Run, el archivo es leído y transformado en un formato estándar que permite construir los requests hacia  **Dataplex**. Finalmente, por cada fila del archivo se genera un DataScan en Dataplex, equivalente a una regla de validación.
## Notas
[¹] La tabla de resultados vive en el proyecto: **quality-rules-load-poc**: *dataplex.data_quality_scans_results*

[²] La configuración de la notificación de los buckets hacia su tópico es del tipo *OBJECT_FINALIZE* en formato *JSON_API_V1*

[³] La Cloud Run es *una* para todas las bu-país (buckets, tópicos/suscripciones).

[⁴] Si deseas agregar una feature, puedes crear una rama en este mismo repositorio a partir de main, desarrolla tu feature, luego haces un Merge Request hacia rama main
