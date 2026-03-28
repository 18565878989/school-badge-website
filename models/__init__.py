"""
Models Package - 数据访问层
导出所有函数保持向后兼容
"""
import sqlite3

# 简繁转换函数
from .user import (
    traditional_to_simplified,
    simplified_to_traditional,
)

# 用户相关
from .user import (
    get_db_connection,
    get_user_by_username,
    get_user_by_id,
    get_user_by_phone,
    get_user_by_oauth,
    get_all_users,
    get_users_with_roles,
    create_user,
    verify_password,
    verify_phone_code,
    is_admin,
    get_user_role,
    get_user_permissions,
    has_permission,
    get_all_roles,
    get_all_permissions,
    get_role_permissions_db,
    update_role_permissions,
    update_user_permissions,
    update_user_role,
    update_user_avatar,
    delete_user,
)

# 学校相关
from .school import (
    get_all_schools,
    get_school_by_id,
    get_schools_by_region,
    get_schools_by_level,
    get_schools_by_region_and_level,
    get_schools_paginated,
    search_schools,
    get_regions,
    get_region_stats,
    get_school_rankings,
    create_school,
    update_school,
    delete_school,
    get_schools_by_source,
    get_source_stats,
    update_school_source,
)

# Likes 相关 (复用school.py的连接)
from .user import get_db_connection

def like_school(user_id, school_id):
    """点赞学校"""
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO likes (user_id, school_id, created_at) VALUES (?, ?, datetime("now"))',
            (user_id, school_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # 已经点赞
    finally:
        conn.close()

def unlike_school(user_id, school_id):
    """取消点赞"""
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM likes WHERE user_id = ? AND school_id = ?',
        (user_id, school_id)
    )
    conn.commit()
    conn.close()

def get_like(user_id, school_id):
    """获取点赞记录"""
    conn = get_db_connection()
    like = conn.execute(
        'SELECT * FROM likes WHERE user_id = ? AND school_id = ?',
        (user_id, school_id)
    ).fetchone()
    conn.close()
    return dict(like) if like else None

def get_likes_count(school_id):
    """获取学校点赞数"""
    conn = get_db_connection()
    count = conn.execute(
        'SELECT COUNT(*) FROM likes WHERE school_id = ?',
        (school_id,)
    ).fetchone()[0]
    conn.close()
    return count

def get_user_liked_schools(user_id):
    """获取用户点赞的学校"""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT s.* FROM schools s
        INNER JOIN likes l ON s.id = l.school_id
        WHERE l.user_id = ?
        ORDER BY l.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(s) for s in schools]

# Admin 日志
def log_admin_action(admin_id, action, target_type=None, target_id=None, details=None):
    """记录管理员操作"""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO admin_logs (admin_id, action, target_type, target_id, details, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    ''', (admin_id, action, target_type, target_id, details))
    conn.commit()
    conn.close()

def get_admin_logs(limit=100):
    """获取管理员操作日志"""
    conn = get_db_connection()
    logs = conn.execute('''
        SELECT l.*, u.username as admin_name
        FROM admin_logs l
        LEFT JOIN users u ON l.admin_id = u.id
        ORDER BY l.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(l) for l in logs]

# 初始化数据库
def init_db():
    """初始化数据库"""
    conn = get_db_connection()
    
    # 创建用户表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            role TEXT DEFAULT 'user',
            oauth_provider TEXT,
            oauth_id TEXT,
            avatar_url TEXT,
            permissions TEXT,
            data_scope TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建学校表
    conn.execute('''
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
            district TEXT,
            finance_type TEXT,
            gender TEXT,
            session_type TEXT,
            supervisor TEXT,
            phone TEXT,
            fax TEXT,
            school_type TEXT,
            source TEXT DEFAULT 'manual',
            source_school_id TEXT,
            qs_rank INTEGER,
            usnews_rank INTEGER,
            the_rank INTEGER,
            arwu_rank INTEGER,
            cwur_rank INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建点赞表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            school_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (school_id) REFERENCES schools(id),
            UNIQUE(user_id, school_id)
        )
    ''')
    
    # 创建管理员日志表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

__all__ = [
    # 简繁转换
    'traditional_to_simplified',
    'simplified_to_traditional',
    # 用户
    'get_user_by_username', 'get_user_by_id', 'get_user_by_phone',
    'get_user_by_oauth', 'get_all_users', 'get_users_with_roles',
    'create_user', 'verify_password', 'verify_phone_code',
    'is_admin', 'get_user_role', 'get_user_permissions', 'has_permission',
    'get_all_roles', 'get_all_permissions', 'get_role_permissions_db',
    'update_role_permissions', 'update_user_permissions', 'update_user_role',
    'update_user_avatar', 'delete_user',
    # 学校
    'get_all_schools', 'get_school_by_id', 'get_schools_by_region',
    'get_schools_by_level', 'get_schools_by_region_and_level',
    'get_schools_paginated', 'search_schools', 'get_regions', 'region_stats',
    'get_school_rankings', 'create_school', 'update_school', 'delete_school',
    'get_schools_by_source', 'get_source_stats', 'update_school_source',
    # 点赞
    'like_school', 'unlike_school', 'get_like', 'get_likes_count', 'get_user_liked_schools',
    # 管理员日志
    'log_admin_action', 'get_admin_logs',
    # 数据库
    'get_db_connection', 'init_db',
]
