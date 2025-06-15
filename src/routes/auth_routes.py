import re
from flask import Blueprint, request, jsonify

import datetime
from flask import current_app
import jwt

from src.controllers.auth_controller import AuthController
from src.models import db
from src.models.user_model import User
from src.routes import require_admin

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
controller = AuthController(db.session, User)

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    # Extraction
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    print("request data:", data)

    # verify required fields
    missing_fields = [field for field in ['first_name', 'last_name', 'email', 'password'] if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # type checking
    if not all(isinstance(field, str) for field in [first_name, last_name, email, password]):
        return jsonify({"error": "All fields must be strings"}), 400

    # check email format
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Invalid email format"}), 400

    #  secure the password
    response, status = controller.create(data)
    return jsonify(response), status


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    # print(email, password)
    user = controller.get_by_email(email)
    # check email format
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Invalid email format"}), 400
    # check if user exists and password is correct
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    # print("SECRET_KEY type:", type(current_app.config['JWT_SECRET_KEY']), "value:", current_app.config['SECRET_KEY'])
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    return jsonify({"access_token": token}), 200


@auth.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    response, status = controller.get_by_id(user_id)
    return jsonify(response), status


@auth.route('/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    response, status = controller.update(user_id, data)
    return jsonify(response), status


@auth.route('/delete/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    response, status = controller.delete(user_id)
    return jsonify(response), status


@auth.route('/get_id/<string:email>', methods=['GET'])
#@require_admin
def get_id(email):
    response, status = controller.provide_user_id(email)
    return jsonify(response), status