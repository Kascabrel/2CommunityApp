import enum
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db

from src.models.contribution_model import UserContributionRun, UserMonthlyContribution, Contribution


class UserRole(enum.Enum):
    ADMIN = 'admin'
    USER = 'user'


class User(db.Model):  # << Corrigé ici
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), unique=True, nullable=False)
    lastname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    salt = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    admin_identifier = db.Column(db.String(200), nullable=True)
    # Relations
    user_contribution_runs = db.relationship('UserContributionRun', back_populates='user')
    monthly_contributions = db.relationship('UserMonthlyContribution', back_populates='user')

    #  to retrieve all monthly contributions where the user is the winner
    won_contributions = db.relationship('Contribution', back_populates='winner_user')

    def set_password(self, password, salt):
        self.password_hash = generate_password_hash(password + salt)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password + self.salt)

    def __repr__(self):
        return f'<User {self.email}>'


class AdminIdentifierCode(db.Model):
    __tablename__ = 'admin_identifier_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)

    def generate_code(self):
        """Generate a unique admin identifier code."""
        import random
        import string

        # Generate a random code of format XX-YY
        part1 = ''.join(random.choices(string.ascii_uppercase, k=2))
        part2 = ''.join(random.choices(string.digits, k=2))
        self.code = f"{part1}-{part2}"
        # chek if the code is not already in the database
        while AdminIdentifierCode.query.filter_by(code=self.code).first():
            part1 = ''.join(random.choices(string.ascii_uppercase, k=2))
            part2 = ''.join(random.choices(string.digits, k=2))
            self.code = f"{part1}-{part2}"

    def __repr__(self):
        return f'<AdminIdentifierCode {self.code}>'
