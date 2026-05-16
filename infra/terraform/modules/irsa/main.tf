locals {
  base_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Cluster     = var.cluster_name
    }
  )

  # Common trust policy for Pod Identity
  pod_identity_trust_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "pods.eks.amazonaws.com"
      }
      Action = [
        "sts:AssumeRole",
        "sts:TagSession"
      ]
    }]
  })
}

# Services Namespace
resource "kubernetes_namespace_v1" "services" {
  metadata {
    name = "services"
    labels = {
      name        = "services"
      environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# 1. API Gateway IAM Role
resource "aws_iam_role" "api_gateway" {
  name = "${var.environment}-${var.cluster_name}-api-gateway-role"

  assume_role_policy = local.pod_identity_trust_policy

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-${var.cluster_name}-api-gateway-role"
    }
  )
}

resource "aws_iam_policy" "api_gateway_secrets" {
  name        = "${var.environment}-${var.cluster_name}-api-gateway-secrets"
  description = "Allows reading JWT secret for API Gateway"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [var.jwt_secret_arn]
      }
    ]
  })

  tags = local.base_tags
}

resource "aws_iam_role_policy_attachment" "api_gateway_secrets" {
  role       = aws_iam_role.api_gateway.name
  policy_arn = aws_iam_policy.api_gateway_secrets.arn
}

resource "aws_eks_pod_identity_association" "api_gateway" {
  cluster_name    = var.cluster_name
  namespace       = kubernetes_namespace_v1.services.metadata[0].name
  service_account = "api-gateway"
  role_arn        = aws_iam_role.api_gateway.arn
}

# 2. Identity Service IAM Role
resource "aws_iam_role" "identity_service" {
  name = "${var.environment}-${var.cluster_name}-identity-service-role"

  assume_role_policy = local.pod_identity_trust_policy

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-${var.cluster_name}-identity-service-role"
    }
  )
}

resource "aws_iam_policy" "identity_service_secrets" {
  name        = "${var.environment}-${var.cluster_name}-identity-service-secrets"
  description = "Allows reading JWT secret and database credentials for Identity Service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [var.jwt_secret_arn, var.identity_db_arn]
      }
    ]
  })

  tags = local.base_tags
}

resource "aws_iam_role_policy_attachment" "identity_service_secrets" {
  role       = aws_iam_role.identity_service.name
  policy_arn = aws_iam_policy.identity_service_secrets.arn
}

resource "aws_eks_pod_identity_association" "identity_service" {
  cluster_name    = var.cluster_name
  namespace       = kubernetes_namespace_v1.services.metadata[0].name
  service_account = "identity-service"
  role_arn        = aws_iam_role.identity_service.arn
}

# 3. Recruitment Service IAM Role
resource "aws_iam_role" "recruitment_service" {
  name = "${var.environment}-${var.cluster_name}-recruitment-service-role"

  assume_role_policy = local.pod_identity_trust_policy

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-${var.cluster_name}-recruitment-service-role"
    }
  )
}

resource "aws_iam_policy" "recruitment_service_secrets" {
  name        = "${var.environment}-${var.cluster_name}-recruitment-service-secrets"
  description = "Allows reading database credentials for Recruitment Service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [var.recruitment_db_arn]
      }
    ]
  })

  tags = local.base_tags
}

resource "aws_iam_policy" "recruitment_service_s3" {
  name        = "${var.environment}-${var.cluster_name}-recruitment-service-s3"
  description = "Allows S3 operations on uploads bucket for Recruitment Service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${var.bucket_arn}/*"
        ]
      }
    ]
  })

  tags = local.base_tags
}

resource "aws_iam_role_policy_attachment" "recruitment_service_secrets" {
  role       = aws_iam_role.recruitment_service.name
  policy_arn = aws_iam_policy.recruitment_service_secrets.arn
}

resource "aws_iam_role_policy_attachment" "recruitment_service_s3" {
  role       = aws_iam_role.recruitment_service.name
  policy_arn = aws_iam_policy.recruitment_service_s3.arn
}

resource "aws_eks_pod_identity_association" "recruitment_service" {
  cluster_name    = var.cluster_name
  namespace       = kubernetes_namespace_v1.services.metadata[0].name
  service_account = "recruitment-service"
  role_arn        = aws_iam_role.recruitment_service.arn
}

# 4. AI Service IAM Role
resource "aws_iam_role" "ai_service" {
  name = "${var.environment}-${var.cluster_name}-ai-service-role"

  assume_role_policy = local.pod_identity_trust_policy

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-${var.cluster_name}-ai-service-role"
    }
  )
}

resource "aws_iam_policy" "ai_service_secrets" {
  name        = "${var.environment}-${var.cluster_name}-ai-service-secrets"
  description = "Allows reading Groq API key and database credentials for AI Service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [var.groq_api_key_arn, var.ai_db_arn]
      }
    ]
  })

  tags = local.base_tags
}

resource "aws_iam_role_policy_attachment" "ai_service_secrets" {
  role       = aws_iam_role.ai_service.name
  policy_arn = aws_iam_policy.ai_service_secrets.arn
}

resource "aws_eks_pod_identity_association" "ai_service" {
  cluster_name    = var.cluster_name
  namespace       = kubernetes_namespace_v1.services.metadata[0].name
  service_account = "ai-service"
  role_arn        = aws_iam_role.ai_service.arn
}
