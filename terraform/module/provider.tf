# Configure GCP project
provider "google" {
  project     = var.project_id
  region      = var.gcp_region
#  credentials = local.creds_json_file
}

#provider "google-beta" {
#  credentials = local.creds_json_file
#}
