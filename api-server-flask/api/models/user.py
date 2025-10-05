"""
User Model
Represents system users and their authentication data
"""

from werkzeug.security import generate_password_hash, check_password_hash
from api.models.base_model import BaseModel
from api.db import db


class Users(BaseModel):
    """
    Model representing system users
    
    Attributes:
        id (int): Primary key
        username (str): Unique username
        email (str): Unique email address
        password (str): Hashed password
        jwt_auth_active (bool): JWT authentication status
    """
    
    __tablename__ = 'users'
    
    id = db.Column(
        db.Integer, 
        primary_key=True,
        comment="Primary key, user identifier"
    )
    username = db.Column(
        db.String(32), 
        nullable=False,
        unique=True,
        index=True,
        comment="Unique username for login"
    )
    email = db.Column(
        db.String(64), 
        nullable=False,  # Changed from nullable=True for better data integrity
        unique=True,
        index=True,
        comment="Unique email address for user communication"
    )
    password = db.Column(
        db.Text,
        nullable=False,
        comment="Hashed password for authentication"
    )
    jwt_auth_active = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Indicates if JWT authentication is currently active for this user"
    )

    def __repr__(self):
        """
        String representation of the Users instance
        
        Returns:
            str: String representation
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def set_password(self, password: str):
        """
        Set hashed password for the user
        
        Args:
            password (str): Plain text password to hash
            
        Raises:
            ValueError: If password is empty or too weak
        """
        if not password or not password.strip():
            raise ValueError("Password cannot be empty")
        
        if len(password.strip()) < 4:  # Minimum password length
            raise ValueError("Password must be at least 4 characters long")
        
        self.password = generate_password_hash(password.strip())

    def check_password(self, password: str) -> bool:
        """
        Verify password against stored hash
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        if not self.password or not password:
            return False
        
        return check_password_hash(self.password, password)

    def check_jwt_auth_active(self) -> bool:
        """
        Check if JWT authentication is active for this user
        
        Returns:
            bool: True if JWT authentication is active
        """
        return self.jwt_auth_active

    def set_jwt_auth_active(self, status: bool):
        """
        Set JWT authentication status
        
        Args:
            status (bool): New JWT authentication status
            
        Raises:
            ValueError: If status is not a boolean
        """
        if not isinstance(status, bool):
            raise ValueError("JWT authentication status must be a boolean")
        
        self.jwt_auth_active = status
        self.save()

    @classmethod
    def get_by_id(cls, user_id: int):
        """
        Get user by ID
        
        Args:
            user_id (int): User ID to retrieve
            
        Returns:
            Users: User instance or None if not found
            
        Raises:
            ValueError: If user_id is not a positive integer
        """
        if not isinstance(user_id, int) or user_id < 1:
            raise ValueError("User ID must be a positive integer")
        
        try:
            return cls.query.get(user_id)
        except Exception as e:
            # current_app.logger.error(f"Error fetching user {user_id}: {str(e)}")
            return None

    @classmethod
    def get_by_email(cls, email: str):
        """
        Get user by email address (case-insensitive)
        
        Args:
            email (str): Email address to search for
            
        Returns:
            Users: User instance or None if not found
        """
        if not email or not email.strip():
            return None
        
        try:
            return cls.query.filter(
                db.func.lower(cls.email) == db.func.lower(email.strip())
            ).first()
        except Exception as e:
            # current_app.logger.error(f"Error fetching user by email '{email}': {str(e)}")
            return None
    
    @classmethod
    def get_by_username(cls, username: str):
        """
        Get user by username (case-insensitive)
        
        Args:
            username (str): Username to search for
            
        Returns:
            Users: User instance or None if not found
        """
        if not username or not username.strip():
            return None
        
        try:
            return cls.query.filter(
                db.func.lower(cls.username) == db.func.lower(username.strip())
            ).first()
        except Exception as e:
            # current_app.logger.error(f"Error fetching user by username '{username}': {str(e)}")
            return None

    def to_json(self):
        """
        Convert user instance to JSON-serializable dictionary
        
        Returns:
            dict: JSON representation of the user (excluding sensitive data)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'jwt_auth_active': self.jwt_auth_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }