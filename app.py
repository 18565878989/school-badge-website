import urllib.parse
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
import sqlite3
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import hashlib
import hmac
import time
from urllib.parse import urlencode
from models import (
    init_db, create_user, verify_password, get_user_by_id, is_admin, get_db_connection,
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
    selected_country = request.args.get('country', '')
    selected_city = request.args.get('city', '')
    selected_level = request.args.get('level', '')
    page = request.args.get('page', 1, type=int)
    per_page = 21  # 21 schools per page
    
    conn = get_db_connection()
    
    # 获取国家列表（仅当选择地区时显示）
    countries = []
    if selected_region:
        countries = conn.execute("SELECT DISTINCT country FROM schools WHERE region = ? ORDER BY country", 
                                  (selected_region,)).fetchall()
        countries = [c[0] for c in countries]
    
    # 获取城市列表（仅当选择国家时显示）
    cities = []
    if selected_country:
        cities = conn.execute("SELECT DISTINCT city FROM schools WHERE country = ? AND city IS NOT NULL AND city != '' ORDER BY city", 
                              (selected_country,)).fetchall()
        cities = [c[0] for c in cities]
    
    # 获取香港区域列表（仅当选择香港时显示）
    hk_districts = []
    if selected_country == 'Hong Kong':
        hk_districts = conn.execute("SELECT DISTINCT district FROM schools WHERE country = 'Hong Kong' AND district IS NOT NULL AND district != '' ORDER BY district").fetchall()
        hk_districts = [d[0] for d in hk_districts]
    
    selected_district = request.args.get('district', '')
    
    # 组合查询：支持搜索 + 地区 + 国家 + 城市 + 区域 + 类型 同时筛选
    if search_query:
        schools = search_schools(search_query, selected_region, selected_level)
    elif selected_country and selected_level and selected_region and selected_district:
        # 完整筛选：地区 + 国家 + 区域 + 类型
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND district = ? AND level = ? ORDER BY name", 
                               (selected_region, selected_country, selected_district, selected_level)).fetchall()
    elif selected_country and selected_level and selected_region and selected_city:
        # 完整筛选：地区 + 国家 + 城市 + 类型
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND city = ? AND level = ? ORDER BY name", 
                               (selected_region, selected_country, selected_city, selected_level)).fetchall()
    elif selected_country and selected_level and selected_region:
        # 完整筛选：地区 + 国家 + 类型
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND level = ? ORDER BY name", 
                               (selected_region, selected_country, selected_level)).fetchall()
    elif selected_region and selected_country and selected_city:
        # 地区 + 国家 + 城市
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND city = ? ORDER BY name", 
                               (selected_region, selected_country, selected_city)).fetchall()
    elif selected_region and selected_country and selected_district:
        # 地区 + 国家 + 区域
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND district = ? ORDER BY name", 
                               (selected_region, selected_country, selected_district)).fetchall()
    elif selected_region and selected_country:
        # 地区 + 国家
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? ORDER BY name", 
                               (selected_region, selected_country)).fetchall()
    elif selected_country and selected_level:
        # 国家 + 类型（无地区时）
        schools = conn.execute("SELECT * FROM schools WHERE country = ? AND level = ? ORDER BY name", 
                               (selected_country, selected_level)).fetchall()
    elif selected_country:
        # 仅国家
        schools = conn.execute("SELECT * FROM schools WHERE country = ? ORDER BY name", 
                               (selected_country,)).fetchall()
    elif selected_region and selected_level:
        schools = get_schools_by_region_and_level(selected_region, selected_level)
    elif selected_region:
        schools = get_schools_by_region(selected_region)
    elif selected_level:
        schools = get_schools_by_level(selected_level)
    else:
        schools = get_all_schools()
    
    # 地区选项列表
    regions = ['Asia', 'North America', 'Europe', 'Oceania', 'Africa', 'South America']
    levels = ['university', 'middle', 'elementary', 'kindergarten']
    
    conn.close()
    
    # Pagination
    total = len(schools)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_schools = schools[start:end]
    
    return render_template('index_apple.html', 
                         schools=paginated_schools, 
                         regions=regions, 
                         levels=levels,
                         countries=countries,
                         cities=cities,
                         hk_districts=hk_districts,
                         search_query=search_query,
                         selected_region=selected_region,
                         selected_country=selected_country,
                         selected_city=selected_city,
                         selected_district=selected_district,
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
    
    # Get badge evolution data
    import sqlite3
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    
    cursor.execute("SELECT * FROM badge_history WHERE school_id = ? ORDER BY year_start ASC", (school_id,))
    badge_history = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM school_events WHERE school_id = ? ORDER BY year ASC", (school_id,))
    events = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM digital_collectibles WHERE school_id = ? AND status = 'active' ORDER BY price ASC", (school_id,))
    digital_collectibles = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM products WHERE school_id = ? AND status = 'active' ORDER BY price ASC", (school_id,))
    products = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Build map query string
    school_dict = dict(school)
    addr = school_dict.get('address', '')
    name = school_dict.get('name', '')
    city = school_dict.get('city', '')
    country = school_dict.get('country', '')
    
    # Use address if available, else name, else district
    if addr:
        map_query = addr
        # Only add country if not in address
        if country and country.lower() not in addr.lower():
            map_query += ',' + country
    elif name:
        map_query = name
        # Add location info
        if school_dict.get('district'):
            map_query += ',' + school_dict.get('district')
        elif city:
            map_query += ',' + city
        if country:
            map_query += ',' + country
    else:
        map_query = ""
    
    return render_template('school.html', 
                         breadcrumb='school',
                         school=school, 
                         likes_count=likes_count,
                         user_liked=user_liked,
                         badge_history=badge_history,
                         events=events,
                         digital_collectibles=digital_collectibles,
                         products=products,
                         map_query=map_query)

@app.route('/badge-history/<int:school_id>')
def badge_history(school_id):
    """Show badge history for a school."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get school info
    cursor.execute("SELECT * FROM schools WHERE id = ?", (school_id,))
    school = cursor.execute("SELECT * FROM schools WHERE id = ?", (school_id,)).fetchone()
    
    if not school:
        conn.close()
        flash('School not found', 'error')
        return redirect(url_for('index'))
    
    # Get badge history
    cursor.execute("SELECT * FROM badge_history WHERE school_id = ? ORDER BY year_start ASC", (school_id,))
    badge_history = [dict(row) for row in cursor.fetchall()]
    
    # Get events
    cursor.execute("SELECT * FROM school_events WHERE school_id = ? ORDER BY year ASC", (school_id,))
    events = [dict(row) for row in cursor.fetchall()]
    
    # Get likes count
    likes_count = cursor.execute("SELECT COUNT(*) FROM likes WHERE school_id = ?", (school_id,)).fetchone()[0]
    
    # Check if user liked
    user_liked = False
    if 'user_id' in session:
        user_liked = cursor.execute("SELECT COUNT(*) FROM likes WHERE user_id = ? AND school_id = ?", (session['user_id'], school_id)).fetchone()[0] > 0
    
    conn.close()
    
    return render_template('badge_history.html', 
                         school=school,
                         badge_history=badge_history,
                         events=events,
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
    return render_template('my_likes.html', schools=liked_schools, breadcrumb='likes')

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

@app.route('/campus/north-america')
def campus_north_america():
    """Campus gallery for North American universities."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'North America' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    conn.close()
    return render_template('campus_north_america.html', schools=schools)

@app.route('/campus/europe')
def campus_europe():
    """Campus gallery for European universities."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'Europe' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    # If no schools with images, show all European universities
    if not schools:
        schools = conn.execute('''
            SELECT id, name, name_cn, region, country, city, 
                   founded, motto, campus_image, campus_image_desc
            FROM schools 
            WHERE region = 'Europe' AND level = 'university'
            ORDER BY country, name
            LIMIT 50
        ''').fetchall()
    
    conn.close()
    return render_template('campus_europe.html', schools=schools)

@app.route('/campus/asia')
def campus_asia():
    """Campus gallery for Asian universities."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'Asia' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    conn.close()
    # If too many, limit to 50
    if len(schools) > 50:
        schools = schools[:50]
    return render_template('campus_asia.html', schools=schools)

@app.route('/campus/oceania')
def campus_oceania():
    """Campus gallery for Oceania universities."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'Oceania' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    # If no schools with images, show all Oceania universities
    if not schools:
        schools = conn.execute('''
            SELECT id, name, name_cn, region, country, city, 
                   founded, motto, campus_image, campus_image_desc
            FROM schools 
            WHERE region = 'Oceania' AND level = 'university'
            ORDER BY country, name
            LIMIT 50
        ''').fetchall()
    
    conn.close()
    return render_template('campus_oceania.html', schools=schools)

@app.route('/campus/south-america')
def campus_south_america():
    """Campus gallery for South American universities."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'South America' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    # If no schools with images, show all South American universities
    if not schools:
        schools = conn.execute('''
            SELECT id, name, name_cn, region, country, city, 
                   founded, motto, campus_image, campus_image_desc
            FROM schools 
            WHERE region = 'South America' AND level = 'university'
            ORDER BY country, name
            LIMIT 50
        ''').fetchall()
    
    conn.close()
    return render_template('campus_south_america.html', schools=schools)

@app.route('/campus/africa')
def campus_africa():
    """Campus gallery for African universities."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'Africa' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    # If no schools with images, show all African universities
    if not schools:
        schools = conn.execute('''
            SELECT id, name, name_cn, region, country, city, 
                   founded, motto, campus_image, campus_image_desc
            FROM schools 
            WHERE region = 'Africa' AND level = 'university'
            ORDER BY country, name
            LIMIT 50
        ''').fetchall()
    
    conn.close()
    return render_template('campus_africa.html', schools=schools)

@app.route('/campus')
def campus():
    """Unified campus gallery with region tabs."""
    conn = get_db_connection()
    
    # Fetch schools for each region
    north_america = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'North America' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    asia = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'Asia' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
        LIMIT 50
    ''').fetchall()
    
    europe = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'Europe' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    oceania = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'Oceania' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    south_america = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'South America' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    africa = conn.execute('''
        SELECT id, name, name_cn, region, country, city, 
               founded, motto, campus_image, campus_image_desc
        FROM schools 
        WHERE region = 'Africa' AND level = 'university'
        AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY country, name
    ''').fetchall()
    
    conn.close()
    
    return render_template('campus.html',
                         north_america=north_america,
                         asia=asia,
                         europe=europe,
                         oceania=oceania,
                         south_america=south_america,
                         africa=africa)

@app.route('/social')
def social():
    """Social hub page - topics and discussions."""
    conn = get_db_connection()
    
    # Get topics
    tab = request.args.get('tab', 'hot')
    if tab == 'hot':
        cursor = conn.execute("""
            SELECT t.*, u.username as author_name, s.name as school_name, s.badge_url as school_badge
            FROM topics t
            LEFT JOIN users u ON t.author_id = u.id
            LEFT JOIN schools s ON t.school_id = s.id
            ORDER BY t.is_hot DESC, t.likes_count DESC, t.created_at DESC
            LIMIT 20
        """)
    else:
        cursor = conn.execute("""
            SELECT t.*, u.username as author_name, s.name as school_name, s.badge_url as school_badge
            FROM topics t
            LEFT JOIN users u ON t.author_id = u.id
            LEFT JOIN schools s ON t.school_id = s.id
            ORDER BY t.created_at DESC
            LIMIT 20
        """)
    
    topics = [dict(row) for row in cursor.fetchall()]
    
    # Get hot topics for sidebar
    cursor = conn.execute("""
        SELECT t.*, u.username as author_name
        FROM topics t
        LEFT JOIN users u ON t.author_id = u.id
        WHERE t.is_hot = 1
        ORDER BY t.likes_count DESC
        LIMIT 5
    """)
    hot_topics = [dict(row) for row in cursor.fetchall()]
    
    # Get replies count
    cursor = conn.execute('SELECT COUNT(*) FROM topic_replies')
    replies_count = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('social.html', 
                          topics=topics, 
                          hot_topics=hot_topics,
                          replies_count=replies_count,
                          tab=tab,
                          online_count=128,
                          breadcrumb='social')
def social():
    """Social hub page."""
    conn = get_db_connection()
    
    # Get popular schools (mock data for demo)
    popular_schools = [
        {'id': 42, 'name': 'Zhejiang University', 'city': 'Hangzhou', 'country': 'China', 'likes_count': 2345, 'badge_url': '/static/images/zju.png'},
        {'id': 7257, 'name': 'Tsinghua University', 'city': 'Beijing', 'country': 'China', 'likes_count': 2123, 'badge_url': None},
        {'id': 7258, 'name': 'Peking University', 'city': 'Beijing', 'country': 'China', 'likes_count': 1987, 'badge_url': None},
        {'id': 8001, 'name': 'Harvard University', 'city': 'Cambridge', 'country': 'United States', 'likes_count': 1876, 'badge_url': None},
        {'id': 8002, 'name': 'Stanford University', 'city': 'Stanford', 'country': 'United States', 'likes_count': 1654, 'badge_url': None},
        {'id': 8003, 'name': 'MIT', 'city': 'Cambridge', 'country': 'United States', 'likes_count': 1543, 'badge_url': None}
    ]
    
    conn.close()
    return render_template('social.html', popular_schools=popular_schools)

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
    
    # 获取所有地区（用于筛选）
    regions = sorted(set(s['region'] for s in schools if s['region']))
    
    return render_template('admin/schools.html', schools=schools, level_stats=level_stats, regions=regions)

@app.route('/admin/school/add', methods=['GET', 'POST'])
@admin_required
def admin_add_school():
    """Add new school."""
    if request.method == 'POST':
        name = request.form.get('name')
        name_cn = request.form.get('name_cn')
        country = request.form.get('country')
        
        # 检查唯一性
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, name_cn, country FROM schools 
            WHERE name = ? AND country = ? AND COALESCE(name_cn, '') = COALESCE(?, '')
        ''', (name, country, name_cn))
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            flash(f'学校已存在: {existing[1]} ({existing[2] or "N/A"}) - {existing[3]}', 'error')
            return redirect(url_for('admin_add_school'))
        
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
            log_admin_action(session['user_id'], 'CREATE_SCHOOL', 'school', school_id, name)
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
        name = request.form.get('name')
        name_cn = request.form.get('name_cn')
        country = request.form.get('country')
        
        # 检查唯一性（排除当前编辑的学校）
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, name_cn, country FROM schools 
            WHERE name = ? AND country = ? AND COALESCE(name_cn, '') = COALESCE(?, '') AND id != ?
        ''', (name, country, name_cn, school_id))
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            flash(f'学校已存在: {existing[1]} ({existing[2] or "N/A"}) - {existing[3]}', 'error')
            return redirect(url_for('admin_edit_school', school_id=school_id))
        
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
        
        if update_school(school_id, **data):
            log_admin_action(session['user_id'], 'UPDATE_SCHOOL', 'school', school_id, name)
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

@app.route('/admin/user/create', methods=['POST'])
@admin_required
def admin_create_user():
    """Create a new user."""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    phone = data.get('phone', '').strip() or None
    role = data.get('role', 'user')
    
    # 验证输入
    if not username or len(username) < 3:
        return jsonify({'success': False, 'message': '用户名至少需要3个字符'})
    
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': '请输入有效的邮箱'})
    
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少需要6个字符'})
    
    if role not in ['admin', 'editor', 'user', 'viewer']:
        return jsonify({'success': False, 'message': '无效的角色'})
    
    # 检查用户名和邮箱是否已存在
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': '用户名或邮箱已存在'})
    
    # 创建用户
    from werkzeug.security import generate_password_hash
    password_hash = generate_password_hash(password)
    
    cursor.execute('''
        INSERT INTO users (username, password_hash, email, phone, role, permissions, data_scope)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, password_hash, email, phone, role, '{}', '["all"]' if role == 'admin' else '["own"]'))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 记录日志
    log_admin_action(session['user_id'], 'CREATE_USER', 'user', user_id, username)
    
    return jsonify({'success': True, 'message': '用户创建成功'})

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
                         role_perms=role_perms,
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

@app.route('/topic/<int:topic_id>')
def topic_detail(topic_id):
    """Topic detail page with replies."""
    conn = get_db_connection()
    
    # Get topic
    cursor = conn.execute('''
        SELECT t.*, u.username as author_name, s.name as school_name, s.badge_url as school_badge
        FROM topics t
        LEFT JOIN users u ON t.author_id = u.id
        LEFT JOIN schools s ON t.school_id = s.id
        WHERE t.id = ?
    ''', (topic_id,))
    topic = dict(cursor.fetchone())
    
    if not topic:
        conn.close()
        return redirect(url_for('social'))
    
    # Get replies
    cursor = conn.execute('''
        SELECT r.*, u.username as author_name
        FROM topic_replies r
        LEFT JOIN users u ON r.author_id = u.id
        WHERE r.topic_id = ?
        ORDER BY r.created_at ASC
    ''', (topic_id,))
    replies = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('topic_detail.html', topic=topic, replies=replies, breadcrumb='social')


@app.route('/share')
def share_page():
    """分享页面"""
    content_type = request.args.get('type', 'post')
    content_id = request.args.get('id', '1')
    return render_template('share.html', content_type=content_type, content_id=content_id)


@app.route('/badges')
def badge_hub():
    """Badge history hub page."""
    conn = get_db_connection()
    
    # Get schools with badge history
    cursor = conn.execute('''
        SELECT DISTINCT s.id, s.name, s.name_cn, s.city, s.country, s.badge_url,
               (SELECT COUNT(*) FROM badge_history bh WHERE bh.school_id = s.id) as badge_count,
               (SELECT COUNT(*) FROM school_events se WHERE se.school_id = s.id) as event_count
        FROM schools s
        LEFT JOIN badge_history bh ON s.id = bh.school_id
        LEFT JOIN school_events se ON s.id = se.school_id
        WHERE bh.school_id IS NOT NULL OR se.school_id IS NOT NULL
        ORDER BY badge_count DESC, event_count DESC
        LIMIT 20
    ''')
    schools = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('badge_hub.html', schools=schools, breadcrumb='badges')

    return render_template('badge_hub.html', schools=schools, breadcrumb='badges')

# ==================== Share API ====================

@app.route('/api/share/config')
def get_share_config():
    """获取分享配置（前端调用）"""
    config = {
        'wechat': {
            'enabled': True,
            'appId': os.environ.get('WECHAT_APP_ID', ''),
            'methods': ['qr', 'link']
        },
        'weibo': {
            'enabled': bool(os.environ.get('WEIBO_APP_KEY')),
            'appKey': os.environ.get('WEIBO_APP_KEY', ''),
        },
        'douyin': {
            'enabled': True,
            'methods': ['link', 'poster']
        },
        'xiaohongshu': {
            'enabled': True,
            'methods': ['link', 'poster']
        },
        'twitter': {
            'enabled': bool(os.environ.get('TWITTER_CLIENT_KEY')),
            'methods': ['link']
        },
        'facebook': {
            'enabled': bool(os.environ.get('FACEBOOK_APP_ID')),
            'methods': ['link']
        },
        'whatsapp': {
            'enabled': True,
            'methods': ['link']
        },
        'copy_link': {
            'enabled': True
        }
    }
    return jsonify({'success': True, 'config': config})

@app.route('/api/share/<content_type>/<int:content_id>')
def get_share_info(content_type, content_id):
    """获取分享信息"""
    conn = get_db_connection()
    
    if content_type == 'post':
        cursor = conn.execute('''
            SELECT p.*, u.username as author_name, s.name as school_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN schools s ON p.school_id = s.id
            WHERE p.id = ?
        ''', (content_id,))
    elif content_type == 'school':
        cursor = conn.execute('''
            SELECT s.*, COUNT(DISTINCT p.id) as posts_count
            FROM schools s
            LEFT JOIN posts p ON s.id = p.school_id
            WHERE s.id = ?
            GROUP BY s.id
        ''', (content_id,))
    elif content_type == 'topic':
        cursor = conn.execute('SELECT * FROM topics WHERE id = ?', (content_id,))
    else:
        return jsonify({'success': False, 'error': 'Invalid content type'}), 400
    
    item = dict(cursor.fetchone())
    conn.close()
    
    if not item:
        return jsonify({'success': False, 'error': 'Content not found'}), 404
    
    # 生成分享URL
    base_url = request.host_url.rstrip('/')
    share_url = f"{base_url}/{content_type}/{content_id}"
    
    # 获取标题和描述
    if content_type == 'post':
        title = item.get('content', '')[:100]
        desc = f"来自 {item.get('author_name', '')} 的分享"
        image = None
    elif content_type == 'school':
        title = item.get('name', '')
        desc = f"{item.get('name_cn', '')} - {item.get('city', '')}"
        image = item.get('badge_url')
    else:
        title = item.get('name', '') or item.get('title', '')
        desc = item.get('description', '')
        image = item.get('cover_image')
    
    return jsonify({
        'success': True,
        'data': {
            'url': share_url,
            'title': title,
            'desc': desc,
            'image': image,
            'content_type': content_type,
            'content_id': content_id
        }
    })

@app.route('/api/share/record', methods=['POST'])
def record_share():
    """记录分享"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    content_type = data.get('content_type')
    content_id = data.get('content_id')
    platform = data.get('platform')
    share_url = data.get('share_url')
    
    if not all([content_type, content_id, platform]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO share_records (content_type, content_id, user_id, platform, share_url, click_count)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (content_type, content_id, session['user_id'], platform, share_url))
    conn.commit()
    share_id = cursor.lastrowid
    conn.close()
    
    # 增加内容的分享数
    if content_type == 'post':
        conn = get_db_connection()
        conn.execute('UPDATE posts SET shares_count = shares_count + 1 WHERE id = ?', (content_id,))
        conn.commit()
        conn.close()
    
    return jsonify({'success': True, 'share_id': share_id})

# ==================== Posts API ====================

@app.route('/api/posts')
def get_posts():
    """获取帖子列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    tab = request.args.get('tab', 'hot')
    school_id = request.args.get('school_id', type=int)
    user_id = request.args.get('user_id', type=int)
    
    conn = get_db_connection()
    
    # 构建查询
    where_clauses = ["status = 'published'"]
    params = []
    
    if school_id:
        where_clauses.append("school_id = ?")
        params.append(school_id)
    
    if user_id:
        where_clauses.append("author_id = ?")
        params.append(user_id)
    
    where_sql = " AND ".join(where_clauses)
    
    if tab == 'hot':
        order_by = "is_hot DESC, likes_count DESC, created_at DESC"
    elif tab == 'latest':
        order_by = "created_at DESC"
    elif tab == 'essence':
        where_sql += " AND is_essence = 1"
        order_by = "likes_count DESC"
    else:
        order_by = "created_at DESC"
    
    offset = (page - 1) * per_page
    
    cursor = conn.execute(f'''
        SELECT p.*, u.username as author_name, u.avatar_url as author_avatar,
               s.name as school_name, s.badge_url as school_badge
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        LEFT JOIN schools s ON p.school_id = s.id
        WHERE {where_sql}
        ORDER BY {order_by}
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    
    posts = [dict(row) for row in cursor.fetchall()]
    
    # 获取总数
    cursor = conn.execute(f'SELECT COUNT(*) FROM posts WHERE {where_sql}', params)
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'posts': posts,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_more': offset + len(posts) < total
    })

@app.route('/api/posts/<int:post_id>')
def get_post(post_id):
    """获取帖子详情"""
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT p.*, u.username as author_name, u.avatar_url as author_avatar,
               s.name as school_name, s.badge_url as school_badge
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        LEFT JOIN schools s ON p.school_id = s.id
        WHERE p.id = ?
    ''', (post_id,))
    
    post = dict(cursor.fetchone())
    
    if not post:
        conn.close()
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    
    # 增加浏览数
    conn.execute('UPDATE posts SET views_count = views_count + 1 WHERE id = ?', (post_id,))
    conn.commit()
    post['views_count'] += 1
    
    conn.close()
    
    return jsonify({'success': True, 'post': post})

@app.route('/api/posts', methods=['POST'])
def create_post():
    """创建帖子"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    content = data.get('content')
    content_type = data.get('content_type', 'text')
    media_urls = data.get('media_urls', [])
    school_id = data.get('school_id')
    tags = data.get('tags', [])
    visibility = data.get('visibility', 'public')
    
    if not content:
        return jsonify({'success': False, 'error': 'Content required'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO posts (author_id, school_id, content_type, content, media_urls, tags, visibility)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], school_id, content_type, content, 
          ','.join(media_urls) if media_urls else None,
          ','.join(tags) if tags else None,
          visibility))
    conn.commit()
    post_id = cursor.lastrowid
    
    # 更新用户帖子数
    conn.execute('UPDATE user_profiles SET posts_count = posts_count + 1 WHERE user_id = ?', 
                 (session['user_id'],))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'post_id': post_id})

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """更新帖子"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    # 检查权限
    conn = get_db_connection()
    cursor = conn.execute('SELECT author_id FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    
    if not post:
        conn.close()
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    
    if post['author_id'] != session['user_id'] and not is_admin(session.get('user_id')):
        conn.close()
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    data = request.get_json()
    content = data.get('content')
    media_urls = data.get('media_urls')
    tags = data.get('tags')
    
    updates = []
    params = []
    
    if content:
        updates.append('content = ?')
        params.append(content)
    if media_urls is not None:
        updates.append('media_urls = ?')
        params.append(','.join(media_urls) if media_urls else None)
    if tags is not None:
        updates.append('tags = ?')
        params.append(','.join(tags) if tags else None)
    
    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(post_id)
        conn.execute(f'UPDATE posts SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()
    
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """删除帖子"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    cursor = conn.execute('SELECT author_id FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    
    if not post:
        conn.close()
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    
    if post['author_id'] != session['user_id'] and not is_admin(session.get('user_id')):
        conn.close()
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    conn.execute('UPDATE posts SET status = ? WHERE id = ?', ('deleted', post_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ==================== Like API ====================

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """点赞帖子"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    
    # 检查是否已点赞
    cursor = conn.execute('''
        SELECT id FROM likes 
        WHERE user_id = ? AND target_type = 'post' AND target_id = ?
    ''', (session['user_id'], post_id))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Already liked'}), 400
    
    # 添加点赞
    conn.execute('''
        INSERT INTO likes (user_id, target_type, target_id)
        VALUES (?, 'post', ?)
    ''', (session['user_id'], post_id))
    
    # 更新帖子点赞数
    conn.execute('UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/posts/<int:post_id>/like', methods=['DELETE'])
def unlike_post(post_id):
    """取消点赞"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT id FROM likes 
        WHERE user_id = ? AND target_type = 'post' AND target_id = ?
    ''', (session['user_id'], post_id))
    
    like = cursor.fetchone()
    
    if not like:
        conn.close()
        return jsonify({'success': False, 'error': 'Not liked yet'}), 400
    
    conn.execute('DELETE FROM likes WHERE id = ?', (like['id'],))
    conn.execute('UPDATE posts SET likes_count = likes_count - 1 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ==================== Comments API ====================

@app.route('/api/posts/<int:post_id>/comments')
def get_comments(post_id):
    """获取评论列表"""
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT c.*, u.username as author_name, u.avatar_url as author_avatar,
               (SELECT username FROM users u2 
                JOIN comments c2 ON c2.author_id = u2.id 
                WHERE c2.id = c.parent_id) as reply_to_name
        FROM comments c
        LEFT JOIN users u ON c.author_id = u.id
        WHERE c.post_id = ? AND c.is_approved = 1
        ORDER BY c.created_at ASC
    ''', (post_id,))
    
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'comments': comments})

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    """创建评论"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    content = data.get('content')
    parent_id = data.get('parent_id')
    media_urls = data.get('media_urls', [])
    
    if not content:
        return jsonify({'success': False, 'error': 'Content required'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO comments (post_id, parent_id, author_id, content, media_urls)
        VALUES (?, ?, ?, ?, ?)
    ''', (post_id, parent_id, session['user_id'], content, 
          ','.join(media_urls) if media_urls else None))
    conn.commit()
    comment_id = cursor.lastrowid
    
    # 更新帖子评论数
    conn.execute('UPDATE posts SET comments_count = comments_count + 1 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'comment_id': comment_id})

# ==================== Follow API ====================

@app.route('/api/users/<int:user_id>/follow', methods=['POST'])
def follow_user(user_id):
    """关注用户"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    if user_id == session['user_id']:
        return jsonify({'success': False, 'error': 'Cannot follow yourself'}), 400
    
    conn = get_db_connection()
    
    # 检查是否已关注
    cursor = conn.execute('''
        SELECT id FROM follows WHERE follower_id = ? AND following_id = ?
    ''', (session['user_id'], user_id))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Already following'}), 400
    
    # 添加关注
    conn.execute('''
        INSERT INTO follows (follower_id, following_id)
        VALUES (?, ?)
    ''', (session['user_id'], user_id))
    
    # 更新关注数
    conn.execute('UPDATE user_profiles SET following_count = following_count + 1 WHERE user_id = ?', 
                 (session['user_id'],))
    conn.execute('UPDATE user_profiles SET followers_count = followers_count + 1 WHERE user_id = ?', 
                 (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/users/<int:user_id>/follow', methods=['DELETE'])
def unfollow_user(user_id):
    """取消关注"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT id FROM follows WHERE follower_id = ? AND following_id = ?
    ''', (session['user_id'], user_id))
    
    follow = cursor.fetchone()
    
    if not follow:
        conn.close()
        return jsonify({'success': False, 'error': 'Not following'}), 400
    
    conn.execute('DELETE FROM follows WHERE id = ?', (follow['id'],))
    conn.execute('UPDATE user_profiles SET following_count = following_count - 1 WHERE user_id = ?', 
                 (session['user_id'],))
    conn.execute('UPDATE user_profiles SET followers_count = followers_count - 1 WHERE user_id = ?', 
                 (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ==================== Notifications API ====================

@app.route('/api/notifications')
def get_notifications():
    """获取通知列表"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT * FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 50
    ''', (session['user_id'],))
    
    notifications = [dict(row) for row in cursor.fetchall()]
    
    # 获取未读数
    cursor = conn.execute('''
        SELECT COUNT(*) FROM notifications 
        WHERE user_id = ? AND is_read = 0
    ''', (session['user_id'],))
    unread_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({'success': True, 'notifications': notifications, 'unread_count': unread_count})

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """标记通知为已读"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?', 
                 (notification_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/notifications/read-all', methods=['POST'])
def mark_all_notifications_read():
    """标记所有通知为已读"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ==================== Collections API ====================

@app.route('/api/collections')
def get_collections():
    """获取收藏夹列表"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    
    cursor = conn.execute('''
        SELECT c.*, 
               (SELECT COUNT(*) FROM collection_items WHERE collection_id = c.id) as items_count
        FROM collections c
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    ''', (session['user_id'],))
    
    collections = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'collections': collections})

@app.route('/api/collections', methods=['POST'])
def create_collection():
    """创建收藏夹"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    is_public = data.get('is_public', 0)
    
    if not name:
        return jsonify({'success': False, 'error': 'Name required'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO collections (user_id, name, description, is_public)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], name, description, is_public))
    conn.commit()
    collection_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'collection_id': collection_id})

@app.route('/api/collections/<int:collection_id>/items', methods=['POST'])
def add_to_collection(collection_id):
    """添加内容到收藏夹"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    content_type = data.get('content_type')
    content_id = data.get('content_id')
    
    if not content_type or not content_id:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    
    # 检查收藏夹归属
    cursor = conn.execute('SELECT user_id FROM collections WHERE id = ?', (collection_id,))
    collection = cursor.fetchone()
    
    if not collection or collection['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'success': False, 'error': 'Collection not found'}), 404
    
    # 检查是否已收藏
    cursor = conn.execute('''
        SELECT id FROM collection_items 
        WHERE collection_id = ? AND content_type = ? AND content_id = ?
    ''', (collection_id, content_type, content_id))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Already in collection'}), 400
    
    # 添加收藏
    conn.execute('''
        INSERT INTO collection_items (collection_id, content_type, content_id)
        VALUES (?, ?, ?)
    ''', (collection_id, content_type, content_id))
    
    # 更新收藏夹数量
    conn.execute('UPDATE collections SET items_count = items_count + 1 WHERE id = ?', (collection_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ==================== Membership API ====================

@app.route('/api/membership/levels')
def get_membership_levels():
    """获取会员等级列表"""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT * FROM membership_levels 
        WHERE is_active = 1 
        ORDER BY sort_order ASC
    ''')
    levels = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'levels': levels})

