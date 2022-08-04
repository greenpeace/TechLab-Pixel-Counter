# Deploy image to Cloud Run

resource "google_secret_manager_secret_iam_member" "function" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.pixelcount.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.function.email}"
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
        image = "eu.gcr.io/social-climate-tech/pixelcount:v3"
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

#resource "google_project_iam_member" "function_trace" {
#  project = var.project_id
#  role    = "roles/cloudtrace.agent"
#  member  = "serviceAccount:${google_service_account.function.email}"
#}

#resource "google_project_iam_member" "secret_manager" {
#  project = var.project_id
#  role    = "roles/secretmanager.admin"
#  member  = "serviceAccount:${google_service_account.function.email}"
#}
