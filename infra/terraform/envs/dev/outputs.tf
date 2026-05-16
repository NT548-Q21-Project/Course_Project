output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways"
  value       = module.vpc.nat_gateway_ids
}

output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint of the EKS cluster"
  value       = module.eks.cluster_endpoint
}

output "cluster_ca_certificate" {
  description = "Base64-encoded certificate authority data for the cluster"
  value       = module.eks.cluster_ca_certificate
}

output "node_group_role_arn" {
  description = "IAM role ARN for the managed node group"
  value       = module.eks.node_group_role_arn
}

output "cluster_security_group_id" {
  description = "Security group ID of the EKS cluster (default node group SG)"
  value       = module.eks.cluster_security_group_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for secrets encryption"
  value       = module.eks.kms_key_arn
}

output "kubeconfig_instructions" {
  description = "Instructions to update kubeconfig"
  value = <<EOT
To configure kubectl to connect to the cluster, run:

aws eks update-kubeconfig \
  --region ${var.region} \
  --name ${module.eks.cluster_name} \
  --kubeconfig ~/.kube/config-${var.environment}

Or set the KUBECONFIG environment variable:
export KUBECONFIG=~/.kube/config-${var.environment}
EOT
}

# ECR Outputs
output "ecr_repository_urls" {
  description = "Map of service names to ECR repository URLs"
  value       = module.ecr.repository_urls
}

# Secrets Outputs
output "groq_api_key_arn" {
  description = "ARN of the Groq API key secret"
  value       = module.secrets.groq_api_key_arn
}

output "jwt_secret_arn" {
  description = "ARN of the JWT secret"
  value       = module.secrets.jwt_secret_arn
}

output "db_credentials_arn" {
  description = "ARN of the database credentials secret"
  value       = module.secrets.db_credentials_arn
}

# RDS Outputs
output "db_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = module.rds.db_endpoint
}

output "db_port" {
  description = "Port of the RDS instance"
  value       = module.rds.db_port
}

output "rds_security_group_id" {
  description = "Security group ID for the RDS instance"
  value       = module.rds.rds_security_group_id
}

# IAM Roles (Pod Identity)
output "lb_controller_role_arn" {
  description = "IAM role ARN for AWS Load Balancer Controller"
  value       = module.alb.lb_controller_role_arn
}

output "api_gateway_role_arn" {
  description = "IAM role ARN for API Gateway service"
  value       = module.irsa.api_gateway_role_arn
}

output "identity_service_role_arn" {
  description = "IAM role ARN for Identity Service"
  value       = module.irsa.identity_service_role_arn
}

output "recruitment_service_role_arn" {
  description = "IAM role ARN for Recruitment Service"
  value       = module.irsa.recruitment_service_role_arn
}

output "ai_service_role_arn" {
  description = "IAM role ARN for AI Service"
  value       = module.irsa.ai_service_role_arn
}

# ArgoCD Outputs
output "argocd_namespace" {
  description = "Kubernetes namespace where ArgoCD is deployed"
  value       = module.argocd.argocd_namespace
}

output "argocd_hostname" {
  description = "Hostname used to access ArgoCD"
  value       = module.argocd.argocd_hostname
}

output "argocd_ingress_status" {
  description = "Status of the ArgoCD ingress (address may be pending until ALB provisions)"
  value       = module.argocd.argocd_ingress_status
}

# Notes for K8s manifests deployment:
# 1. Create ServiceAccount in namespace "services" for each service with the same name as the service:
#    - api-gateway
#    - identity-service
#    - recruitment-service
#    - ai-service
# 2. Create a single Ingress for api-gateway with annotations:
#    kubernetes.io/ingress.class: alb
#    alb.ingress.kubernetes.io/scheme: internet-facing
#    alb.ingress.kubernetes.io/target-type: ip
# 3. Other services should use ClusterIP (internal only)
# 4. The aws-load-balancer-controller is deployed automatically in kube-system namespace
