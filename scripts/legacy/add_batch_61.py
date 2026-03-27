#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 61: 添加第61批亚洲学校（21所）
ID范围: 11645-11665
新增国家/地区: 格鲁吉亚、亚美尼亚、阿塞拜疆、伊朗、伊拉克、以色列、约旦、黎巴嫩、巴勒斯坦、塞浦路斯、土耳其、叙利亚、也门、阿曼、巴林、卡塔尔、阿联酋、沙特、科威特
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第61批学校数据 (21所)
schools_batch_61 = [
    # 高加索大学 (3所)
    (11645, "Tbilisi State University", "第比利斯国立大学", "Asia", "Georgia", "Tbilisi", None, "university", None, "https://www.tsu.edu.ge", None, None, None),
    (11646, "Yerevan State University", "埃里温国立大学", "Asia", "Armenia", "Yerevan", None, "university", None, "https://www.ysu.am", None, None, None),
    (11647, "Baku State University", "巴库国立大学", "Asia", "Azerbaijan", "Baku", None, "university", None, "https://www.bsu.edu.az", None, None, None),
    
    # 中东大学 (12所)
    (11648, "University of Tehran", "德黑兰大学", "Asia", "Iran", "Tehran", None, "university", None, "https://www.ut.ac.ir", None, None, None),
    (11649, "Sharif University of Technology", "谢里夫理工大学", "Asia", "Iran", "Tehran", None, "university", None, "https://www.sharif.edu", None, None, None),
    (11650, "Amirkabir University of Technology", "阿米卡布尔理工大学", "Asia", "Iran", "Tehran", None, "university", None, "https://www.aut.ac.ir", None, None, None),
    (11651, "University of Baghdad", "巴格达大学", "Asia", "Iraq", "Baghdad", None, "university", None, "https://www.uobaghdad.edu.iq", None, None, None),
    (11652, "Hebrew University of Jerusalem", "希伯来大学", "Asia", "Israel", "Jerusalem", None, "university", None, "https://new.huji.ac.il", None, None, None),
    (11653, "Tel Aviv University", "特拉维夫大学", "Asia", "Israel", "Tel Aviv", None, "university", None, "https://www.tau.ac.il", None, None, None),
    (11654, "Technion Israel Institute of Technology", "以色列理工学院", "Asia", "Israel", "Haifa", None, "university", None, "https://www.technion.ac.il", None, None, None),
    (11655, "University of Jordan", "约旦大学", "Asia", "Jordan", "Amman", None, "university", None, "https://www.ju.edu.jo", None, None, None),
    (11656, "American University of Beirut", "贝鲁特美国大学", "Asia", "Lebanon", "Beirut", None, "university", None, "https://www.aub.edu.lb", None, None, None),
    (11657, "Lebanese American University", "黎巴嫩美国大学", "Asia", "Lebanon", "Byblos", None, "university", None, "https://www.lau.edu.lb", None, None, None),
    (11658, "University of Cyprus", "塞浦路斯大学", "Asia", "Cyprus", "Nicosia", None, "university", None, "https://www.ucy.ac.cy", None, None, None),
    (11659, "Cyprus International University", "塞浦路斯国际大学", "Asia", "Cyprus", "Nicosia", None, "university", None, "https://www.ciu.edu.tr", None, None, None),
    
    # 土耳其大学 (6所)
    (11660, "Bogazici University", "博斯菲亚大学", "Asia", "Turkey", "Istanbul", None, "university", None, "https://www.boun.edu.tr", None, None, None),
    (11661, "Istanbul Technical University", "伊斯坦布尔理工大学", "Asia", "Turkey", "Istanbul", None, "university", None, "https://www.itu.edu.tr", None, None, None),
    (11662, "Middle East Technical University", "中东技术大学", "Asia", "Turkey", "Ankara", None, "university", None, "https://www.metu.edu.tr", None, None, None),
    (11663, "Ankara University", "安卡拉大学", "Asia", "Turkey", "Ankara", None, "university", None, "https://www.ankara.edu.tr", None, None, None),
    (11664, "Ege University", "爱琴大学", "Asia", "Turkey", "Izmir", None, "university", None, "https://www.ege.edu.tr", None, None, None),
    (11665, "Hacettepe University", "哈塞特佩大学", "Asia", "Turkey", "Ankara", None, "university", None, "https://www.hacettepe.edu.tr", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_61:
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

print(f"\n🎉 Batch 61 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
