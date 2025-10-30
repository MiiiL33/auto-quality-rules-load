variable "service_account_email" {
	type = string
	description = "Mail de la service account creada"
}

variable "environment" {
	type = string
	description = "Entorno de despliegue"
}

variable "project_id" {
    type = string
    description = "ID del proyecto de GCP"
}

variable "image_tag" {
	type = string
	description = "Tag de la imagen a desplegar en Cloud Run"
}