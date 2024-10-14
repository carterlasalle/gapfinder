from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Favorite, db
import logging
from supabase import create_client, Client
import os

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

supabase: Client = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        logger.info(f"Login attempt for user: {username}")
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            logger.info(f"User {username} logged in successfully")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        logger.warning(f"Failed login attempt for user: {username}")
        flash('Invalid username or password')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New user registered: {username}")
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/favorites', methods=['GET', 'POST', 'DELETE'])
@login_required
def favorites():
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
