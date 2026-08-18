resource "google_project_service" "required_apis" {
  for_each = toset([
    "storage.googleapis.com",
    "bigquery.googleapis.com",
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}


resource "google_storage_bucket" "raw_data" {
  name     = "${var.project_id}-fraud-raw"
  location = var.location

  uniform_bucket_level_access = true
  force_destroy               = true

  labels = {
    environment = var.environment
    project     = "fraud-risk-platform"
    layer       = "raw"
  }

  depends_on = [
    google_project_service.required_apis
  ]
}


resource "google_bigquery_dataset" "raw" {
  dataset_id = "fraud_raw"
  project    = var.project_id
  location   = var.location

  description = "Raw synthetic financial transaction data"

  delete_contents_on_destroy = true

  labels = {
    environment = var.environment
    project     = "fraud-risk-platform"
    layer       = "raw"
  }

  depends_on = [
    google_project_service.required_apis
  ]
}