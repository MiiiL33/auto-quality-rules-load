module "quality_components" {
    for_each = toset(var.bu_country_deploy)
    source   = "./quality-components"

    project_id            = var.project_id
    environment           = var.environment
    area                  = var.area
    service_account_email = var.service_account_email

    bu         = split("-", each.value)[0]
    country    = split("-", each.value)[1]
}

data "google_bigquery_dataset" "dataset" {
	dataset_id = "dataplex"
	project = var.project_id
}

resource "google_bigquery_table" "data_scans_insert_logs" {
	project  = var.project_id
	dataset_id = data.google_bigquery_dataset.dataset.dataset_id
	table_id = "data_scans_insert_logs"
	deletion_protection = false
	description = "Tabla que contiene logs de inserciones de DataScans mediante Reglas de Calidad automáticas"
	labels = {
        bu = "corp"
        country = "cross"
		comp-id = "dtqlty"
		ind     = "fif"
	}
    time_partitioning {
        type = "DAY"
        field = "timestamp"
    }

    clustering = ["scan_id"]

	schema = file("schema_data_scans_insert_logs.json")
}
