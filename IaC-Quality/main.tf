module "service_account" {
    source = "./service-account"
    project_id = var.project_id
}

module "quality_components" {
    source   = "./quality-components"
    project_id            = var.project_id
    environment           = var.environment
    service_account_email = module.service_account.service_account_email
    image_tag             = var.image_tag
    depends_on            = [module.service_account]
}


resource "google_bigquery_dataset" "dataplex" {
    dataset_id = "dataplex"
    project    = var.project_id
    location   = "us-central1"
}

resource "google_bigquery_table" "data_scans_insert_logs" {
	project  = var.project_id
	dataset_id = google_bigquery_dataset.dataplex.dataset_id
	table_id = "data_scans_insert_logs"
	deletion_protection = false
	description = "Tabla que contiene logs de inserciones de DataScans mediante Reglas de Calidad automáticas"
    time_partitioning {
        type = "DAY"
        field = "timestamp"
    }
    clustering = ["scan_id"]
	schema = file("schema_data_scans_insert_logs.json")
    depends_on = [google_bigquery_dataset.dataplex]
}

resource "google_bigquery_table" "data_quality_scans_results" {
    project  = var.project_id
	dataset_id = google_bigquery_dataset.dataplex.dataset_id
	table_id = "data_quality_scans_results"
	deletion_protection = false
    description = "Tabla que contiene resultados de DataScans ejecutados mediante Reglas de Calidad automáticas"
    time_partitioning {
        type = "DAY"
        field = "created_at"
    }
    clustering = ["scan_id"]
    schema = file("schema_data_quality_scans_results.json")
    depends_on = [google_bigquery_dataset.dataplex]
}