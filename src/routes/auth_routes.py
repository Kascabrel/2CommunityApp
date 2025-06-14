import re
from flask import Blueprint, request, jsonify

from src.controllers.auth_controller import AuthController
from src.models import db
from src.models.user_model import User

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
