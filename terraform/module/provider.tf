# Configure GCP project
provider "google" {
  project     = var.project_id
  region      = var.gcp_region
#  credentials = file("access.json")
}
