module "service_account" {
    source = "./service-account"
    project_id = var.project_id
}

module "quality_components" {
    source   = "./quality-components"
    project_id            = var.project_id
    environment           = var.environment
    service_account_email = module.service_account.service_account_email
    depends_on            = [module.service_account]
}


resource "google_bigquery_dataset" "dataplex" {
    dataset_id = "dataplex"
    project    = var.project_id
    location   = "US"
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
}
