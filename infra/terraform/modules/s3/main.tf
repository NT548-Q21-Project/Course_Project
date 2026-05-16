locals {
  base_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Cluster     = var.cluster_name
    }
  )

  bucket_name = "${var.environment}-${var.cluster_name}-uploads"
}

# S3 Bucket for uploads
resource "aws_s3_bucket" "uploads" {
  bucket = local.bucket_name

  tags = merge(
    local.base_tags,
    {
      Name = local.bucket_name
    }
  )
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning
resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  versioning_configuration {
    status = "Enabled"
  }
}
