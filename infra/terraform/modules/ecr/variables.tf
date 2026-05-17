variable "services" {
  description = "List of ECR repository names to create"
  type        = list(string)
  default     = ["api-gateway", "identity-service", "recruitment-service", "ai-service", "frontend"]
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
