from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api.db import db
from api.models.base_model import BaseModel


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(BaseModel):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.Text())
    jwt_auth_active = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return f"User {self.username}"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def to_json(self):
        return {
            '_id': self.id,
            'username': self.username,
            'email': self.email
        }

class JWTTokenBlocklist(BaseModel):
    __tablename__ = 'jwt_token_blocklist'
    
    id = db.Column(db.Integer(), primary_key=True)
    jwt_token = db.Column(db.String(500), nullable=False, index=True)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token[:20]}..."