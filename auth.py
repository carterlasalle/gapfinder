from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, session
from functools import wraps
from supabase import Client

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
            session['access_token'] = response.session.access_token
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Login failed: {str(e)}')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    supabase: Client = current_app.config['SUPABASE']
    supabase.auth.sign_out()
    session.clear()
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
    
    if request.method == 'GET':
        response = supabase.table('favorites').select('*').execute()
        return jsonify(response.data)
    elif request.method == 'POST':
        data = request.json
        response = supabase.table('favorites').insert(data).execute()
        return jsonify(response.data[0]), 201
    elif request.method == 'DELETE':
        favorite_id = request.args.get('id')
        response = supabase.table('favorites').delete().eq('id', favorite_id).execute()
        if response.data:
            return '', 204
        return jsonify({'error': 'Favorite not found'}), 404