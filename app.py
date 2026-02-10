from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import hashlib
import hmac
import time
from urllib.parse import urlencode
from models import (
    init_db, create_user, verify_password, get_user_by_id, is_admin,
    get_all_users, update_user_role, delete_user,
    get_all_schools, get_school_by_id, get_regions,
    get_schools_by_region, get_schools_by_level, get_schools_by_region_and_level,
    get_schools_by_source, get_source_stats, update_school_source,
    search_schools,
    create_school, update_school, delete_school,
    get_like, get_likes_count, like_school,
    unlike_school, get_user_liked_schools,
    log_admin_action, get_admin_logs,
    # Permission functions
    get_user_permissions, has_permission, get_all_roles,
    get_all_permissions, get_role_permissions_db, update_role_permissions,
    get_users_with_roles, update_user_permissions, get_user_role
)
from i18n import _, LANGUAGE_NAMES, get_locale

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# OAuth Configuration - 需要在环境变量中设置
OAUTH_CONFIG = {
    'wechat': {
        'appid': os.environ.get('WECHAT_APPID', ''),
        'appsecret': os.environ.get('WECHAT_APPSECRET', ''),
        'redirect_uri': os.environ.get('WECHAT_REDIRECT_URI', 'http://127.0.0.1:5001/auth/wechat/callback'),
    },
    'alipay': {
        'appid': os.environ.get('ALIPAY_APPID', ''),
        'appprivatekey': os.environ.get('ALIPAY_PRIVATE_KEY', ''),
        'alipaypublickey': os.environ.get('ALIPAY_PUBLIC_KEY', ''),
        'redirect_uri': os.environ.get('ALIPAY_REDIRECT_URI', 'http://127.0.0.1:5001/auth/alipay/callback'),
    },
    'twitter': {
        'client_key': os.environ.get('TWITTER_CLIENT_KEY', ''),
        'client_secret': os.environ.get('TWITTER_CLIENT_SECRET', ''),
        'redirect_uri': os.environ.get('TWITTER_REDIRECT_URI', 'http://127.0.0.1:5001/auth/twitter/callback'),
    },
    'facebook': {
        'appid': os.environ.get('FACEBOOK_APPID', ''),
        'appsecret': os.environ.get('FACEBOOK_APPSECRET', ''),
        'redirect_uri': os.environ.get('FACEBOOK_REDIRECT_URI', 'http://127.0.0.1:5001/auth/facebook/callback'),
    }
}

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
        'is_admin': lambda: 'user_id' in session and is_admin(session.get('user_id')),
        'oauth_configured': {k: bool(v.get('appid') or v.get('client_key')) for k, v in OAUTH_CONFIG.items()}
    }

@app.route('/lang/<lang>')
def set_language(lang):
    """Set the language and redirect back."""
    session['lang'] = lang
    referrer = request.headers.get('Referer', '/')
    return redirect(referrer)

@app.route('/')
def index():
    """Homepage - list schools by region with pagination."""
    search_query = request.args.get('q', '')
    selected_region = request.args.get('region', '')
    selected_level = request.args.get('level', '')
    page = request.args.get('page', 1, type=int)
    per_page = 21  # 21 schools per page
    
    # 组合查询：支持搜索 + 地区 + 类型 同时筛选
    if search_query:
        schools = search_schools(search_query, selected_region, selected_level)
    elif selected_region and selected_level:
        schools = get_schools_by_region_and_level(selected_region, selected_level)
    elif selected_region:
        schools = get_schools_by_region(selected_region)
    elif selected_level:
        schools = get_schools_by_level(selected_level)
    else:
        schools = get_all_schools()
    
    regions = get_regions()
    levels = ['university', 'middle', 'elementary', 'kindergarten']
    
    # Pagination
    total = len(schools)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_schools = schools[start:end]
    
    return render_template('index.html', 
                         schools=paginated_schools, 
                         regions=regions, 
                         levels=levels,
                         search_query=search_query,
                         selected_region=selected_region,
                         selected_level=selected_level,
                         page=page,
                         total_pages=total_pages,
                         total_schools=total)

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

