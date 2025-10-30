variable "project_id" {
    type        = string
    default     = "quality-rules-load-poc"
    description = "ID del proyecto de GCP"
}

variable "environment" {
    type        = string
    default     = "dev"
    description = "Entorno de despliegue"
}

variable "image_tag" {
	type = string
	description = "Tag de la imagen a desplegar en Cloud Run"
}