from api import create_app
from api.db import db
import os

app = create_app()

with app.app_context():
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Check what tables exist
    tables = db.session.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    
    print(f"Existing tables: {[table[0] for table in tables]}")
    
    # Check registered models
    print("SQLAlchemy models:")
    for name, model in db.Model.registry._class_registry.items():
        if hasattr(model, '__tablename__'):
            print(f"  - {name}: {model.__tablename__}")