@app.route('/api/membership/status')
def get_membership_status():
    """获取当前用户会员状态"""
    if 'user_id' not in session:
        return jsonify({'is_member': False, 'level': None})
    
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT m.*, ml.name as level_name, ml.name_cn as level_name_cn, ml.features
        FROM memberships m
        LEFT JOIN membership_levels ml ON m.level = ml.code
        WHERE m.user_id = ? AND m.expire_date > date('now') AND m.level IS NOT NULL
        ORDER BY m.expire_date DESC
        LIMIT 1
    ''', (session['user_id'],))
    
    membership = cursor.fetchone()
    conn.close()
    
    if membership:
        return jsonify({
            'success': True,
            'is_member': True,
            'level': dict(membership)
        })
    else:
        return jsonify({'success': True, 'is_member': False, 'level': None})

@app.route('/api/membership/upgrade', methods=['POST'])
def upgrade_membership():
    """升级会员"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    level_code = data.get('level')
    duration = data.get('duration', 'monthly')  # monthly or yearly
    
    if not level_code:
        return jsonify({'success': False, 'error': 'Level required'}), 400
    
    # 获取会员等级价格
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM membership_levels WHERE code = ?', (level_code,))
    level = cursor.fetchone()
    
    if not level:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid level'}), 400
    
    price = level['price_yearly'] if duration == 'yearly' else level['price_monthly']
    
    # 创建支付订单
    order_no = f"MEM{int(time.time())}{session['user_id']}"
    cursor = conn.execute('''
        INSERT INTO payments (user_id, order_no, amount, product_type, status)
        VALUES (?, ?, ?, 'membership', 'pending')
    ''', (session['user_id'], order_no, price))
    conn.commit()
    payment_id = cursor.lastrowid
    conn.close()
    
    # TODO: 调起支付流程
    
    return jsonify({
        'success': True,
        'payment_id': payment_id,
        'order_no': order_no,
        'amount': price,
        'level': level_code,
        'message': '订单已创建，请完成支付'
    })

# ==================== Payment API ====================

@app.route('/api/payments/create', methods=['POST'])
def create_payment():
    """创建支付订单"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    product_type = data.get('product_type')  # membership, product, etc.
    product_id = data.get('product_id')
    amount = data.get('amount')
    payment_method = data.get('payment_method', 'wechat')
    
    if not amount or amount <= 0:
        return jsonify({'success': False, 'error': 'Invalid amount'}), 400
    
    conn = get_db_connection()
    order_no = f"PAY{int(time.time())}{session['user_id']}"
    
    cursor = conn.execute('''
        INSERT INTO payments (user_id, order_no, amount, payment_method, product_type, product_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], order_no, amount, payment_method, product_type, product_id))
    conn.commit()
    payment_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'success': True,
        'payment_id': payment_id,
        'order_no': order_no,
        'amount': amount,
        'payment_method': payment_method
    })

