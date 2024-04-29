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