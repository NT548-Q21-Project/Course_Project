# Environment
environment = "dev"
region      = "ap-southeast-1"

# Cluster
cluster_name          = "myapp-dev"
kubernetes_version    = "1.33"

# Node Group
node_instance_types   = ["c7i-flex.large"]
node_desired_size     = 2
node_min_size         = 1
node_max_size         = 3
node_disk_size        = 20

# VPC
vpc_cidr              = "10.0.0.0/16"
public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24"]
availability_zones    = ["ap-southeast-1a", "ap-southeast-1b"]
single_nat_gateway    = true  # Cost saving for dev environment
