## GCP project ID
#
#output "gcp_project_id" {
#  value = data.google_project.working_project.project_id
#}

output "url" {
  value = {
    app  = google_cloud_run_service.service.status[0].url
  }
}
