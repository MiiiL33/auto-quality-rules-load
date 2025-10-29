variable "project_id" {
    type = string
    description = "ID del proyecto de GCP"
    default = "fif-df-data-governance"
}

variable "bfa_cl_projects" {
    type = list(string)
    description = "Lista de proyectos BFA-CL para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "bfa_co_projects" {
    type = list(string)
    description = "Lista de proyectos BFA-CO para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "bfa_pe_projects" {
    type = list(string)
    description = "Lista de proyectos BFA-PE para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "sfa_cl_projects" {
    type = list(string)
    description = "Lista de proyectos SFA-CL para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "sfa_co_projects" {
    type = list(string)
    description = "Lista de proyectos SFA-CO para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "sfa_pe_projects" {
    type = list(string)
    description = "Lista de proyectos SFA-PE para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "pay_cl_projects" {
    type = list(string)
    description = "Lista de proyectos PAY-CL para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "pay_co_projects" {
    type = list(string)
    description = "Lista de proyectos SFA-CO para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "pay_pe_projects" {
    type = list(string)
    description = "Lista de proyectos SFA-CO para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "loy_cl_projects" {
    type = list(string)
    description = "Lista de proyectos LOY-CL para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "loy_co_projects" {
    type = list(string)
    description = "Lista de proyectos LOY-CO para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}

variable "loy_pe_projects" {
    type = list(string)
    description = "Lista de proyectos LOY-PE para asignar permisos de Dataplex a la SA"
    default = ["fif-df-data-governance"]
}