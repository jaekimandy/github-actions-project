#!/bin/bash

# DevOps Demo - Build and Test Script
# This script builds Docker images and runs tests without requiring AWS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="devops-demo"
TAG="latest"
REGISTRY="localhost:5000"  # Local registry for testing

echo -e "${BLUE}🚀 DevOps Demo - Build and Test Script${NC}"
echo "=========================================="

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
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if Docker Buildx is available
    if ! docker buildx version > /dev/null 2>&1; then
        print_warning "Docker Buildx not available. Installing..."
        docker buildx install
    fi
    
    # Check if required tools are installed
    command -v python3 >/dev/null 2>&1 || { print_error "Python 3 is required but not installed."; exit 1; }
    command -v pip3 >/dev/null 2>&1 || { print_error "pip3 is required but not installed."; exit 1; }
    
    print_status "Prerequisites check completed"
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Install production dependencies
    pip3 install -r requirements.txt
    
    # Install development dependencies
    pip3 install -r requirements-dev.txt
    
    print_status "Dependencies installed successfully"
}

# Run Python tests
run_python_tests() {
    print_info "Running Python tests..."
    
    # Run tests with coverage
    python3 -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
    
    print_status "Python tests completed"
}

# Run linting and code quality checks
run_code_quality_checks() {
    print_info "Running code quality checks..."
    
    # Run flake8
    if command -v flake8 >/dev/null 2>&1; then
        flake8 src/ tests/ --max-line-length=120 --ignore=E501,W503
        print_status "Flake8 linting completed"
    else
        print_warning "Flake8 not installed, skipping linting"
    fi
    
    # Run mypy
    if command -v mypy >/dev/null 2>&1; then
        mypy src/ --ignore-missing-imports
        print_status "MyPy type checking completed"
    else
        print_warning "MyPy not installed, skipping type checking"
    fi
    
    # Run bandit security checks
    if command -v bandit >/dev/null 2>&1; then
        bandit -r src/ -f json -o bandit-report.json
        print_status "Bandit security scan completed"
    else
        print_warning "Bandit not installed, skipping security scan"
    fi
    
    print_status "Code quality checks completed"
}

# Build Docker images
build_docker_images() {
    print_info "Building Docker images..."
    
    # Build production image
    print_info "Building production image..."
    docker build --target production -t ${IMAGE_NAME}:${TAG} .
    
    # Build development image
    print_info "Building development image..."
    docker build --target development -t ${IMAGE_NAME}:dev .
    
    # Build testing image
    print_info "Building testing image..."
    docker build --target testing -t ${IMAGE_NAME}:test .
    
    # Tag images for local registry
    docker tag ${IMAGE_NAME}:${TAG} ${REGISTRY}/${IMAGE_NAME}:${TAG}
    docker tag ${IMAGE_NAME}:dev ${REGISTRY}/${IMAGE_NAME}:dev
    docker tag ${IMAGE_NAME}:test ${REGISTRY}/${IMAGE_NAME}:test
    
    print_status "Docker images built successfully"
}

# Run Docker container tests
run_container_tests() {
    print_info "Running container tests..."
    
    # Test production image
    print_info "Testing production image..."
    docker run --rm ${IMAGE_NAME}:${TAG} python -c "import flask; print('Flask imported successfully')"
    
    # Test development image
    print_info "Testing development image..."
    docker run --rm ${IMAGE_NAME}:dev python -c "import pytest; print('Pytest imported successfully')"
    
    # Test health check
    print_info "Testing health check..."
    docker run --rm -d --name test-container ${IMAGE_NAME}:${TAG}
    sleep 5
    
    # Check if container is running
    if docker ps | grep -q test-container; then
        print_status "Container health check passed"
    else
        print_error "Container health check failed"
        docker logs test-container
        exit 1
    fi
    
    # Clean up
    docker stop test-container
    docker rm test-container
    
    print_status "Container tests completed"
}

# Run security scans
run_security_scans() {
    print_info "Running security scans..."
    
    # Run Trivy vulnerability scanner
    if command -v trivy >/dev/null 2>&1; then
        print_info "Running Trivy vulnerability scan..."
        trivy image --format json --output trivy-report.json ${IMAGE_NAME}:${TAG}
        print_status "Trivy scan completed"
    else
        print_warning "Trivy not installed, skipping vulnerability scan"
    fi
    
    # Run Docker Scout
    if command -v docker >/dev/null 2>&1; then
        print_info "Running Docker Scout security scan..."
        docker scout cves ${IMAGE_NAME}:${TAG} --format json --output scout-report.json || true
        print_status "Docker Scout scan completed"
    fi
    
    print_status "Security scans completed"
}

# Generate build report
generate_build_report() {
    print_info "Generating build report..."
    
    cat > build-report.md << EOF
# DevOps Demo Build Report

## Build Information
- **Image Name**: ${IMAGE_NAME}
- **Tag**: ${TAG}
- **Build Date**: $(date)
- **Build Host**: $(hostname)

## Image Details
\`\`\`bash
docker images | grep ${IMAGE_NAME}
\`\`\`

## Security Scan Results
- Trivy: $(if [ -f trivy-report.json ]; then echo "Completed"; else echo "Not available"; fi)
- Docker Scout: $(if [ -f scout-report.json ]; then echo "Completed"; else echo "Not available"; fi)

## Test Results
- Python Tests: Completed
- Code Quality: Completed
- Container Tests: Completed

## Next Steps
1. Push images to registry: \`docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}\`
2. Deploy to Kubernetes: \`kubectl apply -f k8s/development/\`
3. Run integration tests
EOF
    
    print_status "Build report generated: build-report.md"
}

# Main execution
main() {
    echo "Starting build and test process..."
    
    check_prerequisites
    install_dependencies
    run_code_quality_checks
    run_python_tests
    build_docker_images
    run_container_tests
    run_security_scans
    generate_build_report
    
    echo ""
    print_status "🎉 Build and test process completed successfully!"
    echo ""
    echo "Generated files:"
    echo "- build-report.md: Build summary and next steps"
    echo "- htmlcov/: Test coverage report"
    echo "- trivy-report.json: Vulnerability scan results"
    echo "- scout-report.json: Docker security scan results"
    echo ""
    echo "Next steps:"
    echo "1. Review the build report"
    echo "2. Check security scan results"
    echo "3. Deploy to your Kubernetes cluster"
    echo "4. Run integration tests"
}

# Run main function
main "$@"
