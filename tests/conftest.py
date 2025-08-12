"""
Common test configuration and fixtures
"""
import pytest
import os
import sys
from unittest.mock import patch

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    test_env = {
        'SECRET_KEY': 'test_secret_key_for_testing',
        'JWT_SECRET': 'test_jwt_secret_for_testing',
        'FLASK_ENV': 'testing',
        'TESTING': 'true'
    }
    
    with patch.dict(os.environ, test_env, clear=False):
        yield


@pytest.fixture
def sample_database_config():
    """Sample database configuration for testing"""
    return {
        'host': 'test-db-host',
        'port': 5432,
        'name': 'test_db',
        'user': 'test_user',
        'password': 'test_password',
        'ssl_mode': 'require',
        'pool_size': 5,
        'max_overflow': 10
    }


@pytest.fixture
def sample_redis_config():
    """Sample Redis configuration for testing"""
    return {
        'host': 'test-redis-host',
        'port': 6379,
        'password': 'test_redis_password',
        'db': 1,
        'ssl': True
    }


@pytest.fixture
def sample_security_config():
    """Sample security configuration for testing"""
    return {
        'secret_key': 'test_secret_key',
        'jwt_secret': 'test_jwt_secret',
        'bcrypt_rounds': 12,
        'session_timeout': 3600,
        'max_login_attempts': 5,
        'lockout_duration': 900
    }
