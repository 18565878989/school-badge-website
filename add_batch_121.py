#!/usr/bin/env python3
"""
添加第121批亚洲学校（21所）
ID范围: 17024-17044
重点：补充中亚、西亚、南亚代表性大学
"""

import sqlite3

# 准备要添加的学校数据
schools_to_add = [
    # 吉尔吉斯斯坦 - 补充
    ("Kyrgyz National University named after Jusup Balasagyn", "吉尔吉斯斯坦国立大学", "Asia", "Kyrgyzstan", "Bishkek", "Kyrgyz National University, Frunze Street, Bishkek, Kyrgyzstan", "university", None, "http://www.knu.kg", None, 1925),
    ("American University of Central Asia", "中亚美国大学", "Asia", "Kyrgyzstan", "Bishkek", "American University of Central Asia, Bishkek, Kyrgyzstan", "university", None, "https://www.auca.kg", None, 1997),
    ("Kyrgyz State University named after I. Arabaev", "吉尔吉斯斯坦国立伊布拉因姆·阿拉巴耶夫大学", "Asia", "Kyrgyzstan", "Bishkek", "Kyrgyz State University, Bishkek, Kyrgyzstan", "university", None, "http://ksu.kg", None, 1938),
    
    # 塔吉克斯坦 - 补充
    ("Tajik National University", "塔吉克斯坦国立大学", "Asia", "Tajikistan", "Dushanbe", "Tajik National University, Dushanbe, Tajikistan", "university", None, "http://www.tnu.tj", None, 1948),
    ("Russian-Tajik Slavonic University", "俄塔斯拉夫大学", "Asia", "Tajikistan", "Dushanbe", "Russian-Tajik Slavonic University, Dushanbe, Tajikistan", "university", None, "http://www.rtsu.tj", None, 2009),
    ("Tajik Technical University named after Academician M. Osimi", "塔吉克斯坦技术大学", "Asia", "Tajikistan", "Dushanbe", "Tajik Technical University, Dushanbe, Tajikistan", "university", None, "http://www.ttu.tj", None, 1956),
    
    # 土库曼斯坦 - 新增
    ("Turkmen State University named after Magtymguly", "土库曼斯坦国立马赫图姆库里大学", "Asia", "Turkmenistan", "Ashgabat", "Turkmen State University, Ashgabat, Turkmenistan", "university", None, "http://www.tsu.edu.tm", None, 1991),
    ("Turkmen Agricultural University", "土库曼斯坦农业大学", "Asia", "Turkmenistan", "Ashgabat", "Turkmen Agricultural University, Ashgabat, Turkmenistan", "university", None, "http://www.tau.edu.tm", None, 1991),
    ("International Turkmen University of Technology", "土库曼斯坦国际技术大学", "Asia", "Turkmenistan", "Ashgabat", "International Turkmen University of Technology, Ashgabat, Turkmenistan", "university", None, None, None, 2014),
    
    # 巴勒斯坦 - 补充
    ("Birzeit University", "比尔宰特大学", "Asia", "Palestine", "Birzeit", "Birzeit University, Birzeit, Palestine", "university", None, "https://www.birzeit.edu", None, 1924),
    ("An-Najah National University", "安纳贾国立大学", "Asia", "Palestine", "Nablus", "An-Najah National University, Nablus, Palestine", "university", None, "https://www.najah.edu", None, 1918),
    ("Hebron University", "希伯伦大学", "Asia", "Palestine", "Hebron", "Hebron University, Hebron, Palestine", "university", None, "https://www.hebron.edu", None, 1980),
    
    # 也门 - 补充
    ("Sana'a University", "萨那大学", "Asia", "Yemen", "Sana'a", "Sana'a University, Sana'a, Yemen", "university", None, "https://www.su.edu.ye", None, 1950),
    ("Yemen University", "也门大学", "Asia", "Yemen", "Aden", "Yemen University, Aden, Yemen", "university", None, "https://yu.edu.ye", None, 1975),
    ("Taiz University", "塔伊兹大学", "Asia", "Yemen", "Taiz", "Taiz University, Taiz, Yemen", "university", None, "https://www.tu.edu.ye", None, 1987),
    
    # 叙利亚 - 补充
    ("University of Damascus", "大马士革大学", "Asia", "Syria", "Damascus", "University of Damascus, Damascus, Syria", "university", None, "https://www.damascusuniversity.edu.sy", None, 1923),
    ("Aleppo University", "阿勒颇大学", "Asia", "Syria", "Aleppo", "Aleppo University, Aleppo, Syria", "university", None, "https://www.alepuniv.edu.sy", None, 1946),
    ("Tishreen University", "提什林大学", "Asia", "Syria", "Latakia", "Tishreen University, Latakia, Syria", "university", None, "https://www.tishreen.edu.sy", None, 1971),
    
    # 约旦 - 补充
    ("University of Jordan", "约旦大学", "Asia", "Jordan", "Amman", "University of Jordan, Amman, Jordan", "university", None, "https://www.ju.edu.jo", None, 1962),
    ("Jordan University of Science and Technology", "约旦科技大学", "Asia", "Jordan", "Irbid", "Jordan University of Science and Technology, Irbid, Jordan", "university", None, "https://www.just.edu.jo", None, 1986),
    ("Hashemite University", "哈希姆大学", "Asia", "Jordan", "Zarqa", "Hashemite University, Zarqa, Jordan", "university", None, "https://www.hu.edu.jo", None, 1999),
]

# 连接数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 获取当前最大ID
cursor.execute("SELECT MAX(id) FROM schools")
max_id = cursor.fetchone()[0] or 0
print(f"当前最大ID: {max_id}")
print(f"将添加 {len(schools_to_add)} 所学校")

# 添加学校
start_id = max_id + 1
for i, (name, name_cn, region, country, city, address, level, badge_url, website, motto, founded) in enumerate(schools_to_add):
    school_id = start_id + i
    cursor.execute("""
        INSERT INTO schools (id, name, name_cn, region, country, city, address, level, badge_url, website, motto, founded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (school_id, name, name_cn, region, country, city, address, level, badge_url, website, motto, founded))
    print(f"✓ 添加 #{school_id}: {name_cn} ({country})")

# 提交并关闭
conn.commit()

# 验证结果
cursor.execute("SELECT COUNT(*) FROM schools WHERE region='Asia'")
asian_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM schools")
total_count = cursor.fetchone()[0]

print(f"\n✅ 成功添加 {len(schools_to_add)} 所亚洲学校")
print(f"亚洲学校总数: {asian_count}")
print(f"全部学校总数: {total_count}")
print(f"ID范围: {start_id}-{start_id + len(schools_to_add) - 1}")

conn.close()
