
locals {
  services = [
    "sourcerepo.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "iam.googleapis.com",
  ]
}

resource "google_project_service" "enabled_service" {
  for_each = toset(local.services)
  project  = var.project_id
  service  = each.key

  provisioner "local-exec" {
    command = "sleep 60"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "sleep 15"
  }
}

locals {
  image = "eu.gcr.io/${var.project_id}/${var.image_name}:v6"
}

resource "null_resource" "docker_build" {

triggers = {
always_run = timestamp()

}

provisioner "local-exec" {
    working_dir = path.module
    command     = "docker buildx build --platform linux/amd64 --push -t ${local.image} ../."
  }
}

# Deploy image to Cloud Run
resource "google_cloud_run_service" "service" {
  depends_on = [
    google_project_service.enabled_service["run.googleapis.com"]
  ]

  name     = "pixelcounter"
  location = var.gcp_region
  autogenerate_revision_name = true

  template {
    spec {
      containers {
        image = local.image
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
  location    = google_cloud_run_service.service.location
  project     = google_cloud_run_service.service.project
  service     = google_cloud_run_service.service.name
  policy_data = data.google_iam_policy.all_users_policy.policy_data
}

# SECRETS
locals {
  app_name = "pixelcounter"
}

resource "google_secret_manager_secret" "pixelcounter" {
  project   = var.project_id
  secret_id = "pixelcounter_token"

  replication {
    user_managed {
      replicas {
        location = "europe-west1"
      }
      replicas {
        location = "europe-north1"
      }
    }
  }

  labels = {
    app         = local.app_name
    entity      = var.entity
    environment = var.environment
    source      = "pixel_token"
  }
}

resource "google_service_account" "function" {
  account_id   = "${local.app_name}-${var.entity}-${var.environment}"
  display_name = "Pixelcounter Service Account"
  project      = var.project_id
}
