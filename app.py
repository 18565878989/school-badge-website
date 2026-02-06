from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
from functools import wraps
from werkzeug.security import generate_password_hash
from models import (
    init_db, create_user, verify_password, get_user_by_id, is_admin,
    get_all_users, update_user_role, delete_user,
    get_all_schools, get_school_by_id, get_regions,
    create_school, update_school, delete_school,
    get_like, get_likes_count, like_school,
    unlike_school, get_user_liked_schools,
    log_admin_action, get_admin_logs
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

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(_('please_login'), 'warning')
            return redirect(url_for('login'))
        if not is_admin(session['user_id']):
            flash(_('no_permission'), 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_globals():
    """Inject global variables into templates."""
    return {
        '_': _,
        'LANGUAGE_NAMES': LANGUAGE_NAMES,
        'current_lang': get_locale(),
        'is_admin': lambda: 'user_id' in session and is_admin(session.get('user_id'))
    }

@app.route('/lang/<lang>')
def set_language(lang):
    """Set the language and redirect back."""
    session['lang'] = lang
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
            session['role'] = user['role']
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
    session.pop('role', None)
    flash(_('logout_success'), 'info')
    return redirect(url_for('index'))

# ==================== Admin Routes ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    schools = get_all_schools()
    users = get_all_users()
    regions = get_regions()
    
    stats = {
        'total_schools': len(schools),
        'total_users': len(users),
        'total_regions': len(regions)
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_schools=schools[:5],
                         recent_users=users[:5])

@app.route('/admin/schools')
@admin_required
def admin_schools():
    """Manage schools."""
    schools = get_all_schools()
    return render_template('admin/schools.html', schools=schools)

@app.route('/admin/school/add', methods=['GET', 'POST'])
@admin_required
def admin_add_school():
    """Add new school."""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'name_cn': request.form.get('name_cn'),
            'region': request.form.get('region'),
            'country': request.form.get('country'),
            'city': request.form.get('city'),
            'address': request.form.get('address'),
            'level': request.form.get('level'),
            'description': request.form.get('description'),
            'website': request.form.get('website'),
            'motto': request.form.get('motto'),
            'founded': request.form.get('founded'),
            'principal': request.form.get('principal')
        }
        
        school_id = create_school(**data)
        if school_id:
            log_admin_action(session['user_id'], 'CREATE_SCHOOL', 'school', school_id, data['name'])
            flash(_('success'), 'success')
            return redirect(url_for('admin_schools'))
        else:
            flash(_('error'), 'error')
    
    regions = ['North America', 'Europe', 'Asia', 'Oceania', 'Africa', 'South America']
    levels = ['university', 'middle', 'elementary', 'kindergarten']
    return render_template('admin/school_form.html', school=None, regions=regions, levels=levels)

@app.route('/admin/school/<int:school_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_school(school_id):
    """Edit school."""
    school = get_school_by_id(school_id)
    if not school:
        flash(_('no_schools'), 'error')
        return redirect(url_for('admin_schools'))
    
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'name_cn': request.form.get('name_cn'),
            'region': request.form.get('region'),
            'country': request.form.get('country'),
            'city': request.form.get('city'),
            'address': request.form.get('address'),
            'level': request.form.get('level'),
            'description': request.form.get('description'),
            'website': request.form.get('website'),
            'motto': request.form.get('motto'),
            'founded': request.form.get('founded'),
            'principal': request.form.get('principal')
        }
        
        if update_school(school_id, **data):
            log_admin_action(session['user_id'], 'UPDATE_SCHOOL', 'school', school_id, data['name'])
            flash(_('success'), 'success')
            return redirect(url_for('admin_schools'))
        else:
            flash(_('error'), 'error')
    
    regions = ['North America', 'Europe', 'Asia', 'Oceania', 'Africa', 'South America']
    levels = ['university', 'middle', 'elementary', 'kindergarten']
    return render_template('admin/school_form.html', school=school, regions=regions, levels=levels)

@app.route('/admin/school/<int:school_id>/delete')
@admin_required
def admin_delete_school(school_id):
    """Delete school."""
    school = get_school_by_id(school_id)
    if school:
        school_name = school['name']
        delete_school(school_id)
        log_admin_action(session['user_id'], 'DELETE_SCHOOL', 'school', school_id, school_name)
        flash(_('success'), 'success')
    else:
        flash(_('error'), 'error')
    return redirect(url_for('admin_schools'))

@app.route('/admin/users')
@admin_required
def admin_users():
    """Manage users."""
    users = get_all_users()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>/promote')
@admin_required
def admin_promote_user(user_id):
    """Promote user to admin."""
    if update_user_role(user_id, 'admin'):
        user = get_user_by_id(user_id)
        log_admin_action(session['user_id'], 'PROMOTE_USER', 'user', user_id, user['username'])
        flash(_('success'), 'success')
    else:
        flash(_('error'), 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/demote')
@admin_required
def admin_demote_user(user_id):
    """Demote admin to user."""
    if update_user_role(user_id, 'user'):
        user = get_user_by_id(user_id)
        log_admin_action(session['user_id'], 'DEMOTE_USER', 'user', user_id, user['username'])
        flash(_('success'), 'success')
    else:
        flash(_('error'), 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/delete')
@admin_required
def admin_delete_user(user_id):
    """Delete user."""
    user = get_user_by_id(user_id)
    if user:
        if user_id == session['user_id']:
            flash(_('error'), 'error')
        else:
            username = user['username']
            delete_user(user_id)
            log_admin_action(session['user_id'], 'DELETE_USER', 'user', user_id, username)
            flash(_('success'), 'success')
    else:
        flash(_('error'), 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/logs')
@admin_required
def admin_logs():
    """View admin logs."""
    logs = get_admin_logs(100)
    return render_template('admin/logs.html', logs=logs)

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
        from models import load_sample_data as load
        load()
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

@app.cli.command('create-admin')
def create_admin_command():
    """Create an admin user."""
    import getpass
    username = input('Username: ')
    email = input('Email: ')
    password = getpass.getpass('Password: ')
    if create_user(username, password, email, role='admin'):
        print(f'Admin {username} created successfully!')
    else:
        print('Failed to create admin.')

@app.cli.command('load-sample-data')
def load_sample_data_command():
    """Load sample data."""
    from models import load_sample_data
    load_sample_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
