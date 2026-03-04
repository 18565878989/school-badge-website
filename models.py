import sqlite3
from datetime import datetime
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash

# 简繁转换映射表
def traditional_to_simplified(text):
    """繁体转简体"""
    if not text:
        return text
    # 常用繁简对照表
    mapping = {
        '大學': '大学', '學院': '学院', '學校': '学校',
        '北京': '北京', '清華': '清华', '交通': '交通',
        '復旦': '复旦', '浙江': '浙江', '南京': '南京',
        '上海': '上海', '武漢': '武汉', '成都': '成都',
        '西安': '西安', '哈爾濱': '哈尔滨', '廣州': '广州',
        '中山': '中山', '廈門': '厦门', '天津': '天津',
        '蘇州': '苏州', '重慶': '重庆', '香港': '香港',
        '澳門': '澳门', '臺灣': '台湾', '臺北': '台北',
        '高雄': '高雄', '新竹': '新竹', '師範': '师范',
        '工業': '工业', '科技': '科技', '醫學': '医学',
        '農業': '农业', '海洋': '海洋', '石油': '石油',
        '理工': '理工', '財經': '财经', '政法': '政法',
        '外語': '外语', '語言': '语言', '音樂': '音乐',
        '美術': '美术', '體育': '体育', '軍事': '军事',
        '航空': '航空', '航天': '航天', '電子': '电子',
        '機械': '机械', '化工': '化工', '建築': '建筑',
        '水利': '水利', '電力': '电力', '鐵路': '铁路',
        '郵電': '邮电', '林業': '林业', '畜牧': '畜牧',
        '醫藥': '医药', '中醫': '中医', '藥學': '药学',
        '護理': '护理', '工商': '工商', '管理': '管理',
        '人力': '人力', '資源': '资源', '環境': '环境',
        '材料': '材料', '能源': '能源', '動力': '动力',
        '計算機': '计算机', '信息': '信息', '軟件': '软件',
        '網絡': '网络', '自動化': '自动化', '光電': '光电',
        '精密': '精密', '儀器': '仪器', '物理': '物理',
        '化學': '化学', '數學': '数学', '生物': '生物',
        '地理': '地理', '歷史': '历史', '哲學': '哲学',
        '經濟': '经济', '法律': '法律', '政治': '政治',
        '社會': '社会', '新聞': '新闻', '傳播': '传播',
        '廣告': '广告', '設計': '设计', '藝術': '艺术',
        '文學': '文学', '語文': '语文', '外文': '外文',
        '國際': '国际', '對外': '对外', '留學': '留学',
        '繼續': '继续', '職業': '职业', '成人': '成人',
        '遠程': '远程', '網絡教育': '网络教育', '開放': '开放',
        '研究': '研究', '研究生': '研究生', '博士': '博士',
        '碩士': '硕士', '學士': '学士', '預科': '预科',
        '附屬': '附属', '附中': '附中', '附小': '附小',
        '實驗': '实验', '外國語': '外国语', '外語': '外语',
        '第一': '第一', '第二': '第二', '第三': '第三',
    }
    result = text
    for trad, simp in mapping.items():
        result = result.replace(trad, simp)
    return result

def simplified_to_traditional(text):
    """简体转繁体"""
    if not text:
        return text
    mapping = {
        '大学': '大學', '学院': '學院', '学校': '學校',
        '清华': '清華', '复旦': '復旦', '师范': '師範',
        '工业': '工業', '科技': '科技', '医学': '醫學',
        '农业': '農業', '海洋': '海洋', '理工': '理工',
        '财经': '財經', '政法': '政法', '外语': '外語',
        '语言': '語言', '音乐': '音樂', '美术': '美術',
        '体育': '體育', '军事': '軍事', '航空': '航空',
        '航天': '航天', '电子': '電子', '机械': '機械',
        '化工': '化工', '建筑': '建築', '水利': '水利',
        '电力': '電力', '铁路': '鐵路', '邮电': '郵電',
        '林业': '林業', '畜牧': '畜牧', '医药': '醫藥',
        '中医': '中醫', '药学': '藥學', '护理': '護理',
        '工商': '工商', '管理': '管理', '人力': '人力',
        '资源': '資源', '环境': '環境', '材料': '材料',
        '能源': '能源', '动力': '動力', '计算机': '計算機',
        '信息': '信息', '软件': '軟件', '网络': '網絡',
        '自动化': '自動化', '光电': '光電', '精密': '精密',
        '仪器': '儀器', '物理': '物理', '化学': '化學',
        '数学': '數學', '生物': '生物', '地理': '地理',
        '历史': '歷史', '哲学': '哲學', '经济': '經濟',
        '法律': '法律', '政治': '政治', '社会': '社會',
        '新闻': '新聞', '传播': '傳播', '广告': '廣告',
        '设计': '設計', '艺术': '藝術', '文学': '文學',
        '语文': '語文', '外文': '外文', '国际': '國際',
        '对外': '對外', '留学': '留學', '继续': '繼續',
        '职业': '職業', '成人': '成人', '远程': '遠程',
        '网络教育': '網絡教育', '开放': '開放', '研究': '研究',
        '研究生': '研究生', '博士': '博士', '硕士': '碩士',
        '学士': '學士', '预科': '預科', '附属': '附屬',
        '附中': '附中', '附小': '附小', '实验': '實驗',
        '外国语': '外國語', '第一': '第一', '第二': '第二',
        '第三': '第三', '台湾': '臺灣', '台北': '臺北',
    }
    result = text
    for simp, trad in mapping.items():
        result = result.replace(simp, trad)
    return result

