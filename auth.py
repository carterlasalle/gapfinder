from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, session
import logging
from supabase import Client
from functools import wraps

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        supabase: Client = current_app.config['SUPABASE']
        try:
            user = supabase.auth.get_user()
            if not user:
                return redirect(url_for('auth.login'))
        except Exception:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        supabase: Client = current_app.config['SUPABASE']
        
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['user'] = response.user
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
    session.pop('user', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        supabase: Client = current_app.config['SUPABASE']
        
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            logger.info(f"New user registered: {email}")
            flash('Registration successful. Please check your email to verify your account.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logger.error(f"Registration error for user {email}: {str(e)}")
            flash(f'Registration failed: {str(e)}')
    
    return render_template('register.html')

@auth_bp.route('/auth/callback')
def auth_callback():
    supabase: Client = current_app.config['SUPABASE']
    code = request.args.get('code')
    
    if code:
        try:
            response = supabase.auth.exchange_code_for_session(code)
            session['user'] = response.user
            flash('Email verified successfully. You are now logged in.')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error in auth callback: {str(e)}")
            flash(f'Error verifying email: {str(e)}')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/favorites', methods=['GET', 'POST', 'DELETE'])
@login_required
def favorites():
    supabase: Client = current_app.config['SUPABASE']
    user = session.get('user')
    
    if request.method == 'GET':
        response = supabase.table('favorites').select('*').eq('user_id', user['id']).execute()
        return jsonify(response.data)
    elif request.method == 'POST':
        data = request.json
        response = supabase.table('favorites').insert({
            'user_id': user['id'],
            'player_name': data['player_name'],
            'section': data['section']
        }).execute()
        return jsonify(response.data[0]), 201
    elif request.method == 'DELETE':
        favorite_id = request.args.get('id')
        response = supabase.table('favorites').delete().eq('id', favorite_id).eq('user_id', user['id']).execute()
        if response.data:
            return '', 204
        return jsonify({'error': 'Favorite not found'}), 404
