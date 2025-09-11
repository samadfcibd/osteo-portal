# api/config.py
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from datetime import timedelta
from urllib.parse import quote_plus

class BaseConfig:
    """Base configuration class with common settings"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'S#perS3crEt_007'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    PDB_FOLDER = 'pdb_files'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # JWT settings
    JWT_EXPIRATION_DELTA = timedelta(hours=1)
    
    # GitHub OAuth (if you're using it)
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    
    # CORS settings
    CORS_ORIGINS = ["http://localhost:3000"]
    

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../db.sqlite3')
    
    # # Enable SQL query logging in development
    # SQLALCHEMY_ENGINE_OPTIONS = {
    #     'echo': True,
    #     'pool_pre_ping': True,
    # }


    USE_SQLITE  = True 

    DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
    DB_USERNAME = os.getenv('DB_USERNAME' , None)
    DB_PASS     = os.getenv('DB_PASS'     , None)
    DB_HOST     = os.getenv('DB_HOST'     , None)
    DB_PORT     = os.getenv('DB_PORT'     , None)
    DB_NAME     = os.getenv('DB_NAME'     , None)

    # try to set up a Relational DBMS
    if DB_ENGINE and DB_NAME and DB_USERNAME:

        try:
            
            # URL encode username and password to handle special characters
            encoded_username = quote_plus(DB_USERNAME) if DB_USERNAME else ''
            encoded_password = quote_plus(DB_PASS) if DB_PASS else ''
            
            # Relational DBMS: PSQL, MySql
            SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
                DB_ENGINE,
                encoded_username,
                encoded_password,
                DB_HOST,
                DB_PORT,
                DB_NAME
            ) 

            USE_SQLITE  = False
            
            # Add MariaDB/MySQL specific engine options
            if 'mysql' in DB_ENGINE:
                SQLALCHEMY_ENGINE_OPTIONS = {
                    'pool_pre_ping': True,
                    'pool_recycle': 300,
                    'connect_args': {
                        'charset': 'utf8mb4',
                    }
                }

        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )
            print('> Fallback to SQLite ')    

    if USE_SQLITE:

        # This will create a file in <app> FOLDER
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../db.sqlite3')
    
    # Production database optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True,
    }

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # Testing database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': 'StaticPool',
        'connect_args': {'check_same_thread': False},
        'echo': False
    }

# Configuration dictionary - THIS IS WHAT WAS MISSING
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# For backwards compatibility with your existing code
# This allows your existing imports to still work
Config = BaseConfig