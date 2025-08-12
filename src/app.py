#!/usr/bin/env python3
"""
DevOps Demo Application
This application demonstrates various DevOps practices including:
- Health checks and monitoring
- Security features
- Configuration management
- Logging and metrics
- API documentation
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, Any

from flask import Flask, jsonify, request, render_template
from flask_caching import Cache
from flask_restx import Api, Resource, fields
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create Flask application
app = Flask(__name__)

# Configuration
app.config.from_object("config.Config")

# Initialize cache
cache = Cache(app)

# Initialize API documentation
api = Api(
    app,
    version="1.0",
    title="DevOps Demo API",
    description="A demonstration of DevOps best practices",
    doc="/docs/",
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency")

# API models for documentation
health_model = api.model(
    "Health",
    {
        "status": fields.String(description="Service status"),
        "timestamp": fields.DateTime(description="Current timestamp"),
        "version": fields.String(description="Application version"),
        "uptime": fields.Float(description="Service uptime in seconds"),
    },
)

metrics_model = api.model(
    "Metrics",
    {
        "requests_total": fields.Integer(description="Total requests"),
        "requests_per_second": fields.Float(description="Requests per second"),
        "average_response_time": fields.Float(description="Average response time"),
    },
)

# Global variables for monitoring
start_time = time.time()
request_times = []


@app.before_request
def before_request():
    """Log request details and start timing"""
    request.start_time = time.time()
    logger.info(
        "Request started",
        method=request.method,
        path=request.path,
        remote_addr=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )


@app.after_request
def after_request(response):
    """Log response details and record metrics"""
    # Calculate request duration
    duration = time.time() - request.start_time
    request_times.append(duration)

    # Keep only last 1000 requests for metrics
    if len(request_times) > 1000:
        request_times.pop(0)

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.path, status=response.status_code
    ).inc()
    REQUEST_LATENCY.observe(duration)

    # Log response details
    logger.info(
        "Request completed",
        method=request.method,
        path=request.path,
        status=response.status_code,
        duration=duration,
    )

    return response


@app.route("/")
def index():
    """Main application page"""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint"""
    uptime = time.time() - start_time
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": uptime,
    }
    return jsonify(health_data)


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@api.route("/api/v1/status")
class StatusAPI(Resource):
    """API endpoint for application status"""

    @api.doc("get_status")
    @api.marshal_with(health_model)
    def get(self):
        """Get application status"""
        uptime = time.time() - start_time
        return {
            "status": "operational",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0",
            "uptime": uptime,
        }


@api.route("/api/v1/metrics")
class MetricsAPI(Resource):
    """API endpoint for application metrics"""

    @api.doc("get_metrics")
    @api.marshal_with(metrics_model)
    def get(self):
        """Get application metrics"""
        if request_times:
            avg_response_time = sum(request_times) / len(request_times)
            requests_per_second = len(request_times) / (time.time() - start_time)
        else:
            avg_response_time = 0
            requests_per_second = 0

        return {
            "requests_total": len(request_times),
            "requests_per_second": requests_per_second,
            "average_response_time": avg_response_time,
        }


@cache.cached(timeout=300)
@app.route("/api/v1/info")
def info():
    """Cached application information"""
    return jsonify(
        {
            "name": "DevOps Demo Application",
            "description": "A demonstration of DevOps best practices",
            "version": "1.0.0",
            "environment": app.config.get("ENV", "development"),
            "features": [
                "Health monitoring",
                "Metrics collection",
                "Structured logging",
                "API documentation",
                "Caching",
                "Security headers",
            ],
        }
    )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return (
        jsonify(
            {"error": "Not found", "message": "The requested resource was not found"}
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error("Internal server error", error=str(error))
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Security: Never run in debug mode in production
    debug_mode = app.config.get("DEBUG", False)
    if os.getenv("FLASK_ENV") == "production" and debug_mode:
        logger.warning("Debug mode disabled in production environment")
        debug_mode = False

    # Security: Use localhost in development, configurable in production
    host = "127.0.0.1" if debug_mode else app.config.get("HOST", "127.0.0.1")

    # Run the application
    app.run(host=host, port=8000, debug=debug_mode)
