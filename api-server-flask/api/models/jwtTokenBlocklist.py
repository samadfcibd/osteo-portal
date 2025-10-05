"""
JWT Token Blocklist Model
Represents revoked JWT tokens for authentication security
"""

from api.models.base_model import BaseModel
from api.db import db


class JWTTokenBlocklist(BaseModel):
    """
    Model representing revoked JWT tokens
    
    Attributes:
        id (int): Primary key
        jwt_token (str): The revoked JWT token
    """
    
    __tablename__ = 'jwt_token_blocklist'
    
    id = db.Column(
        db.Integer, 
        primary_key=True,
        comment="Primary key, blocklist entry identifier"
    )
    jwt_token = db.Column(
        db.String(500), 
        nullable=False,
        unique=True,
        index=True,
        comment="The revoked JWT token string"
    )
    
    def __repr__(self):
        """
        String representation of the JWTTokenBlocklist instance
        
        Returns:
            str: String representation
        """
        token_preview = self.jwt_token[:20] + '...' if len(self.jwt_token) > 20 else self.jwt_token
        return f"<JWTTokenBlocklist(id={self.id}, token='{token_preview}')>"