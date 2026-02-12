#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加第46批亚洲学校（3所）- 补齐第45批
ID范围: 11227-11229
"""

import sqlite3

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

schools_batch_46 = [
    # 东亚 (3)
    {"name": "Seoul National University", "name_cn": "首尔国立大学", "country": "South Korea", "city": "Seoul", "region": "Asia", "level": "university", "founded": 1946, "website": "www.snu.ac.kr"},
    {"name": "Korea Advanced Institute of Science and Technology", "name_cn": "韩国科学技术院", "country": "South Korea", "city": "Daejeon", "region": "Asia", "level": "university", "founded": 1971, "website": "www.kaist.ac.kr"},
    {"name": "Yonsei University", "name_cn": "延世大学", "country": "South Korea", "city": "Seoul", "region": "Asia", "level": "university", "founded": 1885, "website": "www.yonsei.ac.kr"},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) FROM schools")
    max_id = cursor.fetchone()[0] or 0
    
    print(f"当前最大ID: {max_id}")
    print(f"将添加 {len(schools_batch_46)} 所学校")
    print("-" * 60)
    
    added_count = 0
    start_id = max_id + 1
    
    for i, school in enumerate(schools_batch_46):
        school_id = start_id + i
        school['id'] = school_id
        
        cursor.execute('''
            INSERT INTO schools (
                id, name, name_cn, country, city, region, level,
                founded, website, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (
            school['id'],
            school['name'],
            school['name_cn'],
            school['country'],
            school['city'],
            school['region'],
            school['level'],
            school['founded'],
            school['website']
        ))
        
        added_count += 1
        print(f"[{school['id']}] {school['name_cn']} ({school['name']}) - {school['country']}")
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE region='Asia'")
    total_asian = cursor.fetchone()[0]
    
    print("-" * 60)
    print(f"✅ 成功添加 {added_count} 所亚洲学校")
    print(f"📊 亚洲学校总数: {total_asian}")
    print(f"📍 ID范围: {start_id} - {start_id + added_count - 1}")
    
    conn.close()

if __name__ == "__main__":
    main()
