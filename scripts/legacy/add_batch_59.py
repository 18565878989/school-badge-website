#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 59: 添加第59批亚洲学校（21所）
ID范围: 11603-11623
新增国家/地区: 香港、澳门、新加坡、印尼、菲律宾、越南、巴基斯坦、孟加拉
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第59批学校数据 (21所)
schools_batch_59 = [
    # 香港大学 (3所)
    (11603, "The University of Hong Kong", "香港大学", "Asia", "Hong Kong", "Hong Kong", None, "university", None, "https://www.hku.hk", None, None, None),
    (11604, "Chinese University of Hong Kong", "香港中文大学", "Asia", "Hong Kong", "Hong Kong", None, "university", None, "https://www.cuhk.edu.hk", None, None, None),
    (11605, "Hong Kong University of Science and Technology", "香港科技大学", "Asia", "Hong Kong", "Hong Kong", None, "university", None, "https://www.hkust.edu.hk", None, None, None),
    
    # 澳门大学 (2所)
    (11606, "University of Macau", "澳门大学", "Asia", "Macau", "Macau", None, "university", None, "https://www.um.edu.mo", None, None, None),
    (11607, "Macau University of Science and Technology", "澳门科技大学", "Asia", "Macau", "Macau", None, "university", None, "https://www.must.edu.mo", None, None, None),
    
    # 新加坡大学 (2所)
    (11608, "Nanyang Technological University", "南洋理工大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.ntu.edu.sg", None, None, None),
    (11609, "Singapore Institute of Technology", "新加坡理工学院", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.singaporetech.edu.sg", None, None, None),
    
    # 印尼大学 (3所)
    (11610, "Bandung Institute of Technology", "万隆理工大学", "Asia", "Indonesia", "Bandung", None, "university", None, "https://www.itb.ac.id", None, None, None),
    (11611, "Diponegoro University", "迪波内戈罗大学", "Asia", "Indonesia", "Semarang", None, "university", None, "https://www.undip.ac.id", None, None, None),
    (11612, "Airlangga University", "爱尔朗加大学", "Asia", "Indonesia", "Surabaya", None, "university", None, "https://www.unair.ac.id", None, None, None),
    
    # 菲律宾大学 (2所)
    (11613, "University of Santo Tomas", "圣托马斯大学", "Asia", "Philippines", "Manila", None, "university", None, "https://www.ust.edu.ph", None, None, None),
    (11614, "Miriam College Foundation", "米里亚姆学院", "Asia", "Philippines", "Quezon City", None, "university", None, "https://www.miriamcollege.edu", None, None, None),
    
    # 越南大学 (3所)
    (11615, "Vietnam National University, Ho Chi Minh City", "胡志明市国家大学", "Asia", "Vietnam", "Ho Chi Minh City", None, "university", None, "https://www.hcmus.edu.vn", None, None, None),
    (11616, "Ho Chi Minh City University of Technology", "胡志明市理工大学", "Asia", "Vietnam", "Ho Chi Minh City", None, "university", None, "https://www.hcmut.edu.vn", None, None, None),
    (11617, "University of Economics Ho Chi Minh City", "胡志明市经济大学", "Asia", "Vietnam", "Ho Chi Minh City", None, "university", None, "https://www.ueh.edu.vn", None, None, None),
    
    # 南亚大学 (6所)
    (11618, "University of Karachi", "卡拉奇大学", "Asia", "Pakistan", "Karachi", None, "university", None, "https://www.uok.edu.pk", None, None, None),
    (11619, "Lahore University of Management Sciences", "拉合尔管理科学大学", "Asia", "Pakistan", "Lahore", None, "university", None, "https://www.lums.edu.pk", None, None, None),
    (11620, "National University of Sciences and Technology", "国立科学技术大学", "Asia", "Pakistan", "Islamabad", None, "university", None, "https://www.nust.edu.pk", None, None, None),
    (11621, "University of Dhaka", "达卡大学", "Asia", "Bangladesh", "Dhaka", None, "university", None, "https://www.du.ac.bd", None, None, None),
    (11622, "Bangladesh University of Engineering and Technology", "孟加拉工程技术大学", "Asia", "Bangladesh", "Dhaka", None, "university", None, "https://www.buet.ac.bd", None, None, None),
    (11623, "Jahangirnagar University", "贾汉吉尔诺戈尔大学", "Asia", "Bangladesh", "Dhaka", None, "university", None, "https://www.juniv.edu", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_59:
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

print(f"\n🎉 Batch 59 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
