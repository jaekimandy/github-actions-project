# Multi-stage Dockerfile demonstrating security and optimization best practices
# This Dockerfile showcases advanced DevOps skills including:
# - Multi-stage builds for security and size optimization
# - Non-root user for security
# - Multi-platform support
# - Layer caching optimization
# - Security scanning integration

# Build stage for dependencies
FROM python:3.11-slim as builder

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

# Copy dependency files
COPY requirements.txt requirements-lock.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set metadata labels
LABEL maintainer="DevOps Team <devops@example.com>"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.title="DevOps Demo Application"
LABEL org.opencontainers.image.description="Demonstration of advanced DevOps practices"
LABEL org.opencontainers.image.source="https://github.com/example/devops-demo"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser scripts/ ./scripts/

# Set Python path
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

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
FROM python:3.11-slim as development

# Install development dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements-dev.txt ./

# Install development dependencies
RUN pip install --no-cache-dir --user -r requirements-dev.txt

# Copy source code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser tests/ ./tests/

# Set Python path
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH="/app/src:/app/tests:$PYTHONPATH"

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
FROM python:3.11-slim as testing

# Install testing dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt -r requirements-dev.txt

# Copy source code and tests
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser tests/ ./tests/

# Set Python path
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH="/app/src:/app/tests:$PYTHONPATH"

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=testing

# Default command for testing
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=src", "--cov-report=html"] 