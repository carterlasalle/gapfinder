from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import logging
from supabase import Client

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']

@login_manager.user_loader
def load_user(user_id):
    supabase: Client = current_app.config['SUPABASE']
    response = supabase.auth.get_user(user_id)
    if response.user:
        return User(response.user)
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        supabase: Client = current_app.config['SUPABASE']
        
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = User(response.user)
            login_user(user)
            logger.info(f"User {email} logged in successfully")
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Login error for user {email}: {str(e)}")
            flash(f'Login failed: {str(e)}')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    supabase: Client = current_app.config['SUPABASE']
    supabase.auth.sign_out()
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        supabase: Client = current_app.config['SUPABASE']
        
        try:
            response = supabase.auth.sign_up({
                "email": email, 
                "password": password,
                "options": {
                    "data": {
                        "email": email
                    }
                }
            })
            logger.info(f"New user registered: {email}")
            flash('Registration successful. Please check your email to verify your account.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Registration failed. Please try again.')
    
    return render_template('register.html')

@auth_bp.route('/auth/callback')
def auth_callback():
    supabase: Client = current_app.config['SUPABASE']
    code = request.args.get('code')
    
    if code:
        try:
            response = supabase.auth.exchange_code_for_session(code)
            user = User(response.user)
            login_user(user)
            flash('Email verified successfully. You are now logged in.')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error in auth callback: {str(e)}")
            flash('Error verifying email. Please try again or contact support.')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/favorites', methods=['GET', 'POST', 'DELETE'])
@login_required
def favorites():
    supabase: Client = current_app.config['SUPABASE']
    
    if request.method == 'GET':
        response = supabase.table('favorites').select('*').eq('user_id', current_user.id).execute()
        return jsonify(response.data)
    elif request.method == 'POST':
        data = request.json
        response = supabase.table('favorites').insert({
            'user_id': current_user.id,
            'player_name': data['player_name'],
            'section': data['section']
        }).execute()
        return jsonify(response.data[0]), 201
    elif request.method == 'DELETE':
        favorite_id = request.args.get('id')
        response = supabase.table('favorites').delete().eq('id', favorite_id).eq('user_id', current_user.id).execute()
        if response.data:
            return '', 204
        return jsonify({'error': 'Favorite not found'}), 404
