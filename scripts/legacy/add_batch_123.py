#!/usr/bin/env python3
"""
添加第123批亚洲学校（21所）
ID范围: 17135-17155
补充东南亚、南亚国家大学
"""

import sqlite3

schools_to_add = [
    # 格鲁吉亚 - 补充
    ("Tbilisi State University", "第比利斯国立大学", "Asia", "Georgia", "Tbilisi", "Tbilisi State University, Tbilisi, Georgia", "university", None, "https://www.tsu.edu.ge", None, 1918),
    ("Georgian Technical University", "格鲁吉亚技术大学", "Asia", "Georgia", "Tbilisi", "Georgian Technical University, Tbilisi, Georgia", "university", None, "https://gtu.edu.ge", None, 1922),
    ("Ilia State University", "伊利亚州立大学", "Asia", "Georgia", "Tbilisi", "Ilia State University, Tbilisi, Georgia", "university", None, "https://iliauni.edu.ge", None, 2006),
    ("Caucasus University", "高加索大学", "Asia", "Georgia", "Tbilisi", "Caucasus University, Tbilisi, Georgia", "university", None, "https://cu.edu.ge", None, 2004),
    
    # 塞浦路斯 - 补充
    ("University of Cyprus", "塞浦路斯大学", "Asia", "Cyprus", "Nicosia", "University of Cyprus, Nicosia, Cyprus", "university", None, "https://www.ucy.ac.cy", None, 1989),
    ("Cyprus University of Technology", "塞浦路斯理工大学", "Asia", "Cyprus", "Limassol", "Cyprus University of Technology, Limassol, Cyprus", "university", None, "https://www.cut.ac.cy", None, 2004),
    ("European University Cyprus", "塞浦路斯欧洲大学", "Asia", "Cyprus", "Nicosia", "European University Cyprus, Nicosia, Cyprus", "university", None, "https://www.euc.ac.cy", None, 2007),
    ("Frederick University", "弗雷德里克大学", "Asia", "Cyprus", "Nicosia", "Frederick University, Nicosia, Cyprus", "university", None, "https://www.frederick.ac.cy", None, 2007),
    
    # 马尔代夫 - 补充
    ("Maldives National University", "马尔代夫国立大学", "Asia", "Maldives", "Malé", "Maldives National University, Malé, Maldives", "university", None, "https://www.mnu.edu.mv", None, 2011),
    ("Villa College", "维拉学院", "Asia", "Maldives", "Malé", "Villa College, Malé, Maldives", "university", None, "https://www.villacollege.edu.mv", None, 1980),
    
    # 不丹 - 补充
    ("Royal University of Bhutan", "不丹皇家大学", "Asia", "Bhutan", "Thimphu", "Royal University of Bhutan, Thimphu, Bhutan", "university", None, "https://www.rub.edu.bt", None, 2003),
    ("College of Science and Technology", "不丹科学技术学院", "Asia", "Bhutan", "Rinchending", "College of Science and Technology, Rinchending, Bhutan", "university", None, "https://www.cst.edu.bt", None, 2002),
    ("Royal Thimphu College", "皇家廷布学院", "Asia", "Bhutan", "Thimphu", "Royal Thimphu College, Thimphu, Bhutan", "university", None, "https://www.rtc.bt", None, 1999),
    
    # 文莱 - 补充
    ("Universiti Brunei Darussalam", "文莱达鲁萨兰大学", "Asia", "Brunei", "Gadong", "Universiti Brunei Darussalam, Gadong, Brunei", "university", None, "https://www.ubd.edu.bn", None, 1985),
    ("International Islamic University College", "文莱国际伊斯兰大学学院", "Asia", "Brunei", "Gadong", "International Islamic University College, Gadong, Brunei", "university", None, None, None, 1975),
    ("Politeknik Brunei", "文莱理工学院", "Asia", "Brunei", "Berakas", "Politeknik Brunei, Berakas, Brunei", "university", None, "https://www.pb.edu.bn", None, 1998),
    
    # 东帝汶 - 补充
    ("National University of East Timor", "东帝汶国立大学", "Asia", "Timor-Leste", "Dili", "National University of East Timor, Dili, Timor-Leste", "university", None, "https://www.unitel.tl", None, 2000),
    ("East Timor Institute of Business Administration", "东帝工商管理学院", "Asia", "Timor-Leste", "Dili", "East Timor Institute of Business Administration, Dili, Timor-Leste", "university", None, None, None, 2002),
    ("Timor-Leste Catholic University", "东帝汶天主教大学", "Asia", "Timor-Leste", "Dili", "Timor-Leste Catholic University, Dili, Timor-Leste", "university", None, "https://www.uctl.edu.tl", None, 2002),
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
