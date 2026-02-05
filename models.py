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
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create schools table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            level TEXT NOT NULL,
            description TEXT,
            badge_url TEXT,
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

def create_user(username, password, email):
    """Create a new user."""
    password_hash = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
            (username, password_hash, email)
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

def create_school(name, region, country, city, level, description, badge_url=None):
    """Create a new school."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO schools (name, region, country, city, level, description, badge_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (name, region, country, city, level, description, badge_url)
    )
    conn.commit()
    school_id = cursor.lastrowid
    conn.close()
    return school_id

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
        schools = json.load(f)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for school in schools:
        cursor.execute('''
            INSERT OR IGNORE INTO schools (name, region, country, city, level, description, badge_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            school['name'],
            school['region'],
            school['country'],
            school['city'],
            school['level'],
            school.get('description', ''),
            school.get('badge_url', None)
        ))
    
    conn.commit()
    conn.close()
    print(f"Loaded {len(schools)} sample schools")
