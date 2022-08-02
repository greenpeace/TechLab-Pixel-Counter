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
  project     = "social-climate-tech"
  region      = "europe-north1"
}

resource "google_project_service" "cloud_run" {
  service = "iam.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy = false
}

data "google_container_registry_image" "app" {
  name = var.image_name
}

# Deploy image to Cloud Run
resource "google_cloud_run_service" "app" {
  depends_on = [
    google_project_service.cloud_run
  ]

  name     = "app"
  location = var.gcp_region

  template {
    spec {
      containers {
        image = "eu.gcr.io/social-climate-tech/pixelcount"
        ports {
          container_port = 8080
        }
      }
    }
  }
#  provisioner "local-exec" {
#    command = "cd /tmp/${var.source_repo_name}/ && cp ~/gcp_cloudrun_apigateway/cloudbuild.yaml . && git commit -am 'Updating cloudbuild.yaml' && git push origin master"
#  }
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
  location    = google_cloud_run_service.app.location
  project     = google_cloud_run_service.app.project
  service     = google_cloud_run_service.app.name
  policy_data = data.google_iam_policy.all_users_policy.policy_data
}
