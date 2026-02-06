from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
from functools import wraps
from models import (
    init_db, create_user, verify_password, get_user_by_id,
    get_all_schools, get_school_by_id, get_schools_by_region,
    get_schools_by_level, search_schools, get_regions,
    create_school, get_like, get_likes_count, like_school,
    unlike_school, get_user_liked_schools, load_sample_data
)
from i18n import _, LANGUAGE_NAMES, get_locale

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure upload directory exists
os.makedirs('static/images', exist_ok=True)

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(_('please_login'), 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_globals():
    """Inject global variables into templates."""
    return {
        '_': _,
        'LANGUAGE_NAMES': LANGUAGE_NAMES,
        'current_lang': get_locale()
    }

@app.route('/lang/<lang>')
def set_language(lang):
    """Set the language and redirect back."""
    session['lang'] = lang
    # Get the referrer to redirect back
    referrer = request.headers.get('Referer', '/')
    return redirect(referrer)

@app.route('/')
def index():
    """Homepage - list schools by region."""
    search_query = request.args.get('q', '')
    selected_region = request.args.get('region', '')
    selected_level = request.args.get('level', '')
    
    if search_query:
        schools = search_schools(search_query)
    elif selected_region:
        schools = get_schools_by_region(selected_region)
    elif selected_level:
        schools = get_schools_by_level(selected_level)
    else:
        schools = get_all_schools()
    
    regions = get_regions()
    levels = ['university', 'middle', 'elementary', 'kindergarten']
    
    return render_template('index.html', 
                         schools=schools, 
                         regions=regions, 
                         levels=levels,
                         search_query=search_query,
                         selected_region=selected_region,
                         selected_level=selected_level)

@app.route('/school/<int:school_id>')
def school_detail(school_id):
    """School detail page."""
    school = get_school_by_id(school_id)
    if not school:
        flash(_('no_schools'), 'error')
        return redirect(url_for('index'))
    
    likes_count = get_likes_count(school_id)
    user_liked = False
    
    if 'user_id' in session:
        user_liked = get_like(session['user_id'], school_id) is not None
    
    return render_template('school.html', 
                         school=school, 
                         likes_count=likes_count,
                         user_liked=user_liked)

@app.route('/like/<int:school_id>', methods=['POST'])
@login_required
def toggle_like(school_id):
    """Toggle like on a school."""
    school = get_school_by_id(school_id)
    if not school:
        flash(_('no_schools'), 'error')
        return redirect(url_for('index'))
    
    existing_like = get_like(session['user_id'], school_id)
    if existing_like:
        unlike_school(session['user_id'], school_id)
        flash(_('liked'), 'info')
    else:
        like_school(session['user_id'], school_id)
        flash(_('like'), 'success')
    
    return redirect(url_for('school_detail', school_id=school_id))

@app.route('/my-likes')
@login_required
def my_likes():
    """Show user's liked schools."""
    liked_schools = get_user_liked_schools(session['user_id'])
    return render_template('my_likes.html', schools=liked_schools)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if not username or not password or not email:
            flash(_('all_required'), 'error')
            return redirect(url_for('register'))
        
        user_id = create_user(username, password, email)
        if user_id:
            flash(_('register_success'), 'success')
            return redirect(url_for('login'))
        else:
            flash(_('username_exists'), 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = verify_password(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(_('welcome_back').format(user['username']), 'success')
            return redirect(url_for('index'))
        else:
            flash(_('login_error'), 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout."""
    session.pop('user_id', None)
    session.pop('username', None)
    flash(_('logout_success'), 'info')
    return redirect(url_for('index'))

@app.route('/init-db')
def init_database():
    """Initialize the database."""
    init_db()
    flash('Database initialized.', 'success')
    return redirect(url_for('index'))

@app.route('/load-sample-data')
def load_sample():
    """Load sample data."""
    try:
        load_sample_data()
        flash('Sample data loaded.', 'success')
    except Exception as e:
        flash(f'Error loading data: {e}', 'error')
    return redirect(url_for('index'))

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve badge images."""
    return send_from_directory('static/images', filename)

# CLI commands
@app.cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    init_db()
    print('Database initialized.')

@app.cli.command('load-sample-data')
def load_sample_data_command():
    """Load sample data."""
    load_sample_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
