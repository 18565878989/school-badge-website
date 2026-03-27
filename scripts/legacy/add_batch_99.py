#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 99: 添加第99批亚洲学校（21所）
ID范围: 13278-13298
新增国家/地区: 老挝、缅甸、菲律宾、印尼、越南、印度、斯里兰卡、孟加拉
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第99批学校数据 (21所)
schools_batch_99 = [
    # 老挝大学 (2所)
    (13278, "National University of Laos", "老挝国立大学", "Asia", "Laos", "Vientiane", None, "university", None, "https://www.nuol.edu.la", None, None, None),
    (13279, "Savannakhet University", "沙湾拿吉大学", "Asia", "Laos", "Savannakhet", None, "university", None, "https://www.savannakhetuni.edu.la", None, None, None),
    
    # 缅甸大学 (2所)
    (13280, "Mandalay University", "曼德勒大学", "Asia", "Myanmar", "Mandalay", None, "university", None, "https://www.mu.edu.mm", None, None, None),
    (13281, "Dagon University", "大贡大学", "Asia", "Myanmar", "Yangon", None, "university", None, "https://www.dagon.edu.mm", None, None, None),
    
    # 菲律宾大学 (2所)
    (13282, "University of Santo Tomas", "圣托马斯大学", "Asia", "Philippines", "Manila", None, "university", None, "https://www.ust.edu.ph", None, None, None),
    (13283, "Polytechnic University of the Philippines", "菲律宾理工大学", "Asia", "Philippines", "Manila", None, "university", None, "https://www.pup.edu.ph", None, None, None),
    
    # 印尼大学 (2所)
    (13284, "Bina Nusantara University", "印尼必那努斯特拉大学", "Asia", "Indonesia", "Jakarta", None, "university", None, "https://www.binus.ac.id", None, None, None),
    (13285, "Diponegoro University", "迪波内戈罗大学", "Asia", "Indonesia", "Semarang", None, "university", None, "https://www.undip.ac.id", None, None, None),
    
    # 越南大学 (2所)
    (13286, "University of Science and Technology", "科学技术大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://www.hust.edu.vn", None, None, None),
    (13287, "Vietnam National University", "越南国立大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://vnu.edu.vn", None, None, None),
    
    # 印度大学 (3所)
    (13288, "Indian Institute of Technology Madras (IITM)", "印度理工学院马德拉斯校区", "Asia", "India", "Chennai", None, "university", None, "https://www.iitm.ac.in", None, None, None),
    (13289, "Indian Institute of Technology Kanpur (IITK)", "印度理工学院坎普尔校区", "Asia", "India", "Kanpur", None, "university", None, "https://www.iitk.ac.in", None, None, None),
    (13290, "Indian Institute of Technology Kharagpur (IITKGP)", "印度理工学院卡拉格普尔校区", "Asia", "India", "Kharagpur", None, "university", None, "https://www.iitkgp.ac.in", None, None, None),
    
    # 斯里兰卡大学 (2所)
    (13291, "Sri Lanka Institute of Information Technology", "斯里兰卡信息技术学院", "Asia", "Sri Lanka", "Malabe", None, "university", None, "https://www.sliit.lk", None, None, None),
    (13292, "Wayamba University of Sri Lanka", "斯里兰卡韦亚姆大学", "Asia", "Sri Lanka", "Kuliyapitiya", None, "university", None, "https://www.wusl.edu.lk", None, None, None),
    
    # 孟加拉大学 (2所)
    (13293, "Bangladesh University of Textiles", "孟加拉纺织大学", "Asia", "Bangladesh", "Dhaka", None, "university", None, "https://www.butex.edu.bd", None, None, None),
    (13294, "Jahangirnagar University " , "贾汉吉尔诺加尔大学", "Asia", "Bangladesh", "Savar", None, "university", None, "https://www.juniv.edu", None, None, None),
    
    # 尼泊尔大学 (2所)
    (13295, "Purbanchal University", "普尔班乔尔大学", "Asia", "Nepal", "Biratnagar", None, "university", None, "httpsanchalun://www.purbiversity.edu.np", None, None, None),
    (13296, "Mid-West University", "中西部大学", "Asia", "Nepal", "Surkhet", None, "university", None, "https://www.mwu.edu.np", None, None, None),
    
    # 巴基斯坦大学 (2所)
    (13297, "National University of Sciences and Technology (NUST)", "国家科技大学", "Asia", "Pakistan", "Islamabad", None, "university", None, "https://www.nust.edu.pk", None, None, None),
    (13298, "COMSATS University", "COMSATS大学", "Asia", "Pakistan", "Islamabad", None, "university", None, "https://www.comsats.edu.pk", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_99:
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

print(f"\n🎉 Batch 99 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
