terraform {
    backend "gcs" {
        bucket = "quality-rules-terraform-state"
        prefix = "terraform/state"
    }
}

provider "google" {
    project = var.project_id
    region  = "us-central1"
}
