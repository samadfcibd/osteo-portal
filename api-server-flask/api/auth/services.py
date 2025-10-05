"""
Authentication Service
Handles user authentication, token management, and security operations
"""

from datetime import datetime, timezone, timedelta
import jwt
from flask import current_app

from api.models.user import Users
from api.models.jwtTokenBlocklist import JWTTokenBlocklist
from api.db import db

class AuthService:
    """Service class for authentication-related operations"""

    # Token expiration time (30 minutes)
    @staticmethod
    def get_token_expiration_minutes():
        return current_app.config.get('TOKEN_EXPIRATION_MINUTES', 30)


    @staticmethod
    def create_user(username: str, email: str, password: str) -> Users:
        """
        Create a new user with the provided credentials
        
        Args:
            username (str): User's username
            email (str): User's email address
            password (str): User's password
            
        Returns:
            Users: The created user object
            
        Raises:
            ValueError: If email is already taken or validation fails
            Exception: For database or other unexpected errors
        """

        # Check if email already exists
        if Users.get_by_email(email):
            raise ValueError("Email address is already registered")
        
        # Create new user instance
        user = Users(username=username, email=email)
        user.set_password(password)
        user.save()

        return user
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> tuple:
        """
        Authenticate user credentials and generate JWT token
        
        Args:
            email (str): User's email address
            password (str): User's password
            
        Returns:
            tuple: (token, user) where token is JWT string and user is User object
            
        Raises:
            ValueError: If credentials are invalid
            Exception: For token generation or database errors
        """

        # Find user by email
        user = Users.get_by_email(email)

        # Validate user exists and password is correct
        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password")
        

        # Generate JWT token with expiration
        token_payload = {
            'email': email,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=AuthService.get_token_expiration_minutes()),
            'iat': datetime.now(timezone.utc)  # Issued at time
        }
        
        token = jwt.encode(
            token_payload,
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        
        # Activate JWT authentication for user
        user.set_jwt_auth_active(True)
        user.save()
        
        return token, user
    
    @staticmethod
    def revoke_token(token: str) -> None:
        """
        Revoke a JWT token by adding it to the blocklist
        
        Args:
            token (str): The JWT token to revoke
            
        Raises:
            Exception: If there's an error saving to the database
        """
        jwt_block = JWTTokenBlocklist(jwt_token=token)
        jwt_block.save()
    
    @staticmethod
    def is_token_revoked(token: str) -> bool:
        """
        Check if a token has been revoked
        
        Args:
            token (str): The JWT token to check
            
        Returns:
            bool: True if token is revoked, False otherwise
        """
        return db.session.query(JWTTokenBlocklist.id)\
                        .filter_by(jwt_token=token)\
                        .scalar() is not None
    
    
    
    
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and validate JWT token without checking revocation
        
        Args:
            token (str): JWT token to decode
            
        Returns:
            dict: Decoded token payload
            
        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

    @staticmethod
    def refresh_token(old_token: str) -> str:
        """
        Refresh an existing token (revokes old token, issues new one)
        
        Args:
            old_token (str): The existing token to refresh
            
        Returns:
            str: New JWT token
            
        Raises:
            ValueError: If old token is invalid or user not found
        """
        try:
            # Decode the old token to get user email
            payload = AuthService.decode_token(old_token)
            email = payload.get('email')
            
            # Find the user
            user = Users.get_by_email(email)
            if not user:
                raise ValueError("User not found")
            
            # Revoke the old token
            AuthService.revoke_token(old_token)
            
            # Generate new token
            token_payload = {
                'email': email,
                'exp': datetime.now(timezone.utc) + timedelta(minutes=AuthService.TOKEN_EXPIRATION_MINUTES),
                'iat': datetime.now(timezone.utc)
            }
            
            new_token = jwt.encode(
                token_payload,
                current_app.config['SECRET_KEY'],
                algorithm="HS256"
            )
            
            return new_token
            
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Cannot refresh token: {str(e)}")

    @staticmethod
    def get_token_expiration(token: str) -> datetime:
        """
        Get expiration time of a token
        
        Args:
            token (str): JWT token to check
            
        Returns:
            datetime: Expiration datetime
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            payload = AuthService.decode_token(token)
            return datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Cannot get token expiration: {str(e)}")