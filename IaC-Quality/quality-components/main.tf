data "google_project" "id_proyecto" {
	project_id = var.project_id
}

locals {
	project_number = data.google_project.id_proyecto.number
	cloud_run_name = "quality-rules-load-${var.environment}"
}

#Bucket de que contiene reglas de calidad
resource "google_storage_bucket" "quality-rules-load-bucket" {
	project				   		= var.project_id
	name                     	= "quality-rules-load-bucket-${var.environment}"
	location                 	= "us-central1"
	public_access_prevention 	= "enforced"
	uniform_bucket_level_access = true
	versioning {enabled = true}
	#Retención de archivos por 14 días, luego se eliminan
	lifecycle_rule {
		condition {age = 14}
		action {type = "Delete"}
	}
}

resource "google_storage_bucket_iam_member" "sa_bucket_permissions" {
	bucket	   = google_storage_bucket.quality-rules-load-bucket.name
	role       = "roles/storage.objectViewer"
	member     = "serviceAccount:${var.service_account_email}"
	depends_on = [google_storage_bucket.quality-rules-load-bucket]
}

#####Pub/Sub#####
resource "google_pubsub_topic" "quality-rules-load-topic" {
	name    = "quality-rules-load-topic"
	project = var.project_id
}

resource "google_storage_notification" "quality_rules_load_bucket_to_pubsub" {
	bucket         = google_storage_bucket.quality-rules-load-bucket.name
	topic          = google_pubsub_topic.quality-rules-load-topic.id
	payload_format = "JSON_API_V1"
	event_types    = ["OBJECT_FINALIZE"]
	depends_on 	   = [google_storage_bucket.quality-rules-load-bucket, google_pubsub_topic.quality-rules-load-topic]
}

resource "google_cloud_run_service" "quality_rules_cloud_run" {
	name     = "quality-rules-load"
	location = "us-central1"
	project  = var.project_id
	template {
		spec {
			service_account_name = var.service_account_email
			containers {
				image = "us-central1-docker.pkg.dev/${var.project_id}/quality-rules-load/quality-rules-load:latest"
				resources {
					limits = {
						memory = "512Mi"
						cpu    = "1"
					}
				}
			}
		}
	}
	traffic {
		percent         = 100
		latest_revision = true
	}
}


resource "google_cloud_run_service_iam_member" "pubsub_invoker" {
	service    = local.cloud_run_name
	location   = google_cloud_run_service.quality_rules_cloud_run.location
	role       = "roles/run.invoker"
	member     = "serviceAccount:${var.service_account_email}"
	project    = var.project_id
	depends_on = [google_cloud_run_service.quality_rules_cloud_run]
}

# Permiso para leer desde Pub/Sub
resource "google_project_iam_member" "pubsub_subscriber" {
	project = var.project_id
	role    = "roles/pubsub.subscriber"
	member  = "serviceAccount:${var.service_account_email}"
}

resource "google_pubsub_subscription" "quality-rules-load-subscription" {
	name      			 = "quality-rules-load-subscription"
	project   			 = var.project_id
	topic     			 = google_pubsub_topic.quality-rules-load-topic.id
	ack_deadline_seconds = 10
	push_config {
		push_endpoint = "https://${local.cloud_run_name}-${local.project_number}.us-central1.run.app/pubsub"
		oidc_token {
			service_account_email = var.service_account_email
		}
	}
	depends_on = [google_pubsub_topic.quality-rules-load-topic]
}

