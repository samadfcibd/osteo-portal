# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os, random, string
from datetime import timedelta
from urllib.parse import quote_plus

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class BaseConfig():
    
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', None)
    if not JWT_SECRET_KEY:
        JWT_SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))

    GITHUB_CLIENT_ID     = os.getenv('GITHUB_CLIENT_ID' , None)
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_SECRET_KEY', None)
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
    DB_USERNAME = os.getenv('DB_USERNAME' , None)
    DB_PASS     = os.getenv('DB_PASS'     , None)
    DB_HOST     = os.getenv('DB_HOST'     , None)
    DB_PORT     = os.getenv('DB_PORT'     , None)
    DB_NAME     = os.getenv('DB_NAME'     , None)

    USE_SQLITE  = True 

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