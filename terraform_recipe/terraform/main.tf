terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.5.0"
    }
  }
  
}
provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "bucket" {
  name = var.bucket_name # This bucket name must be unique
  uniform_bucket_level_access = true
  location = "US"
}

data "archive_file" "src" {
  type        = "zip"
  source_dir  = "${path.root}/../src" # Directory where your Python source code is
  output_path = "${path.root}/../quotas/src.zip"
}

resource "google_storage_bucket_object" "archive" {
  name   = "${data.archive_file.src.output_md5}.zip"
  bucket = google_storage_bucket.bucket.name
  source = "${path.root}/../quotas/src.zip"
}


resource "google_cloudfunctions_function" "function" {
  name        = "quota-monitoring-function"
  description = "Função para ativar o script de coleta de quotas na GCP e enviar para o zabbix"
  runtime     = "python39"

  environment_variables = {
    HOST_IN_ZABBIX = var.host,
    PROJECT_ID = var.project_id,
    VPC = var.vpc,
  }

  available_memory_mb   = 128
  ingress_settings      = "ALLOW_ALL"
  vpc_connector         = var.vpc_connector
  vpc_connector_egress_settings = "ALL_TRAFFIC"
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  entry_point           = "start" # This is the name of the function that will be executed in your Python code
}

resource "google_service_account" "service_account" {
  account_id   = "cloud-function-invoker"
  display_name = "Cloud Function Tutorial Invoker Service Account"
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_cloud_scheduler_job" "job" {
  name             = "cloud-function-quota-scheduler"
  description      = "Trigger the ${google_cloudfunctions_function.function.name} Cloud Function every X time."
  schedule         = "0 */1 * * *" # Trocar para o tempo desejado para coleta
  attempt_deadline = "320s"

  http_target {
    http_method = "GET"
    uri         = google_cloudfunctions_function.function.https_trigger_url

    oidc_token {
      service_account_email = google_service_account.service_account.email
    }
  }
}