# ==================== Login/Register Routes ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        login_type = request.form.get('type', 'password')
        
        if login_type == 'phone':
            # Phone number login
            phone = request.form.get('phone', '').strip()
            code = request.form.get('code', '').strip()
            
            if not phone or not code:
                flash(_('all_required'), 'error')
                return redirect(url_for('login'))
            
            # Verify SMS code
            if session.get('phone_login_code') != code or session.get('phone_login_phone') != phone:
                flash('验证码错误或已过期', 'error')
                return redirect(url_for('login'))
            
            # Find or create user by phone
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,))
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                # Create new user with phone
                user_id = create_user(f'user_{phone[-4:]}', '', '', phone=phone)
                if not user_id:
                    flash('登录失败', 'error')
                    return redirect(url_for('login'))
                user = get_user_by_id(user_id)
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(_('welcome_back').format(user['username']), 'success')
            return redirect(url_for('index'))
        
        else:
            # Password login
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
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form.get('phone', '').strip()
        
        if not username or not password or not email:
            flash(_('all_required'), 'error')
            return redirect(url_for('register'))
        
        user_id = create_user(username, password, email, phone=phone if phone else None)
        if user_id:
            flash(_('register_success'), 'success')
            return redirect(url_for('login'))
        else:
            flash(_('username_exists'), 'error')
    
    return render_template('register.html')

@app.route('/send-sms', methods=['POST'])
def send_sms():
    """Send SMS verification code."""
    phone = request.form.get('phone', '').strip()
    
    if not phone:
        return jsonify({'success': False, 'error': '请输入手机号'})
    
    # Generate 6-digit code
    code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    # Store in session (in production, use SMS service)
    session['phone_login_code'] = code
    session['phone_login_phone'] = phone
    session['phone_login_expire'] = time.time() + 300  # 5 minutes
    
    # TODO: Integrate with SMS service (Twilio, Aliyun, Tencent Cloud, etc.)
    # For demo, just return success
    print(f"📱 SMS Code for {phone}: {code}")
    
    return jsonify({'success': True, 'message': f'验证码已发送: {code}'})

@app.route('/logout')
def logout():
    """User logout."""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('oauth_provider', None)
    flash(_('logout_success'), 'info')
    return redirect(url_for('index'))

# ==================== OAuth Routes ====================

def generate_oauth_url(provider, state):
    """Generate OAuth authorization URL."""
    config = OAUTH_CONFIG.get(provider, {})
    
    if provider == 'twitter':
        base_url = 'https://twitter.com/i/oauth2/authorize'
        params = {
            'response_type': 'code',
            'client_id': config.get('client_key', ''),
            'redirect_uri': config.get('redirect_uri', ''),
            'scope': 'users.read',
            'state': state,
            'code_challenge': 'challenge',
            'code_challenge_method': 'plain'
        }
    elif provider == 'facebook':
        base_url = 'https://www.facebook.com/v18.0/dialog/oauth'
        params = {
            'client_id': config.get('appid', ''),
            'redirect_uri': config.get('redirect_uri', ''),
            'state': state,
            'scope': 'email,public_profile'
        }
    elif provider == 'wechat':
        base_url = 'https://open.weixin.qq.com/connect/qrconnect'
        params = {
            'appid': config.get('appid', ''),
            'redirect_uri': config.get('redirect_uri', ''),
            'response_type': 'code',
            'state': state,
            'scope': 'snsapi_login'
        }
    elif provider == 'alipay':
        base_url = 'https://openauth.alipay.com/oauth2/publicAppAuthorize.htm'
        params = {
            'app_id': config.get('appid', ''),
            'redirect_uri': config.get('redirect_uri', ''),
            'state': state,
            'scope': 'auth_user'
        }
    else:
        return None
    
    return f"{base_url}?{urlencode(params)}"

@app.route('/auth/<provider>')
def oauth_login(provider):
    """Initiate OAuth login."""
    if provider not in OAUTH_CONFIG:
        flash('不支持的登录方式', 'error')
        return redirect(url_for('login'))
    
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    session['oauth_provider'] = provider
    
    oauth_url = generate_oauth_url(provider, state)
    
    if oauth_url:
        return redirect(oauth_url)
    else:
        flash('OAuth配置未完成，请联系管理员', 'error')
        return redirect(url_for('login'))

