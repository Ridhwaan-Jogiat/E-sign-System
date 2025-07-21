import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail  # ADD THIS LINE
import pytz
from datetime import timedelta


from .config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()
mail = Mail()  # ADD THIS LINE


def create_app(config_class=Config):
    app = Flask(__name__)
    app.jinja_env.globals.update(pytz=pytz, timedelta=timedelta)

    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # ADD THIS LINE

    # Ensure upload directories exist
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'signatures'), exist_ok=True)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.documents import documents_bp
    from app.routes.signatures import signatures_bp
    from app.routes.employees import employees_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(signatures_bp, url_prefix='/signatures')
    app.register_blueprint(employees_bp)

    return app