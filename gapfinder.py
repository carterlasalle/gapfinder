import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from cache import cache
from auth import auth_bp, login_manager
from api import api_bp
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

    # Initialize Supabase client
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY') or os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    # Debug logging
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_KEY: {'*' * (len(supabase_key) - 4) + supabase_key[-4:]}")
    
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL or SUPABASE_KEY is not set")
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    app.config['SUPABASE'] = supabase

    # Initialize extensions
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
            response = supabase.table('favorites').select('*').execute()
            return f"Database connection successful. Number of favorites: {len(response.data)}"
        except Exception as e:
            return f"Database connection failed: {str(e)}"

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
