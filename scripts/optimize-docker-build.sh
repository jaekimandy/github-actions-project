#!/bin/bash

# Docker Build Optimization Script
# This script optimizes Docker builds for faster CI/CD pipelines

set -e

echo "🚀 Optimizing Docker build for faster CI/CD..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Clean up old images and containers to free up space
echo "🧹 Cleaning up old Docker resources..."
docker system prune -f --volumes

# Build with optimized settings
echo "🔨 Building Docker image with optimizations..."

# Build arguments for better caching
BUILD_ARGS="--build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
BUILD_ARGS="$BUILD_ARGS --build-arg VCS_REF=$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"

# Build targets
TARGETS=("production" "development" "testing")

for target in "${TARGETS[@]}"; do
    echo "📦 Building $target target..."
    
    # Build with optimizations
    docker build \
        --target "$target" \
        --tag "app:$target" \
        --file Dockerfile \
        --progress=plain \
        --no-cache=false \
        --compress=false \
        $BUILD_ARGS \
        .
    
    echo "✅ $target target built successfully"
done

# Show build results
echo "📊 Build Results:"
docker images | grep "app:"

echo "🎉 Docker build optimization complete!"
echo ""
echo "💡 Tips for faster builds:"
echo "   - Use 'docker build --target production' for production builds only"
echo "   - Use 'docker build --target development' for development builds only"
echo "   - Use 'docker build --target testing' for testing builds only"
echo "   - The build cache will automatically speed up subsequent builds"
echo ""
echo "🔍 To check build cache usage:"
echo "   docker system df"
echo "   docker builder prune"
