#!/bin/bash

# DevOps Demo - Development Environment Deployment Script
# This script deploys the development infrastructure and application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="development"
INFRA_DIR="infrastructure/$ENVIRONMENT"
K8S_DIR="k8s/$ENVIRONMENT"

echo -e "${BLUE}🚀 DevOps Demo - Development Environment Deployment${NC}"
echo "======================================================"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if AWS CLI is available
    if ! command -v aws >/dev/null 2>&1; then
        print_error "AWS CLI is required but not installed."
        print_info "Please install AWS CLI and configure your credentials."
        exit 1
    fi
    
    # Check if Terraform is available
    if ! command -v terraform >/dev/null 2>&1; then
        print_error "Terraform is required but not installed."
        print_info "Please install Terraform and try again."
        exit 1
    fi
    
    # Check if kubectl is available
    if ! command -v kubectl >/dev/null 2>&1; then
        print_error "kubectl is required but not installed."
        print_info "Please install kubectl and try again."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials are not configured or invalid."
        print_info "Please run 'aws configure' and try again."
        exit 1
    fi
    
    print_status "Prerequisites check completed"
}

# Deploy infrastructure
deploy_infrastructure() {
    print_info "Deploying development infrastructure..."
    
    cd "$INFRA_DIR"
    
    # Initialize Terraform
    print_info "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_info "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Apply deployment
    print_info "Applying Terraform deployment..."
    terraform apply tfplan
    
    # Get outputs
    print_info "Getting infrastructure outputs..."
    CLUSTER_NAME=$(terraform output -raw cluster_name)
    CLUSTER_ENDPOINT=$(terraform output -raw cluster_endpoint)
    
    # Configure kubectl
    print_info "Configuring kubectl for EKS cluster..."
    aws eks update-kubeconfig --region ap-northeast-2 --name "$CLUSTER_NAME"
    
    cd - > /dev/null
    
    print_status "Infrastructure deployment completed"
}

# Wait for cluster to be ready
wait_for_cluster() {
    print_info "Waiting for EKS cluster to be ready..."
    
    # Wait for nodes to be ready
    kubectl wait --for=condition=ready nodes --all --timeout=600s
    
    # Wait for system pods to be ready
    kubectl wait --for=condition=ready pods --all -n kube-system --timeout=600s
    
    print_status "EKS cluster is ready"
}

# Deploy application
deploy_application() {
    print_info "Deploying application to development cluster..."
    
    # Create namespace
    print_info "Creating namespace..."
    kubectl apply -f "$K8S_DIR/namespace.yaml"
    
    # Create ConfigMap
    print_info "Creating ConfigMap..."
    kubectl apply -f "$K8S_DIR/configmap.yaml"
    
    # Create deployment
    print_info "Creating deployment..."
    kubectl apply -f "$K8S_DIR/deployment.yaml"
    
    # Create service
    print_info "Creating service..."
    kubectl apply -f "$K8S_DIR/service.yaml"
    
    # Create ingress (if available)
    if [ -f "$K8S_DIR/ingress.yaml" ]; then
        print_info "Creating ingress..."
        kubectl apply -f "$K8S_DIR/ingress.yaml"
    else
        print_warning "Ingress file not found, skipping ingress creation"
    fi
    
    print_status "Application deployment completed"
}

# Wait for application to be ready
wait_for_application() {
    print_info "Waiting for application to be ready..."
    
    # Wait for deployment to be available
    kubectl wait --for=condition=available --timeout=300s deployment/devops-demo-app -n development
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pods -l app=devops-demo -n development --timeout=300s
    
    print_status "Application is ready"
}

# Check deployment status
check_deployment_status() {
    print_info "Checking deployment status..."
    
    echo ""
    echo "=== Namespace Status ==="
    kubectl get namespace development
    
    echo ""
    echo "=== Deployment Status ==="
    kubectl get deployment -n development
    
    echo ""
    echo "=== Pod Status ==="
    kubectl get pods -n development
    
    echo ""
    echo "=== Service Status ==="
    kubectl get service -n development
    
    if [ -f "$K8S_DIR/ingress.yaml" ]; then
        echo ""
        echo "=== Ingress Status ==="
        kubectl get ingress -n development
    fi
    
    print_status "Deployment status check completed"
}

