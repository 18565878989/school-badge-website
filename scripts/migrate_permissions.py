#!/usr/bin/env python3
"""
权限管理数据库迁移
功能权限 + 数据权限
"""

import sqlite3
import json

def migrate_permissions():
    """执行权限迁移"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("权限管理数据库迁移")
    print("=" * 60)
    
    # 1. 检查是否已有 permission 字段
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # 2. 添加权限相关字段
    new_fields = [
        ('role', "TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user', 'editor', 'viewer'))", None),
        ('permissions', 'TEXT', '{"view_schools": true, "like_schools": true, "edit_all": false, "delete_all": false, "manage_users": false, "view_logs": false, "export_data": false}'),
        ('data_scope', 'TEXT', '["all"]'),
        ('max_schools', 'INTEGER', '0'),
        ('status', 'TEXT', 'active'),
        ('last_login', 'DATETIME', None),
        ('login_count', 'INTEGER DEFAULT 0', None),
    ]
    
    for field_name, field_type, default in new_fields:
        if field_name not in columns:
            print(f"\n添加 {field_name} 字段...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}")
            if default and default.startswith('{'):
                cursor.execute(f"UPDATE users SET {field_name} = ? WHERE {field_name} IS NULL", (default,))
            print(f"  OK {field_name}")
        else:
            print(f"\n{field_name} 字段已存在")
    
    conn.commit()
    
    # 3. 创建权限定义表
    print("\n创建权限定义表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permission_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # 4. 创建角色权限表
    print("创建角色权限表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            permission_code TEXT NOT NULL,
            granted INTEGER DEFAULT 1,
            FOREIGN KEY (permission_code) REFERENCES permission_definitions(code),
            UNIQUE(role, permission_code)
        )
    ''')
    
    conn.commit()
    
    # 5. 插入默认权限定义
    permissions = [
        ('view_schools', '查看学校', '可以查看学校列表和详情', 'schools'),
        ('view_own_likes', '查看已收藏', '可以查看自己收藏的学校', 'schools'),
        ('like_schools', '收藏学校', '可以收藏/取消收藏学校', 'schools'),
        ('edit_all_schools', '编辑所有学校', '可以编辑所有学校', 'schools'),
        ('delete_all_schools', '删除所有学校', '可以删除所有学校', 'schools'),
        ('add_schools', '添加学校', '可以添加新学校', 'schools'),
        ('view_users', '查看用户', '可以查看用户列表', 'users'),
        ('edit_users', '编辑用户', '可以编辑用户信息', 'users'),
        ('manage_users', '管理用户', '可以管理用户权限', 'users'),
        ('delete_users', '删除用户', '可以删除用户', 'users'),
        ('view_logs', '查看日志', '可以查看操作日志', 'system'),
        ('export_data', '导出数据', '可以导出数据', 'system'),
        ('manage_roles', '管理角色', '可以管理角色和权限', 'system'),
        ('view_stats', '查看统计', '可以查看统计数据', 'system'),
    ]
    
    print("插入权限定义...")
    for code, name, desc, category in permissions:
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO permission_definitions (code, name, description, category) VALUES (?, ?, ?, ?)',
                (code, name, desc, category)
            )
        except:
            pass
    
    # 6. 设置默认角色权限
    role_permissions = {
        'admin': ['view_schools', 'view_own_likes', 'like_schools', 'edit_all_schools', 
                  'delete_all_schools', 'add_schools', 'view_users', 'edit_users',
                  'manage_users', 'delete_users', 'view_logs', 'export_data', 
                  'manage_roles', 'view_stats'],
        'editor': ['view_schools', 'view_own_likes', 'like_schools', 'edit_all_schools', 
                   'add_schools', 'view_users', 'view_logs', 'view_stats'],
        'user': ['view_schools', 'view_own_likes', 'like_schools'],
        'viewer': ['view_schools'],
    }
    
    print("设置角色权限...")
    for role, perms in role_permissions.items():
        for perm in perms:
            try:
                cursor.execute(
                    'INSERT OR IGNORE INTO role_permissions (role, permission_code, granted) VALUES (?, ?, 1)',
                    (role, perm)
                )
            except:
                pass
    
    conn.commit()
    
    # 7. 更新现有用户权限
    print("\n更新现有用户权限...")
    admin_perms = {"view_schools": True, "like_schools": True, "view_own_likes": True, 
                   "edit_all_schools": True, "delete_all_schools": True, "add_schools": True,
                   "view_users": True, "edit_users": True, "manage_users": True, "delete_users": True,
                   "view_logs": True, "export_data": True, "manage_roles": True, "view_stats": True}
    cursor.execute("UPDATE users SET role = 'admin', permissions = ?, data_scope = '[\"all\"]' WHERE role = 'admin'", (json.dumps(admin_perms),))
    
    user_perms = {"view_schools": True, "like_schools": True, "view_own_likes": True}
    cursor.execute("UPDATE users SET role = 'user', permissions = ?, data_scope = '[\"own\"]' WHERE role = 'user'", (json.dumps(user_perms),))
    
    conn.commit()
    
    # 8. 统计
    print("\n" + "=" * 60)
    print("迁移完成!")
    print("=" * 60)
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM permission_definitions")
    perm_count = cursor.fetchone()[0]
    
    print(f"\n用户总数: {user_count}")
    print(f"权限定义: {perm_count}")
    
    print("\n按角色统计:")
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    for role, count in cursor.fetchall():
        print(f"  {role}: {count}人")
    
    conn.close()

if __name__ == '__main__':
    migrate_permissions()
