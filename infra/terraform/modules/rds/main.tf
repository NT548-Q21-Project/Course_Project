locals {
  base_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Cluster     = var.cluster_name
    }
  )
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name        = "${var.environment}-${var.cluster_name}-subnet-group"
  description = "Subnet group for RDS instance"
  subnet_ids  = var.private_subnet_ids

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-${var.cluster_name}-subnet-group"
    }
  )
}

# RDS Security Group
# Allows PostgreSQL traffic from the EKS cluster's default security group
resource "aws_security_group" "rds" {
  name_prefix = "${var.environment}-${var.cluster_name}-rds-sg-"
  description = "Security group for RDS PostgreSQL instance"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from EKS cluster"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.eks_cluster_security_group_id]
  }

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-${var.cluster_name}-rds-sg"
    }
  )
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier              = "${var.environment}-${var.cluster_name}"
  engine                  = "postgres"
  engine_version          = "18.3"
  instance_class          = var.instance_class
  allocated_storage       = var.allocated_storage
  storage_type            = "gp2"
  db_name                 = "appdb"
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  skip_final_snapshot     = true
  publicly_accessible     = false
  multi_az                = false

  tags = merge(
    local.base_tags,
    {
      Name = "${var.environment}-${var.cluster_name}-rds"
    }
  )
}
