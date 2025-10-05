"""
Authentication Decorators
Provides JWT token validation and user authentication decorators
"""

from functools import wraps
import jwt
from flask import request, current_app

from api.models.user import Users
from api.auth.services import AuthService

def token_required(f):
    """
    Decorator to validate JWT token and authenticate user
    
    This decorator:
    - Checks for the presence of JWT token in Authorization header
    - Validates token signature and expiration
    - Checks if token has been revoked
    - Verifies user exists and is active
    - Injects current_user into the decorated function
    
    Args:
        f (function): The function to be decorated
        
    Returns:
        function: Decorated function with user authentication
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        """
        Inner decorator function that handles token validation
        
        Returns:
            Response: Original function response or error response
        """
        # Extract token from Authorization header
        token = request.headers.get("authorization")

        # Check if token exists
        if not token:
            return {
                "success": False, 
                "msg": "Valid JWT token is missing"
            }, 401  # Unauthorized

        try:
            # Decode and verify JWT token
            
            # token_data = jwt.decode(
            #     token, 
            #     current_app.config['SECRET_KEY'], 
            #     algorithms=["HS256"]
            # )
            token_data = AuthService.decode_token(token)


            # Get user from database using email in token
            current_user = Users.get_by_email(token_data["email"])

            # Verify user exists
            if not current_user:
                return {
                    "success": False,
                    "msg": "Invalid token. User does not exist."
                }, 401  # Unauthorized

            # Check if token has been revoked
            if AuthService.is_token_revoked(token):
                return {
                    "success": False, 
                    "msg": "Token has been revoked."
                }, 401  # Unauthorized

            # Check if user's JWT authentication is active
            if not current_user.check_jwt_auth_active():
                return {
                    "success": False, 
                    "msg": "User authentication is disabled."
                }, 401  # Unauthorized

        except jwt.ExpiredSignatureError:
            # Handle expired token
            return {
                "success": False, 
                "msg": "Token has expired. Please login again."
            }, 401  # Unauthorized
        
        except jwt.InvalidTokenError:
            # Handle invalid token format or signature
            return {
                "success": False, 
                "msg": "Invalid token provided."
            }, 401  # Unauthorized
            
        except Exception as e:
            # Handle any other unexpected errors
            # Log the actual error for debugging
            # current_app.logger.error(f"Token validation error: {str(e)}")
            return {
                "success": False, 
                "msg": "Token validation failed."
            }, 400  # Bad Request

        return f(current_user, *args, **kwargs)

    return decorator