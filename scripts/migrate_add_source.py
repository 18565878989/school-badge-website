#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加数据来源和更新时间字段
"""

import sqlite3

def migrate_database():
    """执行数据库迁移"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("数据库迁移 - 添加数据来源字段")
    print("=" * 60)
    
    # 1. 检查是否已有source字段
    cursor.execute("PRAGMA table_info(schools)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # 2. 添加source字段
    if 'source' not in columns:
        print("\n添加 source 字段...")
        cursor.execute("ALTER TABLE schools ADD COLUMN source TEXT DEFAULT 'manual'")
        print("  ✓ source 字段已添加")
    else:
        print("\nsource 字段已存在")
    
    # 3. 检查是否已有updated_at字段
    if 'updated_at' not in columns:
        print("添加 updated_at 字段...")
        cursor.execute("ALTER TABLE schools ADD COLUMN updated_at DATETIME")
        print("  ✓ updated_at 字段已添加")
    else:
        print("updated_at 字段已存在")
    
    # 4. 检查是否已有created_at字段
    if 'created_at' not in columns:
        print("添加 created_at 字段...")
        cursor.execute("ALTER TABLE schools ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        print("  ✓ created_at 字段已添加")
    else:
        print("created_at 字段已存在")
    
    conn.commit()
    
    # 5. 更新现有数据的数据来源
    print("\n更新现有数据...")
    cursor.execute("UPDATE schools SET source = 'schooland.hk' WHERE source = 'manual' OR source IS NULL")
    updated = cursor.rowcount
    print(f"  已更新 {updated} 条记录的数据来源为 'schooland.hk'")
    
    # 6. 设置updated_at
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(f"UPDATE schools SET updated_at = '{now}' WHERE updated_at IS NULL")
    print(f"  已设置更新时间")
    
    conn.commit()
    
    # 7. 验证迁移结果
    print("\n验证迁移结果:")
    cursor.execute("SELECT source, COUNT(*) FROM schools GROUP BY source")
    for source, count in cursor.fetchall():
        print(f"  {source}: {count}所")
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE updated_at IS NOT NULL")
    with_time = cursor.fetchone()[0]
    print(f"\n有更新时间的学校: {with_time}所")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("迁移完成!")
    print("=" * 60)

if __name__ == '__main__':
    migrate_database()
