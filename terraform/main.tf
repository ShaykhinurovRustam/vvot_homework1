terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  cloud_id = var.cloud_id
  folder_id = var.folder_id
  service_account_key_file = "/Users/rustamshayk/.yc-keys/key.json"
}

resource "yandex_iam_service_account" "tg-bot" {
  name = "tg-bot"
  folder_id = var.folder_id
}

resource "yandex_resourcemanager_folder_iam_binding" "storage-iam" {
  folder_id = var.folder_id
  role = "storage.admin"

  members = [
    "serviceAccount:${yandex_iam_service_account.tg-bot.id}",
  ]
}

resource "yandex_resourcemanager_folder_iam_binding" "ocr-iam" {
  folder_id = var.folder_id
  role = "ai.vision.user"

  members = [
    "serviceAccount:${yandex_iam_service_account.tg-bot.id}",
  ]
}

resource "yandex_resourcemanager_folder_iam_binding" "gpt-iam" {
  folder_id = var.folder_id
  role = "ai.languageModels.user"

  members = [
    "serviceAccount:${yandex_iam_service_account.tg-bot.id}",
  ]
}

resource "yandex_resourcemanager_folder_iam_binding" "admin-iam" {
  folder_id = var.folder_id
  role = "serverless.functions.admin"

  members = [
    "serviceAccount:${yandex_iam_service_account.tg-bot.id}",
  ]
}

resource "yandex_storage_bucket" "bucket" {
  bucket = "tg-bot-instructions"
  folder_id = var.folder_id
}

resource "yandex_storage_object" "instruction" {
  bucket = yandex_storage_bucket.bucket.id
  key = "instruction.txt"
  source = "./instruction.txt"
}

resource "archive_file" "zip" {
  type = "zip"
  output_path = "bot.zip"
  source_dir = "bot"
}

resource "yandex_function" "func" {
  depends_on = [
    yandex_resourcemanager_folder_iam_binding.admin-iam
  ]

  name = "telegram-bot"
  user_hash = archive_file.zip.output_sha256
  runtime = "python39"
  entrypoint = "main.handler"
  memory = 128
  execution_timeout = 10
  service_account_id = yandex_iam_service_account.tg-bot.id

  storage_mounts {
    mount_point_name = "images"
    bucket = yandex_storage_bucket.bucket.bucket
    prefix = ""
  }

  environment = {
    "TELEGRAM_TOKEN" = var.tg_bot_key
    "IMAGES_BUCKET" = yandex_storage_bucket.bucket.bucket
    "YANDEX_API_KEY" = var.yandex_api_key
    "CATALOG_ID" = var.folder_id
    "INSTRUCTION_URL" = "https://${yandex_storage_bucket.bucket.bucket}.storage.yandexcloud.net/${yandex_storage_object.instruction.key}"
  }

  content {
    zip_filename = archive_file.zip.output_path
  }
}

resource "yandex_function_iam_binding" "function-iam" {
  function_id = yandex_function.func.id
  role = "serverless.functions.invoker"

  members = [
    "system:allUsers",
  ]
}

resource "null_resource" "curl" {
  provisioner "local-exec" {
    command = "curl --insecure -X POST https://api.telegram.org/bot${var.tg_bot_key}/setWebhook?url=https://functions.yandexcloud.net/${yandex_function.func.id}"
  }

  triggers = {
    on_version_change = var.tg_bot_key
  }

  provisioner "local-exec" {
    when = destroy
    command = "curl --insecure -X POST https://api.telegram.org/bot${self.triggers.on_version_change}/deleteWebhook"
  }
}

output "func_url" {
  value = "https://functions.yandexcloud.net/${yandex_function.func.id}"
}