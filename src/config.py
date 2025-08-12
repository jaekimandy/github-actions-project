"""
Configuration management for DevOps Demo Application
This module demonstrates configuration best practices including:
- Environment-based configuration
- Security considerations
- Validation and defaults
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str
    port: int
    name: str
    user: str
    password: str
    ssl_mode: str = 'require'
    pool_size: int = 10
    max_overflow: int = 20
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database config from environment variables"""
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            name=os.getenv('DB_NAME', 'devops_demo'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            ssl_mode=os.getenv('DB_SSL_MODE', 'require'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20'))
        )


@dataclass
class RedisConfig:
    """Redis configuration settings"""
    host: str
    port: int
    password: Optional[str] = None
    db: int = 0
    ssl: bool = True
    
    @classmethod
    def from_env(cls) -> 'RedisConfig':
        """Create Redis config from environment variables"""
        return cls(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB', '0')),
            ssl=os.getenv('REDIS_SSL', 'true').lower() == 'true'
        )


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    secret_key: str
    jwt_secret: str
    bcrypt_rounds: int = 12
    session_timeout: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Create security config from environment variables"""
        return cls(
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
            jwt_secret=os.getenv('JWT_SECRET', 'jwt-secret-key-change-in-production'),
            bcrypt_rounds=int(os.getenv('BCRYPT_ROUNDS', '12')),
            session_timeout=int(os.getenv('SESSION_TIMEOUT', '3600')),
            max_login_attempts=int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
            lockout_duration=int(os.getenv('LOCKOUT_DURATION', '900'))
        )


@dataclass
class MonitoringConfig:
    """Monitoring configuration settings"""
    prometheus_enabled: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    log_level: str = 'INFO'
    structured_logging: bool = True
    
    @classmethod
    def from_env(cls) -> 'MonitoringConfig':
        """Create monitoring config from environment variables"""
        return cls(
            prometheus_enabled=os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true',
            metrics_port=int(os.getenv('METRICS_PORT', '9090')),
            health_check_interval=int(os.getenv('HEALTH_CHECK_INTERVAL', '30')),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            structured_logging=os.getenv('STRUCTURED_LOGGING', 'true').lower() == 'true'
        )


@dataclass
class CacheConfig:
    """Cache configuration settings"""
    type: str = 'redis'
    host: str = 'localhost'
    port: int = 6379
    password: Optional[str] = None
    db: int = 1
    default_timeout: int = 300
    key_prefix: str = 'devops_demo:'
    
    @classmethod
    def from_env(cls) -> 'CacheConfig':
        """Create cache config from environment variables"""
        return cls(
            type=os.getenv('CACHE_TYPE', 'redis'),
            host=os.getenv('CACHE_HOST', 'localhost'),
            port=int(os.getenv('CACHE_PORT', '6379')),
            password=os.getenv('CACHE_PASSWORD'),
            db=int(os.getenv('CACHE_DB', '1')),
            default_timeout=int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300')),
            key_prefix=os.getenv('CACHE_KEY_PREFIX', 'devops_demo:')
        )


@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = False
    testing: bool = False
    host: str = '0.0.0.0'
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create app config from environment variables"""
        return cls(
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            testing=os.getenv('TESTING', 'false').lower() == 'true',
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', '8000')),
            workers=int(os.getenv('WORKERS', '4')),
            timeout=int(os.getenv('TIMEOUT', '30'))
        )


class Config:
    """Main configuration class that aggregates all configs"""
    
    def __init__(self):
        self.database = DatabaseConfig.from_env()
        self.redis = RedisConfig.from_env()
        self.security = SecurityConfig.from_env()
        self.monitoring = MonitoringConfig.from_env()
        self.cache = CacheConfig.from_env()
        self.app = AppConfig.from_env()
        
        # Flask-specific configuration
        self.SECRET_KEY = self.security.secret_key
        self.DEBUG = self.app.debug
        self.TESTING = self.app.testing
        
        # Cache configuration
        self.CACHE_TYPE = self.cache.type
        self.CACHE_REDIS_HOST = self.cache.host
        self.CACHE_REDIS_PORT = self.cache.port
        self.CACHE_REDIS_PASSWORD = self.cache.password
        self.CACHE_REDIS_DB = self.cache.db
        self.CACHE_DEFAULT_TIMEOUT = self.cache.default_timeout
        self.CACHE_KEY_PREFIX = self.cache.key_prefix
        
        # Database configuration
        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{self.database.user}:{self.database.password}"
            f"@{self.database.host}:{self.database.port}/{self.database.name}"
            f"?sslmode={self.database.ssl_mode}"
        )
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': self.database.pool_size,
            'max_overflow': self.database.max_overflow,
            'pool_pre_ping': True,
            'pool_recycle': 300
        }
        
        # Security configuration
        self.SESSION_COOKIE_SECURE = not self.app.debug
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = 'Lax'
        self.PERMANENT_SESSION_LIFETIME = self.security.session_timeout
        
        # Logging configuration
        self.LOG_LEVEL = self.monitoring.log_level
        self.STRUCTURED_LOGGING = self.monitoring.structured_logging
        
        # Monitoring configuration
        self.PROMETHEUS_ENABLED = self.monitoring.prometheus_enabled
        self.METRICS_PORT = self.monitoring.metrics_port
        self.HEALTH_CHECK_INTERVAL = self.monitoring.health_check_interval
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            'app': {
                'debug': self.app.debug,
                'testing': self.app.testing,
                'host': self.app.host,
                'port': self.app.port,
                'workers': self.app.workers,
                'timeout': self.app.timeout
            },
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'name': self.database.name,
                'user': self.database.user,
                'ssl_mode': self.database.ssl_mode,
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'db': self.redis.db,
                'ssl': self.redis.ssl
            },
            'cache': {
                'type': self.cache.type,
                'host': self.cache.host,
                'port': self.cache.port,
                'db': self.cache.db,
                'default_timeout': self.cache.default_timeout,
                'key_prefix': self.cache.key_prefix
            },
            'monitoring': {
                'prometheus_enabled': self.monitoring.prometheus_enabled,
                'metrics_port': self.monitoring.metrics_port,
                'health_check_interval': self.monitoring.health_check_interval,
                'log_level': self.monitoring.log_level,
                'structured_logging': self.monitoring.structured_logging
            }
        }
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        try:
            # Validate required fields
            if not self.security.secret_key or self.security.secret_key == 'dev-secret-key-change-in-production':
                raise ValueError("SECRET_KEY must be set and changed from default")
            
            if not self.security.jwt_secret or self.security.jwt_secret == 'jwt-secret-key-change-in-production':
                raise ValueError("JWT_SECRET must be set and changed from default")
            
            # Validate port ranges
            if not (1 <= self.app.port <= 65535):
                raise ValueError("Port must be between 1 and 65535")
            
            if not (1 <= self.database.port <= 65535):
                raise ValueError("Database port must be between 1 and 65535")
            
            if not (1 <= self.redis.port <= 65535):
                raise ValueError("Redis port must be between 1 and 65535")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    def __init__(self):
        super().__init__()
        self.app.debug = True
        self.app.testing = False
        self.monitoring.log_level = 'DEBUG'
        self.cache.type = 'simple'  # Use simple cache for development


class TestingConfig(Config):
    """Testing environment configuration"""
    
    def __init__(self):
        super().__init__()
        self.app.debug = False
        self.app.testing = True
        self.monitoring.log_level = 'DEBUG'
        self.cache.type = 'simple'
        self.database.name = 'devops_demo_test'


class ProductionConfig(Config):
    """Production environment configuration"""
    
    def __init__(self):
        super().__init__()
        self.app.debug = False
        self.app.testing = False
        self.monitoring.log_level = 'WARNING'
        self.cache.type = 'redis'
        self.security.bcrypt_rounds = 14  # Higher security in production


# Configuration factory
def get_config(environment: str = None) -> Config:
    """Get configuration based on environment"""
    if environment is None:
        environment = os.getenv('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    config_class = configs.get(environment.lower(), DevelopmentConfig)
    return config_class() 