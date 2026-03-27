#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 98: 添加第98批亚洲学校（21所）
ID范围: 13257-13277
新增国家/地区: 阿塞拜疆、阿曼、阿联酋、沙特阿拉伯、卡塔尔、科威特、巴林、也门
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第98批学校数据 (21所)
schools_batch_98 = [
    # 阿塞拜疆大学 (2所)
    (13257, "Baku State University", "巴库国立大学", "Asia", "Azerbaijan", "Baku", None, "university", None, "https://bsu.edu.az", None, None, None),
    (13258, "Azerbaijan Technical University", "阿塞拜疆理工大学", "Asia", "Azerbaijan", "Baku", None, "university", None, "https://www.atu.edu.az", None, None, None),
    
    # 阿曼大学 (2所)
    (13259, "Sultan Qaboos University", "苏丹卡布斯大学", "Asia", "Oman", "Muscat", None, "university", None, "https://www.squ.edu.om", None, None, None),
    (13260, "Al Baha University", "阿尔巴哈大学", "Asia", "Oman", "Al Baha", None, "university", None, "https://www.bu.edu.sa", None, None, None),
    
    # 阿联酋大学 (3所)
    (13261, "Khalifa University", "哈利法大学", "Asia", "UAE", "Abu Dhabi", None, "university", None, "https://www.ku.ac.ae", None, None, None),
    (13262, "United Arab Emirates University", "阿联酋大学", "Asia", "UAE", "Al Ain", None, "university", None, "https://www.uaeu.ac.ae", None, None, None),
    (13263, "American University of Sharjah", "沙迦美国大学", "Asia", "UAE", "Sharjah", None, "university", None, "https://www.aus.edu", None, None, None),
    
    # 沙特阿拉伯大学 (3所)
    (13264, "King Fahd University of Petroleum and Minerals", "法赫德国王石油矿产大学", "Asia", "Saudi Arabia", "Dhahran", None, "university", None, "https://www.kfupm.edu.sa", None, None, None),
    (13265, "King Abdulaziz University", "阿卜杜勒阿齐兹国王大学", "Asia", "Saudi Arabia", "Jeddah", None, "university", None, "https://www.kau.edu.sa", None, None, None),
    (13266, "King Abdullah University of Science and Technology", "阿卜杜拉国王科技大学", "Asia", "Saudi Arabia", "Thuwal", None, "university", None, "https://www.kaust.edu.sa", None, None, None),
    
    # 卡塔尔大学 (2所)
    (13267, "Qatar University", "卡塔尔大学", "Asia", "Qatar", "Doha", None, "university", None, "https://www.qu.edu.qa", None, None, None),
    (13268, "Hamad Bin Khalifa University", "哈马德本哈利法大学", "Asia", "Qatar", "Doha", None, "university", None, "https://www.hbku.edu.qa", None, None, None),
    
    # 科威特大学 (2所)
    (13269, "Kuwait University", "科威特大学", "Asia", "Kuwait", "Kuwait City", None, "university", None, "https://www.ku.edu.kw", None, None, None),
    (13270, "American University of Kuwait", "科威特美国大学", "Asia", "Kuwait", "Kuwait City", None, "university", None, "https://www.auk.edu.kw", None, None, None),
    
    # 巴林大学 (2所)
    (13271, "University of Bahrain", "巴林大学", "Asia", "Bahrain", "Sakhir", None, "university", None, "https://www.uob.edu.bh", None, None, None),
    (13272, "Bahrain University", "巴林大学", "Asia", "Bahrain", "Manama", None, "university", None, "https://www.universityofbahrain.edu.bh", None, None, None),
    
    # 也门大学 (2所)
    (13273, "Sana'a University", "萨那大学", "Asia", "Yemen", "Sana'a", None, "university", None, "https://www.su.edu.ye", None, None, None),
    (13274, "Yemen University", "也门大学", "Asia", "Yemen", "Aden", None, "university", None, "https://www.yemenuniv.edu.ye", None, None, None),
    
    # 蒙古大学 (2所)
    (13275, "Mongolian University of Science and Technology", "蒙古科技大学", "Asia", "Mongolia", "Ulaanbaatar", None, "university", None, "https://www.must.edu.mn", None, None, None),
    (13276, "Health Sciences University of Mongolia", "蒙古健康科学大学", "Asia", "Mongolia", "Ulaanbaatar", None, "university", None, "https://www.hsum.edu.mn", None, None, None),
    
    # 柬埔寨大学 (1所)
    (13277, "Royal University of Cambodia", "柬埔寨皇家大学", "Asia", "Cambodia", "Phnom Penh", None, "university", None, "https://www.ruc.edu.kh", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_98:
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

print(f"\n🎉 Batch 98 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
