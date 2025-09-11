from functools import wraps
import jwt
from flask import request, current_app
from api.models.user import Users
from api.auth.services import AuthService

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("authorization")
        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 400

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.get_by_email(data["email"])

            if not current_user:
                return {
                    "success": False,
                    "msg": "Sorry. Wrong auth token. This user does not exist."
                }, 400

            if AuthService.is_token_revoked(token):
                return {"success": False, "msg": "Token revoked."}, 400

            if not current_user.check_jwt_auth_active():
                return {"success": False, "msg": "Token expired."}, 400

        except jwt.ExpiredSignatureError:
            return {"success": False, "msg": "Token expired"}, 401
        except Exception:
            return {"success": False, "msg": "Token is invalid"}, 400

        return f(current_user, *args, **kwargs)

    return decorator