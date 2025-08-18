# Production environment variable values

aws_region   = "ap-northeast-2" # Seoul, Korea
environment  = "production"
project_name = "devops-demo"

# VPC Configuration
vpc_cidr             = "10.0.0.0/16"
availability_zones   = ["ap-northeast-2a", "ap-northeast-2c"] # Seoul, Korea - 2 AZs
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]         # Seoul, Korea - 2 AZs
public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24"]     # Seoul, Korea - 2 AZs

# EKS Configuration
kubernetes_version = "1.28"

# Database Configuration
db_username = "admin"

# SSL Certificate (실제 인증서 ARN으로 교체 필요)
certificate_arn = ""
