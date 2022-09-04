variable "entity" {
  type = string
  default = "pixelcounter"
}
variable "environment" {
  type = string
  default = "dev"
}
variable "gcp_region" {
  type = string
  default = "europe-north1"
}
variable "image_name" {
  type = string
  default = "pixelcounter"
}
variable "project_id" {
  type = string
  default = "make-smthng-website"
}

variable "namespace" {
  type        = string
  default     = "pipeline"
}

############### Standard Greenpeace Used Varibles #############################
###############################################################################
#variable "Greenpeace_Environment" {
#  type = string
#  #default = "test"
#  description = "Environment test/stage/prod used for GCP and the CI server."
#}

#variable "Deploy_Instance" {
#  type        = string
#  default     = "test"
#  description = "Where Greenpeace_Environment is constant, (ie prod) used for Terraform Code paths."
#}

#variable "Service_Accounts_Dir" {
#  type        = string
#  default     = "."
#  description = "Direcorty Containg Service account files"
#}

# Current greenpeace.org and gp-test.org are held in "global-it-infrastructure" GCP Project
#variable "cloud_dns_project_id" {
#  type        = string
#  default     = "global-it-infrastructure"
#  description = "GCP project ID of project holding cloud DNS"
#}

# Current VPC project is "global-it-operations" GCP Project
#variable "vpc_project_id" {
#  type        = string
#  default     = "gl5-core"
#  description = "GCP project ID of project holding VPC"
#}

#variable "DNS_CLOUD_VPC_DOMAIN" {
#  type        = string
#  default     = "greenpeace-net"
#  description = "Google cloud DNS Manged zone name"
#}

#variable "DNS_CLOUD_EXT_DOMAIN" {
#  type        = string
#  default     = "gp-test-org"
#  description = "Google cloud DNS Manged zone name"
#}

############# Gitlab CI Pre-defined Variables ################
#############################################################

#variable "CI_PROJECT_NAME" {
#  type        = string
#  default     = "ci-project-name"
#  description = "The name of the gitlab project where CI/CD is running"
#}

#variable "KUBE_NAMESPACE" {
#  type    = string
#  default = "kube-namespace"
#}

#variable "CI_COMMIT_REF_SLUG" {
#  type    = string
#  default = "commit-ref-name"
#}

#variable "CI_PROJECT_PATH_SLUG" {
#  type    = string
#  default = "ci-project-path-slug"
#}

#variable "CI_ENVIRONMENT_SLUG" {
#  type    = string
#  default = "ci-envirment-slug"
#}

############# Labels ########################################
#############################################################

#variable "label_name" {
#  type        = string
#  default     = "resource_name"
#  description = "Label name"
#}

#variable "label_service_name" {
#  type        = string
#  default     = "service_name"
#  description = "Label service_name"
#}

#variable "label_service_component" {
#  type        = string
#  default     = "service_component"
#  description = "Label service_component"
#}

#variable "label_service_owner" {
#  type        = string
#  default     = "service_owner"
#  description = "Label service_owner"
#}

#variable "label_business_contact" {
#  type        = string
#  default     = "business_contact"
#  description = "Label business_contact"
#}

#variable "label_budget_code" {
#  type        = string
#  default     = "budget_code"
#  description = "Label budget_code"
#}

#variable "label_tech_contact" {
#  type        = string
#  default     = "tech_contact"
#  description = "Label tech_contact"
#}

variable "label_release_id" {
  type        = string
  default     = "release_id"
  description = "Label release_id"
}

########## Variables Used In Terrform Code ###################
############################################################

#variable "greenpeace_org_id" {
#  type        = string
#  default     = "12345678"
#  description = "greenpeace.org id number"
#}

#variable "DNS_WEB_APP_NAME" {
#  type        = string
#  default     = "web-app"
#  description = "Production web app dns name"
#}