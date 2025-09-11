from datetime import datetime, timezone, timedelta
import jwt
from flask import current_app
from api.models.user import Users, JWTTokenBlocklist
from api.db import db

class AuthService:
    # @staticmethod
    # def create_user(username, email, password):
    #     """Create a new user"""
    #     if Users.get_by_email(email):
    #         raise ValueError("Email already taken")
        
    #     user = Users(username=username, email=email)
    #     user.set_password(password)
    #     user.save()
    #     return user
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user and return token"""
        user = Users.get_by_email(email)
        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")
        
        token = jwt.encode(
            {'email': email, 'exp': datetime.utcnow() + timedelta(minutes=30)},
            current_app.config['SECRET_KEY']
        )
        
        user.set_jwt_auth_active(True)
        user.save()
        
        return token, user
    
    # @staticmethod
    # def revoke_token(token):
    #     """Add token to blocklist"""
    #     jwt_block = JWTTokenBlocklist(jwt_token=token)
    #     jwt_block.save()
    
    # @staticmethod
    # def is_token_revoked(token):
    #     """Check if token is in blocklist"""
    #     return db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar() is not None