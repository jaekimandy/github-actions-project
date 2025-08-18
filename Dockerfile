# Multi-stage Dockerfile demonstrating security and optimization best practices
# This Dockerfile showcases advanced DevOps skills including:
# - Multi-stage builds for security and size optimization
# - Non-root user for security
# - Multi-platform support
# - Layer caching optimization
# - Security scanning integration
# - GitHub Actions CI/CD optimized
#
# Build targets:
# - production: Production-ready image with minimal dependencies
# - development: Development environment optimized for GitHub Actions
# - testing: Testing environment for CI/CD pipelines
#
# Build commands:
# - docker build --target production -t app:prod .
# - docker build --target development -t app:dev .
# - docker build --target testing -t app:test .
#
# GitHub Actions optimization:
# - Heavy packages (Jupyter, Sphinx) removed from dev requirements
# - Core development tools only for faster CI/CD builds
# - Optimized pip caching and layer ordering for faster builds

# Build stage for dependencies
FROM python:3.11-slim AS builder

# Set build arguments
ARG BUILDPLATFORM
ARG TARGETPLATFORM
ARG BUILD_DATE
ARG VCS_REF

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pip configuration for optimized installations
COPY pip.conf /etc/pip.conf

# Copy dependency files first for better layer caching
COPY requirements.txt ./
COPY requirements-dev.txt ./

# Install Python dependencies with optimized pip settings
RUN pip install --cache-dir /tmp/pip-cache \
    --timeout 300 \
    --retries 3 \
    --retries-delay 5 \
    -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Set metadata labels
LABEL maintainer="DevOps Team <devops@example.com>"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.title="DevOps Demo Application"
LABEL org.opencontainers.image.description="Demonstration of advanced DevOps practices"
LABEL org.opencontainers.image.source="https://github.com/example/devops-demo"

# Install runtime dependencies (GCC not needed for runtime)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser scripts/ ./scripts/

# Set Python path
ENV PYTHONPATH="/app/src"

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production

# Default command
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]

# Development stage
FROM python:3.11-slim AS development

# Install development dependencies (GCC needed for some dev packages)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    vim \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy pip configuration for optimized installations
COPY pip.conf /etc/pip.conf

# Copy requirements first for better layer caching
COPY requirements.txt requirements-dev.txt ./

# Install development dependencies with optimized pip settings
RUN pip install --cache-dir /tmp/pip-cache \
    --timeout 300 \
    --retries 3 \
    --retries-delay 5 \
    -r requirements.txt -r requirements-dev.txt

# Copy source code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser tests/ ./tests/

# Set Python path
ENV PYTHONPATH="/app/src:/app/tests"

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development

# Default command for development
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000", "--reload"]

# Testing stage
FROM python:3.11-slim AS testing

# Install testing dependencies (GCC needed for some test packages)
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy pip configuration for optimized installations
COPY pip.conf /etc/pip.conf

# Copy requirements first for better layer caching
COPY requirements.txt requirements-dev.txt ./

# Install dependencies with optimized pip settings
RUN pip install --cache-dir /tmp/pip-cache \
    --timeout 300 \
    --retries 3 \
    --retries-delay 5 \
    -r requirements.txt -r requirements-dev.txt

# Copy source code and tests
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser tests/ ./tests/

# Set Python path
ENV PYTHONPATH="/app/src:/app/tests"

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=testing

# Default command for testing
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=src", "--cov-report=html"] 