import jwt
from functools import wraps
from flask import request, jsonify, current_app
from community.controllers.auth_controller import AuthController
from community.models import db
from community.models.user_model import User, UserRole


def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant ou invalide"}), 401

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = payload.get("sub")

            if not user_id:
                return jsonify({"error": "Token invalide"}), 401

            # Utilisation du contrôleur pour récupérer l’utilisateur
            controller = AuthController(db.session, User)
            user = controller.get_by_id(user_id)

            if not user or user.role != UserRole.ADMIN:
                return jsonify({"error": "Accès réservé aux administrateurs"}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expiré"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401

        return f(*args, **kwargs)

    return decorated_function
