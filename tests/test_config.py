"""
Tests for configuration management
"""

import os
import pytest
from src.config import (
    Config, DevelopmentConfig, TestingConfig,
    ProductionConfig, StagingConfig, get_config,
    validate_config, get_database_config, get_redis_config
)


class TestConfig:
    """Test configuration classes"""

    def test_base_config_defaults(self):
        """Test base configuration defaults"""
        config = Config()

        assert config.SECRET_KEY == 'dev-secret-key-change-in-production'
        assert config.DEBUG is False
        assert config.DATABASE_URL == 'sqlite:///dev.db'
        assert config.REDIS_URL == 'redis://localhost:6379'
        assert config.CACHE_TYPE == 'simple'
        assert config.LOG_LEVEL == 'INFO'
        assert config.METRICS_ENABLED is True
        assert config.API_RATE_LIMIT == 100

    def test_development_config(self):
        """Test development configuration"""
        config = DevelopmentConfig()

        assert config.DEBUG is True
        assert config.LOG_LEVEL == 'DEBUG'
        assert config.CACHE_TYPE == 'simple'
        assert config.DATABASE_URL == 'sqlite:///dev.db'
        assert config.REDIS_URL == 'redis://localhost:6379'
        assert config.CORS_ORIGINS == ['*']
        assert config.API_RATE_LIMIT == 1000

    def test_testing_config(self):
        """Test testing configuration"""
        config = TestingConfig()

        assert config.TESTING is True
        assert config.DEBUG is False
        assert config.LOG_LEVEL == 'DEBUG'
        assert config.CACHE_TYPE == 'simple'
        assert config.DATABASE_URL == 'sqlite:///test.db'
        assert config.REDIS_URL == 'redis://localhost:6379'
        assert config.WTF_CSRF_ENABLED is False

    def test_production_config(self):
        """Test production configuration"""
        config = ProductionConfig()

        assert config.DEBUG is False
        assert config.LOG_LEVEL == 'WARNING'
        assert config.CACHE_TYPE == 'redis'
        assert config.SECURITY_HEADERS_ENABLED is True
        assert config.CORS_ORIGINS == [
            'https://devops-demo.com', 'https://www.devops-demo.com']
        assert config.API_RATE_LIMIT == 100
        assert config.SESSION_TIMEOUT == 3600
        assert config.COMPRESSION_ENABLED is True
        assert config.SESSION_COOKIE_SECURE is True
        assert config.SESSION_COOKIE_HTTPONLY is True
        assert config.SESSION_COOKIE_SAMESITE == 'Lax'
        assert config.LOG_FORMAT == 'json'
        assert config.LOG_ROTATION == 'daily'
        assert config.LOG_RETENTION == 30

    def test_staging_config(self):
        """Test staging configuration"""
        config = StagingConfig()

        assert config.DEBUG is False
        assert config.LOG_LEVEL == 'INFO'
        assert config.CACHE_TYPE == 'redis'
        assert config.SECURITY_HEADERS_ENABLED is True
        assert config.CORS_ORIGINS == ['https://staging.devops-demo.com']
        assert config.API_RATE_LIMIT == 500