def get_db_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table with roles and OAuth support
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user')),
            oauth_provider TEXT,
            oauth_id TEXT,
            avatar_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create schools table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_cn TEXT,
            region TEXT NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT,
            level TEXT NOT NULL,
            description TEXT,
            badge_url TEXT,
            website TEXT,
            motto TEXT,
            founded INTEGER,
            principal TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create likes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            school_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (school_id) REFERENCES schools (id),
            UNIQUE(user_id, school_id)
        )
    ''')
    
    # Create admin audit log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    """Get user by username."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get user by ID."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_phone(phone):
    """Get user by phone number."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    conn.close()
    return user

def get_user_by_oauth(provider, oauth_id):
    """Get user by OAuth provider and ID."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE oauth_provider = ? AND oauth_id = ?', 
        (provider, oauth_id)
    ).fetchone()
    conn.close()
    return user

def create_user(username, password, email, role='user', phone=None, oauth_provider=None, oauth_id=None, avatar_url=None):
    """Create a new user."""
    password_hash = generate_password_hash(password) if password else ''
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''INSERT INTO users (username, password_hash, email, phone, role, oauth_provider, oauth_id, avatar_url) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, password_hash, email, phone, role, oauth_provider, oauth_id, avatar_url)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def verify_password(username, password):
    """Verify user password."""
    user = get_user_by_username(username)
    if user and user['password_hash'] and check_password_hash(user['password_hash'], password):
        return user
    return None

def verify_phone_code(phone, code):
    """Verify phone SMS code."""
    from flask import session
    if session.get('phone_login_code') == code and session.get('phone_login_phone') == phone:
        return True
    return False

def is_admin(user_id):
    """Check if user is admin."""
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user and user['role'] == 'admin'

def get_user_role(user_id):
    """Get user role."""
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user['role'] if user else None

def get_user_permissions(user_id):
    """Get user permissions as dict."""
    import json
    conn = get_db_connection()
    user = conn.execute('SELECT permissions, role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if not user:
        return {}
    
    # 返回用户自定义权限或角色默认权限
    if user['permissions']:
        try:
            return json.loads(user['permissions'])
        except:
            return get_role_permissions(user['role'])
    
    return get_role_permissions(user['role'])

def get_role_permissions(role):
    """Get default permissions for a role."""
    import json
    conn = get_db_connection()
    perms = conn.execute(
        'SELECT permission_code, granted FROM role_permissions WHERE role = ?',
        (role,)
    ).fetchall()
    conn.close()
    
    result = {}
    for p in perms:
        result[p['permission_code']] = bool(p['granted'])
    return result

def has_permission(user_id, permission_code):
    """Check if user has specific permission."""
    perms = get_user_permissions(user_id)
    return perms.get(permission_code, False)

def get_all_roles():
    """Get all roles."""
    conn = get_db_connection()
    roles = conn.execute('SELECT DISTINCT role FROM users UNION SELECT DISTINCT role FROM role_permissions').fetchall()
    conn.close()
    return [r[0] for r in roles]

def get_all_permissions():
    """Get all permission definitions."""
    conn = get_db_connection()
    perms = conn.execute('SELECT * FROM permission_definitions WHERE is_active = 1 ORDER BY category, name').fetchall()
    conn.close()
    return [dict(p) for p in perms]

def get_role_permissions_db(role):
    """Get role permissions from database."""
    conn = get_db_connection()
    perms = conn.execute(
        'SELECT pd.* FROM permission_definitions pd '
        'JOIN role_permissions rp ON pd.code = rp.permission_code '
        'WHERE rp.role = ? AND pd.is_active = 1',
        (role,)
    ).fetchall()
    conn.close()
    return [dict(p) for p in perms]

def update_role_permissions(role, permissions):
    """Update role permissions."""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 删除旧权限
    cursor.execute('DELETE FROM role_permissions WHERE role = ?', (role,))
    
    # 插入新权限
    for perm_code, granted in permissions.items():
        if granted:
            cursor.execute(
                'INSERT INTO role_permissions (role, permission_code, granted) VALUES (?, ?, 1)',
                (role, perm_code)
            )
    
    # 更新用户的自定义权限
    user_perms = {"role_permissions": permissions}
    cursor.execute('UPDATE users SET permissions = ? WHERE role = ?', (json.dumps(user_perms), role))
    
    conn.commit()
    conn.close()

def update_user_permissions(user_id, permissions):
    """Update user custom permissions (override role)."""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 保存用户自定义权限
    cursor.execute('UPDATE users SET permissions = ? WHERE id = ?', (json.dumps(permissions), user_id))
    
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_users_with_roles():
    """Get all users with their roles."""
    conn = get_db_connection()
    users = conn.execute(
        'SELECT id, username, email, role, permissions, data_scope, status, created_at, last_login, login_count '
        'FROM users ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return [dict(u) for u in users]

def create_user(username, password, email, role='user', phone=None, oauth_provider=None, oauth_id=None, avatar_url=None):
    """Create a new user."""
    import json
    password_hash = generate_password_hash(password) if password else ''
    data_scope = '["all"]' if role == 'admin' else '["own"]'
    permissions = json.dumps(get_role_permissions(role))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''INSERT INTO users (username, password_hash, email, phone, role, oauth_provider, oauth_id, avatar_url, permissions, data_scope) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, password_hash, email, phone, role, oauth_provider, oauth_id, avatar_url, permissions, data_scope)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_user_role(user_id, new_role, data_scope='["all"]'):
    """Update user role and permissions."""
    import json
    permissions = json.dumps(get_role_permissions(new_role))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ?, permissions = ?, data_scope = ? WHERE id = ?', 
                  (new_role, permissions, data_scope, user_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_all_users():
    """Get all users."""
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, email, phone, role, oauth_provider, avatar_url, created_at FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return users

def update_user_role(user_id, new_role):
    """Update user role."""
    if new_role not in ('admin', 'user'):
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def update_user_avatar(user_id, avatar_url):
    """Update user avatar."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET avatar_url = ? WHERE id = ?', (avatar_url, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Delete a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete user's likes first
    cursor.execute('DELETE FROM likes WHERE user_id = ?', (user_id,))
    # Delete user
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def get_all_schools():
    """Get all schools."""
    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM schools ORDER BY name').fetchall()
    conn.close()
    return schools

def get_school_by_id(school_id):
    """Get school by ID."""
    conn = get_db_connection()
    school = conn.execute('SELECT * FROM schools WHERE id = ?', (school_id,)).fetchone()
    conn.close()
    return school

def get_schools_by_region(region):
    """Get schools by region."""
    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM schools WHERE region = ? ORDER BY name', (region,)).fetchall()
    conn.close()
    return schools

def get_schools_by_region_and_level(region, level):
    """Get schools by region and level."""
    conn = get_db_connection()
    schools = conn.execute(
        'SELECT * FROM schools WHERE region = ? AND level = ? ORDER BY name', 
        (region, level)
    ).fetchall()
    conn.close()
    return schools

def get_schools_by_level(level):
    """Get schools by level."""
    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM schools WHERE level = ? ORDER BY name', (level,)).fetchall()
    conn.close()
    return schools

def search_schools(query, region=None, level=None):
    """Search schools by name, country, or city with optional filters.
    Supports both simplified and traditional Chinese."""
    conn = get_db_connection()
    
    # 生成简繁两种查询
    query_simp = query
    query_trad = simplified_to_traditional(query)
    
    # 如果简繁相同，只查一次
    if query_simp == query_trad:
        sql = 'SELECT * FROM schools WHERE (name LIKE ? OR name_cn LIKE ? OR country LIKE ? OR city LIKE ?)'
        params = [f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%']
    else:
        # 简繁分开查，用UNION合并去重
        sql = '''
            SELECT * FROM schools WHERE (name LIKE ? OR name_cn LIKE ? OR country LIKE ? OR city LIKE ?)
            UNION
            SELECT * FROM schools WHERE (name LIKE ? OR name_cn LIKE ? OR country LIKE ? OR city LIKE ?)
        '''
        params = [
            f'%{query_simp}%', f'%{query_simp}%', f'%{query_simp}%', f'%{query_simp}%',
            f'%{query_trad}%', f'%{query_trad}%', f'%{query_trad}%', f'%{query_trad}%'
        ]
    
    if region:
        sql += ' AND region = ?'
        params.append(region)
    
    if level:
        sql += ' AND level = ?'
        params.append(level)
    
    sql += ' ORDER BY name'
    
    schools = conn.execute(sql, params).fetchall()
    conn.close()
    return schools

def get_regions():
    """Get all unique regions."""
    conn = get_db_connection()
    regions = conn.execute('SELECT DISTINCT region FROM schools ORDER BY region').fetchall()
    conn.close()
    return [r['region'] for r in regions]

def get_schools_by_source(source):
    """Get schools by data source."""
    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM schools WHERE source = ? ORDER BY name', (source,)).fetchall()
    conn.close()
    return schools

def get_schools_by_source_and_region(source, region):
    """Get schools by source and region."""
    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM schools WHERE source = ? AND region = ? ORDER BY name', (source, region)).fetchall()
    conn.close()
    return schools

def get_source_stats():
    """Get statistics by data source."""
    conn = get_db_connection()
    stats = conn.execute('SELECT source, COUNT(*) as count, MAX(updated_at) as last_updated FROM schools GROUP BY source ORDER BY count DESC').fetchall()
    conn.close()
    return [dict(s) for s in stats]

def update_school_source(school_id, source):
    """Update school data source."""
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('UPDATE schools SET source = ?, updated_at = ? WHERE id = ?', (source, now, school_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def create_school(name, name_cn=None, region=None, country=None, city=None, address=None, 
                  level=None, description=None, badge_url=None, website=None, 
                  motto=None, founded=None, principal=None, source='manual'):
    """Create a new school."""
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO schools (name, name_cn, region, country, city, address, level, description, badge_url, website, motto, founded, principal, source, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name, name_cn, region, country, city, address, level, description, 
        badge_url, website, motto, founded, principal, source, now, now
    ))
    conn.commit()
    school_id = cursor.lastrowid
    conn.close()
    return school_id

def update_school(school_id, **kwargs):
    """Update a school."""
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = ['updated_at = ?']
    values = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    
    for key, value in kwargs.items():
        if value is not None and key not in ('id', 'created_at'):
            fields.append(f'{key} = ?')
            values.append(value)
    
    if len(fields) == 1:  # 只有updated_at
        conn.close()
        return False
    
    values.append(school_id)
    query = f'UPDATE schools SET {", ".join(fields)} WHERE id = ?'
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_school(school_id):
    """Delete a school."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete likes for this school
    cursor.execute('DELETE FROM likes WHERE school_id = ?', (school_id,))
    # Delete school
    cursor.execute('DELETE FROM schools WHERE id = ?', (school_id,))
    conn.commit()
    conn.close()
    return True

def log_admin_action(admin_id, action, target_type=None, target_id=None, details=None):
    """Log admin action."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO admin_logs (admin_id, action, target_type, target_id, details) VALUES (?, ?, ?, ?, ?)',
        (admin_id, action, target_type, target_id, details)
    )
    conn.commit()
    conn.close()

def get_admin_logs(limit=100):
    """Get admin logs."""
    conn = get_db_connection()
    logs = conn.execute('''
        SELECT l.*, u.username 
        FROM admin_logs l 
        LEFT JOIN users u ON l.admin_id = u.id 
        ORDER BY l.created_at DESC 
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return logs

