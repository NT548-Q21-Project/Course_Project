variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "jwt_secret_arn" {
  description = "ARN of the JWT secret"
  type        = string
}

variable "identity_db_arn" {
  description = "ARN of the identity service database credentials secret"
  type        = string
}

variable "recruitment_db_arn" {
  description = "ARN of the recruitment service database credentials secret"
  type        = string
}

variable "ai_db_arn" {
  description = "ARN of the AI service database credentials secret"
  type        = string
}

variable "groq_api_key_arn" {
  description = "ARN of the Groq API key secret"
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 bucket for uploads"
  type        = string
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
