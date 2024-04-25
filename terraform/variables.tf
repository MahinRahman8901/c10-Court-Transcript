# Variable secrets on local terraform.tfvars file
variable "AWS_KEY" {
  description = "AWS Access Key"
  type        = string
  sensitive   = true
}

variable "AWS_SKEY" {
  description = "AWS Secret Key"
  type        = string
  sensitive   = true
}

variable "DB_USER" {
    description = "Database user"
    type = string
}

variable "DB_PASSWORD" {
  description = "Database password"
  type        = string
  sensitive   = true  
}

variable "DB_NAME" {
    description = "Database name"
    type = string
}

variable "DB_HOST" {
    description = "Database host URL"
    type = string
}

variable "DB_PORT" {
    description = "Database port"
    type = string
}

variable "BASE_URL" {
    description = "Website URL"
    type = string
}

variable "COMM_QUERY_EXTENSION" {
    description = "Default query - High Court"
    type = string
}

variable "STORAGE_FOLDER" {
    description = "Data folder name"
    type = string
}

variable "OPENAI_API_KEY" {
    description = "API Key for GPT"
    type = string
    sensitive = true
}