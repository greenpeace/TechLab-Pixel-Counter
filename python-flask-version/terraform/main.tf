# Filename: main.tf
# Configure GCP project
provider "google" {
  project = "social-climate-tech"
}
# Deploy image to Cloud Run
resource "google_cloud_run_service" "pixelcounter" {
  name     = "pixelcounter"
  location = "europe-north1-a"
  template {
    spec {
      containers {
        image = "eu.gcr.io/social-climate-tech/pixelcounter"
      }
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
}
# Create public access
data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}
# Enable public access on Cloud Run service
resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_service.pixelcounter.location
  project     = google_cloud_run_service.pixelcounter.project
  service     = google_cloud_run_service.pixelcounter.name
  policy_data = data.google_iam_policy.noauth.policy_data
}
# Return service URL
output "url" {
  value = "${google_cloud_run_service.pixelcounter.status[0].url}"
}