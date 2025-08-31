# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os, json

from flask import Flask, request
from flask_cors import CORS

from .routes import rest_api
from .models import db

app = Flask(__name__)

app.config.from_object('api.config.BaseConfig')

db.init_app(app)
rest_api.init_app(app)
# CORS(app)

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"],
        "supports_credentials": True
    }
})

# Setup database
@app.before_first_request
def initialize_database():
    try:
        db.create_all()
    except Exception as e:

        print('> Error: DBMS Exception: ' + str(e) )

        # # fallback to SQLite
        # BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        # app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

        # print('> Fallback to SQLite ')
        # db.create_all()

"""
   Custom responses
"""

# @app.after_request
# def after_request(response):
#     """
#        Sends back a custom error with {"success", "msg"} format
#     """

#     if int(response.status_code) >= 400:
#         response_data = json.loads(response.get_data())
#         if "errors" in response_data:
#             response_data = {"success": False,
#                              "msg": list(response_data["errors"].items())[0][1]}
#             response.set_data(json.dumps(response_data))
#         response.headers.add('Content-Type', 'application/json')
#     return response


@app.after_request
def after_request(response):
    """
    Custom response handler that:
    - Skips OPTIONS requests
    - Only processes error responses
    - Maintains CORS headers
    """
    # Skip OPTIONS requests
    if request.method == 'OPTIONS':
        return response
    
    # Only process error responses
    if int(response.status_code) >= 400:
        try:
            response_data = json.loads(response.get_data())
            if "errors" in response_data:
                response_data = {
                    "success": False,
                    "msg": list(response_data["errors"].items())[0][1]
                }
                response.set_data(json.dumps(response_data))
            response.headers.add('Content-Type', 'application/json')
        except json.JSONDecodeError:
            # If response is not JSON, leave it as is
            pass
    
    # Ensure CORS headers are always present
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    
    return response

