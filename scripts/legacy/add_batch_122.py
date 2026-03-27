#!/usr/bin/env python3
"""
添加第122批亚洲学校（21所）
ID范围: 17115-17135
继续补充中亚、西亚、南亚代表性大学
"""

import sqlite3

schools_to_add = [
    # 黎巴嫩 - 补充
    ("American University of Beirut", "贝鲁特美国大学", "Asia", "Lebanon", "Beirut", "American University of Beirut, Beirut, Lebanon", "university", None, "https://www.aub.edu.lb", None, 1866),
    ("Lebanese American University", "黎巴嫩美国大学", "Asia", "Lebanon", "Beirut", "Lebanese American University, Beirut, Lebanon", "university", None, "https://www.lau.edu.lb", None, 1924),
    ("Saint Joseph University of Beirut", "贝鲁特圣约瑟夫大学", "Asia", "Lebanon", "Beirut", "Saint Joseph University, Beirut, Lebanon", "university", None, "https://www.usj.edu.lb", None, 1875),
    ("Holy Spirit University of Kaslik", "卡斯利克圣灵大学", "Asia", "Lebanon", "Jounieh", "Holy Spirit University of Kaslik, Jounieh, Lebanon", "university", None, "https://www.usek.edu.lb", None, 1949),
    ("Lebanese University", "黎巴嫩大学", "Asia", "Lebanon", "Beirut", "Lebanese University, Beirut, Lebanon", "university", None, "https://www.ul.edu.lb", None, 1951),
    
    # 科威特 - 补充
    ("Kuwait University", "科威特大学", "Asia", "Kuwait", "Kuwait City", "Kuwait University, Kuwait City, Kuwait", "university", None, "https://www.kuniv.edu.kw", None, 1966),
    ("American University of Kuwait", "科威特美国大学", "Asia", "Kuwait", "Kuwait City", "American University of Kuwait, Kuwait City, Kuwait", "university", None, "https://www.auk.edu.kw", None, 1996),
    ("Gulf University for Science and Technology", "海湾科技大学", "Asia", "Kuwait", "Kuwait City", "Gulf University for Science and Technology, Kuwait City, Kuwait", "university", None, "https://www.gust.edu.kw", None, 2002),
    
    # 巴林 - 补充
    ("University of Bahrain", "巴林大学", "Asia", "Bahrain", "Sakhir", "University of Bahrain, Sakhir, Bahrain", "university", None, "https://www.uob.edu.bh", None, 1986),
    ("Bahrain University", "巴林王国大学", "Asia", "Bahrain", "Manama", "Bahrain University, Manama, Bahrain", "university", None, None, None, 1978),
    ("Royal University for Women", "皇家女子大学", "Asia", "Bahrain", "Riffa", "Royal University for Women, Riffa, Bahrain", "university", None, "https://www.ruw.edu.bh", None, 2005),
    
    # 阿曼 - 补充
    ("Sultan Qaboos University", "苏丹卡布斯大学", "Asia", "Oman", "Muscat", "Sultan Qaboos University, Muscat, Oman", "Asia", "Oman", "https://www.squ.edu.om", None, 1986),
    ("Dhofar University", "佐法尔大学", "Asia", "Oman", "Salalah", "Dhofar University, Salalah, Oman", "university", None, "https://www.du.edu.om", None, 2004),
    ("Nizwa University", "尼兹瓦大学", "Asia", "Oman", "Nizwa", "Nizwa University, Nizwa, Oman", "university", None, "https://www.nizwa.edu.om", None, 2012),
    
    # 阿塞拜疆 - 补充
    ("Baku State University", "巴库国立大学", "Asia", "Azerbaijan", "Baku", "Baku State University, Baku, Azerbaijan", "university", None, "https://bsu.edu.az", None, 1919),
    ("Azerbaijan State University of Oil and Industry", "阿塞拜疆国立石油工业大学", "Asia", "Azerbaijan", "Baku", "Azerbaijan State Oil Academy, Baku, Azerbaijan", "university", None, "https://www.asoiu.edu.az", None, 1920),
    ("Azerbaijan State University of Economics", "阿塞拜疆国立经济大学", "Asia", "Azerbaijan", "Baku", "Azerbaijan State University of Economics, Baku, Azerbaijan", "university", None, "https://unec.edu.az", None, 1930),
    
    # 亚美尼亚 - 补充
    ("Yerevan State University", "埃里温国立大学", "Asia", "Armenia", "Yerevan", "Yerevan State University, Yerevan, Armenia", "university", None, "https://www.ysu.am", None, 1919),
    ("National Polytechnic University of Armenia", "亚美尼亚国立理工大学", "Asia", "Armenia", "Yerevan", "National Polytechnic University of Armenia, Yerevan, Armenia", "university", None, "https://www.polytech.am", None, 1933),
    ("Armenian State University of Economics", "亚美尼亚国立经济大学", "Asia", "Armenia", "Yerevan", "Armenian State University of Economics, Yerevan, Armenia", "university", None, "https://asue.am", None, 1922),
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
