variable "cloud_id" {
  description = "ID облака в Yandex Cloud"
  type = string
}

variable "folder_id" {
  description = "ID каталога в Yandex Cloud"
  type = string
}

variable "tg_bot_key" {
  description = "Токен Telegram-бота"
  type = string
}

variable "yandex_api_key" {
  description = "API-ключ для Yandex Cloud"
  type = string
}

variable "instruction_file_path" {
  description = "Путь к файлу с инструкцией для YandexGPT API"
  type = string
}