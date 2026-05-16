output "groq_api_key_arn" {
  description = "ARN of the Groq API key secret"
  value       = aws_secretsmanager_secret.groq_api_key.arn
}

output "jwt_secret_arn" {
  description = "ARN of the JWT secret"
  value       = aws_secretsmanager_secret.jwt_secret.arn
}

output "identity_db_arn" {
  description = "ARN of the identity service database credentials secret"
  value       = aws_secretsmanager_secret.identity_db.arn
}

output "recruitment_db_arn" {
  description = "ARN of the recruitment service database credentials secret"
  value       = aws_secretsmanager_secret.recruitment_db.arn
}

output "ai_db_arn" {
  description = "ARN of the AI service database credentials secret"
  value       = aws_secretsmanager_secret.ai_db.arn
}
