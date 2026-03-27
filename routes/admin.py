"""
Admin routes module
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from functools import wraps
import sqlite3
from models import (
    get_all_schools, get_school_by_id, create_school, update_school, delete_school,
    get_all_users, get_user_by_id, update_user_role, delete_user,
    is_admin, get_regions, get_source_stats,
    log_admin_action, get_admin_logs,
    get_user_permissions, has_permission, get_all_roles,
    get_all_permissions, get_role_permissions_db, update_role_permissions,
    get_users_with_roles, update_user_permissions, get_user_role
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, redirect, url_for, flash
        from i18n import _
        if 'user_id' not in session:
            flash(_('please_login'), 'warning')
            return redirect(url_for('login'))
        if not is_admin(session['user_id']):
            flash(_('no_permission'), 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('')
@admin_required
def dashboard():
    """Admin dashboard."""
    schools = get_all_schools()
    users = get_all_users()
    regions = get_regions()
    source_stats = get_source_stats()
    
    hk_count = sum(1 for s in schools if s['region'] == 'Hong Kong')
    schooland_count = sum(1 for s in schools if s['source'] == 'schooland.hk')
    manual_count = sum(1 for s in schools if s['source'] != 'schooland.hk')
    
    last_updated = None
    for s in source_stats:
        if s.get('last_updated'):
            last_updated = s['last_updated'][:10]
            break
    if not last_updated:
        for s in schools:
            if s.get('updated_at'):
                last_updated = s['updated_at'][:10]
                break
    
    stats = {
        'total_schools': len(schools),
        'total_users': len(users),
        'total_regions': len(regions),
        'hk_schools': hk_count,
        'schooland_count': schooland_count,
        'manual_count': manual_count,
        'last_updated': last_updated
    }
    
    sorted_schools = sorted(schools, key=lambda x: x.get('updated_at') or x.get('created_at') or '', reverse=True)
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_schools=sorted_schools[:5],
                         recent_users=users[:5])

@admin_bp.route('/schools')
@admin_required
def schools():
    """Manage schools."""
    schools_list = get_all_schools()
    level_stats = {}
    for school in schools_list:
        level = school.get('level', 'unknown')
        level_stats[level] = level_stats.get(level, 0) + 1
    
    regions = sorted(set(s.get('region') for s in schools_list if s.get('region')))
    
    return render_template('admin/schools.html', 
                         schools=schools_list, 
                         level_stats=level_stats, 
                         regions=regions)

@admin_bp.route('/school/add', methods=['GET', 'POST'])
@admin_required
def add_school():
    """Add new school."""
    from app import app
    
    if request.method == 'POST':
        name = request.form.get('name')
        name_cn = request.form.get('name_cn')
        country = request.form.get('country')
        
        conn = sqlite3.connect(app.config.get('DATABASE', 'database.db'))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, name_cn, country FROM schools 
            WHERE name = ? AND country = ? AND COALESCE(name_cn, '') = COALESCE(?, '')
        ''', (name, country, name_cn))
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            flash(f'School already exists: {existing[1]} ({existing[2] or "N/A"}) - {existing[3]}', 'error')
            return redirect(url_for('admin.add_school'))
        
        data = {
            'name': name,
            'name_cn': name_cn,
            'region': request.form.get('region'),
            'country': country,
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
            flash(_('School added successfully'), 'success')
            return redirect(url_for('admin.schools'))
        else:
            flash(_('Failed to add school'), 'error')
    
    regions = get_regions()
    return render_template('admin/school_form.html', school=None, regions=regions)

@admin_bp.route('/school/<int:school_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_school(school_id):
    """Edit school."""
    school = get_school_by_id(school_id)
    if not school:
        flash(_('School not found'), 'error')
        return redirect(url_for('admin.schools'))
    
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
            flash(_('School updated successfully'), 'success')
            return redirect(url_for('admin.schools'))
        else:
            flash(_('Failed to update school'), 'error')
    
    regions = get_regions()
    return render_template('admin/school_form.html', school=school, regions=regions)

@admin_bp.route('/school/<int:school_id>/delete')
@admin_required
def delete_school_route(school_id):
    """Delete school."""
    if delete_school(school_id):
        flash(_('School deleted successfully'), 'success')
    else:
        flash(_('Failed to delete school'), 'error')
    return redirect(url_for('admin.schools'))

@admin_bp.route('/users')
@admin_required
def users():
    """Manage users."""
    users_list = get_all_users()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/user/create', methods=['POST'])
@admin_required
def create_user():
    """Create user."""
    from app import app
    from werkzeug.security import generate_password_hash
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    conn = sqlite3.connect(app.config.get('DATABASE', 'database.db'))
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (username, email, generate_password_hash(password), role))
        conn.commit()
        flash(_('User created successfully'), 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/promote')
@admin_required
def promote_user(user_id):
    """Promote user to admin."""
    if update_user_role(user_id, 'admin'):
        flash(_('User promoted to admin'), 'success')
    else:
        flash(_('Failed to promote user'), 'error')
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/demote')
@admin_required
def demote_user(user_id):
    """Demote user from admin."""
    if update_user_role(user_id, 'user'):
        flash(_('User demoted to user'), 'success')
    else:
        flash(_('Failed to demote user'), 'error')
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/delete')
@admin_required
def delete_user_route(user_id):
    """Delete user."""
    if delete_user(user_id):
        flash(_('User deleted successfully'), 'success')
    else:
        flash(_('Failed to delete user'), 'error')
    return redirect(url_for('admin.users'))

@admin_bp.route('/logs')
@admin_required
def logs():
    """Admin logs."""
    admin_logs = get_admin_logs(limit=100)
    return render_template('admin/logs.html', logs=admin_logs)

@admin_bp.route('/permissions')
@admin_required
def permissions():
    """Manage permissions."""
    roles = get_all_roles()
    permissions_list = get_all_permissions()
    role_perms = {}
    for role in roles:
        role_perms[role] = get_role_permissions_db(role)
    
    users_with_roles = get_users_with_roles()
    
    return render_template('admin/permissions.html', 
                         roles=roles,
                         permissions=permissions_list,
                         role_perms=role_perms,
                         users=users_with_roles)

@admin_bp.route('/role/<role>/permissions', methods=['POST'])
@admin_required
def update_role_permissions_route(role):
    """Update role permissions."""
    perm_list = request.form.getlist('permissions')
    if update_role_permissions(role, perm_list):
        flash(_('Permissions updated'), 'success')
    else:
        flash(_('Failed to update permissions'), 'error')
    return redirect(url_for('admin.permissions'))

@admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
@admin_required
def update_user_role_route(user_id):
    """Update user role."""
    role = request.form.get('role')
    if update_user_permissions(user_id, role):
        flash(_('User role updated'), 'success')
    else:
        flash(_('Failed to update user role'), 'error')
    return redirect(url_for('admin.permissions'))


def register_routes(app):
    """Register admin routes with the Flask app."""
    app.register_blueprint(admin_bp)
