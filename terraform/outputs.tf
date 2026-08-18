output "raw_bucket_name" {
  description = "Cloud Storage raw data bucket"
  value       = google_storage_bucket.raw_data.name
}

output "raw_bucket_uri" {
  description = "Cloud Storage URI"
  value       = "gs://${google_storage_bucket.raw_data.name}"
}

output "bigquery_raw_dataset" {
  description = "BigQuery raw dataset"
  value       = google_bigquery_dataset.raw.dataset_id
}