@app.route('/auth/<provider>/callback')
def oauth_callback(provider):
    """Handle OAuth callback."""
    state = request.args.get('state', '')
    code = request.args.get('code')
    
    # Verify state
    if state != session.get('oauth_state'):
        flash('OAuth验证失败', 'error')
        return redirect(url_for('login'))
    
    # TODO: Exchange code for access token and get user info
    # This requires actual API calls to each provider
    
    # For demo, create a mock user
    provider_id = f"{provider}_{state[:8]}"
    username = f"{provider}_{state[:6]}"
    email = f"{username}@oauth.local"
    
    # Check if user exists
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE oauth_provider = ? AND oauth_id = ?', (provider, provider_id))
    user = cursor.fetchone()
    
    if not user:
        # Create new user
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, email, oauth_provider, oauth_id) VALUES (?, ?, ?, ?, ?)',
                (username, '', email, provider, provider_id)
            )
            user_id = cursor.lastrowid
            conn.commit()
        except:
            # User might exist with same email
            username = f"{provider}_{secrets.randbelow(10000)}"
            cursor.execute(
                'INSERT INTO users (username, password_hash, email, oauth_provider, oauth_id) VALUES (?, ?, ?, ?, ?)',
                (username, '', email, provider, provider_id)
            )
            user_id = cursor.lastrowid
            conn.commit()
    else:
        user_id = user[0]
    
    conn.close()
    
    user = get_user_by_id(user_id)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['oauth_provider'] = provider
        flash(f'{provider.title()} 登录成功！', 'success')
    
    return redirect(url_for('index'))

# ==================== Admin Routes ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    schools = get_all_schools()
    users = get_all_users()
    regions = get_regions()
    source_stats = get_source_stats()
    
    # 计算统计
    hk_count = sum(1 for s in schools if s['region'] == 'Hong Kong')
    schooland_count = sum(1 for s in schools if s['source'] == 'schooland.hk')
    manual_count = sum(1 for s in schools if s['source'] != 'schooland.hk')
    
    # 获取最后更新时间
    last_updated = None
    for s in source_stats:
        if s['source'] == 'schooland.hk' and s.get('last_updated'):
            last_updated = s['last_updated'][:10]
            break
    if not last_updated:
        for s in schools:
            if s['updated_at']:
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
    
    # 按更新时间排序的学校
    sorted_schools = sorted(schools, key=lambda x: x['updated_at'] if x['updated_at'] else x['created_at'] if x['created_at'] else '', reverse=True)
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_schools=sorted_schools[:5],
                         recent_users=users[:5])

@app.route('/admin/schools')
@admin_required
def admin_schools():
    """Manage schools."""
    schools = get_all_schools()
    
    # 按类型统计
    level_stats = {}
    for school in schools:
        level = school['level']
        level_stats[level] = level_stats.get(level, 0) + 1
    
    return render_template('admin/schools.html', schools=schools, level_stats=level_stats)

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

@app.route('/admin/permissions')
@admin_required
def admin_permissions():
    """Permission management page."""
    users = get_users_with_roles()
    roles = get_all_roles()
    all_perms = get_all_permissions()
    
    # 角色权限统计
    role_stats = {}
    for u in users:
        role_stats[u['role']] = role_stats.get(u['role'], 0) + 1
    
    # 角色权限详情
    role_perms = {}
    for r in roles:
        perms = get_role_permissions_db(r)
        role_perms[r] = [p['code'] for p in perms]
    
    role_names = {
        'admin': '管理员',
        'editor': '编辑者',
        'user': '普通用户',
        'viewer': '访客'
    }
    
    category_names = {
        'schools': '学校管理',
        'users': '用户管理',
        'system': '系统管理'
    }
    
    return render_template('admin/permissions.html',
                         users=users,
                         roles=roles,
                         role_stats=role_stats,
                         role_permissions=role_perms,
                         role_names=role_names,
                         category_names=category_names)

@app.route('/admin/role/<role>/permissions', methods=['POST'])
@admin_required
def admin_update_role_permissions(role):
    """Update role permissions."""
    data = request.get_json()
    permissions = data.get('permissions', [])
    update_role_permissions(role, permissions)
    return jsonify({'success': True})

@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@admin_required
def admin_update_user_role(user_id):
    """Update user role."""
    data = request.get_json()
    role = data.get('role')
    if update_user_role(user_id, role):
        return jsonify({'success': True})
    return jsonify({'success': False})

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
        from models import load_sample_data
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
