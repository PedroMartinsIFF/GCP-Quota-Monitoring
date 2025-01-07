variable "project_id" {
  description = "Project ID para fazer o deploy da solução"
  type        = string
}

variable "bucket_name" {
  description = "Nome do bucket onde o código da aplicação vai ficar armazenado"
  type        = string
}

variable "region" {
  description = "Região para fazer o deploy da aplicação"
  type        = string
}

variable "host" {
  description = "Nome do bucket onde o código da aplicação vai ficar armazenado"
  type        = string
}


variable "vpc" {
  description = "True or False. Coloque como True apenas se o seu projeto for o que guarda as VPCs da Globo"
  type        = string
}

variable "vpc_connector" {
  description = "Todo o trafico do zabbix passa por um connector que aponta para o proxy GCP-PASSIVE, insira o nome do connector do seu projeto"
  type        = string
}