@app.route('/api/payments/<order_no>/status')
def get_payment_status(order_no):
    """查询支付状态"""
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM payments WHERE order_no = ?', (order_no,))
    payment = cursor.fetchone()
    conn.close()
    
    if not payment:
        return jsonify({'success': False, 'error': 'Order not found'}), 404
    
    return jsonify({'success': True, 'payment': dict(payment)})

# ==================== Ad Positions API ====================

@app.route('/api/ads/positions')
def get_ad_positions():
    """获取广告位列表"""
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM ad_positions WHERE is_active = 1 ORDER BY id')
    positions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'positions': positions})

@app.route('/api/ads/<position_code>')
def get_ads(position_code):
    """获取广告位广告"""
    conn = get_db_connection()
    
    # 获取广告位信息
    cursor = conn.execute('SELECT * FROM ad_positions WHERE code = ? AND is_active = 1', (position_code,))
    position = cursor.fetchone()
    
    if not position:
        conn.close()
        return jsonify({'success': False, 'error': 'Position not found'}), 404
    
    # 获取广告列表
    cursor = conn.execute('''
        SELECT a.*, ad.company_name as advertiser_name
        FROM ads a
        LEFT JOIN advertisers ad ON a.advertiser_id = ad.id
        WHERE a.position_id = ? AND a.status = 'active' 
        AND (a.start_date IS NULL OR a.start_date <= date('now'))
        AND (a.end_date IS NULL OR a.end_date >= date('now'))
        ORDER BY a.views_count DESC
        LIMIT 5
    ''', (position['id'],))
    
    ads = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'position': dict(position),
        'ads': ads
    })

