variable "project_id" {
    type        = string
    default     = "fif-df-data-governance"
    description = "ID del proyecto de GCP"
}

variable "environment" {
    type        = string
    default     = "dev"
    description = "Entorno de despliegue"
}

variable "area" {
    type        = string
    default     = "none"
    description = "Área a desplegar"
}

variable "bu_country_deploy" {
    type        = list(string)
    default     = ["bfa-cl"]
    description = "Lista de BU-PAÍS a desplegar"
}

variable "service_account_email" {
    type        = string
    description = "Mail de la service account existente"
}
