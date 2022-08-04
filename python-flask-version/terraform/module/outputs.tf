output "url" {
  value = "${google_cloud_run_service.pixelcount.status[0].url}"
}