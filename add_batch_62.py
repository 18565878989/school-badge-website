#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 62: 添加第62批亚洲学校（21所）
ID范围: 11908-11928
新增国家/地区: 阿联酋、朝鲜、文莱、塞浦路斯、澳门、东帝汶、巴勒斯坦
填补缺失ID: 11908, 11909
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第62批学校数据 (21所)
schools_batch_62 = [
    # 填补缺失的ID (2所)
    (11908, "Khalifa University", "哈利法大学", "Asia", "United Arab Emirates", "Abu Dhabi", None, "university", None, "https://www.ku.ac.ae", None, None, None),
    (11909, "Zayed University", "扎耶德大学", "Asia", "United Arab Emirates", "Abu Dhabi", None, "university", None, "https://www.zu.ac.ae", None, None, None),
    
    # 阿联酋大学 (4所)
    (11910, "United Arab Emirates University", "阿联酋大学", "Asia", "United Arab Emirates", "Al Ain", None, "university", None, "https://www.uaeu.ac.ae", None, None, None),
    (11911, "American University in Dubai", "迪拜美国大学", "Asia", "United Arab Emirates", "Dubai", None, "university", None, "https://www.aud.edu", None, None, None),
    (11912, "University of Wollongong in Dubai", "卧龙岗大学迪拜分校", "Asia", "United Arab Emirates", "Dubai", None, "university", None, "https://www.uowdubai.ac.ae", None, None, None),
    (11913, "Abu Dhabi University", "阿布扎比大学", "Asia", "United Arab Emirates", "Abu Dhabi", None, "university", None, "https://www.adu.ac.ae", None, None, None),
    
    # 朝鲜大学 (3所)
    (11914, "Kim Il-sung University", "金日成综合大学", "Asia", "North Korea", "Pyongyang", None, "university", None, "https://www.kyonggi.edu", None, None, None),
    (11915, "Pyongyang University of Science and Technology", "平壤科学技术大学", "Asia", "North Korea", "Pyongyang", None, "university", None, "https://www.put.edu", None, None, None),
    (11916, "Kim Hyong Jik University of Education", "金亨稷师范大学", "Asia", "North Korea", "Pyongyang", None, "university", None, "https://www.khj.ac.kr", None, None, None),
    
    # 文莱大学 (2所)
    (11917, "Universiti Brunei Darussalam", "文莱达鲁萨兰大学", "Asia", "Brunei", "Gadong", None, "university", None, "https://www.ubd.edu.bn", None, None, None),
    (11918, "International Islamic University College", "国际伊斯兰大学学院", "Asia", "Brunei", "Seria", None, "university", None, "https://www.uci.edu.bn", None, None, None),
    
    # 塞浦路斯大学 (3所)
    (11919, "Eastern Mediterranean University", "东地中海大学", "Asia", "Cyprus", "Famagusta", None, "university", None, "https://www.emu.edu.tr", None, None, None),
    (11920, "Near East University", "近东大学", "Asia", "Cyprus", "North Cyprus", None, "university", None, "https://www.neu.edu.tr", None, None, None),
    (11921, "Girne American University", "吉尔内美国大学", "Asia", "Cyprus", "Kyrenia", None, "university", None, "https://www.gau.edu.tr", None, None, None),
    
    # 澳门大学 (3所)
    (11922, "University of Macau", "澳门大学", "Asia", "Macau", "Macau", None, "university", None, "https://www.um.edu.mo", None, None, None),
    (11923, "Macau University of Science and Technology", "澳门科技大学", "Asia", "Macau", "Macau", None, "university", None, "https://www.must.edu.mo", None, None, None),
    (11924, "City University of Macau", "澳门城市大学", "Asia", "Macau", "Macau", None, "university", None, "https://www.cityu.edu.mo", None, None, None),
    
    # 东帝汶大学 (3所)
    (11925, "National University of Timor-Leste", "东帝汶国立大学", "Asia", "Timor-Leste", "Dili", None, "university", None, "https://www.unetl.edu.tl", None, None, None),
    (11926, "East Timor Institute of Accounting and Business", "东帝汶会计商业学院", "Asia", "Timor-Leste", "Dili", None, "university", None, "https://www.iadb.tl", None, None, None),
    (11927, "Dili Institute of Technology", "帝力理工学院", "Asia", "Timor-Leste", "Dili", None, "university", None, "https://www.dit.tl", None, None, None),
    
    # 巴勒斯坦大学 (2所)
    (11928, "Birzeit University", "比尔宰特大学", "Asia", "Palestine", "Birzeit", None, "university", None, "https://www.birzeit.edu", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_62:
    # 检查是否已存在
    cursor.execute('SELECT id FROM schools WHERE id = ?', (school[0],))
    existing = cursor.fetchone()
    
    if existing:
        print(f"⏭ ID {school[0]}: {school[1]} ({school[2]}) - 已存在")
        skipped_count += 1
        continue
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO schools (
                id, name, name_cn, region, country, city, address, level,
                badge_url, website, motto, founded, principal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', school)
        added_count += 1
        print(f"✓ ID {school[0]}: {school[1]} ({school[2]})")
    except Exception as e:
        print(f"✗ 添加失败 ID {school[0]}: {e}")

# 提交事务
conn.commit()

# 统计更新
cursor.execute('SELECT COUNT(*) FROM schools WHERE region = "Asia"')
asia_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM schools')
total_count = cursor.fetchone()[0]
cursor.execute('SELECT MAX(id) FROM schools')
max_id = cursor.fetchone()[0]

print(f"\n🎉 Batch 62 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
