# Production environment variable values

aws_region = "us-west-2"
environment = "production"
project_name = "devops-demo"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnet_cidrs = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

# EKS Configuration
kubernetes_version = "1.28"

# Database Configuration
db_username = "admin"

# SSL Certificate (실제 인증서 ARN으로 교체 필요)
certificate_arn = ""
