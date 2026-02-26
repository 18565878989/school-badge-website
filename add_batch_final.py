#!/usr/bin/env python3
"""
添加补充批次（4所）
ID范围: 17190-17193
完成100所目标
"""

import sqlite3

schools_to_add = [
    # 伊拉克 - 补充
    ("University of Baghdad", "巴格达大学", "Asia", "Iraq", "Baghdad", "University of Baghdad, Baghdad, Iraq", "university", None, "https://www.uobaghdad.edu.iq", None, 1957),
    ("University of Technology, Baghdad", "巴格达技术大学", "Asia", "Iraq", "Baghdad", "University of Technology, Baghdad, Iraq", "university", None, "https://www.uotechnology.edu.iq", None, 1975),
    
    # 伊朗 - 补充
    ("Sharif University of Technology", "谢里夫理工大学", "Asia", "Iran", "Tehran", "Sharif University of Technology, Tehran, Iran", "university", None, "https://www.sharif.edu", None, 1966),
    ("Isfahan University of Technology", "伊斯法罕理工大学", "Asia", "Iran", "Isfahan", "Isfahan University of Technology, Isfahan, Iran", "university", None, "https://www.iut.ac.ir", None, 1978),
]

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT MAX(id) FROM schools")
max_id = cursor.fetchone()[0] or 0
print(f"当前最大ID: {max_id}")
print(f"将添加 {len(schools_to_add)} 所学校")

start_id = max_id + 1
for i, school_data in enumerate(schools_to_add):
    school_id = start_id + i
    name, name_cn, region, country, city, address, level, badge_url, website, motto, founded = school_data
    cursor.execute("""
        INSERT INTO schools (id, name, name_cn, region, country, city, address, level, badge_url, website, motto, founded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (school_id, name, name_cn, region, country, city, address, level, badge_url, website, motto, founded))
    print(f"✓ 添加 #{school_id}: {name_cn} ({country})")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM schools WHERE region='Asia'")
asian_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM schools")
total_count = cursor.fetchone()[0]

print(f"\n✅ 成功添加 {len(schools_to_add)} 所亚洲学校")
print(f"亚洲学校总数: {asian_count}")
print(f"全部学校总数: {total_count}")
print(f"ID范围: {start_id}-{start_id + len(schools_to_add) - 1}")

conn.close()
