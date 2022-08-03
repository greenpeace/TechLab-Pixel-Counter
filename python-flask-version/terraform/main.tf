# main.tf
terraform {
  required_version = ">= 0.14"

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }
}
# Configure GCP project
provider "google" {
  credentials = file("../key.json")
  project     = var.project_id
  region      = var.gcp_region
}

resource "google_project_service" "cloud_run" {
  service = "iam.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy = false
}

data "google_container_registry_image" "pixelcount" {
  name = var.image_name
}

# Deploy image to Cloud Run
resource "google_cloud_run_service" "pixelcount" {
  depends_on = [
    google_project_service.cloud_run
  ]

  name     = "pixelcount"
  location = var.gcp_region

  template {
    spec {
      containers {
        image = "eu.gcr.io/social-climate-tech/pixelcount:v2"
        ports {
          container_port = 8080
        }
      }
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Create public access
data "google_iam_policy" "all_users_policy" {
  binding {
    role    = "roles/run.invoker"
    members = ["allUsers"]
  }
}

# Enable public access on Cloud Run service
resource "google_cloud_run_service_iam_policy" "all_users_iam_policy" {
  location    = google_cloud_run_service.pixelcount.location
  project     = google_cloud_run_service.pixelcount.project
  service     = google_cloud_run_service.pixelcount.name
  policy_data = data.google_iam_policy.all_users_policy.policy_data
}
