import enum

from werkzeug.security import generate_password_hash, check_password_hash

from src.models import db


class UserRole(enum.Enum):
    ADMIN = 'admin'
    USER = 'user'


class User(db.model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), unique=True, nullable=False)
    lastname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    salt = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)

    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the user's password."""
        return check_password_hash(password, self.password_hash)

    def __repr__(self):
        return f'<User {self.username}>'
