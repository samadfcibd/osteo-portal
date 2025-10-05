# api/__init__.py (Application Factory Pattern)

import os
import json
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_restx import Api

from .db import init_db
from .config import config


def create_app(config_name=None):
    '''
    Application factory pattern for creating Flask app instances.
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
    
    Returns:
        Flask: Configured Flask application instance
    '''
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask application
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_db(app)
    
    # Configure CORS
    configure_cors(app)

    # Register root route to redirect to docs
    register_root_route(app)
    
    # Register API routes (this will create the API instance)
    api = register_api_routes(app)    
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register request/response handlers
    register_request_handlers(app)
    
    return app


def configure_cors(app):
    '''Configure CORS settings'''
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ["http://localhost:3000"]),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Authorization", "Content-Type"],
            "supports_credentials": True
        }
    })

def register_root_route(app):
    '''Register root route to redirect to API documentation'''
    
    @app.route('/')
    def root_redirect():  # CHANGED: Different function name to avoid conflicts
        '''Redirect root to API documentation'''
        return redirect('/docs/')


def register_api_routes(app):
    '''Register all API routes and namespaces'''
    
    # Create API instance FIRST
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Enter: Bearer &lt;your_token&gt;'
        }
    }
    
    api = Api(
        app,
        version="1.0", 
        title="Osteoarthritis management portal API",
        description="A comprehensive API for osteoarthritis disease management research data",
        doc='/docs/',
        authorizations=authorizations,
        security='Bearer Auth'
    )

    # Import namespaces AFTER creating the API
    from .auth.routes import auth_ns
    from .organisms.routes import organisms_ns
    from .organismUpload.routes import organismUpload_ns
    from .pdbUpload.routes import pdbUpload_ns
    # from .uploads.routes import uploads_ns
    # from .imports.routes import imports_ns
    
    # Register namespaces with the API instance
    api.add_namespace(auth_ns, path='/api/users')
    api.add_namespace(organisms_ns, path='/api/organisms')
    api.add_namespace(organismUpload_ns, path='/api/csv-import')
    api.add_namespace(pdbUpload_ns, path='/api')
    # api.add_namespace(uploads_ns, path='/api/uploads') 
    # api.add_namespace(imports_ns, path='/api/imports')

    return api



def register_error_handlers(app):
    '''Register custom error handlers'''
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            "success": False,
            "msg": "Bad request",
            "error": str(error),
            "documentation": "/docs"
        }, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {
            "success": False,
            "msg": "Unauthorized access",
            "documentation": "/docs"
        }, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {
            "success": False,
            "msg": "Forbidden",
            "documentation": "/docs"
        }, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            "success": False,
            "msg": "Resource not found",
            "documentation": "/docs",
            "available_endpoints": {
                "authentication": "/api/auth",
                "organisms": "/api/organisms",
                "data_upload": "/api/upload", 
                "pdb_management": "/api/pdb",
                "documentation": "/docs"
            }
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            "success": False,
            "msg": "Internal server error",
            "documentation": "/docs"
        }, 500

def register_request_handlers(app):
    '''Register before/after request handlers'''
    
    @app.before_first_request
    def initialize_database():
        '''Initialize database tables on first request'''
        try:
            from .db import db
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f'Database initialization error: {str(e)}')
            # Add fallback logic here if needed
    
    @app.after_request
    def after_request(response):
        '''Custom response handler'''
        # Skip OPTIONS requests
        if request.method == 'OPTIONS':
            return response
        
        # Process error responses
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
            except (json.JSONDecodeError, ValueError):
                # If response is not JSON, leave it as is
                pass
        
        return response
    
    @app.before_request
    def log_request_info():
        '''Log request information (optional, useful for debugging)'''
        if app.config.get('DEBUG'):
            print(f"Request: {request.method} {request.url}")


# For backwards compatibility, create a default app instance
app = create_app()