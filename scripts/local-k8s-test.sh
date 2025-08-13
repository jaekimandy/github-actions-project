#!/bin/bash

# DevOps Demo - Local Kubernetes Test Script
# This script tests the application on a local Kubernetes cluster

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="development"
APP_NAME="devops-demo-app"
SERVICE_NAME="devops-demo-service"

echo -e "${BLUE}🚀 DevOps Demo - Local Kubernetes Test Script${NC}"
echo "=================================================="

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
    
    # Check if kubectl is available
    if ! command -v kubectl >/dev/null 2>&1; then
        print_error "kubectl is required but not installed."
        print_info "Please install kubectl and ensure you have a local cluster running."
        exit 1
    fi
    
    # Check if kubectl can connect to a cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        print_error "Cannot connect to Kubernetes cluster."
        print_info "Please ensure your local cluster (Docker Desktop, Minikube, or Kind) is running."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_status "Prerequisites check completed"
}

# Setup local environment
setup_local_environment() {
    print_info "Setting up local environment..."
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace $NAMESPACE >/dev/null 2>&1; then
        print_info "Creating namespace: $NAMESPACE"
        kubectl apply -f k8s/$NAMESPACE/namespace.yaml
    fi
    
    # Create ConfigMap
    print_info "Applying ConfigMap..."
    kubectl apply -f k8s/$NAMESPACE/configmap.yaml
    
    # Create deployment
    print_info "Applying deployment..."
    kubectl apply -f k8s/$NAMESPACE/deployment.yaml
    
    # Create service
    print_info "Applying service..."
    kubectl apply -f k8s/$NAMESPACE/service.yaml
    
    # Create ingress (if nginx-ingress is available)
    if kubectl get namespace ingress-nginx >/dev/null 2>&1; then
        print_info "Applying ingress..."
        kubectl apply -f k8s/$NAMESPACE/ingress.yaml
    else
        print_warning "nginx-ingress not found, skipping ingress creation"
    fi
    
    print_status "Local environment setup completed"
}

# Wait for deployment to be ready
wait_for_deployment() {
    print_info "Waiting for deployment to be ready..."
    
    kubectl wait --for=condition=available --timeout=300s deployment/$APP_NAME -n $NAMESPACE
    
    print_status "Deployment is ready"
}

# Check deployment status
check_deployment_status() {
    print_info "Checking deployment status..."
    
    # Get deployment status
    kubectl get deployment $APP_NAME -n $NAMESPACE
    
    # Get pod status
    kubectl get pods -n $NAMESPACE -l app=devops-demo
    
    # Get service status
    kubectl get service $SERVICE_NAME -n $NAMESPACE
    
    print_status "Deployment status check completed"
}

# Test application endpoints
test_application_endpoints() {
    print_info "Testing application endpoints..."
    
    # Get pod name
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=devops-demo -o jsonpath='{.items[0].metadata.name}')
    
    if [ -z "$POD_NAME" ]; then
        print_error "No pods found for the application"
        return 1
    fi
    
    print_info "Testing health endpoint..."
    kubectl exec -n $NAMESPACE $POD_NAME -- curl -f http://localhost:8000/health
    
    print_info "Testing metrics endpoint..."
    kubectl exec -n $NAMESPACE $POD_NAME -- curl -f http://localhost:8000/metrics
    
    print_info "Testing API endpoint..."
    kubectl exec -n $NAMESPACE $POD_NAME -- curl -f http://localhost:8000/api/v1/status
    
    print_status "Application endpoint tests completed"
}

# Test service connectivity
test_service_connectivity() {
    print_info "Testing service connectivity..."
    
    # Test service from within the cluster
    kubectl run test-client --rm -i --restart=Never --image=curlimages/curl -- curl -f http://$SERVICE_NAME.$NAMESPACE.svc.cluster.local:8000/health
    
    print_status "Service connectivity test completed"
}

# Run load tests
run_load_tests() {
    print_info "Running load tests..."
    
    # Create a temporary pod for load testing
    kubectl run load-test --rm -i --restart=Never --image=curlimages/curl -- sh -c "
        echo 'Starting load test...'
        for i in {1..10}; do
            curl -f http://$SERVICE_NAME.$NAMESPACE.svc.cluster.local:8000/health
            echo 'Request $i completed'
            sleep 0.1
        done
        echo 'Load test completed'
    "
    
    print_status "Load tests completed"
}

# Check application logs
check_application_logs() {
    print_info "Checking application logs..."
    
    # Get pod name
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=devops-demo -o jsonpath='{.items[0].metadata.name}')
    
    if [ -z "$POD_NAME" ]; then
        print_error "No pods found for the application"
        return 1
    fi
    
    print_info "Recent application logs:"
    kubectl logs -n $NAMESPACE $POD_NAME --tail=20
    
    print_status "Application logs check completed"
}

# Check resource usage
check_resource_usage() {
    print_info "Checking resource usage..."
    
    # Get resource usage for pods
    kubectl top pods -n $NAMESPACE
    
    # Get resource usage for nodes
    kubectl top nodes
    
    print_status "Resource usage check completed"
}

# Cleanup test resources
cleanup_test_resources() {
    print_info "Cleaning up test resources..."
    
    # Delete test pods
    kubectl delete pod load-test -n $NAMESPACE --ignore-not-found=true
    kubectl delete pod test-client -n $NAMESPACE --ignore-not-found=true
    
    print_status "Test resources cleanup completed"
}

# Generate test report
generate_test_report() {
    print_info "Generating test report..."
    
    cat > k8s-test-report.md << EOF
# DevOps Demo - Kubernetes Test Report

## Test Information
- **Test Date**: $(date)
- **Test Environment**: Local Kubernetes
- **Namespace**: $NAMESPACE
- **Application**: $APP_NAME

## Test Results
- ✅ Prerequisites Check: Passed
- ✅ Environment Setup: Completed
- ✅ Deployment: Ready
- ✅ Endpoint Tests: Completed
- ✅ Service Connectivity: Tested
- ✅ Load Tests: Completed
- ✅ Logs Check: Completed
- ✅ Resource Usage: Monitored

## Application Status
\`\`\`bash
kubectl get all -n $NAMESPACE
\`\`\`

## Pod Logs
\`\`\`bash
kubectl logs -n $NAMESPACE -l app=devops-demo --tail=50
\`\`\`

## Next Steps
1. Review the test report
2. Check application logs for any issues
3. Monitor resource usage
4. Deploy to production when ready
EOF
    
    print_status "Test report generated: k8s-test-report.md"
}

# Main execution
main() {
    echo "Starting local Kubernetes tests..."
    
    check_prerequisites
    setup_local_environment
    wait_for_deployment
    check_deployment_status
    test_application_endpoints
    test_service_connectivity
    run_load_tests
    check_application_logs
    check_resource_usage
    cleanup_test_resources
    generate_test_report
    
    echo ""
    print_status "🎉 Local Kubernetes tests completed successfully!"
    echo ""
    echo "Generated files:"
    echo "- k8s-test-report.md: Test summary and results"
    echo ""
    echo "Application is running at:"
    echo "- Service: $SERVICE_NAME.$NAMESPACE.svc.cluster.local:8000"
    echo "- Health: http://localhost:8000/health (port-forward)"
    echo ""
    echo "To access the application from your local machine:"
    echo "kubectl port-forward -n $NAMESPACE service/$SERVICE_NAME 8000:8000"
    echo ""
    echo "To view logs:"
    echo "kubectl logs -n $NAMESPACE -l app=devops-demo -f"
}

# Run main function
main "$@"
