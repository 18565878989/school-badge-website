#!/usr/bin/env python3
"""
学校数据完整性检查工具
检查重复数据、缺失字段等问题
"""

import sqlite3

def check_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("🛡️ 学校数据库完整性检查")
    print("=" * 70)
    
    # 1. 基本统计
    cursor.execute("SELECT COUNT(*) FROM schools")
    total = cursor.fetchone()[0]
    print(f"\n📊 基本统计:")
    print(f"   总学校数: {total}")
    
    # 2. 检查唯一性约束
    print(f"\n🔍 唯一性检查:")
    cursor.execute("SELECT COUNT(DISTINCT name || '|' || country || '|' || COALESCE(name_cn, '')) FROM schools")
    unique_count = cursor.fetchone()[0]
    if unique_count == total:
        print(f"   ✅ 所有记录唯一: {total}/{total}")
    else:
        duplicate_count = total - unique_count
        print(f"   ⚠️ 发现重复: {duplicate_count} 条重复数据")
        
        # 显示重复项
        cursor.execute('''
            SELECT name, name_cn, country, COUNT(*) as cnt 
            FROM schools 
            GROUP BY name, country, COALESCE(name_cn, '')
            HAVING COUNT(*) > 1
            ORDER BY cnt DESC
            LIMIT 10
        ''')
        print("\n   重复数据示例:")
        for row in cursor.fetchall():
            print(f"      - {row[0]} ({row[1] or 'N/A'}) - {row[2]}: {row[3]}条")
    
    # 3. 检查缺失字段
    print(f"\n📋 字段完整性:")
    fields = ['name_cn', 'badge_url', 'website', 'motto', 'description', 'city', 'address']
    for field in fields:
        cursor.execute(f"SELECT COUNT(*) FROM schools WHERE {field} IS NULL OR {field} = ''")
        null_count = cursor.fetchone()[0]
        filled = total - null_count
        pct = (filled / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"   {field:15s}: [{bar}] {filled}/{total} ({pct:.1f}%)")
    
    # 4. 检查索引
    print(f"\n📑 索引状态:")
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='schools'")
    indexes = cursor.fetchall()
    for name, sql in indexes:
        status = "✅" if sql else "❌"
        print(f"   {status} {name}")
    
    # 5. 建议
    print(f"\n💡 建议:")
    if unique_count < total:
        print("   ⚠️  需要清理重复数据")
    if null_count > total * 0.5:
        print("   💡 建议补充中文名称和校徽URL")
    
    conn.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_database()
