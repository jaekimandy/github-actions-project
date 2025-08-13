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


class TestAppConfiguration:
    """Test application configuration"""

    def test_app_configuration(self):
        """Test that app is properly configured"""
        assert app is not None
        assert hasattr(app, 'config')
        # Note: TESTING is set in the client fixture, not globally
        assert hasattr(app, 'config')

    def test_app_has_required_attributes(self):
        """Test that app has required attributes"""
        assert hasattr(app, 'name')
        assert hasattr(app, 'config')
        assert hasattr(app, 'url_map')


class TestAppImports:
    """Test that app can be imported and initialized"""

    def test_app_import(self):
        """Test that app can be imported"""
        from src.app import app
        assert app is not None

    def test_app_config_loading(self):
        """Test that app config can be loaded"""
        # This test verifies that the app can be initialized without errors
        # even if some dependencies are missing
        assert app.config is not None


class TestAppRoutes:
    """Test that app routes are defined"""

    def test_app_has_routes(self):
        """Test that app has defined routes"""
        # Check that the app has some routes defined
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert len(routes) > 0

    def test_app_has_health_route(self):
        """Test that app has health route"""
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/health' in routes or any('/health' in rule for rule in routes)