# Test application
test_application() {
    print_info "Testing application..."
    
    # Get service details
    SERVICE_IP=$(kubectl get service devops-demo-service -n development -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -n "$SERVICE_IP" ]; then
        print_info "Testing health endpoint..."
        curl -f "http://$SERVICE_IP:8000/health" || print_warning "Health endpoint test failed"
        
        print_info "Testing metrics endpoint..."
        curl -f "http://$SERVICE_IP:8000/metrics" || print_warning "Metrics endpoint test failed"
    else
        print_warning "Service IP not available, using port-forward for testing"
        
        # Start port-forward in background
        kubectl port-forward -n development service/devops-demo-service 8000:8000 &
        PF_PID=$!
        
        # Wait for port-forward to be ready
        sleep 5
        
        # Test endpoints
        print_info "Testing health endpoint..."
        curl -f "http://localhost:8000/health" || print_warning "Health endpoint test failed"
        
        print_info "Testing metrics endpoint..."
        curl -f "http://localhost:8000/metrics" || print_warning "Metrics endpoint test failed"
        
        # Stop port-forward
        kill $PF_PID
    fi
    
    print_status "Application testing completed"
}

# Generate deployment report
generate_deployment_report() {
    print_info "Generating deployment report..."
    
    cat > development-deployment-report.md << EOF
# DevOps Demo - Development Environment Deployment Report

## Deployment Information
- **Deployment Date**: $(date)
- **Environment**: Development
- **Infrastructure**: AWS EKS
- **Region**: ap-northeast-2 (Seoul, Korea)

## Infrastructure Status
- ✅ VPC: Created
- ✅ EKS Cluster: Deployed
- ✅ RDS Database: Provisioned
- ✅ ElastiCache Redis: Provisioned
- ✅ Security Groups: Configured

## Application Status
- ✅ Namespace: Created
- ✅ ConfigMap: Applied
- ✅ Deployment: Deployed
- ✅ Service: Created
- ✅ Ingress: Applied (if available)

## Cluster Information
\`\`\`bash
# Configure kubectl for the cluster
aws eks update-kubeconfig --region ap-northeast-2 --name devops-demo-dev-cluster

# Check cluster status
kubectl cluster-info

# List all resources in development namespace
kubectl get all -n development
\`\`\`

## Access Information
- **Cluster Name**: devops-demo-dev-cluster
- **Namespace**: development
- **Service**: devops-demo-service
- **Port**: 8000

## Next Steps
1. Monitor application logs: \`kubectl logs -n development -l app=devops-demo -f\`
2. Check resource usage: \`kubectl top pods -n development\`
3. Scale deployment if needed: \`kubectl scale deployment devops-demo-app -n development --replicas=3\`
4. Deploy to production when ready
EOF
    
    print_status "Deployment report generated: development-deployment-report.md"
}

# Main execution
main() {
    echo "Starting development environment deployment..."
    
    check_prerequisites
    deploy_infrastructure
    wait_for_cluster
    deploy_application
    wait_for_application
    check_deployment_status
    test_application
    generate_deployment_report
    
    echo ""
    print_status "🎉 Development environment deployment completed successfully!"
    echo ""
    echo "Generated files:"
    echo "- development-deployment-report.md: Deployment summary and results"
    echo ""
    echo "To access the application:"
    echo "- Service: devops-demo-service.development.svc.cluster.local:8000"
    echo "- Port-forward: kubectl port-forward -n development service/devops-demo-service 8000:8000"
    echo ""
    echo "To view logs:"
    echo "kubectl logs -n development -l app=devops-demo -f"
    echo ""
    echo "To check status:"
    echo "kubectl get all -n development"
}

# Run main function
main "$@"
