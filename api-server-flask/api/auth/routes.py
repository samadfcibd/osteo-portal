"""
Authentication Blueprint
Handles user registration, login, and logout operations
"""

from flask import Blueprint, request
from flask_restx import Api, Resource, fields, Namespace

from api.auth.services import AuthService
from api.auth.decorators import token_required

# Initialize Blueprint and Namespace
auth_bp = Blueprint('auth', __name__)
# Initialize Namespace
auth_ns = Namespace('auth', description='User authentication and authorization operations')

# Data models for request validation
signup_model = auth_ns.model('SignUp', {
    "username": fields.String(
        required=True, 
        min_length=2, 
        max_length=32,
        example="john_doe",
        description="User's username"
    ),
    "email": fields.String(
        required=True, 
        min_length=4, 
        max_length=64,
        example="user@example.com",
        description="User's email address"
    ),
    "password": fields.String(
        required=True, 
        min_length=4, 
        max_length=16,
        example="securepassword123",
        description="User's password"
    )
})

login_model = auth_ns.model('Login', {
    "email": fields.String(
        required=True, 
        min_length=4, 
        max_length=64,
        example="user@example.com", 
        description="User's email address"
    ),
    "password": fields.String(
        required=True, 
        min_length=4, 
        max_length=16,
        example="securepassword123",
        description="User's password"
    )
})

user_response_model = auth_ns.model('UserResponse', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='User email')
})

login_response_model = auth_ns.model('LoginResponse', {
    'success': fields.Boolean(description='Operation status'),
    'token': fields.String(description='JWT token'),
    'user': fields.Nested(user_response_model),
    'msg': fields.String(description='Response message')
})

register_response_model = auth_ns.model('RegisterResponse', {
    'success': fields.Boolean(description='Operation status'),
    'userID': fields.Integer(description='New user ID'),
    'msg': fields.String(description='Response message')
})

refresh_response_model = auth_ns.model('RefreshResponse', {
    'success': fields.Boolean(description='Operation status'),
    'token': fields.String(description='New JWT token'),
    'user': fields.Nested(user_response_model),
    'msg': fields.String(description='Response message')
})


@auth_ns.route('/register')
class Register(Resource):
    """
    Handles user registration
    """

    @auth_ns.expect(signup_model, validate=True)
    @auth_ns.response(201, 'User successfully registered', register_response_model)
    @auth_ns.response(400, 'Invalid input data')
    @auth_ns.response(500, 'Internal server error')
    
    def post(self):
        """
        Register a new user
        
        Returns:
            dict: Registration response with user ID and message
        """
        try:
            req_data = request.get_json()
            
            # Create new user
            user = AuthService.create_user(
                username=req_data.get("username"),
                email=req_data.get("email"),
                password=req_data.get("password")
            )

            return {
                "success": True,
                "userID": user.id,
                "msg": "User successfully registered"
            }, 201
        
        except ValueError as e:
            # Handle business logic errors (e.g., duplicate email)
            return {
                "success": False, 
                "msg": str(e)
            }, 400
        
        except Exception as e:
            # Handle unexpected errors
            # Log the actual error for debugging while returning generic message
            # logger.error(f"Registration error: {str(e)}")
            return {
                "success": False, 
                "msg": "Registration failed"
            }, 500

@auth_ns.route('/login')
class Login(Resource):
    """
    Handles user authentication
    """

    @auth_ns.expect(login_model, validate=True)
    @auth_ns.response(200, 'Login successful', login_response_model)
    @auth_ns.response(400, 'Invalid credentials')
    @auth_ns.response(500, 'Internal server error')
    def post(self):
        """
        Authenticate user and return JWT token
        
        Returns:
            dict: Authentication response with token and user data
        """
        try:
            req_data = request.get_json()

            # Authenticate user and generate token
            token, user = AuthService.authenticate_user(
                email=req_data.get("email"),
                password=req_data.get("password")
            )
            return {
                "success": True,
                "token": token,
                "user": user.to_json()
            }, 200
        except ValueError as e:
            # Handle authentication failures
            return {
                "success": False, 
                "msg": str(e)
            }, 400
        
        except Exception as e:
            # Handle unexpected errors
            # logger.error(f"Login error: {str(e)}")
            return {
                "success": False, 
                "msg": "Authentication failed"
            }, 500

@auth_ns.route('/logout')
class Logout(Resource):
    """
    Handles user logout and token revocation
    """

    @token_required
    @auth_ns.response(200, 'Logout successful')
    @auth_ns.response(400, 'Logout failed')
    @auth_ns.response(401, 'Unauthorized')
    def post(self, current_user):
        """
        Logout user and revoke JWT token
        
        Args:
            current_user: Authenticated user object from token_required decorator
            
        Returns:
            dict: Logout response
        """
        try:
            # Extract token from authorization header
            token = request.headers.get("authorization")

            # Revoke the token
            AuthService.revoke_token(token)

            # Deactivate JWT authentication (implementation depends on your User model)
            self.set_jwt_auth_active(False)
            self.save()
            
            return {
                "success": True,
                "msg": "User successfully logged out"
            }, 200
        except Exception as e:
            # logger.error(f"Logout error: {str(e)}")
            return {
                "success": False, 
                "msg": "Logout failed"
            }, 400
        

@auth_ns.route('/refresh')
class RefreshToken(Resource):
    """
    Handles JWT token refresh
    """
    
    @token_required
    @auth_ns.response(200, 'Token refreshed successfully', refresh_response_model)
    @auth_ns.response(400, 'Token refresh failed')
    @auth_ns.response(401, 'Unauthorized')
    def post(self, current_user):
        """
        Refresh JWT token - revokes old token and issues new one
        
        Args:
            current_user: Authenticated user object from token_required decorator
            
        Returns:
            dict: New token and user data
        """
        try:
            # Extract token from authorization header
            old_token = request.headers.get("authorization")
            
            # Use the new refresh_token method
            new_token = AuthService.refresh_token(old_token)
            
            return {
                "success": True,
                "token": new_token,
                "user": current_user.to_json(),
                "msg": "Token refreshed successfully"
            }, 200
            
        except ValueError as e:
            return {"success": False, "msg": str(e)}, 400
        except Exception as e:
            # logger.error(f"Token refresh error: {str(e)}")
            return {"success": False, "msg": "Token refresh failed"}, 500