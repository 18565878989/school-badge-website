#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 50: 添加第50批亚洲学校（21所）
ID范围: 11293-11313
新增国家/地区: 土耳其、伊朗、伊拉克、以色列、约旦、黎巴嫩、塞浦路斯、巴勒斯坦
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第50批学校数据 (21所)
schools_batch_50 = [
    # 土耳其大学 (6所)
    (11293, "Istanbul Technical University", "伊斯坦布尔技术大学", "Asia", "Turkey", "Istanbul", None, "university", None, "https://www.itu.edu.tr", None, None, None),
    (11294, "Middle East Technical University", "中东技术大学", "Asia", "Turkey", "Ankara", None, "university", None, "https://www.metu.edu.tr", None, None, None),
    (11295, "Bogazici University", "博斯菲亚大学", "Asia", "Turkey", "Istanbul", None, "university", None, "https://www.boun.edu.tr", None, None, None),
    (11296, "Hacettepe University", "哈塞特佩大学", "Asia", "Turkey", "Ankara", None, "university", None, "https://www.hacettepe.edu.tr", None, None, None),
    (11297, "Ankara University", "安卡拉大学", "Asia", "Turkey", "Ankara", None, "university", None, "https://www.ankara.edu.tr", None, None, None),
    (11298, "Ege University", "爱琴海大学", "Asia", "Turkey", "Izmir", None, "university", None, "https://www.ege.edu.tr", None, None, None),
    
    # 伊朗大学 (5所)
    (11299, "University of Tehran", "德黑兰大学", "Asia", "Iran", "Tehran", None, "university", None, "https://ut.ac.ir", None, None, None),
    (11300, "Sharif University of Technology", "谢里夫理工大学", "Asia", "Iran", "Tehran", None, "university", None, "https://sharif.edu", None, None, None),
    (11301, "Amirkabir University of Technology", "阿米尔卡比尔理工大学", "Asia", "Iran", "Tehran", None, "university", None, "https://aut.ac.ir", None, None, None),
    (11302, "Tehran University of Medical Sciences", "德黑兰医科大学", "Asia", "Iran", "Tehran", None, "university", None, "https://tums.ac.ir", None, None, None),
    (11303, "Isfahan University of Technology", "伊斯法罕理工大学", "Asia", "Iran", "Isfahan", None, "university", None, "https://iut.ac.ir", None, None, None),
    
    # 伊拉克大学 (3所)
    (11304, "University of Baghdad", "巴格达大学", "Asia", "Iraq", "Baghdad", None, "university", None, "https://UoBaghdad.edu.iq", None, None, None),
    (11305, "University of Basrah", "巴士拉大学", "Asia", "Iraq", "Basrah", None, "university", None, "https://ub.edu.iq", None, None, None),
    (11306, "Mustansiriya University", "穆斯坦西里亚大学", "Asia", "Iraq", "Baghdad", None, "university", None, "https://uomustansiriyah.edu.iq", None, None, None),
    
    # 以色列大学 (4所)
    (11307, "Hebrew University of Jerusalem", "耶路撒冷希伯来大学", "Asia", "Israel", "Jerusalem", None, "university", None, "https://new.huji.ac.il", None, None, None),
    (11308, "Tel Aviv University", "特拉维夫大学", "Asia", "Israel", "Tel Aviv", None, "university", None, "https://www.tau.ac.il", None, None, None),
    (11309, "Technion - Israel Institute of Technology", "以色列理工学院", "Asia", "Israel", "Haifa", None, "university", None, "https://www.technion.ac.il", None, None, None),
    (11310, "Weizmann Institute of Science", "魏茨曼科学研究所", "Asia", "Israel", "Rehovot", None, "university", None, "https://www.weizmann.ac.il", None, None, None),
    
    # 约旦大学 (2所)
    (11311, "University of Jordan", "约旦大学", "Asia", "Jordan", "Amman", None, "university", None, "https://www.ju.edu.jo", None, None, None),
    (11312, "Hashemite University", "哈希姆大学", "Asia", "Jordan", "Zarqa", None, "university", None, "https://www.hu.edu.jo", None, None, None),
    
    # 黎巴嫩大学 (1所)
    (11313, "American University of Beirut", "贝鲁特美国大学", "Asia", "Lebanon", "Beirut", None, "university", None, "https://www.aub.edu.lb", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_50:
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

print(f"\n📊 Batch 50 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
