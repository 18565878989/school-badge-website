#!/usr/bin/env python3
"""
学校表结构增强 - 添加香港教育局网站字段
参考: https://www.edb.gov.hk
"""

import sqlite3

def migrate_schools_schema():
    """增强学校表结构"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("学校表结构增强")
    print("=" * 60)
    
    # 检查现有字段
    cursor.execute("PRAGMA table_info(schools)")
    existing_fields = [col[1] for col in cursor.fetchall()]
    
    print("现有字段:", len(existing_fields))
    
    # 新增字段
    new_fields = [
        ('school_code', 'TEXT', '学校编号'),
        ('district', 'TEXT', '区域'),
        ('finance_type', 'TEXT', '办学类型'),
        ('gender', 'TEXT', '性别'),
        ('session_type', 'TEXT', '授课时间'),
        ('supervisor', 'TEXT', '校监'),
        ('phone', 'TEXT', '电话'),
        ('fax', 'TEXT', '传真'),
        ('school_type', 'TEXT', '学校类别'),
        ('source_school_id', 'TEXT', '源网站ID'),
    ]
    
    added = []
    for field_name, field_type, description in new_fields:
        if field_name not in existing_fields:
            print(f"添加 {field_name}...")
            cursor.execute(f"ALTER TABLE schools ADD COLUMN {field_name} {field_type}")
            added.append(field_name)
            print(f"  OK")
        else:
            print(f"{field_name} 已存在")
    
    conn.commit()
    cursor.execute("PRAGMA table_info(schools)")
    print(f"新字段总数: {len(cursor.fetchall())}")
    conn.close()
    print(f"成功添加 {len(added)} 个新字段")
    return added

if __name__ == '__main__':
    migrate_schools_schema()
