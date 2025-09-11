# api/db.py
"""
Database configuration and initialization module.
This file centralizes all database-related setup and utilities.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from sqlalchemy.pool import StaticPool

# Define naming convention for database constraints
# This helps with migrations and makes constraint names predictable
naming_convention = {
    "ix": "ix_%(column_0_label)s",  # Index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # Unique constraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check constraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # Foreign key
    "pk": "pk_%(table_name)s"  # Primary key
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=naming_convention)

# Initialize SQLAlchemy with custom metadata
db = SQLAlchemy(metadata=metadata)

# Initialize Flask-Migrate for database migrations
migrate = Migrate()


def init_db(app):
    """
    Initialize database with Flask application.
    
    Args:
        app: Flask application instance
    """
    # Configure SQLAlchemy
    db.init_app(app)
    
    # Configure Flask-Migrate
    migrate.init_app(app, db)
    
    # Additional database configuration
    configure_database_settings(app)


def configure_database_settings(app):
    """
    Configure additional database settings based on environment.
    
    Args:
        app: Flask application instance
    """
    # Set database engine options based on environment
    if app.config.get('TESTING'):
        # For testing, use in-memory SQLite with specific settings
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': StaticPool,
            'connect_args': {
                'check_same_thread': False,
            },
            'echo': False
        }
    elif app.config.get('DEBUG'):
        # For development, enable SQL logging
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'echo': True,  # Log SQL statements
            'pool_pre_ping': True,  # Verify connections before use
        }
    else:
        # For production, optimize for performance
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 10,
            'pool_timeout': 20,
            'pool_recycle': -1,
            'pool_pre_ping': True,
        }


def create_tables(app=None):
    """
    Create all database tables.
    
    Args:
        app: Flask application instance (optional, uses current app context if None)
    """
    if app:
        with app.app_context():
            db.create_all()
    else:
        db.create_all()


def drop_tables(app=None):
    """
    Drop all database tables.
    WARNING: This will delete all data!
    
    Args:
        app: Flask application instance (optional, uses current app context if None)
    """
    if app:
        with app.app_context():
            db.drop_all()
    else:
        db.drop_all()


def reset_database(app=None):
    """
    Reset database by dropping and recreating all tables.
    WARNING: This will delete all data!
    
    Args:
        app: Flask application instance (optional, uses current app context if None)
    """
    drop_tables(app)
    create_tables(app)


# Database utility functions
def get_session():
    """
    Get current database session.
    
    Returns:
        SQLAlchemy session object
    """
    return db.session


def safe_commit():
    """
    Safely commit database transaction with error handling.
    
    Returns:
        bool: True if commit successful, False otherwise
    """
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        # You might want to log this error
        print(f"Database commit failed: {str(e)}")
        return False


def safe_rollback():
    """
    Safely rollback database transaction.
    """
    try:
        db.session.rollback()
    except Exception as e:
        print(f"Database rollback failed: {str(e)}")


# Context manager for database transactions
class DatabaseTransaction:
    """
    Context manager for handling database transactions safely.
    
    Usage:
        with DatabaseTransaction():
            # Your database operations here
            user = Users(username="test")
            db.session.add(user)
            # Automatic commit on success, rollback on exception
    """
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exception occurred, commit the transaction
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
        else:
            # Exception occurred, rollback the transaction
            db.session.rollback()
        
        return False  # Don't suppress exceptions


# Database health check function
def check_database_connection():
    """
    Check if database connection is healthy.
    
    Returns:
        dict: Connection status and information
    """
    try:
        # Execute a simple query to test connection
        result = db.session.execute('SELECT 1').scalar()
        
        if result == 1:
            return {
                'status': 'healthy',
                'message': 'Database connection is working',
                'engine': str(db.engine.url),
                'pool_size': db.engine.pool.size(),
                'checked_out': db.engine.pool.checkedout(),
            }
        else:
            return {
                'status': 'unhealthy',
                'message': 'Unexpected query result',
                'engine': str(db.engine.url)
            }
            
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}',
            'engine': str(db.engine.url) if hasattr(db, 'engine') else 'Unknown'
        }


# Export commonly used objects
__all__ = [
    'db',
    'migrate', 
    'init_db',
    'create_tables',
    'drop_tables', 
    'reset_database',
    'get_session',
    'safe_commit',
    'safe_rollback',
    'DatabaseTransaction',
    'check_database_connection'
]