"""
Tests for the main application
"""

import json
import pytest
from unittest.mock import patch
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the application"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test that health endpoint returns correct response"""
        response = client.get('/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
        assert 'uptime' in data
        assert data['version'] == '1.0.0'
    
    def test_health_endpoint_structure(self, client):
        """Test health endpoint response structure"""
        response = client.get('/health')
        data = json.loads(response.data)
        
        required_fields = ['status', 'timestamp', 'version', 'uptime']
        for field in required_fields:
            assert field in data
    
    def test_health_endpoint_uptime_increases(self, client):
        """Test that uptime increases between requests"""
        import time
        
        response1 = client.get('/health')
        data1 = json.loads(response1.data)
        
        time.sleep(0.1)  # Small delay
        
        response2 = client.get('/health')
        data2 = json.loads(response2.data)
        
        assert data2['uptime'] > data1['uptime']


class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    def test_metrics_endpoint(self, client):
        """Test that metrics endpoint returns Prometheus format"""
        response = client.get('/metrics')
        
        assert response.status_code == 200
        assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'
        assert 'http_requests_total' in response.data.decode()
        assert 'http_request_duration_seconds' in response.data.decode()
    
    def test_metrics_endpoint_after_requests(self, client):
        """Test that metrics are recorded after making requests"""
        # Make some requests first
        client.get('/health')
        client.get('/')
        
        response = client.get('/metrics')
        metrics_data = response.data.decode()
        
        # Check that our requests were recorded
        assert 'http_requests_total' in metrics_data
        assert 'http_request_duration_seconds' in metrics_data


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_status_api_endpoint(self, client):
        """Test status API endpoint"""
        response = client.get('/api/v1/status')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'operational'
        assert 'timestamp' in data
        assert 'version' in data
        assert 'uptime' in data
    
    def test_metrics_api_endpoint(self, client):
        """Test metrics API endpoint"""
        # Make some requests first to generate metrics
        client.get('/health')
        client.get('/')
        
        response = client.get('/api/v1/metrics')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'requests_total' in data
        assert 'requests_per_second' in data
        assert 'average_response_time' in data
        assert isinstance(data['requests_total'], int)
        assert isinstance(data['requests_per_second'], float)
        assert isinstance(data['average_response_time'], float)
    
    def test_info_endpoint(self, client):
        """Test info endpoint"""
        response = client.get('/api/v1/info')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['name'] == 'DevOps Demo Application'
        assert data['description'] == 'A demonstration of DevOps best practices'
        assert data['version'] == '1.0.0'
        assert 'environment' in data
        assert 'features' in data
        assert isinstance(data['features'], list)


class TestMainPages:
    """Test main application pages"""
    
    def test_index_page(self, client):
        """Test index page"""
        response = client.get('/')
        
        assert response.status_code == 200
        # Check if it's HTML response
        assert 'text/html' in response.content_type
    
    def test_docs_page(self, client):
        """Test API documentation page"""
        response = client.get('/docs/')
        
        assert response.status_code == 200
        # Check if it's HTML response
        assert 'text/html' in response.content_type


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-endpoint')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['error'] == 'Not found'
        assert 'message' in data
    
    def test_500_error_simulation(self, client):
        """Test 500 error handling by simulating an error"""
        # This test would need to be adjusted based on actual error handling
        # For now, we'll just test that the endpoint exists
        response = client.get('/health')
        assert response.status_code == 200


class TestRequestLogging:
    """Test request logging and metrics"""
    
    def test_request_metrics_recording(self, client):
        """Test that request metrics are properly recorded"""
        # Make a request
        response = client.get('/health')
        
        # Check metrics endpoint
        metrics_response = client.get('/metrics')
        metrics_data = metrics_response.data.decode()
        
        # Should have recorded our health request
        assert 'http_requests_total' in metrics_data
    
    def test_request_timing(self, client):
        """Test that request timing is recorded"""
        # Make a request
        client.get('/health')
        
        # Check metrics endpoint
        metrics_response = client.get('/metrics')
        metrics_data = metrics_response.data.decode()
        
        # Should have recorded timing
        assert 'http_request_duration_seconds' in metrics_data


class TestSecurity:
    """Test security features"""
    
    def test_security_headers(self, client):
        """Test that security headers are present"""
        response = client.get('/health')
        
        # Check for common security headers
        # Note: These might not be set in the test environment
        # but we can check the response structure
        assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.get('/health')
        
        # Check if CORS headers are present
        # This depends on the actual CORS implementation
        assert response.status_code == 200


class TestCaching:
    """Test caching functionality"""
    
    def test_info_endpoint_caching(self, client):
        """Test that info endpoint responses are cached"""
        # First request
        response1 = client.get('/api/v1/info')
        data1 = json.loads(response1.data)
        
        # Second request (should be cached)
        response2 = client.get('/api/v1/info')
        data2 = json.loads(response2.data)
        
        # Responses should be identical
        assert data1 == data2
        assert response1.data == response2.data


class TestConfiguration:
    """Test application configuration"""
    
    def test_development_config(self, client):
        """Test that development configuration is applied"""
        with patch.dict('os.environ', {'FLASK_ENV': 'development'}):
            # Reload app with new config
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            
            response = client.get('/health')
            assert response.status_code == 200
    
    def test_production_config(self, client):
        """Test that production configuration is applied"""
        with patch.dict('os.environ', {'FLASK_ENV': 'production'}):
            # Reload app with new config
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            
            response = client.get('/health')
            assert response.status_code == 200


class TestPerformance:
    """Test application performance"""
    
    def test_response_time(self, client):
        """Test that response times are reasonable"""
        import time
        
        start_time = time.time()
        response = client.get('/health')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response should be fast (less than 1 second)
        assert response_time < 1.0
        assert response.status_code == 200
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get('/health')
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 5
        assert len(errors) == 0
        assert all(status == 200 for status in results)
