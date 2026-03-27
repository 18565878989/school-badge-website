#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 65: 添加第65批亚洲学校（21所）
ID范围: 11971-11991
新增国家/地区: 沙特阿拉伯、伊拉克、以色列、伊朗、蒙古、老挝、柬埔寨、尼泊尔、斯里兰卡
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第65批学校数据 (21所)
schools_batch_65 = [
    # 沙特阿拉伯大学 (3所)
    (11971, "King Saud University", "沙特国王大学", "Asia", "Saudi Arabia", "Riyadh", None, "university", None, "https://www.ksu.edu.sa", None, None, None),
    (11972, "King Abdullah University of Science and Technology", "阿卜杜拉国王科技大学", "Asia", "Saudi Arabia", "Thuwal", None, "university", None, "https://www.kaust.edu.sa", None, None, None),
    (11973, "Prince Mohammad bin Fahd University", "穆罕默德国王大学", "Asia", "Saudi Arabia", "Khobar", None, "university", None, "https://www.pmu.edu.sa", None, None, None),
    
    # 伊拉克大学 (3所)
    (11974, "University of Technology Iraq", "伊拉克理工大学", "Asia", "Iraq", "Baghdad", None, "university", None, "https://www.uotechnology.edu.iq", None, None, None),
    (11975, "Al-Mustansiriya University", "穆斯坦西里亚大学", "Asia", "Iraq", "Baghdad", None, "university", None, "https://www.uomustansiriyah.edu.iq", None, None, None),
    (11976, "University of Basrah", "巴士拉大学", "Asia", "Iraq", "Basrah", None, "university", None, "https://www.uobasrah.edu.iq", None, None, None),
    
    # 以色列大学 (3所)
    (11977, "Bar-Ilan University", "巴伊兰大学", "Asia", "Israel", "Ramat Gan", None, "university", None, "https://www.biu.ac.il", None, None, None),
    (11978, "Ben-Gurion University of the Negev", "本古里安大学", "Asia", "Israel", "Beersheba", None, "university", None, "https://www.bgu.ac.il", None, None, None),
    (11979, "University of Haifa", "海法大学", "Asia", "Israel", "Haifa", None, "university", None, "https://www.haifa.ac.il", None, None, None),
    
    # 伊朗大学 (3所)
    (11980, "Isfahan University of Technology", "伊斯法罕理工大学", "Asia", "Iran", "Isfahan", None, "university", None, "https://www.iut.ac.ir", None, None, None),
    (11981, "Shahid Beheshti University", "沙希德·贝赫什提大学", "Asia", "Iran", "Tehran", None, "university", None, "https://www.sbu.ac.ir", None, None, None),
    (11982, "Tehran University of Medical Sciences", "德黑兰医科大学", "Asia", "Iran", "Tehran", None, "university", None, "https://www.tums.ac.ir", None, None, None),
    
    # 蒙古大学 (3所)
    (11983, "National University of Mongolia", "蒙古国立大学", "Asia", "Mongolia", "Ulaanbaatar", None, "university", None, "https://www.num.edu.mn", None, None, None),
    (11984, "Mongolian University of Science and Technology", "蒙古科技大学", "Asia", "Mongolia", "Ulaanbaatar", None, "university", None, "https://www.must.edu.mn", None, None, None),
    (11985, "Mongolian State University", "蒙古国立大学", "Asia", "Mongolia", "Ulaanbaatar", None, "university", None, "https://www.msu.edu.mn", None, None, None),
    
    # 老挝大学 (2所)
    (11986, "National University of Laos", "老挝国立大学", "Asia", "Laos", "Vientiane", None, "university", None, "https://www.nuol.edu.la", None, None, None),
    (11987, "Souphanouvong University", "苏发努冯大学", "Asia", "Laos", "Savannakhet", None, "university", None, "https://www.su.edu.la", None, None, None),
    
    # 柬埔寨大学 (2所)
    (11988, "Royal University of Phnom Penh", "金边皇家大学", "Asia", "Cambodia", "Phnom Penh", None, "university", None, "https://www.rupp.edu.kh", None, None, None),
    (11989, "Institute of Technology of Cambodia", "柬埔寨理工学院", "Asia", "Cambodia", "Phnom Penh", None, "university", None, "https://www.itc.edu.kh", None, None, None),
    
    # 尼泊尔大学 (1所)
    (11990, "Tribhuvan University " , "特里布文大学", "Asia", "Nepal", "Kirtipur", None, "university", None, "https://www.tribhuvan.edu.np", None, None, None),
    
    # 斯里兰卡大学 (1所)
    (11991, "University of Colombo", "科伦坡大学", "Asia", "Sri Lanka", "Colombo", None, "university", None, "https://www.cmb.ac.lk", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_65:
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

print(f"\n🎉 Batch 65 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
