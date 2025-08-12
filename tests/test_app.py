"""
Tests for the Flask application
"""
import pytest
from unittest.mock import patch, MagicMock
from src.app import app, REQUEST_COUNT, REQUEST_LATENCY


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test that health endpoint returns 200 and correct data structure"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'status' in data
        assert 'timestamp' in data
        assert 'version' in data
        assert 'uptime' in data
        assert data['status'] == 'healthy'


class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    def test_metrics_endpoint(self, client):
        """Test that metrics endpoint returns 200 and Prometheus format"""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_api_docs_redirect(self, client):
        """Test that /docs/ redirects to API documentation"""
        response = client.get('/docs/')
        assert response.status_code in [200, 302]  # 302 for redirect, 200 for direct access


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test that non-existent endpoints return 404"""
        response = client.get('/nonexistent/')
        assert response.status_code == 404


class TestApplicationConfiguration:
    """Test application configuration"""
    
    def test_app_config_loaded(self):
        """Test that app configuration is loaded from config module"""
        assert app.config is not None
    
    def test_cache_initialized(self):
        """Test that cache is initialized"""
        assert hasattr(app, 'extensions')
        assert 'cache' in app.extensions
    
    def test_api_initialized(self):
        """Test that Flask-RESTX API is initialized"""
        assert hasattr(app, 'extensions')
        assert 'restx' in app.extensions


class TestMetricsCollection:
    """Test Prometheus metrics collection"""
    
    def test_request_counter_exists(self):
        """Test that request counter metric exists"""
        assert REQUEST_COUNT is not None
        assert REQUEST_COUNT._name == 'http_requests'
    
    def test_request_latency_histogram_exists(self):
        """Test that request latency histogram exists"""
        assert REQUEST_LATENCY is not None
        assert REQUEST_LATENCY._name == 'http_request_duration_seconds'


class TestLogging:
    """Test logging configuration"""
    
    def test_logger_configured(self):
        """Test that structured logging is configured"""
        import structlog
        assert structlog.is_configured()
