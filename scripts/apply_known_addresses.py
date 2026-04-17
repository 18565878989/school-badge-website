#!/usr/bin/env python3
"""
应用已知大学地址到数据库
"""
import sqlite3
import json
import sys
from datetime import datetime

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
KNOWN_ADDRESSES_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/data/known_university_addresses.json'

def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def load_known_addresses():
    with open(KNOWN_ADDRESSES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['universities']

def find_matching_schools(university_name, conn):
    """在数据库中查找匹配的学校"""
    # 精确匹配
    school = conn.execute("""
        SELECT id, name, address FROM schools 
        WHERE name = ? AND (address IS NULL OR address = '')
    """, (university_name,)).fetchone()
    
    if school:
        return [school]
    
    # 模糊匹配 - 包含学校名
    name_part = university_name.split()[0]  # 取第一个词
    schools = conn.execute("""
        SELECT id, name, address FROM schools 
        WHERE name LIKE ? AND (address IS NULL OR address = '')
        LIMIT 3
    """, (f'%{name_part}%',)).fetchall()
    
    return schools

def update_school_address(school_id, address, city, country):
    """更新学校地址"""
    conn = get_db_connection()
    conn.execute("""
        UPDATE schools 
        SET address = ?, city = ?, updated_at = ?
        WHERE id = ?
    """, (address, city, datetime.now().isoformat(), school_id))
    conn.commit()
    conn.close()

def main():
    known_addresses = load_known_addresses()
    total = 0
    updated = 0
    
    print(f"加载了 {len(known_addresses)} 个已知地址")
    print("=" * 50)
    
    for name, info in known_addresses.items():
        total += 1
        address = info.get('address', '')
        city = info.get('city', '')
        country = info.get('country', '')
        
        conn = get_db_connection()
        schools = find_matching_schools(name, conn)
        conn.close()
        
        if schools:
            for school_id, school_name, current_addr in schools:
                print(f"[{total}] {school_name[:40]}... ", end="", flush=True)
                if current_addr is None or current_addr == '':
                    update_school_address(school_id, address, city, country)
                    updated += 1
                    print(f"✓ {address[:50]}...")
                else:
                    print("已有地址，跳过")
        else:
            print(f"[{total}] {name}: 未找到匹配学校")
    
    print("=" * 50)
    print(f"完成! 总计: {total}, 更新: {updated}")

if __name__ == '__main__':
    main()
