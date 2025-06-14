from flask import Flask

from src.models import db
from src.routes.auth_routes import auth


def register_blueprints(app):
    """Register all blueprints for the application."""
    app.register_blueprint(auth, url_prefix='/auth')


def create_app(testing=False, development=False, production=False):
    app = Flask(__name__)

    if testing:
        app.config.from_object('config.TestingConfig')
    elif development:
        app.config.from_object('config.DevelopmentConfig')
    else:
        app.config.from_object('config.ProductionConfig')

    with app.app_context():
        db.init_app(app)
        db.create_all()
        print('Database tables created successfully.')
        register_blueprints(app)
    return app
