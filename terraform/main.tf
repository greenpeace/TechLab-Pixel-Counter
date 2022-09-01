# main.tf
terraform {
  required_version = ">= 0.14"
  required_providers {
      google = {
        source  = "hashicorp/google"
        version = "4.34.0"
      }

      google-beta = {
        source  = "hashicorp/google-beta"
        version = "4.34.0"
      }
  }
    backend "gcs" {
      bucket = "msw-terraform-state"
      # Structure:
      # state/<application/<entity>/<environment>/
      prefix = "state/makesmthngwebsite/test/"
      # This configuration expects GOOGLE_CREDENTIALS to be avalible
      #credentials = "${file("${var.Service_Accounts_Dir}/sa_tfst_bucket_key.json")}"
      #bucket = "${TERRAFORM_STATE_BUCKET_NAME}"
      #prefix = "${TERRAFORM_STATE_BUCKET_DIR}"
    }
}

# Read the modules
module "example" {
  source = "./module/"
}

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

resource "google_sourcerepo_repository" "repo" {
  depends_on = [
    google_project_service.enabled_service["sourcerepo.googleapis.com"]
  ]
  name       = "${var.namespace}-repo"
}

resource "google_cloudbuild_trigger" "trigger" {
  depends_on = [
    google_project_service.enabled_service["cloudbuild.googleapis.com"]
  ]
trigger_template {
    branch_name = "master"
    repo_name   = google_sourcerepo_repository.repo.name
  }
build {
    step {
      name = "gcr.io/cloud-builders/go"
      args = ["test"]
      env  = ["PROJECT_ROOT=${var.namespace}"]
    }
step {
      name = "gcr.io/cloud-builders/docker"
      args = ["buildx", "build", "--platform linux/amd64", "--push", "-t", local.image, "."]
    }

step {
      name = "gcr.io/cloud-builders/gcloud"
      args = ["run", "deploy", google_cloud_run_service.service.name, "--image", local.image, "--region", var.region, "--platform", "managed", "-q"]
    }
  }
}

data "google_project" "project" {}

resource "google_project_iam_member" "cloudbuild_roles" {
  depends_on = [google_cloudbuild_trigger.trigger]
  for_each   = toset(["roles/run.admin", "roles/iam.serviceAccountUser"])
  project    = var.project_id
  role       = each.key
  member     = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

#data "google_project" "working_project" {
#  project_id = var.Greenpeace_Environment == "prod" ? "global-it-operations" : "global-it-operations-test"
#}

#locals {
#  creds_json_file = file("${var.Service_Accounts_Dir}/${var.Greenpeace_Environment}_terraform-deploy_key.json")
#}

#locals {
#  project_id = var.Greenpeace_Environment == "prod" ? "global-iac-terraform" : "test-global-iac-terraform"
#}

#locals {
#  release_id_raw = lower(replace(var.label_release_id, ".", "-"))
#  labels = {
#    name              = lower(var.label_name) # name should be the hostname of the VM resource but if it is not defined pull in a default value.
#    service_name      = lower(var.label_service_name)
#    service_component = lower(var.label_service_component)
#    service_owner     = lower(var.label_service_owner)
#    business_contact  = lower(var.label_business_contact)
#    budget_code       = lower(var.label_budget_code)
#    tech_contact      = lower(var.label_tech_contact)
#    release_id        = substr("${local.release_id_raw}", 0, min(length("${local.release_id_raw}"), 62))
#  }
#}



