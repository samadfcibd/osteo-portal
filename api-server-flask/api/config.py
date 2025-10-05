"""
Application Configuration Settings
Environment-specific configurations for development, production, and testing
"""

import os
from datetime import timedelta
from urllib.parse import quote_plus
from typing import Dict, Any, Optional


def _build_mysql_uri(engine: str, username: str, password: str, host: str, port: str, database: str) -> str:
    """
    Build MySQL connection URI with proper encoding
    """
    # Default to pymysql driver if not specified
    if engine == 'mysql':
        engine = 'mysql+pymysql'
    
    # URL encode credentials to handle special characters
    encoded_username = quote_plus(username) if username else ''
    encoded_password = quote_plus(password) if password else ''
    
    # Build connection URI
    uri = f"{engine}://{encoded_username}:{encoded_password}@{host}:{port}/{database}"
    
    # Add MySQL-specific connection parameters
    uri += "?charset=utf8mb4&ssl_disabled=true"
    
    return uri

class BaseConfig:
    """Base configuration class with common settings across all environments"""

    # Flask Application
    FLASK_APP: str = os.environ.get('FLASK_APP', 'run.py')
    
    # Application Security
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = False
    TESTING: bool = False

    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: Dict[str, Any] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False,
    }

    # JWT Configuration
    TOKEN_EXPIRATION_MINUTES: int = int(os.environ.get('JWT_EXPIRATION_MINUTES', '30'))
    JWT_EXPIRATION_DELTA: timedelta = timedelta(minutes=TOKEN_EXPIRATION_MINUTES)

    # File Upload Configuration
    UPLOAD_FOLDER: str = os.environ.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'uploads'))
    PDB_FOLDER: str = os.environ.get('PDB_FOLDER', 'pdb_files')
    MAX_CONTENT_LENGTH: int = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))  # 16MB

    # CORS Configuration
    CORS_ORIGINS: list = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')

    
    # GitHub OAuth (if you're using it)
    # GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    # GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    
    # API Configuration
    API_PREFIX: str = os.environ.get('API_PREFIX', '/api')
    API_VERSION: str = os.environ.get('API_VERSION', 'v1')

    # Logging Configuration
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE: str = os.environ.get('LOG_FILE', 'app.log')
    LOG_MAX_BYTES: int = int(os.environ.get('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.environ.get('LOG_BACKUP_COUNT', '5'))

    @classmethod
    def init_app(cls, app):
        """Initialize application with this configuration"""
        # Ensure upload directory exists
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(cls.UPLOAD_FOLDER, cls.PDB_FOLDER), exist_ok=True)
    

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    """Development environment configuration"""
    
    DEBUG: bool = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG')

    # MySQL Development Database Configuration
    DB_ENGINE: str = os.getenv('DB_ENGINE', 'mysql+pymysql')
    DB_USERNAME: str = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD: str = os.getenv('DB_PASS', 'root@123')  # FIXED: Using DB_PASS from .env
    DB_HOST: str = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT: str = os.getenv('DB_PORT', '3306')
    DB_NAME: str = os.getenv('DB_NAME', 'osteoarthritis_db')
    
    # Build MySQL connection URI
    SQLALCHEMY_DATABASE_URI: str = _build_mysql_uri(
        DB_ENGINE, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
    )
    
    # Development-specific database options
    SQLALCHEMY_ENGINE_OPTIONS: Dict[str, Any] = {
        **BaseConfig.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': True,
        'echo_pool': True,
    }

    @classmethod
    def init_app(cls, app):
        """Development-specific initialization"""
        super().init_app(app)
        
        # Development logging setup
        import logging
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )


class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    
    DEBUG: bool = False
    LOG_LEVEL: str = 'WARNING'
    
    # MySQL Production Database Configuration
    DB_ENGINE: str = os.getenv('DB_ENGINE', 'mysql')
    DB_USERNAME: str = os.getenv('DB_USERNAME', '')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_HOST: str = os.getenv('DB_HOST', '')
    DB_PORT: str = os.getenv('DB_PORT', '3306')
    DB_NAME: str = os.getenv('DB_NAME', 'biomolecule_prod')
    
    # Build MySQL connection URI
    SQLALCHEMY_DATABASE_URI: str = _build_mysql_uri(
        DB_ENGINE, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
    )
    
    # Production database optimizations
    SQLALCHEMY_ENGINE_OPTIONS: Dict[str, Any] = {
        **BaseConfig.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': int(os.getenv('DB_POOL_SIZE', '20')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '30')),
        'pool_timeout': 30,
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
    }
    
    # Production security settings
    SECRET_KEY: str = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production environment")

    @classmethod
    def init_app(cls, app):
        """Production-specific initialization"""
        super().init_app(app)
        
        # Production logging with rotation
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            cls.LOG_FILE,
            maxBytes=cls.LOG_MAX_BYTES,
            backupCount=cls.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
        file_handler.setLevel(getattr(logging, cls.LOG_LEVEL))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, cls.LOG_LEVEL))

class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    
    TESTING: bool = True
    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'
    
    # MySQL Testing Database Configuration
    DB_ENGINE: str = os.getenv('DB_ENGINE', 'mysql')
    DB_USERNAME: str = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'password')
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: str = os.getenv('DB_PORT', '3306')
    DB_NAME: str = os.getenv('DB_NAME', 'biomolecule_test')
    
    # Build MySQL connection URI
    SQLALCHEMY_DATABASE_URI: str = _build_mysql_uri(
        DB_ENGINE, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
    )
    
    # Testing-specific settings
    SQLALCHEMY_ENGINE_OPTIONS: Dict[str, Any] = {
        **BaseConfig.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': False,
    }
    
    # Testing features
    WTF_CSRF_ENABLED: bool = False
    PRESERVE_CONTEXT_ON_EXCEPTION: bool = False

class DockerConfig(DevelopmentConfig):
    """Docker-specific development configuration"""
    
    DB_HOST: str = os.getenv('DB_HOST', 'mysql')
    DB_PASSWORD: str = os.getenv('DB_PASS', 'docker_password')


def get_config(config_name: Optional[str] = None) -> BaseConfig:
    """
    Retrieve configuration based on environment
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_mapping = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'docker': DockerConfig,
    }
    
    config_class = config_mapping.get(config_name.lower())
    if not config_class:
        raise ValueError(f"Invalid configuration name: {config_name}")
    
    return config_class


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig,
}

# For backwards compatibility
Config = BaseConfig