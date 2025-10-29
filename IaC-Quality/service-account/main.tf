resource "google_service_account" "pubsub_cloudrun_sa" {
	account_id                   = "quality-rules-exec-sa"
	project                      = var.project_id
	display_name                 = "quality-rules-exec-sa"
	create_ignore_already_exists = true
}

resource "google_project_iam_member" "sa_bucket_permissions" {
	project    = var.project_id
	role       = "roles/storage.objectViewer"
	member     = "serviceAccount:${google_service_account.pubsub_cloudrun_sa.email}"
	depends_on = [google_service_account.pubsub_cloudrun_sa]
}

resource "google_project_iam_member" "sa_dataplex" {
	project     = var.project_id
	role        = "roles/dataplex.dataScanCreator"
	member      = "serviceAccount:${google_service_account.pubsub_cloudrun_sa.email}"
	depends_on  = [google_service_account.pubsub_cloudrun_sa]
}

resource "google_project_iam_member" "sa_bigquery_dataEditor" {
	project     = var.project_id
	role        = "roles/bigquery.dataEditor"
	member      = "serviceAccount:${google_service_account.pubsub_cloudrun_sa.email}"
	depends_on  = [google_service_account.pubsub_cloudrun_sa]
}

resource "google_project_iam_member" "sa_bigquery_jobUser" {
	project		= var.project_id
	role        = "roles/bigquery.jobUser"
	member      = "serviceAccount:${google_service_account.pubsub_cloudrun_sa.email}"
	depends_on  = [google_service_account.pubsub_cloudrun_sa]
}

resource "google_project_iam_member" "sa_bigquery_data_viewer" {
	project		= var.project_id
	role		= "roles/bigquery.dataViewer"
	member		= "serviceAccount:${google_service_account.pubsub_cloudrun_sa.email}"
	depends_on	= [google_service_account.pubsub_cloudrun_sa]
}

resource "google_project_iam_member" "fine_grained_reader" {
	project = var.project_id
	role    = "roles/datacatalog.categoryFineGrainedReader"
	member  = "serviceAccount:${google_service_account.pubsub_cloudrun_sa.email}"
}
