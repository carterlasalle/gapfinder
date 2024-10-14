from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, session
from functools import wraps
from supabase import Client
import uuid

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        supabase: Client = current_app.config['SUPABASE']
        if 'access_token' not in session:
            return redirect(url_for('auth.login'))
        try:
            user = supabase.auth.get_user(session['access_token'])
            if not user:
                raise ValueError("Invalid user")
        except Exception:
            session.pop('access_token', None)
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'access_token' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        supabase: Client = current_app.config['SUPABASE']
        
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['access_token'] = response.session.access_token
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Login failed: {str(e)}')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    supabase: Client = current_app.config['SUPABASE']
    try:
        supabase.auth.sign_out(session['access_token'])
    except Exception:
        pass  # If sign out fails, we'll still remove the token from the session
    session.pop('access_token', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        supabase: Client = current_app.config['SUPABASE']
        
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            flash('Registration successful. Please check your email to verify your account.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}')
    
    return render_template('register.html')

@auth_bp.route('/favorites', methods=['GET', 'POST', 'DELETE'])
@login_required
def favorites():
    supabase: Client = current_app.config['SUPABASE']
    user = supabase.auth.get_user(session['access_token'])
    
    if request.method == 'GET':
        response = supabase.table('favorites').select('*').eq('user_id', user.user.id).execute()
        return jsonify(response.data)
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            data['user_id'] = user.user.id  # user.user.id is already a UUID
            response = supabase.table('favorites').insert(data).execute()
            if 'error' in response:
                return jsonify({'error': response['error']['message']}), 500
            return jsonify(response.data[0]), 201
        except Exception as e:
            current_app.logger.error(f"Error in POST /favorites: {str(e)}")
            return jsonify({'error': str(e)}), 500
    elif request.method == 'DELETE':
        try:
            favorite_id = request.args.get('id')
            response = supabase.table('favorites').delete().eq('id', favorite_id).eq('user_id', user.user.id).execute()
            if response.data:
                return jsonify({'message': 'Favorite deleted successfully'}), 200
            return jsonify({'error': 'Favorite not found or not authorized to delete'}), 404
        except Exception as e:
            current_app.logger.error(f"Error in DELETE /favorites: {str(e)}")
            return jsonify({'error': str(e)}), 500
