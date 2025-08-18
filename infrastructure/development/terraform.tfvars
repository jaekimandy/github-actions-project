# Development environment variable values

aws_region   = "ap-northeast-2"  # Seoul, Korea
environment  = "development"
project_name = "devops-demo"

# VPC Configuration - Development: smaller network
vpc_cidr             = "10.1.0.0/16"
availability_zones   = ["us-west-2a", "us-west-2b"]
private_subnet_cidrs = ["10.1.1.0/24", "10.1.2.0/24"]
public_subnet_cidrs  = ["10.1.101.0/24", "10.1.102.0/24"]

# EKS Configuration
kubernetes_version = "1.28"

# Database Configuration
db_username = "admin"
