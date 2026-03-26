#!/usr/bin/env python3
"""
Pytest configuration and fixtures for school-badge-website tests.
"""
import os
import sys
import sqlite3
import json

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'


@pytest.fixture(scope='session')
def project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope='session')
def test_db_path(project_root):
    return os.path.join(project_root, 'database.db')


@pytest.fixture(scope='function')
def test_db(test_db_path):
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture(scope='function')
def empty_db():
    """Create an empty in-memory database for unit tests."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.executescript('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user')),
            oauth_provider TEXT,
            oauth_id TEXT,
            avatar_url TEXT,
            permissions TEXT,
            data_scope TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE schools (
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
            source TEXT DEFAULT 'manual',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            school_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (school_id) REFERENCES schools (id),
            UNIQUE(user_id, school_id)
        );
        CREATE TABLE admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE permission_definitions (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE role_permissions (
            role TEXT NOT NULL,
            permission_code TEXT NOT NULL,
            granted INTEGER DEFAULT 1,
            PRIMARY KEY (role, permission_code)
        );
    ''')
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def app(test_db_path):
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    with flask_app.test_request_context():
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
        sess['role'] = 'user'
    return client


@pytest.fixture
def admin_client(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 999
        sess['username'] = 'admin'
        sess['role'] = 'admin'
    return client


@pytest.fixture
def sample_user(empty_db):
    from werkzeug.security import generate_password_hash
    conn = empty_db
    now = '2026-01-01 00:00:00'
    conn.execute('''
        INSERT INTO users (username, password_hash, email, phone, role, permissions, data_scope, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('testuser', generate_password_hash('testpass'), 'test@example.com', '1234567890', 'user', json.dumps({}), '["own"]', now))
    conn.commit()
    user = conn.execute('SELECT * FROM users WHERE username = ?', ('testuser',)).fetchone()
    return dict(user)


@pytest.fixture
def sample_admin(empty_db):
    from werkzeug.security import generate_password_hash
    conn = empty_db
    now = '2026-01-01 00:00:00'
    conn.execute('''
        INSERT INTO users (username, password_hash, email, phone, role, permissions, data_scope, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('admin', generate_password_hash('adminpass'), 'admin@example.com', '9999999999', 'admin', json.dumps({}), '["all"]', now))
    conn.commit()
    user = conn.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
    return dict(user)


@pytest.fixture
def sample_schools(empty_db):
    conn = empty_db
    now = '2026-01-01 00:00:00'
    schools = [
        ('Harvard University', '哈佛大学', 'North America', 'USA', 'Cambridge', 'Massachusetts Hall', 'university', 'Old university', 'http://badge.url', 'http://harvard.edu', 'Veritas', 1636, 'Larry Bacow'),
        ('Tsinghua University', '清华大学', 'Asia', 'China', 'Beijing', 'No. 1 Tsinghua Park', 'university', 'Top university', 'http://badge2.url', 'http://tsinghua.edu.cn', 'Self-discipline', 1911, 'Qiu Yong'),
        ('PKU Primary School', '北京大学附属小学', 'Asia', 'China', 'Beijing', 'No. 5 Yiheyuan Road', 'primary', 'Primary school', None, None, None, None, None),
        ('Oxford University', '牛津大学', 'Europe', 'UK', 'Oxford', 'Wellington Square', 'university', 'Old university', None, 'http://ox.ac.uk', 'Dominus Illuminatio Mea', 1096, 'Irene Tracey'),
    ]
    for school in schools:
        conn.execute('''
            INSERT INTO schools (name, name_cn, region, country, city, address, level, description, badge_url, website, motto, founded, principal, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*school, now, now))
    conn.commit()
    result = conn.execute('SELECT * FROM schools').fetchall()
    return [dict(row) for row in result]
