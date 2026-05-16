variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version for the EKS cluster"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where the cluster will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "IDs of the private subnets for node group"
  type        = list(string)
}

variable "node_instance_types" {
  description = "Instance types for the managed node group"
  type        = list(string)
}

variable "node_desired_size" {
  description = "Desired number of nodes in the node group"
  type        = number
}

variable "node_min_size" {
  description = "Minimum number of nodes in the node group"
  type        = number
}

variable "node_max_size" {
  description = "Maximum number of nodes in the node group"
  type        = number
}

variable "node_disk_size" {
  description = "Disk size in GB for node group instances"
  type        = number
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
