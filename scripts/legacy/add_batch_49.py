#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加第49批亚洲学校（21所）
ID范围: 11272-11292
"""

import sqlite3

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

schools_batch_49 = [
    # 东亚 (5)
    {"name": "Zhejiang University", "name_cn": "浙江大学", "country": "China", "city": "Hangzhou", "region": "Asia", "level": "university", "founded": 1897, "website": "www.zju.edu.cn"},
    {"name": "Shanghai Jiao Tong University", "name_cn": "上海交通大学", "country": "China", "city": "Shanghai", "region": "Asia", "level": "university", "founded": 1896, "website": "www.sjtu.edu.cn"},
    {"name": "Nanjing University", "name_cn": "南京大学", "country": "China", "city": "Nanjing", "region": "Asia", "level": "university", "founded": 1902, "website": "www.nju.edu.cn"},
    {"name": "Wuhan University", "name_cn": "武汉大学", "country": "China", "city": "Wuhan", "region": "Asia", "level": "university", "founded": 1893, "website": "www.whu.edu.cn"},
    {"name": "Sun Yat-sen University", "name_cn": "中山大学", "country": "China", "city": "Guangzhou", "region": "Asia", "level": "university", "founded": 1924, "website": "www.sysu.edu.cn"},
    
    # 东南亚 (6)
    {"name": "University of Santo Tomas", "name_cn": "圣托马斯大学", "country": "Philippines", "city": "Manila", "region": "Asia", "level": "university", "founded": 1611, "website": "www.ust.edu.ph"},
    {"name": "Miriam College Foundation", "name_cn": "米里亚姆学院", "country": "Philippines", "city": "Quezon City", "region": "Asia", "level": "university", "founded": 1926, "website": "www.miriamcollege.edu"},
    {"name": "Ateneo de Naga University", "name_cn": "那牙雅典耀大学", "country": "Philippines", "city": "Naga City", "region": "Asia", "level": "university", "founded": 1935, "website": "www.ateneo.edu"},
    {"name": "Xavier University - Ateneo de Cagayan", "name_cn": "卡加延雅典耀大学", "country": "Philippines", "city": "Cagayan de Oro", "region": "Asia", "level": "university", "founded": 1933, "website": "www.xu.edu.ph"},
    {"name": "San Beda University", "name_cn": "圣贝达大学", "country": "Philippines", "city": "Manila", "region": "Asia", "level": "university", "founded": 1899, "website": "www.sanbeda.edu.ph"},
    {"name": "University of Asia Pacific", "name_cn": "亚洲太平洋大学", "country": "Philippines", "city": "Manila", "region": "Asia", "level": "university", "founded": 1995, "website": "www.uap.edu.ph"},
    
    # 南亚 (5)
    {"name": "Osmania University", "name_cn": "奥斯曼尼亚大学", "country": "India", "city": "Hyderabad", "region": "Asia", "level": "university", "founded": 1918, "website": "www.osmania.ac.in"},
    {"name": "Banaras Hindu University", "name_cn": "贝拿勒斯印度大学", "country": "India", "city": "Varanasi", "region": "Asia", "level": "university", "founded": 1916, "website": "www.bhu.ac.in"},
    {"name": "Jamia Millia Islamia", "name_cn": "伊斯兰大学", "country": "India", "city": "New Delhi", "region": "Asia", "level": "university", "founded": 1920, "website": "www.jmi.ac.in"},
    {"name": "Aligarh Muslim University", "name_cn": "阿里格尔穆斯林大学", "country": "India", "city": "Aligarh", "region": "Asia", "level": "university", "founded": 1875, "website": "www.amu.ac.in"},
    {"name": "University of Dhaka", "name_cn": "达卡大学", "country": "Bangladesh", "city": "Dhaka", "region": "Asia", "level": "university", "founded": 1921, "website": "www.du.ac.bd"},
    
    # 中东 (5)
    {"name": "Birla Institute of Technology and Science", "name_cn": "比尔拉科学技术学院", "country": "Oman", "city": "Muscat", "region": "Asia", "level": "university", "founded": 1984, "website": "www.bits.edu.om"},
    {"name": "Sultan Qaboos University", "name_cn": "苏丹卡布斯大学", "country": "Oman", "city": "Muscat", "region": "Asia", "level": "university", "founded": 1986, "website": "www.squ.edu.om"},
    {"name": "American University of Oman", "name_cn": "阿曼美国大学", "country": "Oman", "city": "Muscat", "region": "Asia", "level": "university", "founded": 2013, "website": "www.auoman.edu.om"},
    {"name": "University of Bahrain", "name_cn": "巴林大学", "country": "Bahrain", "city": "Sakhir", "region": "Asia", "level": "university", "founded": 1986, "website": "www.uob.edu.bh"},
    {"name": "Arabian Gulf University", "name_cn": "阿拉伯湾大学", "country": "Bahrain", "city": "Manama", "region": "Asia", "level": "university", "founded": 1980, "website": "www.agu.edu.bh"},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) FROM schools")
    max_id = cursor.fetchone()[0] or 0
    
    print(f"当前最大ID: {max_id}")
    print(f"将添加 {len(schools_batch_49)} 所学校")
    print("-" * 60)
    
    added_count = 0
    start_id = max_id + 1
    
    for i, school in enumerate(schools_batch_49):
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