class TestConfigFunctions:
    """Test configuration utility functions"""

    def test_get_config_default(self):
        """Test getting default configuration"""
        config_class = get_config()
        # In test environment, FLASK_ENV is set to 'testing' in conftest.py
        assert config_class == TestingConfig

    def test_get_config_development(self):
        """Test getting development configuration"""
        config_class = get_config('development')
        assert config_class == DevelopmentConfig

    def test_get_config_testing(self):
        """Test getting testing configuration"""
        config_class = get_config('testing')
        assert config_class == TestingConfig

    def test_get_config_production(self):
        """Test getting production configuration"""
        config_class = get_config('production')
        assert config_class == ProductionConfig

    def test_get_config_staging(self):
        """Test getting staging configuration"""
        config_class = get_config('staging')
        assert config_class == StagingConfig

    def test_get_config_invalid(self):
        """Test getting invalid configuration"""
        config_class = get_config('invalid')
        assert config_class == DevelopmentConfig  # Should return default

    def test_validate_config_success(self):
        """Test successful configuration validation"""
        # Set required environment variables
        os.environ['SECRET_KEY'] = 'test-secret'
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['REDIS_URL'] = 'redis://localhost:6379'

        assert validate_config() is True

        # Clean up
        del os.environ['SECRET_KEY']
        del os.environ['DATABASE_URL']
        del os.environ['REDIS_URL']

    def test_validate_config_failure(self):
        """Test failed configuration validation"""
        # Don't set required environment variables
        # The function should return False when required vars are missing
        # But since Config class has default values, it might return True
        # Let's test the actual behavior
        result = validate_config()
        # The function checks if the environment variables are set
        # Since we haven't set them, it should return False
        assert result is False

    def test_get_database_config_development(self):
        """Test getting database config for development"""
        os.environ['FLASK_ENV'] = 'development'
        db_config = get_database_config()

        assert db_config['pool_size'] == 5
        assert db_config['max_overflow'] == 10
        assert db_config['pool_timeout'] == 30
        assert db_config['pool_recycle'] == 900
        assert db_config['echo'] is True

        del os.environ['FLASK_ENV']

    def test_get_database_config_staging(self):
        """Test getting database config for staging"""
        os.environ['FLASK_ENV'] = 'staging'
        db_config = get_database_config()

        assert db_config['pool_size'] == 10
        assert db_config['max_overflow'] == 20
        assert db_config['pool_timeout'] == 30
        assert db_config['pool_recycle'] == 1800
        assert db_config['echo'] is False

        del os.environ['FLASK_ENV']

    def test_get_database_config_production(self):
        """Test getting database config for production"""
        os.environ['FLASK_ENV'] = 'production'
        db_config = get_database_config()

        assert db_config['pool_size'] == 20
        assert db_config['max_overflow'] == 30
        assert db_config['pool_timeout'] == 30
        assert db_config['pool_recycle'] == 3600
        assert db_config['echo'] is False

        del os.environ['FLASK_ENV']

    def test_get_redis_config_development(self):
        """Test getting Redis config for development"""
        os.environ['FLASK_ENV'] = 'development'
        redis_config = get_redis_config()

        assert redis_config['socket_connect_timeout'] == 10
        assert redis_config['socket_timeout'] == 10
        assert redis_config['retry_on_timeout'] is False
        assert redis_config['health_check_interval'] == 60

        del os.environ['FLASK_ENV']

    def test_get_redis_config_production(self):
        """Test getting Redis config for production"""
        os.environ['FLASK_ENV'] = 'production'
        redis_config = get_redis_config()

        assert redis_config['socket_connect_timeout'] == 5
        assert redis_config['socket_timeout'] == 5
        assert redis_config['retry_on_timeout'] is True
        assert redis_config['health_check_interval'] == 30

        del os.environ['FLASK_ENV']


class TestEnvironmentVariables:
    """Test configuration with environment variables"""

    def test_config_with_env_vars(self):
        """Test configuration with environment variables"""
        # Set environment variables
        os.environ['FLASK_ENV'] = 'production'
        os.environ['LOG_LEVEL'] = 'ERROR'
        os.environ['CACHE_TYPE'] = 'memcached'
        os.environ['API_RATE_LIMIT'] = '500'

        config_class = get_config()

        assert config_class == ProductionConfig

        # Create an instance to test the actual values
        config_instance = config_class()
        assert config_instance.LOG_LEVEL == 'ERROR'
        assert config_instance.CACHE_TYPE == 'memcached'
        assert config_instance.API_RATE_LIMIT == 500

        # Clean up
        del os.environ['FLASK_ENV']
        del os.environ['LOG_LEVEL']
        del os.environ['CACHE_TYPE']
        del os.environ['API_RATE_LIMIT']

    def test_config_with_invalid_env_vars(self):
        """Test configuration with invalid environment variables"""
        # Set invalid environment variables
        os.environ['API_RATE_LIMIT'] = 'invalid'
        os.environ['HEALTH_CHECK_INTERVAL'] = 'not-a-number'

        config = get_config()

        # Should use defaults for invalid values
        assert config.API_RATE_LIMIT == 100
        assert config.HEALTH_CHECK_INTERVAL == 30

        # Clean up
        del os.environ['API_RATE_LIMIT']
        del os.environ['HEALTH_CHECK_INTERVAL']
