# SECRETS
locals {
  app_name = "pixelcount"
}

resource "google_secret_manager_secret" "pixelcount" {
  project   = var.project_id
  secret_id = "pixelcount_token"

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
  display_name = "Pixelcount Service Account"
  project      = var.project_id
}
