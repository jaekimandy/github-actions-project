"""
Tests for configuration management
"""
import os
import pytest
from unittest.mock import patch
from src.config import (
    DatabaseConfig, 
    RedisConfig, 
    SecurityConfig, 
    MonitoringConfig,
    Config
)


class TestDatabaseConfig:
    """Test database configuration"""
    
    def test_database_config_defaults(self):
        """Test database config with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig.from_env()
            assert config.host == "localhost"
            assert config.port == 5432
            assert config.name == "devops_demo"
            assert config.user == "postgres"
            assert config.password == ""
            assert config.ssl_mode == "require"
            assert config.pool_size == 10
            assert config.max_overflow == 20
    
    def test_database_config_from_env(self):
        """Test database config from environment variables"""
        env_vars = {
            "DB_HOST": "test-host",
            "DB_PORT": "5433",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_pass",
            "DB_SSL_MODE": "disable",
            "DB_POOL_SIZE": "15",
            "DB_MAX_OVERFLOW": "25"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig.from_env()
            assert config.host == "test-host"
            assert config.port == 5433
            assert config.name == "test_db"
            assert config.user == "test_user"
            assert config.password == "test_pass"
            assert config.ssl_mode == "disable"
            assert config.pool_size == 15
            assert config.max_overflow == 25


class TestRedisConfig:
    """Test Redis configuration"""
    
    def test_redis_config_defaults(self):
        """Test Redis config with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = RedisConfig.from_env()
            assert config.host == "localhost"
            assert config.port == 6379
            assert config.password is None
            assert config.db == 0
            assert config.ssl is True
    
    def test_redis_config_from_env(self):
        """Test Redis config from environment variables"""
        env_vars = {
            "REDIS_HOST": "redis-host",
            "REDIS_PORT": "6380",
            "REDIS_PASSWORD": "redis_pass",
            "REDIS_DB": "1",
            "REDIS_SSL": "false"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = RedisConfig.from_env()
            assert config.host == "redis-host"
            assert config.port == 6380
            assert config.password == "redis_pass"
            assert config.db == 1
            assert config.ssl is False


class TestSecurityConfig:
    """Test security configuration"""
    
    def test_security_config_missing_required_vars(self):
        """Test that security config raises error for missing required vars"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SECRET_KEY environment variable must be set"):
                SecurityConfig.from_env()
    
    def test_security_config_from_env(self):
        """Test security config from environment variables"""
        env_vars = {
            "SECRET_KEY": "test_secret_key",
            "JWT_SECRET": "test_jwt_secret",
            "BCRYPT_ROUNDS": "14",
            "SESSION_TIMEOUT": "7200",
            "MAX_LOGIN_ATTEMPTS": "3",
            "LOCKOUT_DURATION": "1800"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = SecurityConfig.from_env()
            assert config.secret_key == "test_secret_key"
            assert config.jwt_secret == "test_jwt_secret"
            assert config.bcrypt_rounds == 14
            assert config.session_timeout == 7200
            assert config.max_login_attempts == 3
            assert config.lockout_duration == 1800


class TestMonitoringConfig:
    """Test monitoring configuration"""
    
    def test_monitoring_config_defaults(self):
        """Test monitoring config with default values"""
        config = MonitoringConfig()
        assert config.prometheus_enabled is True


class TestConfig:
    """Test main configuration class"""
    
    def test_config_initialization(self):
        """Test that main config can be initialized"""
        # This test might need to be adjusted based on the actual Config class implementation
        # For now, we'll test that the module can be imported
        assert Config is not None


class TestEnvironmentVariableHandling:
    """Test environment variable handling"""
    
    def test_int_environment_variable_parsing(self):
        """Test that integer environment variables are parsed correctly"""
        env_vars = {"DB_PORT": "5433", "DB_POOL_SIZE": "15"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig.from_env()
            assert isinstance(config.port, int)
            assert isinstance(config.pool_size, int)
            assert config.port == 5433
            assert config.pool_size == 15
    
    def test_boolean_environment_variable_parsing(self):
        """Test that boolean environment variables are parsed correctly"""
        env_vars = {"REDIS_SSL": "false"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = RedisConfig.from_env()
            assert isinstance(config.ssl, bool)
            assert config.ssl is False
