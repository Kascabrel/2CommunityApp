from flask import Flask

from src.models import db
from src.routes.auth_routes import auth
from src.routes.contribution_routes import contribution_bp


def register_blueprints(app):
    """Register all blueprints for the application."""
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(contribution_bp, url_prefix='/contribution')


def create_app(testing=False, development=False):
    app = Flask(__name__)

    if testing:
        app.config.from_object('config.TestingConfig')
    elif development:
        app.config.from_object('config.DevelopmentConfig')
    else:
        app.config.from_object('config.ProductionConfig')

    db.init_app(app)
    register_blueprints(app)
    with app.app_context():
        db.create_all()
        print('Database tables created successfully.')
        if development:  # Ne crée que si test ou dev
            create_initial_admin()

    return app


def create_initial_admin():
    from src.models.user_model import User, AdminIdentifierCode, db, UserRole
    from werkzeug.security import generate_password_hash
    import secrets
    import os

    if not User.query.filter_by(role=UserRole.ADMIN).first():
        print("Creating default admin user...")

        salt = secrets.token_hex(8)
        admin = User(
            firstname='Admin',
            lastname='Default',
            email='admin@example.com',
            salt=salt,
            role=UserRole.ADMIN
        )
        admin.set_password(os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin123"), salt)

        code = AdminIdentifierCode()
        code.generate_code()
        db.session.add(code)

        admin.admin_identifier = code.code

        db.session.add(admin)
        db.session.commit()

        print(f"✅ Admin user created with identifier: {code.code}")
