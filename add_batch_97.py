#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 97: 添加第97批亚洲学校（21所）
ID范围: 13236-13256
新增国家/地区: 伊朗、伊拉克、以色列、约旦、黎巴嫩、土耳其、哈萨克斯坦、乌兹别克斯坦
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第97批学校数据 (21所)
schools_batch_97 = [
    # 伊朗大学 (3所)
    (13236, "Sharif University of Technology", "谢里夫理工大学", "Asia", "Iran", "Tehran", None, "university", None, "https://www.sharif.edu", None, None, None),
    (13237, "Amirkabir University of Technology", "阿米尔卡比尔理工大学", "Asia", "Iran", "Tehran", None, "university", None, "https://www.aut.ac.ir", None, None, None),
    (13238, "Iran University of Science and Technology", "伊朗科技大学", "Asia", "Iran", "Tehran", None, "university", None, "https://www.iust.ac.ir", None, None, None),
    
    # 伊拉克大学 (2所)
    (13239, "University of Baghdad", "巴格达大学", "Asia", "Iraq", "Baghdad", None, "university", None, "https://www.uobaghdad.edu.iq", None, None, None),
    (13240, "University of Karbala", "卡尔巴拉大学", "Asia", "Iraq", "Karbala", None, "university", None, "https://www.uokarbala.edu.iq", None, None, None),
    
    # 以色列大学 (2所)
    (13241, "Hebrew University of Jerusalem", "耶路撒冷希伯来大学", "Asia", "Israel", "Jerusalem", None, "university", None, "https://new.huji.ac.il", None, None, None),
    (13242, "Technion - Israel Institute of Technology", "以色列理工学院", "Asia", "Israel", "Haifa", None, "university", None, "https://www.technion.ac.il", None, None, None),
    
    # 约旦大学 (2所)
    (13243, "University of Jordan", "约旦大学", "Asia", "Jordan", "Amman", None, "university", None, "https://www.ju.edu.jo", None, None, None),
    (13244, "Jordan University of Science and Technology", "约旦科技大学", "Asia", "Jordan", "Irbid", None, "university", None, "https://www.just.edu.jo", None, None, None),
    
    # 黎巴嫩大学 (2所)
    (13245, "American University of Beirut", "贝鲁特美国大学", "Asia", "Lebanon", "Beirut", None, "university", None, "https://www.aub.edu.lb", None, None, None),
    (13246, "Lebanese American University", "黎巴嫩美国大学", "Asia", "Lebanon", "Byblos", None, "university", None, "https://www.lau.edu.lb", None, None, None),
    
    # 土耳其大学 (3所)
    (13247, "Boğaziçi University", "博斯菲亚大学", "Asia", "Turkey", "Istanbul", None, "university", None, "https://www.boun.edu.tr", None, None, None),
    (13248, "Middle East Technical University (METU)", "中东理工大学", "Asia", "Turkey", "Ankara", None, "university", None, "https://www.metu.edu.tr", None, None, None),
    (13249, "Istanbul Technical University", "伊斯坦布尔理工大学", "Asia", "Turkey", "Istanbul", None, "university", None, "https://www.itu.edu.tr", None, None, None),
    
    # 哈萨克斯坦大学 (2所)
    (13250, "Al-Farabi Nazarbayev University", "阿尔法拉比纳扎尔巴耶夫大学", "Asia", "Kazakhstan", "Almaty", None, "university", None, "https://nu.edu.kz", None, None, None),
    (13251, "Kazakh National University", "哈萨克斯坦国立大学", "Asia", "Kazakhstan", "Almaty", None, "university", None, "https://www.kaznu.edu.kz", None, None, None),
    
    # 乌兹别克斯坦大学 (2所)
    (13252, "Tashkent State Technical University", "塔什干国立技术大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://tstu.uz", None, None, None),
    (13253, "National University of Uzbekistan", "乌兹别克斯坦国立大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://nuu.uz", None, None, None),
    
    # 格鲁吉亚大学 (2所)
    (13254, "Tbilisi State University", "第比利斯国立大学", "Asia", "Georgia", "Tbilisi", None, "university", None, "https://www.tsu.edu.ge", None, None, None),
    (13255, "Georgian Technical University", "格鲁吉亚理工大学", "Asia", "Georgia", "Tbilisi", None, "university", None, "https://www.gtu.edu.ge", None, None, None),
    
    # 亚美尼亚大学 (1所)
    (13256, "Yerevan State University", "埃里温国立大学", "Asia", "Armenia", "Yerevan", None, "university", None, "https://www.ysu.am", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_97:
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

print(f"\n🎉 Batch 97 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
