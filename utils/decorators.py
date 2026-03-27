"""
Decorators for routes
"""

from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def cacheable(timeout=300):
    """Decorator to cache function results."""
    def decorator(f):
        cache = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                import time
                if time.time() - cache[key]['time'] < timeout:
                    return cache[key]['value']
            
            value = f(*args, **kwargs)
            cache[key] = {'value': value, 'time': time.time()}
            return value
        
        return decorated_function
    return decorator
