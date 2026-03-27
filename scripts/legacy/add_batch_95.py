#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 95: 添加第95批亚洲学校（21所）
ID范围: 13194-13214
新增国家/地区: 菲律宾、马来西亚、新加坡、印尼、越南、泰国、缅甸、印度
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第95批学校数据 (21所)
schools_batch_95 = [
    # 菲律宾大学 (3所)
    (13194, "Ateneo de Manila University", "马尼拉雅典耀大学", "Asia", "Philippines", "Quezon City", None, "university", None, "https://www.ateneo.edu", None, None, None),
    (13195, "De La Salle University", "菲律宾德拉萨大学", "Asia", "Philippines", "Manila", None, "university", None, "https://www.dlsu.edu.ph", None, None, None),
    (13196, "University of the Philippines Diliman", "菲律宾大学迪里曼校区", "Asia", "Philippines", "Quezon City", None, "university", None, "https://www.upd.edu.ph", None, None, None),
    
    # 马来西亚大学 (3所)
    (13197, "Universiti Malaya (UM)", "马来亚大学", "Asia", "Malaysia", "Kuala Lumpur", None, "university", None, "https://www.um.edu.my", None, None, None),
    (13198, "Universiti Kebangsaan Malaysia (UKM)", "马来西亚国立大学", "Asia", "Malaysia", "Bangi", None, "university", None, "https://www.ukm.my", None, None, None),
    (13199, "Universiti Putra Malaysia (UPM)", "马来西亚博特拉大学", "Asia", "Malaysia", "Serdang", None, "university", None, "https://www.upm.edu.my", None, None, None),
    
    # 新加坡大学 (2所)
    (13200, "Nanyang Technological University (NTU)", "南洋理工大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.ntu.edu.sg", None, None, None),
    (13201, "Singapore Management University (SMU)", "新加坡管理大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.smu.edu.sg", None, None, None),
    
    # 印尼大学 (3所)
    (13202, "Universitas Indonesia", "印尼大学", "Asia", "Indonesia", "Depok", None, "university", None, "https://www.ui.ac.id", None, None, None),
    (13203, "Gadjah Mada University", "加查马达大学", "Asia", "Indonesia", "Yogyakarta", None, "university", None, "https://www.ugm.ac.id", None, None, None),
    (13204, "Institut Teknologi Bandung (ITB)", "万隆理工学院", "Asia", "Indonesia", "Bandung", None, "university", None, "https://www.itb.ac.id", None, None, None),
    
    # 越南大学 (3所)
    (13205, "Vietnam National University, Hanoi", "河内国家大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://vnu.edu.vn", None, None, None),
    (13206, "Vietnam National University, Ho Chi Minh City", "胡志明市国家大学", "Asia", "Vietnam", "Ho Chi Minh City", None, "university", None, "https://vnuhcm.edu.vn", None, None, None),
    (13207, "Hanoi University of Science and Technology", "河内科技大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://www.hust.edu.vn", None, None, None),
    
    # 泰国大学 (3所)
    (13208, "Chulalongkorn University", "朱拉隆功大学", "Asia", "Thailand", "Bangkok", None, "university", None, "https://www.chula.ac.th", None, None, None),
    (13209, "Mahidol University", "玛希隆大学", "Asia", "Thailand", "Nakhon Pathom", None, "university", None, "https://www.mahidol.ac.th", None, None, None),
    (13210, "Chiang Mai University", "清迈大学", "Asia", "Thailand", "Chiang Mai", None, "university", None, "https://www.cmu.ac.th", None, None, None),
    
    # 缅甸大学 (2所)
    (13211, "University of Yangon", "仰光大学", "Asia", "Myanmar", "Yangon", None, "university", None, "https://www.yu.edu.mm", None, None, None),
    (13212, "Yangon Technological University", "仰光理工大学", "Asia", "Myanmar", "Yangon", None, "university", None, "https://www.ytu.edu.mm", None, None, None),
    
    # 印度大学 (2所)
    (13213, "Indian Institute of Technology Bombay (IITB)", "印度理工学院孟买校区", "Asia", "India", "Mumbai", None, "university", None, "https://www.iitb.ac.in", None, None, None),
    (13214, "Indian Institute of Technology Delhi (IITD)", "印度理工学院德里校区", "Asia", "India", "New Delhi", None, "university", None, "https://home.iitd.ac.in", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_95:
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

print(f"\n🎉 Batch 95 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