def get_like(user_id, school_id):
    """Check if user liked a school."""
    conn = get_db_connection()
    like = conn.execute(
        'SELECT * FROM likes WHERE user_id = ? AND school_id = ?',
        (user_id, school_id)
    ).fetchone()
    conn.close()
    return like

def get_likes_count(school_id):
    """Get total likes for a school."""
    conn = get_db_connection()
    count = conn.execute(
        'SELECT COUNT(*) FROM likes WHERE school_id = ?',
        (school_id,)
    ).fetchone()[0]
    conn.close()
    return count

def get_user_liked_schools(user_id):
    """Get all schools liked by a user."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT s.* FROM schools s
        JOIN likes l ON s.id = l.school_id
        WHERE l.user_id = ?
        ORDER BY l.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return schools

def like_school(user_id, school_id):
    """Like a school."""
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO likes (user_id, school_id) VALUES (?, ?)',
            (user_id, school_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def unlike_school(user_id, school_id):
    """Unlike a school."""
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM likes WHERE user_id = ? AND school_id = ?',
        (user_id, school_id)
    )
    conn.commit()
    conn.close()
    return True

def load_sample_data():
    """Load sample school data from JSON file."""
    import json
    
    with open('data/sample_schools.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        schools = data.get('schools', data)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for school in schools:
        cursor.execute('''
            INSERT OR IGNORE INTO schools (name, name_cn, region, country, city, address, level, description, badge_url, website, motto, founded, principal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            school['name'],
            school.get('name_cn'),
            school['region'],
            school['country'],
            school['city'],
            school.get('address', ''),
            school['level'],
            school.get('description', ''),
            school.get('badge_url', None),
            school.get('website', None),
            school.get('motto', None),
            school.get('founded', None),
            school.get('principal', None)
        ))
    
    conn.commit()
    conn.close()
    print(f"Loaded {len(schools)} sample schools")
