#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加第47批亚洲学校（21所）
ID范围: 11230-11250
"""

import sqlite3

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

schools_batch_47 = [
    # 东南亚 (6)
    {"name": "Kasetsart University", "name_cn": "农业大学", "country": "Thailand", "city": "Bangkok", "region": "Asia", "level": "university", "founded": 1943, "website": "www.ku.ac.th"},
    {"name": "Chiang Mai University", "name_cn": "清迈大学", "country": "Thailand", "city": "Chiang Mai", "region": "Asia", "level": "university", "founded": 1964, "website": "www.cmu.ac.th"},
    {"name": "Thammasat University", "name_cn": "法政大学", "country": "Thailand", "city": "Bangkok", "region": "Asia", "level": "university", "founded": 1934, "website": "www.tu.ac.th"},
    {"name": "Hanoi National University", "name_cn": "河内国家大学", "country": "Vietnam", "city": "Hanoi", "region": "Asia", "level": "university", "founded": 1906, "website": "www.hnue.edu.vn"},
    {"name": "Ho Chi Minh City National University", "name_cn": "胡志明市国家大学", "country": "Vietnam", "city": "Ho Chi Minh City", "region": "Asia", "level": "university", "founded": 1955, "website": "www.hcmunre.edu.vn"},
    {"name": "National University of Singapore", "name_cn": "新加坡国立大学", "country": "Singapore", "city": "Singapore", "region": "Asia", "level": "university", "founded": 1905, "website": "www.nus.edu.sg"},
    
    # 南亚 (5)
    {"name": "Indian Institute of Technology Bombay", "name_cn": "印度理工学院孟买分校", "country": "India", "city": "Mumbai", "region": "Asia", "level": "university", "founded": 1958, "website": "www.iitb.ac.in"},
    {"name": "Indian Institute of Technology Delhi", "name_cn": "印度理工学院德里分校", "country": "India", "city": "New Delhi", "region": "Asia", "level": "university", "founded": 1961, "website": "www.iitd.ac.in"},
    {"name": "University of Madras", "name_cn": "马德拉斯大学", "country": "India", "city": "Chennai", "region": "Asia", "level": "university", "founded": 1857, "website": "www.unom.ac.in"},
    {"name": "University of Calcutta", "name_cn": "加尔各答大学", "country": "India", "city": "Kolkata", "region": "Asia", "level": "university", "founded": 1857, "website": "www.caluniv.ac.in"},
    {"name": "Punjab University", "name_cn": "旁遮普大学（印度）", "country": "India", "city": "Chandigarh", "region": "Asia", "level": "university", "founded": 1882, "website": "www.puchd.ac.in"},
    
    # 中东 (5)
    {"name": "American University of Cairo", "name_cn": "开罗美国大学", "country": "Egypt", "city": "Cairo", "region": "Asia", "level": "university", "founded": 1919, "website": "www.aucegypt.edu"},
    {"name": "Cairo University", "name_cn": "开罗大学", "country": "Egypt", "city": "Cairo", "region": "Asia", "level": "university", "founded": 1908, "website": "www.cu.edu.eg"},
    {"name": "King Abdulaziz University", "name_cn": "阿卜杜勒阿齐兹国王大学", "country": "Saudi Arabia", "city": "Jeddah", "region": "Asia", "level": "university", "founded": 1967, "website": "www.kau.edu.sa"},
    {"name": "Qatar University", "name_cn": "卡塔尔大学", "country": "Qatar", "city": "Doha", "region": "Asia", "level": "university", "founded": 1973, "website": "www.qu.edu.qa"},
    {"name": "United Arab Emirates University", "name_cn": "阿联酋大学", "country": "UAE", "city": "Al Ain", "region": "Asia", "level": "university", "founded": 1976, "website": "www.uaeu.ac.ae"},
    
    # 中亚 (5)
    {"name": "Tashkent State Technical University", "name_cn": "塔什干国立技术大学", "country": "Uzbekistan", "city": "Tashkent", "region": "Asia", "level": "university", "founded": 1954, "website": "www.tstu.uz"},
    {"name": "Tashkent State University of Economics", "name_cn": "塔什干国立经济大学", "country": "Uzbekistan", "city": "Tashkent", "region": "Asia", "level": "university", "founded": 1931, "website": "www.tsue.uz"},
    {"name": "Kazakhstan National University", "name_cn": "哈萨克斯坦国立大学", "country": "Kazakhstan", "city": "Almaty", "region": "Asia", "level": "university", "founded": 1934, "website": "www.kaznu.kz"},
    {"name": "Kazakhstan Academy of Sciences", "name_cn": "哈萨克斯坦科学院", "country": "Kazakhstan", "city": "Almaty", "region": "Asia", "level": "university", "founded": 1946, "website": "www.nasacademy.kz"},
    {"name": "American University of Central Asia", "name_cn": "中亚美国大学", "country": "Kyrgyzstan", "city": "Bishkek", "region": "Asia", "level": "university", "founded": 1997, "website": "www.auca.kg"},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) FROM schools")
    max_id = cursor.fetchone()[0] or 0
    
    print(f"当前最大ID: {max_id}")
    print(f"将添加 {len(schools_batch_47)} 所学校")
    print("-" * 60)
    
    added_count = 0
    start_id = max_id + 1
    
    for i, school in enumerate(schools_batch_47):
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
