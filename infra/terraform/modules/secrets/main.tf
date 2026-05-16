locals {
  base_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Cluster     = var.cluster_name
    }
  )

  # Extract RDS host from endpoint (host:port format)
  rds_host = split(":", var.rds_endpoint)[0]

  # Database passwords (shared across all services)
  db_password = random_password.db_password.result
}

# Random password for database
resource "random_password" "db_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# 1. Groq API Key Secret
resource "aws_secretsmanager_secret" "groq_api_key" {
  name                = "${var.environment}-groq-api-key"
  description         = "Groq AI API key for ai-service"
  recovery_window_in_days = 0

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-groq-api-key"
    }
  )
}

resource "aws_secretsmanager_secret_version" "groq_api_key" {
  secret_id     = aws_secretsmanager_secret.groq_api_key.id
  secret_string = jsonencode({
    LLM_API_KEY = "REPLACE_ME"
  })
}

# 2. JWT Secret
resource "aws_secretsmanager_secret" "jwt_secret" {
  name                = "${var.environment}-jwt-secret"
  description         = "JWT signing secret for identity-service"
  recovery_window_in_days = 0

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-jwt-secret"
    }
  )
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = jsonencode({
    JWT_SECRET_KEY = random_password.jwt_secret.result
  })
}

resource "random_password" "jwt_secret" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# 3. Identity Service Database Secret
resource "aws_secretsmanager_secret" "identity_db" {
  name                = "${var.environment}-identity-db"
  description         = "PostgreSQL credentials for identity-service"
  recovery_window_in_days = 0

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-identity-db"
    }
  )
}

resource "aws_secretsmanager_secret_version" "identity_db" {
  secret_id     = aws_secretsmanager_secret.identity_db.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql+psycopg://appuser:${local.db_password}@${local.rds_host}:5432/identity_db"
  })
}

# 4. Recruitment Service Database Secret
resource "aws_secretsmanager_secret" "recruitment_db" {
  name                = "${var.environment}-recruitment-db"
  description         = "PostgreSQL credentials for recruitment-service"
  recovery_window_in_days = 0

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-recruitment-db"
    }
  )
}

resource "aws_secretsmanager_secret_version" "recruitment_db" {
  secret_id     = aws_secretsmanager_secret.recruitment_db.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql+psycopg://appuser:${local.db_password}@${local.rds_host}:5432/recruitment_db"
  })
}

# 5. AI Service Database Secret
resource "aws_secretsmanager_secret" "ai_db" {
  name                = "${var.environment}-ai-db"
  description         = "PostgreSQL credentials for ai-service"
  recovery_window_in_days = 0

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-ai-db"
    }
  )
}

resource "aws_secretsmanager_secret_version" "ai_db" {
  secret_id     = aws_secretsmanager_secret.ai_db.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql+psycopg://appuser:${local.db_password}@${local.rds_host}:5432/ai_db"
  })
}
