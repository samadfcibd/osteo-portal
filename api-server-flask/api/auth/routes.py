from flask import Blueprint, request
from flask_restx import Resource, fields, Namespace
from api.auth.services import AuthService
from api.auth.decorators import token_required

auth_bp = Blueprint('auth', __name__)
auth_ns = Namespace('auth', description='Authentication operations')

signup_model = auth_ns.model('SignUpModel', {
    "username": fields.String(required=True, min_length=2, max_length=32),
    "email": fields.String(required=True, min_length=4, max_length=64),
    "password": fields.String(required=True, min_length=4, max_length=16)
})

login_model = auth_ns.model('LoginModel', {
    "email": fields.String(required=True, min_length=4, max_length=64),
    "password": fields.String(required=True, min_length=4, max_length=16)
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(signup_model, validate=True)
    def post(self):
        try:
            req_data = request.get_json()
            user = AuthService.create_user(
                req_data.get("username"),
                req_data.get("email"),
                req_data.get("password")
            )
            return {
                "success": True,
                "userID": user.id,
                "msg": "User successfully registered"
            }, 201
        except ValueError as e:
            return {"success": False, "msg": str(e)}, 400
        except Exception as e:
            return {"success": False, "msg": str(e)}, 500
            # return {"success": False, "msg": "Registration failed"}, 500

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model, validate=True)
    def post(self):
        try:
            req_data = request.get_json()
            token, user = AuthService.authenticate_user(
                req_data.get("email"),
                req_data.get("password")
            )
            return {
                "success": True,
                "token": token,
                "user": user.to_json()
            }, 200
        except ValueError as e:
            return {"success": False, "msg": str(e)}, 400
        except Exception as e:
            return {"success": False, "msg": "Authentication failed"}, 500

@auth_ns.route('/logout')
class Logout(Resource):
    @token_required
    def post(self, current_user):
        try:
            token = request.headers.get("authorization")
            AuthService.revoke_token(token)

            self.set_jwt_auth_active(False)
            self.save()
            return {"success": True}, 200
        except Exception as e:
            return {"success": False, "msg": str(e)}, 400