@app.route('/api/ads/<int:ad_id>/click', methods=['POST'])
def click_ad(ad_id):
    """记录广告点击"""
    conn = get_db_connection()
    
    # 更新点击数
    conn.execute('UPDATE ads SET clicks_count = clicks_count + 1 WHERE id = ?', (ad_id,))
    conn.commit()
    
    # 获取广告跳转链接
    cursor = conn.execute('SELECT target_url FROM ads WHERE id = ?', (ad_id,))
    ad = cursor.fetchone()
    conn.close()
    
    if ad and ad['target_url']:
        return jsonify({'success': True, 'url': ad['target_url']})
    else:
        return jsonify({'success': False, 'error': 'Ad not found'}), 404

# ==================== Shop API ====================

@app.route('/api/shop/products')
def get_shop_products():
    """获取商品列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    category = request.args.get('category')
    keyword = request.args.get('keyword')
    
    conn = get_db_connection()
    
    where_clauses = ["status = 'active'"]
    params = []
    
    if category:
        where_clauses.append("category = ?")
        params.append(category)
    
    if keyword:
        where_clauses.append("(name LIKE ? OR description LIKE ?)")
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    
    where_sql = " AND ".join(where_clauses)
    offset = (page - 1) * per_page
    
    cursor = conn.execute(f'''
        SELECT * FROM shop_products
        WHERE {where_sql}
        ORDER BY is_featured DESC, sold_count DESC, created_at DESC
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    
    products = [dict(row) for row in cursor.fetchall()]
    
    # 获取分类
    cursor = conn.execute('''
        SELECT category, COUNT(*) as count 
        FROM shop_products 
        WHERE status = 'active' 
        GROUP BY category
    ''')
    categories = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'products': products,
        'categories': categories
    })

@app.route('/api/shop/products/<int:product_id>')
def get_shop_product(product_id):
    """获取商品详情"""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT sp.*, u.username as seller_name
        FROM shop_products sp
        LEFT JOIN users u ON sp.seller_id = u.id
        WHERE sp.id = ? AND sp.status = 'active'
    ''', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    
    return jsonify({'success': True, 'product': dict(product)})

@app.route('/api/shop/cart')
def get_cart():
    """获取购物车"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT c.*, sp.name, sp.price, sp.images, sp.stock
        FROM carts c
        JOIN shop_products sp ON c.product_id = sp.id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    ''', (session['user_id'],))
    
    items = [dict(row) for row in cursor.fetchall()]
    
    # 计算总价
    total = sum(item['price'] * item['quantity'] for item in items)
    
    conn.close()
    
    return jsonify({
        'success': True,
        'items': items,
        'total': total,
        'count': len(items)
    })

@app.route('/api/shop/cart', methods=['POST'])
def add_to_cart():
    """添加商品到购物车"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'success': False, 'error': 'Product ID required'}), 400
    
    conn = get_db_connection()
    
    # 检查商品是否存在
    cursor = conn.execute('SELECT stock, status FROM shop_products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    
    if not product or product['status'] != 'active':
        conn.close()
        return jsonify({'success': False, 'error': 'Product not available'}), 400
    
    if product['stock'] < quantity:
        conn.close()
        return jsonify({'success': False, 'error': 'Insufficient stock'}), 400
    
    # 检查购物车是否已有
    cursor = conn.execute('''
        SELECT id, quantity FROM carts WHERE user_id = ? AND product_id = ?
    ''', (session['user_id'], product_id))
    cart_item = cursor.fetchone()
    
    if cart_item:
        new_quantity = cart_item['quantity'] + quantity
        if new_quantity > product['stock']:
            conn.close()
            return jsonify({'success': False, 'error': 'Insufficient stock'}), 400
        conn.execute('UPDATE carts SET quantity = ? WHERE id = ?', (new_quantity, cart_item['id']))
    else:
        conn.execute('''
            INSERT INTO carts (user_id, product_id, quantity)
            VALUES (?, ?, ?)
        ''', (session['user_id'], product_id, quantity))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Added to cart'})

@app.route('/api/shop/cart/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    """从购物车移除"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    conn.execute('DELETE FROM carts WHERE id = ? AND user_id = ?', (cart_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/shop/orders', methods=['POST'])
def create_shop_order():
    """创建商城订单"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    data = request.get_json()
    items = data.get('items', [])
    shipping_name = data.get('shipping_name')
    shipping_phone = data.get('shipping_phone')
    shipping_address = data.get('shipping_address')
    note = data.get('note', '')
    
    if not items:
        return jsonify({'success': False, 'error': 'No items'}), 400
    
    conn = get_db_connection()
    
    # 计算总价并验证库存
    total_amount = 0
    order_items = []
    
    for item in items:
        cursor = conn.execute('SELECT * FROM shop_products WHERE id = ?', (item['product_id'],))
        product = cursor.fetchone()
        
        if not product or product['status'] != 'active':
            conn.close()
            return jsonify({'success': False, 'error': f"Product {item['product_id']} not available"}), 400
        
        if product['stock'] < item['quantity']:
            conn.close()
            return jsonify({'success': False, 'error': f"Insufficient stock for {product['name']}"}), 400
        
        subtotal = product['price'] * item['quantity']
        total_amount += subtotal
        
        order_items.append({
            'product_id': product['id'],
            'product_name': product['name'],
            'product_image': product['images'].split(',')[0] if product['images'] else None,
            'price': product['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal
        })
    
    # 创建订单
    order_no = f"ORD{int(time.time())}{session['user_id']}"
    cursor = conn.execute('''
        INSERT INTO shop_orders (order_no, user_id, total_amount, actual_amount, 
                                shipping_name, shipping_phone, shipping_address, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order_no, session['user_id'], total_amount, total_amount,
          shipping_name, shipping_phone, shipping_address, note))
    conn.commit()
    order_id = cursor.lastrowid
    
    # 创建订单明细
    for item in order_items:
        conn.execute('''
            INSERT INTO shop_order_items (order_id, product_id, product_name, product_image, 
                                         price, quantity, subtotal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, item['product_id'], item['product_name'], item['product_image'],
              item['price'], item['quantity'], item['subtotal']))
        
        # 减少库存
        conn.execute('UPDATE shop_products SET stock = stock - ?, sold_count = sold_count + ? WHERE id = ?',
                    (item['quantity'], item['quantity'], item['product_id']))
    
    # 清空购物车
    conn.execute('DELETE FROM carts WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'order_id': order_id,
        'order_no': order_no,
        'total_amount': total_amount
    })

@app.route('/api/shop/orders')
def get_shop_orders():
    """获取订单列表"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Login required'}), 401
    
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT * FROM shop_orders
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 20
    ''', (session['user_id'],))
    
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'orders': orders})

