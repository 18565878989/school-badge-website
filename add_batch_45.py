#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加第45批亚洲学校（21所）
ID范围: 11209-11229
"""

import sqlite3

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

schools_batch_45 = [
    # 东南亚 - 印尼 (3)
    {"name": "Bandung Institute of Technology", "name_cn": "万隆理工大学", "country": "Indonesia", "city": "Bandung", "region": "Asia", "level": "university", "founded": 1959, "website": "www.itb.ac.id"},
    {"name": "Surabaya Institute of Technology", "name_cn": "泗水理工大学", "country": "Indonesia", "city": "Surabaya", "region": "Asia", "level": "university", "founded": 1960, "website": "www.its.ac.id"},
    {"name": "Diponegoro University", "name_cn": "迪波内戈罗大学", "country": "Indonesia", "city": "Semarang", "region": "Asia", "level": "university", "founded": 1957, "website": "www.undip.ac.id"},
    
    # 东南亚 - 菲律宾 (3)
    {"name": "University of the Philippines", "name_cn": "菲律宾大学", "country": "Philippines", "city": "Quezon City", "region": "Asia", "level": "university", "founded": 1908, "website": "www.up.edu.ph"},
    {"name": "Ateneo de Manila University", "name_cn": "马尼拉雅典耀大学", "country": "Philippines", "city": "Quezon City", "region": "Asia", "level": "university", "founded": 1859, "website": "www.ateneo.edu"},
    {"name": "De La Salle University", "name_cn": "德拉萨大学", "country": "Philippines", "city": "Manila", "region": "Asia", "level": "university", "founded": 1911, "website": "www.dlsu.edu.ph"},
    
    # 南亚 (5)
    {"name": "Bangladesh University of Engineering and Technology", "name_cn": "孟加拉工程技术大学", "country": "Bangladesh", "city": "Dhaka", "region": "Asia", "level": "university", "founded": 1962, "website": "www.buet.ac.bd"},
    {"name": "Bangladesh Agricultural University", "name_cn": "孟加拉农业大学", "country": "Bangladesh", "city": "Mymensingh", "region": "Asia", "level": "university", "founded": 1961, "website": "www.bau.edu.bd"},
    {"name": "Jawaharlal Nehru University", "name_cn": "贾瓦哈拉尔·尼赫鲁大学", "country": "India", "city": "New Delhi", "region": "Asia", "level": "university", "founded": 1969, "website": "www.jnu.ac.in"},
    {"name": "Delhi University", "name_cn": "德里大学", "country": "India", "city": "New Delhi", "region": "Asia", "level": "university", "founded": 1922, "website": "www.du.ac.in"},
    {"name": "University of Karachi", "name_cn": "卡拉奇大学", "country": "Pakistan", "city": "Karachi", "region": "Asia", "level": "university", "founded": 1951, "website": "www.uok.edu.pk"},
    
    # 东南亚 - 泰国/越南/缅甸 (5)
    {"name": "Chulalongkorn University", "name_cn": "朱拉隆功大学", "country": "Thailand", "city": "Bangkok", "region": "Asia", "level": "university", "founded": 1917, "website": "www.chula.ac.th"},
    {"name": "Mahidol University", "name_cn": "玛希隆大学", "country": "Thailand", "city": "Nakhon Pathom", "region": "Asia", "level": "university", "founded": 1888, "website": "www.mahidol.ac.th"},
    {"name": "Vietnam National University", "name_cn": "越南国立大学", "country": "Vietnam", "city": "Hanoi", "region": "Asia", "level": "university", "founded": 1906, "website": "www.vnu.edu.vn"},
    {"name": "University of Yangon", "name_cn": "仰光大学", "country": "Myanmar", "city": "Yangon", "region": "Asia", "level": "university", "founded": 1920, "website": "www.yu.edu.mm"},
    {"name": "Royal University of Phnom Penh", "name_cn": "金边皇家大学", "country": "Cambodia", "city": "Phnom Penh", "region": "Asia", "level": "university", "founded": 1960, "website": "www.rupp.edu.kh"},
    
    # 中亚/西亚 (2)
    {"name": "King Saud University", "name_cn": "沙特国王大学", "country": "Saudi Arabia", "city": "Riyadh", "region": "Asia", "level": "university", "founded": 1957, "website": "www.ksu.edu.sa"},
    {"name": "Kuwait University", "name_cn": "科威特大学", "country": "Kuwait", "city": "Kuwait City", "region": "Asia", "level": "university", "founded": 1966, "website": "www.ku.edu.kw"},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) FROM schools")
    max_id = cursor.fetchone()[0] or 0
    
    print(f"当前最大ID: {max_id}")
    print(f"将添加 {len(schools_batch_45)} 所学校")
    print("-" * 60)
    
    added_count = 0
    start_id = max_id + 1
    
    for i, school in enumerate(schools_batch_45):
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
