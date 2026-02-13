#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 64: 添加第64批亚洲学校（21所）
ID范围: 11950-11970
新增国家/地区: 科威特、黎巴嫩、约旦、巴林、卡塔尔、阿曼、也门、叙利亚
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第64批学校数据 (21所)
schools_batch_64 = [
    # 科威特大学 (3所)
    (11950, "Kuwait University", "科威特大学", "Asia", "Kuwait", "Kuwait City", None, "university", None, "https://www.ku.edu.kw", None, None, None),
    (11951, "American University of Kuwait", "科威特美国大学", "Asia", "Kuwait", "Kuwait City", None, "university", None, "https://www.auk.edu.kw", None, None, None),
    (11952, "Gulf University for Science and Technology", "海湾科技大学", "Asia", "Kuwait", "Kuwait City", None, "university", None, "https://www.gust.edu.kw", None, None, None),
    
    # 黎巴嫩大学 (3所)
    (11953, "Saint Joseph University", "圣约瑟夫大学", "Asia", "Lebanon", "Beirut", None, "university", None, "https://www.usj.edu.lb", None, None, None),
    (11954, "Notre Dame University Lebanon", "黎巴嫩圣母大学", "Asia", "Lebanon", "Zouk Mosbeh", None, "university", None, "https://www.ndu.edu.lb", None, None, None),
    (11955, "Holy Spirit University of Kaslik", "卡斯里克神圣精神大学", "Asia", "Lebanon", "Jounieh", None, "university", None, "https://www.usek.edu.lb", None, None, None),
    
    # 约旦大学 (3所)
    (11956, "Jordan University of Science and Technology", "约旦科技大学", "Asia", "Jordan", "Irbid", None, "university", None, "https://www.just.edu.jo", None, None, None),
    (11957, "Hashemite University", "哈希姆大学", "Asia", "Jordan", "Zarqa", None, "university", None, "https://www.hu.edu.jo", None, None, None),
    (11958, "Al-Balqa Applied University", "巴尔卡应用大学", "Asia", "Jordan", "Al-Salt", None, "university", None, "https://www.bau.edu.jo", None, None, None),
    
    # 巴林大学 (3所)
    (11959, "University of Bahrain", "巴林大学", "Asia", "Bahrain", "Sakhir", None, "university", None, "https://www.uob.edu.bh", None, None, None),
    (11960, "Bahrain University", "巴林王国大学", "Asia", "Bahrain", "Sakhir", None, "university", None, "https://www.bah.edu.bh", None, None, None),
    (11961, "Arabian Gulf University", "海湾阿拉伯大学", "Asia", "Bahrain", "Manama", None, "university", None, "https://www.agu.edu.bh", None, None, None),
    
    # 卡塔尔大学 (3所)
    (11962, "Qatar University", "卡塔尔大学", "Asia", "Qatar", "Doha", None, "university", None, "https://www.qu.edu.qa", None, None, None),
    (11963, "Hamad Bin Khalifa University", "哈马德本哈里法大学", "Asia", "Qatar", "Doha", None, "university", None, "https://www.hbku.edu.qa", None, None, None),
    (11964, "Texas A&M University at Qatar", "德州农工大学卡塔尔分校", "Asia", "Qatar", "Doha", None, "university", None, "https://www.qatar.tamu.edu", None, None, None),
    
    # 阿曼大学 (3所)
    (11965, "Sultan Qaboos University", "苏丹卡布斯大学", "Asia", "Oman", "Muscat", None, "university", None, "https://www.squ.edu.om", None, None, None),
    (11966, "Oman College of Management and Technology", "阿曼管理与技术学院", "Asia", "Oman", "Muscat", None, "university", None, "https://www.ocmt.edu.om", None, None, None),
    (11967, "University of Technology and Applied Sciences", "技术与应用科学大学", "Asia", "Oman", "Muscat", None, "university", None, "https://www.utas.edu.om", None, None, None),
    
    # 也门大学 (3所)
    (11968, "Sana'a University", "萨那大学", "Asia", "Yemen", "Sana'a", None, "university", None, "https://www.su.edu.ye", None, None, None),
    (11969, "University of Yemen", "也门大学", "Asia", "Yemen", "Sana'a", None, "university", None, "https://www.uy.edu.ye", None, None, None),
    (11970, "Aden University", "亚丁大学", "Asia", "Yemen", "Aden", None, "university", None, "https://www.aden.edu.ye", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_64:
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

print(f"\n🎉 Batch 64 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
