#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加第48批亚洲学校（21所）
ID范围: 11251-11271
"""

import sqlite3

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

schools_batch_48 = [
    # 东亚 (6)
    {"name": "Korea University", "name_cn": "高丽大学", "country": "South Korea", "city": "Seoul", "region": "Asia", "level": "university", "founded": 1905, "website": "www.korea.ac.kr"},
    {"name": "Sungkyunkwan University", "name_cn": "成均馆大学", "country": "South Korea", "city": "Suwon", "region": "Asia", "level": "university", "founded": 1398, "website": "www.skku.edu"},
    {"name": "Pohang University of Science and Technology", "name_cn": "浦项工科大学", "country": "South Korea", "city": "Pohang", "region": "Asia", "level": "university", "founded": 1986, "website": "www.postech.ac.kr"},
    {"name": "Tsinghua University", "name_cn": "清华大学", "country": "China", "city": "Beijing", "region": "Asia", "level": "university", "founded": 1911, "website": "www.tsinghua.edu.cn"},
    {"name": "Peking University", "name_cn": "北京大学", "country": "China", "city": "Beijing", "region": "Asia", "level": "university", "founded": 1898, "website": "www.pku.edu.cn"},
    {"name": "Fudan University", "name_cn": "复旦大学", "country": "China", "city": "Shanghai", "region": "Asia", "level": "university", "founded": 1905, "website": "www.fudan.edu.cn"},
    
    # 东南亚 (6)
    {"name": "Nanyang Technological University", "name_cn": "南洋理工大学", "country": "Singapore", "city": "Singapore", "region": "Asia", "level": "university", "founded": 1981, "website": "www.ntu.edu.sg"},
    {"name": "Singapore Management University", "name_cn": "新加坡管理大学", "country": "Singapore", "city": "Singapore", "region": "Asia", "level": "university", "founded": 2000, "website": "www.smu.edu.sg"},
    {"name": "University of Malaya", "name_cn": "马来亚大学", "country": "Malaysia", "city": "Kuala Lumpur", "region": "Asia", "level": "university", "founded": 1949, "website": "www.um.edu.my"},
    {"name": "National University of Malaysia", "name_cn": "马来西亚国立大学", "country": "Malaysia", "city": "Bangi", "region": "Asia", "level": "university", "founded": 1970, "website": "www.ukm.my"},
    {"name": "University of Science Malaysia", "name_cn": "马来西亚理科大学", "country": "Malaysia", "city": "Gelugor", "region": "Asia", "level": "university", "founded": 1969, "website": "www.usm.my"},
    {"name": "Technology University of Malaysia", "name_cn": "马来西亚工艺大学", "country": "Malaysia", "city": "Shah Alam", "region": "Asia", "level": "university", "founded": 1972, "website": "www.utem.edu.my"},
    
    # 南亚 (5)
    {"name": "Indian Institute of Technology Madras", "name_cn": "印度理工学院马德拉斯分校", "country": "India", "city": "Chennai", "region": "Asia", "level": "university", "founded": 1959, "website": "www.iitm.ac.in"},
    {"name": "Indian Institute of Technology Kanpur", "name_cn": "印度理工学院坎普尔分校", "country": "India", "city": "Kanpur", "region": "Asia", "level": "university", "founded": 1959, "website": "www.iitk.ac.in"},
    {"name": "University of Mumbai", "name_cn": "孟买大学", "country": "India", "city": "Mumbai", "region": "Asia", "level": "university", "founded": 1857, "website": "www.mu.ac.in"},
    {"name": "University of Colombo", "name_cn": "科伦坡大学（斯里兰卡）", "country": "Sri Lanka", "city": "Colombo", "region": "Asia", "level": "university", "founded": 1942, "website": "www.cmb.ac.lk"},
    {"name": "University of Peradeniya", "name_cn": "佩拉德尼亚大学（斯里兰卡）", "country": "Sri Lanka", "city": "Peradeniya", "region": "Asia", "level": "university", "founded": 1942, "website": "www.pdn.ac.lk"},
    
    # 中东 (4)
    {"name": "American University of Dubai", "name_cn": "迪拜美国大学", "country": "UAE", "city": "Dubai", "region": "Asia", "level": "university", "founded": 1995, "website": "www.aud.edu"},
    {"name": "Zayed University", "name_cn": "扎耶德大学", "country": "UAE", "city": "Abu Dhabi", "region": "Asia", "level": "university", "founded": 1998, "website": "www.zu.ac.ae"},
    {"name": "King Fahd University of Petroleum and Minerals", "name_cn": "法赫德国王石油矿产大学", "country": "Saudi Arabia", "city": "Dhahran", "region": "Asia", "level": "university", "founded": 1963, "website": "www.kfupm.edu.sa"},
    {"name": "Princess Nourah Bint Abdulrahman University", "name_cn": "诺拉公主大学", "country": "Saudi Arabia", "city": "Riyadh", "region": "Asia", "level": "university", "founded": 1970, "website": "www.pnu.edu.sa"},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) FROM schools")
    max_id = cursor.fetchone()[0] or 0
    
    print(f"当前最大ID: {max_id}")
    print(f"将添加 {len(schools_batch_48)} 所学校")
    print("-" * 60)
    
    added_count = 0
    start_id = max_id + 1
    
    for i, school in enumerate(schools_batch_48):
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
