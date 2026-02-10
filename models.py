import sqlite3
from datetime import datetime
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash

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
    """Search schools by name, country, or city with optional filters."""
    conn = get_db_connection()
    
    sql = 'SELECT * FROM schools WHERE (name LIKE ? OR name_cn LIKE ? OR country LIKE ? OR city LIKE ?)'
    params = [f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%']
    
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
