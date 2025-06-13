from flask import Flask


def register_blueprints(app):
    """Register all blueprints for the application."""
    pass  # Import and register the blueprints here


def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.Config')

    with app.app_context():
        # register blueprints
        register_blueprints(app)
    return app
