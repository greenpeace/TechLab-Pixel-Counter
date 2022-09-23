locals {
  app_name = "pixelcounter"
  services = [
    "sourcerepo.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "iam.googleapis.com",
  ]
  image = "eu.gcr.io/${var.project_id}/${var.image_name}:v0.1"
}
