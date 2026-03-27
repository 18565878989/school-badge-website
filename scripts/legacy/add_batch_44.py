#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加第44批亚洲学校（21所）
ID范围: 11020-11040
"""

import sqlite3

# 数据库路径
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

# 第44批学校数据
schools_batch_44 = [
    # 东南亚
    {"name": "University of Indonesia", "name_cn": "印度尼西亚大学", "country": "Indonesia", "city": "Jakarta", "region": "Asia", "level": "university", "founded": 1849, "website": "www.ui.ac.id"},
    {"name": "Gadjah Mada University", "name_cn": "加查马达大学", "country": "Indonesia", "city": "Yogyakarta", "region": "Asia", "level": "university", "founded": 1949, "website": "www.ugm.ac.id"},
    {"name": "Bogor Agricultural University", "name_cn": "茂物农业大学", "country": "Indonesia", "city": "Bogor", "region": "Asia", "level": "university", "founded": 1963, "website": "www.ipb.ac.id"},
    
    # 南亚
    {"name": "University of Colombo", "name_cn": "科伦坡大学", "country": "Sri Lanka", "city": "Colombo", "region": "Asia", "level": "university", "founded": 1942, "website": "www.cmb.ac.lk"},
    {"name": "University of Peradeniya", "name_cn": "佩拉德尼亚大学", "country": "Sri Lanka", "city": "Peradeniya", "region": "Asia", "level": "university", "founded": 1942, "website": "www.pdn.ac.lk"},
    {"name": "Tribhuvan University", "name_cn": "特里布文大学", "country": "Nepal", "city": "Kirtipur", "region": "Asia", "level": "university", "founded": 1959, "website": "www.tu.edu.np"},
    {"name": "Kathmandu University", "name_cn": "加德满都大学", "country": "Nepal", "city": "Dhulikhel", "region": "Asia", "level": "university", "founded": 1991, "website": "www.ku.edu.np"},
    {"name": "University of Punjab", "name_cn": "旁遮普大学", "country": "Pakistan", "city": "Lahore", "region": "Asia", "level": "university", "founded": 1882, "website": "www.pu.edu.pk"},
    {"name": "Pakistan Institute of Engineering and Applied Sciences", "name_cn": "巴基斯坦工程技术学院", "country": "Pakistan", "city": "Islamabad", "region": "Asia", "level": "university", "founded": 1967, "website": "www.pieas.edu.pk"},
    
    # 中亚
    {"name": "Al-Farabi Kazakh National University", "name_cn": "阿里-法拉比哈萨克斯坦国立大学", "country": "Kazakhstan", "city": "Almaty", "region": "Asia", "level": "university", "founded": 1934, "website": "www.kaznu.kz"},
    {"name": "Kazakh National Technical University", "name_cn": "哈萨克斯坦国立技术大学", "country": "Kazakhstan", "city": "Almaty", "region": "Asia", "level": "university", "founded": 1932, "website": "www.enu.kz"},
    {"name": "Kyrgyz National University", "name_cn": "吉尔吉斯斯坦国立大学", "country": "Kyrgyzstan", "city": "Bishkek", "region": "Asia", "level": "university", "founded": 1951, "website": "www.knu.kg"},
    {"name": "Tajik National University", "name_cn": "塔吉克斯坦国立大学", "country": "Tajikistan", "city": "Dushanbe", "region": "Asia", "level": "university", "founded": 1948, "website": "www.tnu.tj"},
    {"name": "Turkmen State University", "name_cn": "土库曼斯坦国立大学", "country": "Turkmenistan", "city": "Ashgabat", "region": "Asia", "level": "university", "founded": 1991, "website": "www.tsu.edu.tm"},
    {"name": "National University of Uzbekistan", "name_cn": "乌兹别克斯坦国立大学", "country": "Uzbekistan", "city": "Tashkent", "region": "Asia", "level": "university", "founded": 1918, "website": "www.nuu.uz"},
    
    # 高加索
    {"name": "Tbilisi State University", "name_cn": "第比利斯国立大学", "country": "Georgia", "city": "Tbilisi", "region": "Asia", "level": "university", "founded": 1918, "website": "www.tsu.edu.ge"},
    {"name": "Yerevan State University", "name_cn": "埃里温国立大学", "country": "Armenia", "city": "Yerevan", "region": "Asia", "level": "university", "founded": 1919, "website": "www.ysu.am"},
    {"name": "Baku State University", "name_cn": "巴库国立大学", "country": "Azerbaijan", "city": "Baku", "region": "Asia", "level": "university", "founded": 1919, "website": "www.bsu.edu.az"},
    
    # 中东
    {"name": "University of Tehran", "name_cn": "德黑兰大学", "country": "Iran", "city": "Tehran", "region": "Asia", "level": "university", "founded": 1934, "website": "www.ut.ac.ir"},
    {"name": "American University of Beirut", "name_cn": "贝鲁特美国大学", "country": "Lebanon", "city": "Beirut", "region": "Asia", "level": "university", "founded": 1866, "website": "www.aub.edu.lb"},
    {"name": "American University of Sharjah", "name_cn": "沙迦美国大学", "country": "UAE", "city": "Sharjah", "region": "Asia", "level": "university", "founded": 1997, "website": "www.aus.edu"},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取当前最大ID
    cursor.execute("SELECT MAX(id) FROM schools")
    max_id = cursor.fetchone()[0] or 0
    
    print(f"当前最大ID: {max_id}")
    print(f"将添加 {len(schools_batch_44)} 所学校")
    print("-" * 60)
    
    added_count = 0
    start_id = max_id + 1
    
    for i, school in enumerate(schools_batch_44):
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
    
    # 验证
    cursor.execute("SELECT COUNT(*) FROM schools WHERE region='Asia'")
    total_asian = cursor.fetchone()[0]
    
    print("-" * 60)
    print(f"✅ 成功添加 {added_count} 所亚洲学校")
    print(f"📊 亚洲学校总数: {total_asian}")
    print(f"📍 ID范围: {start_id} - {start_id + added_count - 1}")
    
    conn.close()

if __name__ == "__main__":
    main()
