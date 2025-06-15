import secrets
from sqlalchemy.exc import IntegrityError
from src.controllers import BaseController
from src.models.user_model import UserRole, AdminIdentifierCode


class AuthController(BaseController):
    def __init__(self, db_session, model_class):
        super().__init__(db_session, model_class)
        self.model_class = model_class

    def create(self, data: dict):
        existing_user = self.db_session.query(self.model_class).filter_by(email=data['email']).first()
        if existing_user:
            return {"error": "Email already registered"}, 409

        salt = secrets.token_hex(16)
        role = UserRole.USER

        if 'role' in data and data['role'] == 'admin':
            admin_identifier = data.get('admin_identifier')
            identifier_code = self.db_session.query(AdminIdentifierCode).filter_by(code=admin_identifier).first()
            if not identifier_code:
                return {"error": "Invalid admin identifier"}, 400
            role = UserRole.ADMIN

        user = self.model_class(
            firstname=data['first_name'],
            lastname=data['last_name'],
            email=data['email'],
            salt=salt,
            role=role
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
        user = self.db_session.query(self.model_class).get(item_id)
        if user:
            return {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "role": user.role.value,
                "admin_identifier": user.admin_identifier
            }, 200
        return {"error": "User not found"}, 404

    def update(self, item_id: int, data: dict):
        user = self.db_session.query(self.model_class).get(item_id)
        if not user:
            return {"error": "User not found"}, 404

        try:
            for key in ['first_name', 'last_name', 'email']:
                if key in data:
                    setattr(user, key.replace('first_name', 'firstname').replace('last_name', 'lastname'), data[key])

            if 'password' in data:
                salt = secrets.token_hex(16)
                user.set_password(data['password'], salt)
                user.salt = salt

            self.db_session.commit()
            return {"message": "User updated successfully"}, 200
        except Exception as e:
            self.db_session.rollback()
            return {"error": str(e)}, 500

    def delete(self, item_id: int):
        user = self.db_session.query(self.model_class).get(item_id)
        if not user:
            return {"error": "User not found"}, 404

        try:
            self.db_session.delete(user)
            self.db_session.commit()
            return {"message": "User deleted successfully"}, 200
        except Exception as e:
            self.db_session.rollback()
            return {"error": str(e)}, 500

    def convert_dict_to_model(self, data: dict):
        return self.model_class(**data)

    def get_by_email(self, email: str):
        return self.db_session.query(self.model_class).filter_by(email=email).first()

    def get_by_id(self, user_id: int):
        user = self.db_session.query(self.model_class).filter_by(id=user_id).first()
        if not user:
            return None
        return user

    def provide_user_id(self, email):
        """ this method  will be use just for testing to provide the user_id to use in oother workflow"""
        user = self.db_session.query(self.model_class).filter_by(email=email).first()

        if user is None:
            return {"message": "user not found"}, 404  # ✅ Gérer l'erreur proprement

        return {"message": "user found", "user_id": user.id}, 200
