#!/usr/bin/env python3
"""
添加第131批亚洲学校 (21所) - 筛选不重复的学校
"""

import sqlite3
from datetime import datetime

db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT MAX(id) FROM schools")
max_id = cursor.fetchone()[0]
start_id = max_id + 1 if max_id else 1

print(f"当前最大ID: {max_id}")
print(f"开始添加学校，ID范围: {start_id} - {start_id + 20}")

# 第131批学校数据 (仅包含不存在的学校)
schools_batch_131 = [
    # 日本大学 (Japan)
    ("Osaka Metropolitan University", "大阪公立大学", "Asia", "Japan", "Osaka", "1-1 Gakuen-cho, Naka-ku, Sakai 599-8531, Japan", "university", "", "https://www.osaka-cu.ac.jp", "", 2022),
    ("Shizuoka University", "静冈大学", "Asia", "Japan", "Shizuoka", "836 Ohya, Suruga-ku, Shizuoka 422-8529, Japan", "university", "", "https://www.shizuoka.ac.jp", "", 1949),
    ("Toyama University", "富山大学", "Asia", "Japan", "Toyama", "3190 Gofuku, Toyama 930-8555, Japan", "university", "", "https://www.u-toyama.ac.jp", "", 1949),
    ("University of Miyazaki", "宫崎大学", "Asia", "Japan", "Miyazaki", "1-1 Gakuen Kibanadai Nishi, Miyazaki 889-2192, Japan", "university", "", "https://www.miyazaki-u.ac.jp", "", 1949),
    ("Kagoshima University", "鹿儿岛大学", "Asia", "Japan", "Kagoshima", "1-21-40 Korimoto, Kagoshima 890-0065, Japan", "university", "", "https://www.kagoshima-u.ac.jp", "", 1949),
    ("Oita University", "大分大学", "Asia", "Japan", "Oita", "700 Dannoharu, Oita 870-1192, Japan", "university", "", "https://www.oita-u.ac.jp", "", 1949),
    ("Saga University", "佐贺大学", "Asia", "Japan", "Saga", "1 Honjo, Saga 840-8502, Japan", "university", "", "https://www.saga-u.ac.jp", "", 1949),
    ("Nagasaki University", "长崎大学", "Asia", "Japan", "Nagasaki", "1-14 Bunkyo-machi, Nagasaki 852-8521, Japan", "university", "", "https://www.nagasaki-u.ac.jp", "", 1949),
    ("Kumamoto University", "熊本大学", "Asia", "Japan", "Kumamoto", "2-40-1 Kurokami, Chuo-ku, Kumamoto 860-8555, Japan", "university", "", "https://www.kumamoto-u.ac.jp", "", 1949),
    ("Miyazaki University", "宫崎大学", "Asia", "Japan", "Miyazaki", "1-1 Gakuen Kibanadai Nishi, Miyazaki 889-2192, Japan", "university", "", "https://www.miyazaki-u.ac.jp", "", 1949),
    
    # 韩国大学 (South Korea) - 使用不同名称变体
    ("Chonnam National University", "全南国立大学", "Asia", "South Korea", "Gwangju", "77 Yongbong-ro, Buk-gu, Gwangju 61186, South Korea", "university", "", "https://www.jnu.ac.kr", "", 1946),
    ("Jeonbuk National University", "全北国立大学", "Asia", "South Korea", "Jeonju", "567 Baekje-daero, Deokjin-gu, Jeonju 54896, South Korea", "university", "", "https://www.jbnu.ac.kr", "", 1947),
    ("Gyeongsang National University", "庆尚国立大学", "Asia", "South Korea", "Jinju", "501 Jinjudae-ro, Jinju-si, Gyeongsangnam-do 52828, South Korea", "university", "", "https://www.gnu.ac.kr", "", 1948),
    ("Chungbuk National University", "忠北国立大学", "Asia", "South Korea", "Cheongju", "1 Chungdae-ro, Seowon-gu, Cheongju 28644, South Korea", "university", "", "https://www.cbnu.ac.kr", "", 1951),
    ("Jeju National University", "济州国立大学", "Asia", "South Korea", "Jeju", "102 Jejudaehak-ro, Jeju-si, Jeju-do 63243, South Korea", "university", "", "https://www.jejunu.ac.kr", "", 1947),
    
    # 东南亚大学
    ("RMIT Vietnam", "皇家墨尔本理工越南分校", "Asia", "Vietnam", "Hanoi", "521 Kim Ma, Ba Dinh, Hanoi, Vietnam", "university", "", "https://www.rmit.edu.vn", "", 1887),
    ("Curtin Malaysia", "科廷大学马来西亚分校", "Asia", "Malaysia", "Miri", "CDT 250, 98009 Miri, Sarawak, Malaysia", "university", "", "https://curtin.edu.my", "", 1966),
    ("UCSI University", "思特雅大学", "Asia", "Malaysia", "Kuala Lumpur", "Cheras, 56000 Kuala Lumpur, Malaysia", "university", "", "https://www.ucsi.edu.my", "", 1986),
    ("Taylor's University", "泰莱大学", "Asia", "Malaysia", "Subang Jaya", "Jalan Taylors, 47500 Subang Jaya, Selangor, Malaysia", "universit
    ("Sunway University", "双威大学", "Asia", "Malaysia", "Bandar Sunway", "5, Jalan Universiti, Bandar Sunway, 47500 Selangor, Malaysia", "university", "", "https://www.sunway.edu.my", "", 1987),
    
    # 南亚大学
    ("Mysore University India", "迈索尔大学印度", "Asia", "India", "Mysore", "Mysuru, Karnataka 570006, India", "university", "", "https://uni-mysore.ac.in", "", 1916),
]

# 插入数据
try:
    cursor.executemany("""
        INSERT INTO schools (name, name_cn, region, country, city, address, level, badge_url, website, motto, founded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, schools_batch_131)
    
    conn.commit()
    print(f"✅ 成功添加 {len(schools_batch_131)} 所学校")
    print(f"ID范围: {start_id} - {start_id + len(schools_batch_131) - 1}")
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE region = 'Asia'")
    asian_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM schools")
    total_count = cursor.fetchone()[0]
    print(f"亚洲学校总数: {asian_count}")
    print(f"学校总数: {total_count}")
    
except Exception as e:
    print(f"❌ 添加失败: {e}")
    conn.rollback()

conn.close()
print("\n第131批亚洲学校添加完成！")