# ==================== Statistics API ====================

@app.route('/api/stats/overview')
def get_stats_overview():
    """获取数据概览"""
    if not is_admin(session.get('user_id')):
        return jsonify({'success': False, 'error': 'Admin required'}), 403
    
    conn = get_db_connection()
    
    # 用户统计
    cursor = conn.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # 会员统计
    cursor = conn.execute('''
        SELECT ml.name_cn, COUNT(m.id) as count
        FROM membership_levels ml
        LEFT JOIN memberships m ON ml.code = m.level
        GROUP BY ml.code
    ''')
    membership_stats = [dict(row) for row in cursor.fetchall()]
    
    # 帖子统计
    cursor = conn.execute("SELECT COUNT(*) FROM posts WHERE status = 'published'")
    total_posts = cursor.fetchone()[0]
    
    # 评论统计
    cursor = conn.execute('SELECT COUNT(*) FROM comments')
    total_comments = cursor.fetchone()[0]
    
    # 分享统计
    cursor = conn.execute('''
        SELECT platform, COUNT(*) as count, SUM(click_count) as clicks
        FROM share_records
        GROUP BY platform
    ''')
    share_stats = [dict(row) for row in cursor.fetchall()]
    
    # 订单统计
    cursor = conn.execute('''
        SELECT COUNT(*), SUM(actual_amount) FROM shop_orders WHERE status = 'paid'
    ''')
    order_stats = dict(cursor.fetchone())
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'membership_stats': membership_stats,
            'total_posts': total_posts,
            'total_comments': total_comments,
            'share_stats': share_stats,
            'order_count': order_stats[0] or 0,
            'order_amount': order_stats[1] or 0
        }
    })

# ==================== Pages ====================

@app.route('/membership')
def membership_page():
    """会员中心页面"""
    return render_template('membership.html')

@app.route('/shop')
def shop_page():
    """商城页面"""
    return render_template('shop.html')

@app.route('/social-v2')
def social_v2_page():
    """新版社交页面（Apple风格）"""
    return render_template('social_v2.html')

# Run without debug mode and without reloader
if __name__ == '__main__':
    # Disable debug mode explicitly
    app.debug = False
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
