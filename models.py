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
    
    # Create users table with roles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user')),
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

def create_user(username, password, email, role='user'):
    """Create a new user."""
    password_hash = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)',
            (username, password_hash, email, role)
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
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def is_admin(user_id):
    """Check if user is admin."""
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user and user['role'] == 'admin'

def get_all_users():
    """Get all users."""
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC').fetchall()
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
    return True

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

def get_schools_by_level(level):
    """Get schools by level."""
    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM schools WHERE level = ? ORDER BY name', (level,)).fetchall()
    conn.close()
    return schools

def search_schools(query):
    """Search schools by name, country, or city."""
    conn = get_db_connection()
    schools = conn.execute(
        'SELECT * FROM schools WHERE name LIKE ? OR country LIKE ? OR city LIKE ? ORDER BY name',
        (f'%{query}%', f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return schools

def get_regions():
    """Get all unique regions."""
    conn = get_db_connection()
    regions = conn.execute('SELECT DISTINCT region FROM schools ORDER BY region').fetchall()
    conn.close()
    return [r['region'] for r in regions]

def create_school(name, name_cn=None, region=None, country=None, city=None, address=None, 
                  level=None, description=None, badge_url=None, website=None, 
                  motto=None, founded=None, principal=None):
    """Create a new school."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO schools (name, name_cn, region, country, city, address, level, description, badge_url, website, motto, founded, principal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name, name_cn, region, country, city, address, level, description, 
        badge_url, website, motto, founded, principal
    ))
    conn.commit()
    school_id = cursor.lastrowid
    conn.close()
    return school_id

def update_school(school_id, **kwargs):
    """Update a school."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f'{key} = ?')
            values.append(value)
    
    if not fields:
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
        schools = data.get('schools', data)  # Support both formats
    
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
