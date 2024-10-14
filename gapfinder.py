import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not found. Skipping .env file loading.")

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
from bs4 import BeautifulSoup
import logging
from cache import cache
from models import db, User, migrate
from auth import auth_bp, login_manager
from api import api_bp
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
    
    # Modify the database URI to use 'postgresql' instead of 'postgres'
    db_uri = os.environ.get('POSTGRES_URL_NON_POOLING')
    if db_uri and db_uri.startswith('postgres://'):
        db_uri = db_uri.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Print the database URI for debugging
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt = Bcrypt(app)
    login_manager.init_app(app)
    cache.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/test_db')
    def test_db():
        try:
            users = User.query.all()
            return f"Database connection successful. Number of users: {len(users)}"
        except Exception as e:
            return f"Database connection failed: {str(e)}"

    # Logging configuration
    if not app.debug:
        app.logger.setLevel(logging.INFO)
        app.logger.info('Gapfinder startup')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
