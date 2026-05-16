# Local values for consistent tagging
locals {
  default_tags = {
    Project     = "mlops-course-project"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  module_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

# Random password for RDS (generated here to avoid circular dependency)
resource "random_password" "db_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Load common modules
module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr              = var.vpc_cidr
  public_subnet_cidrs   = var.public_subnet_cidrs
  private_subnet_cidrs  = var.private_subnet_cidrs
  availability_zones    = var.availability_zones
  cluster_name          = var.cluster_name
  single_nat_gateway    = var.single_nat_gateway
  environment           = var.environment
  tags                  = local.module_tags
}

module "eks" {
  source = "../../modules/eks"

  cluster_name               = var.cluster_name
  kubernetes_version         = var.kubernetes_version
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  environment                = var.environment
  tags                       = local.module_tags

  # Node Group configuration
  node_instance_types        = var.node_instance_types
  node_desired_size          = var.node_desired_size
  node_min_size              = var.node_min_size
  node_max_size              = var.node_max_size
  node_disk_size             = var.node_disk_size

  depends_on = [module.vpc]
}

# ECR Module - Container repositories for all services
module "ecr" {
  source = "../../modules/ecr"

  environment = var.environment
  tags        = local.module_tags
}

# S3 Module - Uploads bucket
module "s3" {
  source = "../../modules/s3"

  environment  = var.environment
  cluster_name = var.cluster_name
  tags         = local.module_tags
}

# RDS Module - PostgreSQL database
# Uses EKS cluster's default security group for ingress
module "rds" {
  source = "../../modules/rds"

  environment                   = var.environment
  cluster_name                  = var.cluster_name
  vpc_id                        = module.vpc.vpc_id
  private_subnet_ids            = module.vpc.private_subnet_ids
  eks_cluster_security_group_id = module.eks.cluster_security_group_id
  db_username                   = "appuser"
  db_password                   = random_password.db_password.result
  tags                          = local.module_tags
}

# Secrets Manager Module - Application secrets
# Note: secrets module generates its own JWT password and constructs DATABASE_URLs
# using the RDS endpoint. The RDS password is managed separately here.
module "secrets" {
  source = "../../modules/secrets"

  environment   = var.environment
  cluster_name  = var.cluster_name
  rds_endpoint  = module.rds.db_endpoint
  tags          = local.module_tags

  depends_on = [module.rds]
}

# IAM Roles with Pod Identity for all services
module "irsa" {
  source = "../../modules/irsa"

  cluster_name       = var.cluster_name
  environment        = var.environment
  jwt_secret_arn     = module.secrets.jwt_secret_arn
  identity_db_arn    = module.secrets.identity_db_arn
  recruitment_db_arn = module.secrets.recruitment_db_arn
  ai_db_arn          = module.secrets.ai_db_arn
  groq_api_key_arn   = module.secrets.groq_api_key_arn
  bucket_arn         = module.s3.bucket_arn
  tags               = local.module_tags

  depends_on = [module.s3, module.secrets]
}

# AWS Load Balancer Controller
module "alb" {
  source = "../../modules/alb"

  cluster_name           = var.cluster_name
  cluster_endpoint       = module.eks.cluster_endpoint
  cluster_ca_certificate = module.eks.cluster_ca_certificate
  vpc_id                 = module.vpc.vpc_id
  environment            = var.environment
  tags                   = local.module_tags

  depends_on = [module.irsa]
}

# ArgoCD - GitOps Continuous Delivery
module "argocd" {
  source = "../../modules/argocd"

  cluster_name    = var.cluster_name
  environment     = var.environment
  argocd_hostname = var.argocd_hostname
  tags            = local.module_tags

  depends_on = [module.alb]
}

# External Secrets Operator
module "eso" {
  source = "../../modules/eso"

  cluster_name = var.cluster_name
  environment  = var.environment
  tags         = local.module_tags

  depends_on = [module.eks]
}
