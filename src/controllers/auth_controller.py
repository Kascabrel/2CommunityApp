import secrets
from sqlalchemy.exc import IntegrityError
from src.controllers import BaseController
from src.models.user_model import UserRole


class AuthController(BaseController):
    def __init__(self, db_session, model_class):
        super().__init__(db_session, model_class)
        self.model_class = model_class

    def create(self, data: dict):  # returns and response and  status code
        # check if the email is already registered
        existing_user = self.db_session.query(self.model_class).filter_by(email=data['email']).first()
        if existing_user:
            return {"error": "Email already registered"}, 409

        # generate a salt and hash the password
        salt = secrets.token_hex(16)
        user = self.model_class(
            firstname=data['first_name'],
            lastname=data['last_name'],
            email=data['email'],
            salt=salt,
            role = data.get('role', UserRole.USER)
        )
        user.set_password(data['password'], salt)

        try:
            self.db_session.add(user)
            self.db_session.commit()
            return {"message": "User registered successfully"}, 201
        except IntegrityError:
            self.db_session.rollback()
            return {"error": "User already exists with provided details"}, 409
        except Exception as e:
            self.db_session.rollback()
            return {"error": str(e)}, 500

    def get_by_id(self, item_id: int):
        pass

    def update(self, item_id: int, data: dict):
        pass

    def delete(self, item_id: int):
        pass

    def convert_dict_to_model(self, data: dict):
        """Convert a dictionary to a model instance."""
        return self.model_class(**data)
