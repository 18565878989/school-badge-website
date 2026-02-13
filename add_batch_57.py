#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 57: 添加第57批亚洲学校（21所）
ID范围: 11561-11581
新增国家/地区: 越南、泰国、印尼、菲律宾、马来西亚、新加坡
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第57批学校数据 (21所)
schools_batch_57 = [
    # 越南大学 (4所)
    (11561, "Vietnam National University, Hanoi", "河内国家大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://vnu.edu.vn", None, None, None),
    (11562, "Hanoi University of Science and Technology", "河内科学技术大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://hust.edu.vn", None, None, None),
    (11563, "University of Economics and Business - VNU", "河内经济与商业大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://ueb.edu.vn", None, None, None),
    (11564, "Hanoi Medical University", "河内医科大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://hmu.edu.vn", None, None, None),
    
    # 泰国大学 (4所)
    (11565, "Chulalongkorn University", "朱拉隆功大学", "Asia", "Thailand", "Bangkok", None, "university", None, "https://www.chula.ac.th", None, None, None),
    (11566, "Mahidol University", "马希隆大学", "Asia", "Thailand", "Bangkok", None, "university", None, "https://www.mahidol.ac.th", None, None, None),
    (11567, "Chiang Mai University", "清迈大学", "Asia", "Thailand", "Chiang Mai", None, "university", None, "https://www.cmu.ac.th", None, None, None),
    (11568, "Kasetsart University", "农业大学", "Asia", "Thailand", "Bangkok", None, "university", None, "https://www.ku.ac.th", None, None, None),
    
    # 印尼大学 (4所)
    (11569, "University of Indonesia", "印尼大学", "Asia", "Indonesia", "Jakarta", None, "university", None, "https://www.ui.ac.id", None, None, None),
    (11570, "Bandung Institute of Technology", "万隆理工大学", "Asia", "Indonesia", "Bandung", None, "university", None, "https://www.itb.ac.id", None, None, None),
    (11571, "Gadjah Mada University", "加查马达大学", "Asia", "Indonesia", "Yogyakarta", None, "university", None, "https://www.ugm.ac.id", None, None, None),
    (11572, "Bogor Agricultural University", "茂物农业大学", "Asia", "Indonesia", "Bogor", None, "university", None, "https://www.ipb.ac.id", None, None, None),
    
    # 菲律宾大学 (3所)
    (11573, "University of the Philippines Diliman", "菲律宾大学迪利曼", "Asia", "Philippines", "Quezon City", None, "university", None, "https://www.upd.edu.ph", None, None, None),
    (11574, "Ateneo de Manila University", "马尼拉雅典耀大学", "Asia", "Philippines", "Quezon City", None, "university", None, "https://www.ateneo.edu", None, None, None),
    (11575, "De La Salle University", "菲律宾德拉萨大学", "Asia", "Philippines", "Manila", None, "university", None, "https://www.dlsu.edu.ph", None, None, None),
    
    # 马来西亚大学 (3所)
    (11576, "University of Malaya", "马来亚大学", "Asia", "Malaysia", "Kuala Lumpur", None, "university", None, "https://www.um.edu.my", None, None, None),
    (11577, "Universiti Kebangsaan Malaysia", "马来西亚国立大学", "Asia", "Malaysia", "Bangi", None, "university", None, "https://www.ukm.my", None, None, None),
    (11578, "Universiti Sains Malaysia", "马来西亚理科大学", "Asia", "Malaysia", "Penang", None, "university", None, "https://www.usm.my", None, None, None),
    
    # 新加坡大学 (3所)
    (11579, "National University of Singapore", "新加坡国立大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.nus.edu.sg", None, None, None),
    (11580, "Nanyang Technological University", "南洋理工大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.ntu.edu.sg", None, None, None),
    (11581, "Singapore Management University", "新加坡管理大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.smu.edu.sg", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_57:
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

print(f"\n🎉 Batch 57 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
