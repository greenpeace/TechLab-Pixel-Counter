# main.tf
terraform {
  required_version = ">= 0.14"

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }
  backend "gcs" {
    bucket = "sct-terraform-state"
    # Structure:
    # state/<application/<entity>/<environment>/
    prefix = "state/socialclimatetech/test/"
  }
}

# Read the modules
module "example" {
  source = "./module/"
}
