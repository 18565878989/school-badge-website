#!/usr/bin/env python3
"""
添加第124批亚洲学校（21所）
ID范围: 17154-17174
补充东亚、东南亚国家大学
"""

import sqlite3

schools_to_add = [
    # 蒙古 - 补充
    ("Mongolian University of Science and Technology", "蒙古科技大学", "Asia", "Mongolia", "Ulaanbaatar", "Mongolian University of Science and Technology, Ulaanbaatar, Mongolia", "university", None, "https://www.must.edu.mn", None, 1960),
    ("Mongolian State University", "蒙古国立大学", "Asia", "Mongolia", "Ulaanbaatar", "Mongolian State University, Ulaanbaatar, Mongolia", "university", None, "https://www.msu.edu.mn", None, 1942),
    ("National University of Mongolia", "蒙古国家大学", "Asia", "Mongolia", "Ulaanbaatar", "National University of Mongolia, Ulaanbaatar, Mongolia", "university", None, "https://www.num.edu.mn", None, 1979),
    ("Mongolian University of Life Sciences", "蒙古生命科学大学", "Asia", "Mongolia", "Ulaanbaatar", "Mongolian University of Life Sciences, Ulaanbaatar, Mongolia", "university", None, "https://www.muls.edu.mn", None, 1958),
    ("Hunnu University", "汉努大学", "Asia", "Mongolia", "Ulaanbaatar", "Hunnu University, Ulaanbaatar, Mongolia", "university", None, "https://www.hunnu.edu.mn", None, 2008),
    
    # 朝鲜 - 补充
    ("Kim Il Sung University", "金日成综合大学", "Asia", "North Korea", "Pyongyang", "Kim Il Sung University, Pyongyang, North Korea", "university", None, "https://www.kiaps.edu.kp", None, 1946),
    ("Kim Jong-sik University of Chemical Technology", "金正日化学工业大学", "Asia", "North Korea", "Pyongyang", "Kim Jong-sik University of Chemical Technology, Pyongyang, North Korea", "university", None, None, None, 1960),
    ("Pyongyang University of Mechanical Engineering", "平壤机械大学", "Asia", "North Korea", "Pyongyang", "Pyongyang University of Mechanical Engineering, Pyongyang, North Korea", "university", None, None, None, 1948),
    ("Pyongyang University of Science and Technology", "平壤科学技术大学", "Asia", "North Korea", "Pyongyang", "Pyongyang University of Science and Technology, Pyongyang, North Korea", "university", None, "https://www.put.edu.kp", None, 2010),
    ("University of Foreign Studies", "外语大学", "Asia", "North Korea", "Pyongyang", "University of Foreign Studies, Pyongyang, North Korea", "university", None, None, None, 1964),
    
    # 老挝 - 补充
    ("National University of Laos", "老挝国立大学", "Asia", "Laos", "Vientiane", "National University of Laos, Vientiane, Laos", "university", None, "https://www.nuol.edu.la", None, 1995),
    ("Souphanouvong University", "苏发努冯大学", "Asia", "Laos", "Savannakhet", "Souphanouvong University, Savannakhet, Laos", "university", None, "https://www.spu.edu.la", None, 2007),
    ("Champasak University", "占巴塞大学", "Asia", "Laos", "Pakse", "Champasak University, Pakse, Laos", "university", None, "https://www.cup.edu.la", None, 2007),
    
    # 孟加拉 - 补充
    ("Bangladesh University of Engineering and Technology", "孟加拉工程技术大学", "Asia", "Bangladesh", "Dhaka", "Bangladesh University of Engineering and Technology, Dhaka, Bangladesh", "university", None, "https://www.buet.ac.bd", None, 1962),
    ("Bangabandhu Sheikh Mujib Medical University", "孟加拉国父谢赫·穆吉布医科大学", "Asia", "Bangladesh", "Dhaka", "Bangabandhu Sheikh Mujib Medical University, Dhaka, Bangladesh", "university", None, "https://www.bsmmu.edu.bd", None, 1998),
    ("Jahangirnagar University", "贾汉吉尔诺戈尔大学", "Asia", "Bangladesh", "Savar", "Jahangirnagar University, Savar, Bangladesh", "university", None, "https://www.juniv.edu", None, 1970),
    ("Islamic University, Bangladesh", "孟加拉伊斯兰大学", "Asia", "Bangladesh", "Kushtia", "Islamic University, Bangladesh, Kushtia, Bangladesh", "university", None, "https://www.iu.ac.bd", None, 1979),
    ("Chittagong University of Engineering and Technology", "吉大港工程技术大学", "Asia", "Bangladesh", "Chittagong", "Chittagong University of Engineering and Technology, Chittagong, Bangladesh", "university", None, "https://www.cuet.ac.bd", None, 2003),
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
