"""
Configuration management for DevOps Demo Application
This module handles environment-specific configuration and secrets management
"""

import os
from typing import Optional


class Config:
    """Base configuration class"""

    # Basic Flask configuration
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'

    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///dev.db'

    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'

    # Cache configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'simple'
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_TTL', 300))

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'text')

    # Security configuration
    SECURITY_HEADERS_ENABLED = os.environ.get(
        'SECURITY_HEADERS_ENABLED', 'true').lower() == 'true'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))

    # Monitoring configuration
    METRICS_ENABLED = os.environ.get(
        'METRICS_ENABLED', 'true').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 30))

    # Application configuration
    APP_NAME = "DevOps Demo Application"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "A demonstration of DevOps best practices"

    # Session configuration
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))

    # File upload configuration
    MAX_UPLOAD_SIZE = os.environ.get('MAX_UPLOAD_SIZE', '10MB')

    # Compression configuration
    COMPRESSION_ENABLED = os.environ.get(
        'COMPRESSION_ENABLED', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Development environment configuration"""

    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    CACHE_TYPE = 'simple'
    DATABASE_URL = 'sqlite:///dev.db'
    REDIS_URL = 'redis://localhost:6379'
    CORS_ORIGINS = ['*']
    API_RATE_LIMIT = 1000


class TestingConfig(Config):
    """Testing environment configuration"""

    TESTING = True
    DEBUG = False
    LOG_LEVEL = 'DEBUG'
    CACHE_TYPE = 'simple'
    DATABASE_URL = 'sqlite:///test.db'
    REDIS_URL = 'redis://localhost:6379'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration"""

    DEBUG = False
    LOG_LEVEL = 'WARNING'
    CACHE_TYPE = 'redis'
    SECURITY_HEADERS_ENABLED = True
    CORS_ORIGINS = ['https://devops-demo.com', 'https://www.devops-demo.com']
    API_RATE_LIMIT = 100
    SESSION_TIMEOUT = 3600
    COMPRESSION_ENABLED = True

    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Production logging
    LOG_FORMAT = 'json'
    LOG_ROTATION = 'daily'
    LOG_RETENTION = 30


class StagingConfig(Config):
    """Staging environment configuration"""

    DEBUG = False
    LOG_LEVEL = 'INFO'
    CACHE_TYPE = 'redis'
    SECURITY_HEADERS_ENABLED = True
    CORS_ORIGINS = ['https://staging.devops-demo.com']
    API_RATE_LIMIT = 500


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    return config.get(config_name, config['default'])


def validate_config() -> bool:
    """Validate that all required configuration is present"""
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'REDIS_URL'
    ]

    missing_vars = []
    for var in required_vars:
        if not getattr(Config, var, None):
            missing_vars.append(var)

    if missing_vars:
        print(f"Missing required configuration variables: {missing_vars}")
        return False

    return True


# Environment-specific configuration
def get_database_config():
    """Get database configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')

    if env == 'production':
        return {
            'pool_size': 20,
            'max_overflow': 30,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'echo': False
        }
    elif env == 'staging':
        return {
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 30,
            'pool_recycle': 1800,
            'echo': False
        }
    else:
        return {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 900,
            'echo': True
        }


def get_redis_config():
    """Get Redis configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')

    if env == 'production':
        return {
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30
        }
    else:
        return {
            'socket_connect_timeout': 10,
            'socket_timeout': 10,
            'retry_on_timeout': False,
            'health_check_interval': 60
        }
