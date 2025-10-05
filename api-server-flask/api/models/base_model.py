"""
Base Model
Abstract base class with common fields and methods for all models
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    """
    Abstract base model providing common fields and methods
    
    Attributes:
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
    """
    
    __abstract__ = True
    
    created_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Record creation timestamp in UTC"
    )
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Record last update timestamp in UTC"
    )
    
    
    def save(self):
        """
        Save the current instance to the database
        
        Raises:
            Exception: If database operation fails
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Re-raise with context for better error handling
            raise Exception(f"Failed to save {self.__class__.__name__}: {str(e)}") from e
        
    def update(self, **kwargs):
        """
        Update model attributes and save to database
        
        Args:
            **kwargs: Attribute names and values to update
            
        Raises:
            ValueError: If invalid attributes are provided
            Exception: If database operation fails
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    raise ValueError(f"Invalid attribute: {key}")
            
            self.save()
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update {self.__class__.__name__}: {str(e)}") from e
        
    def delete(self):
        """
        Delete the current instance from the database
        
        Raises:
            Exception: If database operation fails
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete {self.__class__.__name__}: {str(e)}") from e
        
    def to_dict(self):
        """
        Convert model instance to dictionary
        
        Returns:
            dict: Dictionary representation of the model instance
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Handle datetime serialization
            if isinstance(value, datetime):
                value = value.isoformat()
                
            result[column.name] = value
            
        return result