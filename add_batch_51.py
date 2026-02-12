#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 51: 添加第51批亚洲学校（21所）
ID范围: 11314-11334
新增国家/地区: 塞浦路斯、巴勒斯坦、叙利亚、也门、阿曼、阿联酋、卡塔尔、巴林
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第51批学校数据 (21所)
schools_batch_51 = [
    # 塞浦路斯大学 (3所)
    (11314, "University of Cyprus", "塞浦路斯大学", "Asia", "Cyprus", "Nicosia", None, "university", None, "https://www.ucy.ac.cy", None, None, None),
    (11315, "Cyprus University of Technology", "塞浦路斯理工大学", "Asia", "Cyprus", "Limassol", None, "university", None, "https://www.cut.ac.cy", None, None, None),
    (11316, "European University Cyprus", "塞浦路斯欧洲大学", "Asia", "Cyprus", "Nicosia", None, "university", None, "https://www.euc.ac.cy", None, None, None),
    
    # 巴勒斯坦大学 (2所)
    (11317, "Birzeit University", "比尔宰特大学", "Asia", "Palestine", "Birzeit", None, "university", None, "https://www.birzeit.edu", None, None, None),
    (11318, "Hebrew University of Jerusalem - Mount Scopus", "耶路撒冷希伯来大学-斯科普斯山校区", "Asia", "Palestine", "Jerusalem", None, "university", None, "https://new.huji.ac.il", None, None, None),
    
    # 叙利亚大学 (2所)
    (11319, "University of Damascus", "大马士革大学", "Asia", "Syria", "Damascus", None, "university", None, "https://www.damascusuniversity.edu.sy", None, None, None),
    (11320, "Aleppo University", "阿勒颇大学", "Asia", "Syria", "Aleppo", None, "university", None, "https://www.alepuniv.edu.sy", None, None, None),
    
    # 也门大学 (2所)
    (11321, "Sana'a University", "萨那大学", "Asia", "Yemen", "Sana'a", None, "university", None, "https://www.sanauniv.edu.ye", None, None, None),
    (11322, "University of Aden", "亚丁大学", "Asia", "Yemen", "Aden", None, "university", None, "https://www.univ-aden.edu.ye", None, None, None),
    
    # 阿曼大学 (2所)
    (11323, "Sultan Qaboos University", "苏丹卡布斯大学", "Asia", "Oman", "Muscat", None, "university", None, "https://www.squ.edu.om", None, None, None),
    (11324, "German University of Technology in Oman", "阿曼德国理工大学", "Asia", "Oman", "Muscat", None, "university", None, "https://www.gutech.edu.om", None, None, None),
    
    # 阿联酋大学 (4所)
    (11325, "United Arab Emirates University", "阿联酋大学", "Asia", "UAE", "Al Ain", None, "university", None, "https://www.uaeu.ac.ae", None, None, None),
    (11326, "Khalifa University", "哈利法大学", "Asia", "UAE", "Abu Dhabi", None, "university", None, "https://www.ku.ac.ae", None, None, None),
    (11327, "American University of Sharjah", "沙迦美国大学", "Asia", "UAE", "Sharjah", None, "university", None, "https://www.aus.edu", None, None, None),
    (11328, "Dubai University", "迪拜大学", "Asia", "UAE", "Dubai", None, "university", None, "https://www.du.ac.ae", None, None, None),
    
    # 卡塔尔大学 (3所)
    (11329, "Qatar University", "卡塔尔大学", "Asia", "Qatar", "Doha", None, "university", None, "https://www.qu.edu.qa", None, None, None),
    (11330, "Hamad Bin Khalifa University", "哈马德本哈里发大学", "Asia", "Qatar", "Doha", None, "university", None, "https://www.hbku.edu.qa", None, None, None),
    (11331, "Georgetown University in Qatar", "乔治城大学卡塔尔分校", "Asia", "Qatar", "Doha", None, "university", None, "https://www.qatar.georgetown.edu", None, None, None),
    
    # 巴林大学 (3所)
    (11332, "University of Bahrain", "巴林大学", "Asia", "Bahrain", "Sakhir", None, "university", None, "https://www.uob.edu.bh", None, None, None),
    (11333, "Bahrain University", "巴林大学", "Asia", "Bahrain", "Sakhir", None, "university", None, "https://www.bu.edu.bh", None, None, None),
    (11334, "Arabian Gulf University", "海湾阿拉伯大学", "Asia", "Bahrain", "Manama", None, "university", None, "https://www.agu.edu.bh", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_51:
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

print(f"\n📊 Batch 51 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
