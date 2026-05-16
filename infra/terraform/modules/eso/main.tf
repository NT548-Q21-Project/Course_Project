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

# IAM Policy for External Secrets Operator
resource "aws_iam_policy" "eso_secrets" {
  name        = "${var.environment}-${var.cluster_name}-eso-secrets"
  description = "Allows ESO to read secrets from AWS Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecrets"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.base_tags
}

# IAM Role for External Secrets Operator
resource "aws_iam_role" "eso" {
  name = "${var.environment}-${var.cluster_name}-eso-role"

  assume_role_policy = local.pod_identity_trust_policy

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-${var.cluster_name}-eso-role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "eso_secrets" {
  role       = aws_iam_role.eso.name
  policy_arn = aws_iam_policy.eso_secrets.arn
}

# Pod Identity Association for External Secrets Operator
resource "aws_eks_pod_identity_association" "eso" {
  cluster_name    = var.cluster_name
  namespace       = "external-secrets"
  service_account = "external-secrets"
  role_arn        = aws_iam_role.eso.arn
}

# External Secrets Operator Helm Release
resource "helm_release" "eso" {
  name       = "external-secrets"
  repository = "https://charts.external-secrets.io"
  chart      = "external-secrets"
  namespace  = "external-secrets"
  create_namespace = true

  set = [
    {
      name  = "clusterName"
      value = var.cluster_name
    },
    {
      name  = "serviceAccount.name"
      value = "aws-load-balancer-controller"
    }
  ]

  depends_on = [
    aws_eks_pod_identity_association.eso
  ]
}
