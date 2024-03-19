from flask import Flask
from config import Config, TestConfig
from .db import db
from flask_migrate import Migrate
from flask_login import LoginManager
from app.members.models import Member
import logging

# Create an instance of LoginManager
login_manager = LoginManager()

def create_app(config=None):
    # Initialize Flask application
    app = Flask(__name__)
    
    # Load configuration from config.py

    if config == 'test':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)  # Initialize database connection
    migrate = Migrate(app, db)  # Initialize Flask-Migrate
    login_manager.init_app(app)  # Configure Flask-Login with the application instance

    # Import and register blueprints
    from app.members.views import members_bp
    from app.routes import bp as routes_bp
    from app.dependents.views import dependents_bp
    from app.admin_routes import admin_bp
    from app.cases.views import cases_bp
    from app.cases.active import active_cases_bp

    app.register_blueprint(members_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(dependents_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(active_cases_bp)

    # Import and register models to create database tables
    from app.members import models

    # Create the first admin user
    #with app.app_context():
        #Member.create_first_admin()
    
    configure_logging(app)


    return app

# Define the user_loader function outside the create_app function
@login_manager.user_loader
def load_user(member_id):
    print(f"Debug: Attempting to load user with ID: {member_id}")
    member = Member.query.get(int(member_id))
    print(f"Debug: Retrieved user: {member}")  # Print the retrieved user object
    return member

def configure_logging(app):
    # Set the log level
    # log_level = logging.DEBUG if app.debug else logging.INFO
    log_level = logging.DEBUG
    app.logger.setLevel(log_level)

    # Create a stream handler to log to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)

    # Create a formatter for the log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)

    # Add the stream handler to the app's logger
    app.logger.addHandler(stream_handler)


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
