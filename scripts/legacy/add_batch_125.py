#!/usr/bin/env python3
"""
添加第125批亚洲学校（22所）
ID范围: 17172-17193
完成100所目标，补充南亚、东南亚国家大学
"""

import sqlite3

schools_to_add = [
    # 尼泊尔 - 补充
    ("Tribhuvan University", "特里布文大学", "Asia", "Nepal", "Kirtipur", "Tribhuvan University, Kirtipur, Nepal", "university", None, "https://www.tribhuvanuniversity.edu.np", None, 1959),
    ("Kathmandu University", "加德满都大学", "Asia", "Nepal", "Dhulikhel", "Kathmandu University, Dhulikhel, Nepal", "university", None, "https://www.ku.edu.np", None, 1991),
    ("Pokhara University", "博卡拉大学", "Asia", "Nepal", "Pokhara", "Pokhara University, Pokhara, Nepal", "university", None, "https://www.pu.edu.np", None, 1996),
    ("Purbanchal University", "东大学", "Asia", "Nepal", "Birtamode", "Purbanchal University, Birtamode, Nepal", "university", None, "https://www.purbanchaluniversity.edu.np", None, 1993),
    ("Mid-West University", "中西部大学", "Asia", "Nepal", "Birendranagar", "Mid-West University, Birendranagar, Nepal", "university", None, "https://www.mwu.edu.np", None, 2010),
    
    # 斯里兰卡 - 补充
    ("University of Moratuwa", "莫拉图瓦大学", "Asia", "Sri Lanka", "Moratuwa", "University of Moratuwa, Moratuwa, Sri Lanka", "university", None, "https://www.uom.lk", None, 1942),
    ("University of Kelaniya", "凯拉尼亚大学", "Asia", "Sri Lanka", "Kelaniya", "University of Kelaniya, Kelaniya, Sri Lanka", "university", None, "https://www.kln.ac.lk", None, 1959),
    ("University of Jaffna", "贾夫纳大学", "Asia", "Sri Lanka", "Jaffna", "University of Jaffna, Jaffna, Sri Lanka", "university", None, "https://www.jfn.ac.lk", None, 1974),
    ("University of Ruhuna", "鲁胡纳大学", "Asia", "Sri Lanka", "Matara", "University of Ruhuna, Matara, Sri Lanka", "university", None, "https://www.ruh.ac.lk", None, 1978),
    ("Sabaragamuwa University of Sri Lanka", "斯里兰卡萨伯勒格穆沃大学", "Asia", "Sri Lanka", "Belihuloya", "Sabaragamuwa University of Sri Lanka, Belihuloya, Sri Lanka", "university", None, "https://www.sab.ac.lk", None, 1991),
    
    # 巴基斯坦 - 补充
    ("Pakistan Institute of Engineering and Applied Sciences", "巴基斯坦工程技术科学研究所", "Asia", "Pakistan", "Islamabad", "Pakistan Institute of Engineering and Applied Sciences, Islamabad, Pakistan", "university", None, "https://www.pieas.edu.pk", None, 1967),
    ("University of Engineering and Technology, Lahore", "拉合尔工程技术大学", "Asia", "Pakistan", "Lahore", "University of Engineering and Technology, Lahore, Pakistan", "university", None, "https://www.uet.edu.pk", None, 1921),
    ("Pakistan Institute of Development Economics", "巴基斯坦发展经济研究所", "Asia", "Pakistan", "Islamabad", "Pakistan Institute of Development Economics, Islamabad, Pakistan", "university", None, "https://www.pide.org.pk", None, 1957),
    ("NED University of Engineering and Technology", "NED工程技术大学", "Asia", "Pakistan", "Karachi", "NED University of Engineering and Technology, Karachi, Pakistan", "university", None, "https://www.neduet.edu.pk", None, 1921),
    ("University of Agriculture, Faisalabad", "费萨拉巴德农业大学", "Asia", "Pakistan", "Faisalabad", "University of Agriculture, Faisalabad, Pakistan", "university", None, "https://www.uaf.edu.pk", None, 1906),
    
    # 阿富汗 - 补充
    ("Kabul University", "喀布尔大学", "Asia", "Afghanistan", "Kabul", "Kabul University, Kabul, Afghanistan", "university", None, "https://www.ku.edu.af", None, 1932),
    ("American University of Afghanistan", "阿富汗美国大学", "Asia", "Afghanistan", "Kabul", "American University of Afghanistan, Kabul, Afghanistan", "university", None, "https://www.afghanuniversity.edu", None, 2006),
    ("Kabul University of Medical Sciences", "喀布尔医科大学", "Asia", "Afghanistan", "Kabul", "Kabul University of Medical Sciences, Kabul, Afghanistan", "university", None, None, None, 2004),
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
