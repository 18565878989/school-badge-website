"""
Authentication routes module
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import sqlite3
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_user_by_id, is_admin, get_db_connection
from i18n import _

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(_('please_login'), 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        conn = get_db_connection()
        user = conn.execute('''
            SELECT * FROM users WHERE username = ? OR email = ?
        ''', (username, username)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if remember:
                session.permanent = True
            
            flash(_('Login successful'), 'success')
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('index'))
        else:
            flash(_('Invalid username or password'), 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register page."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash(_('Passwords do not match'), 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash(_('Password must be at least 6 characters'), 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        # Check if username or email already exists
        existing = conn.execute('''
            SELECT id FROM users WHERE username = ? OR email = ?
        ''', (username, email)).fetchone()
        
        if existing:
            flash(_('Username or email already exists'), 'error')
            conn.close()
            return render_template('register.html')
        
        # Create user
        try:
            conn.execute('''
                INSERT INTO users (username, email, password_hash, role, created_at)
                VALUES (?, ?, ?, 'user', datetime('now'))
            ''', (username, email, generate_password_hash(password)))
            conn.commit()
            flash(_('Registration successful. Please login.'), 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Logout."""
    session.clear()
    flash(_('Logged out successfully'), 'success')
    return redirect(url_for('index'))

@auth_bp.route('/send-sms', methods=['POST'])
def send_sms():
    """Send SMS verification code."""
    phone = request.form.get('phone')
    
    if not phone:
        return jsonify({'success': False, 'message': 'Phone number is required'})
    
    # Generate verification code
    code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    # Store in session (in production, use Redis or database)
    session['sms_code'] = code
    session['sms_phone'] = phone
    
    # In production, integrate with SMS service
    # For now, just return the code (for testing)
    return jsonify({
        'success': True, 
        'message': f'SMS sent (code: {code})'
    })


def register_routes(app):
    """Register auth routes with the Flask app."""
    app.register_blueprint(auth_bp)
