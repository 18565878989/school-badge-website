#!/usr/bin/env python3
"""
添加第133批亚洲学校 (21所)
继续从上次中断的位置添加
"""

import sqlite3

db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT MAX(id) FROM schools")
max_id = cursor.fetchone()[0]
start_id = max_id + 1

print(f"当前最大ID: {max_id}")
print(f"开始添加学校，ID范围: {start_id} - {start_id + 20}")

# 第133批学校数据
schools_batch_133 = [
    # 继续添加新的亚洲大学
    ("Universitas Gadjah Mada", "加查马达大学", "Asia", "Indonesia", "Yogyakarta", "Bulaksumur, Yogyakarta 55281, Indonesia", "university", "", "https://ugm.ac.id", "", 1949),
    ("Universitas Indonesia", "印度尼西亚大学", "Asia", "Indonesia", "Depok", "Kampus UI, Depoh 16424, Indonesia", "university", "", "https://ui.ac.id", "", 1949),
    ("Universitas Brawijaya", "布拉维查亚大学", "Asia", "Indonesia", "Malang", "Jalan Veteran, Malang 65145, Indonesia", "university", "", "https://ub.ac.id", "", 1963),
    ("Korea Advanced Institute of Science and Technology", "韩国科学技术院", "Asia", "South Korea", "Daejeon", "291 Daehak-ro, Yuseong-gu, Daejeon 34141, South Korea", "university", "", "https://kaist.ac.kr", "", 1971),
    ("Pohang University of Science and Technology", "浦项工科大学", "Asia", "South Korea", "Pohang", "77 Cheongam-ro, Nam-gu, Pohang 37673, South Korea", "university", "", "https://postech.ac.kr", "", 1986),
    ("Korea University", "高丽大学", "Asia", "South Korea", "Seoul", "145 Anam-ro, Seongbuk-gu, Seoul 02841, South Korea", "university", "", "https://korea.ac.kr", "", 1905),
    ("Yonsei University", "延世大学", "Asia", "South Korea", "Seoul", "50 Yonsei-ro, Seodaemun-gu, Seoul 03722, South Korea", "university", "", "https://yonsei.ac.kr", "", 1885),
    ("Tsinghua University", "清华大学", "Asia", "China", "Beijing", "Beijing 100084, China", "university", "", "https://tsinghua.edu.cn", "", 1911),
    ("Peking University", "北京大学", "Asia", "China", "Beijing", "Beijing 100871, China", "university", "", "https://pku.edu.cn", "", 1898),
    ("Fudan University", "复旦大学", "Asia", "China", "Shanghai", "220 Handan Road, Shanghai 200433, China", "university", "", "https://fudan.edu.cn", "", 1905),
    ("Shanghai Jiao Tong University", "上海交通大学", "Asia", "China", "Shanghai", "800 Dongchuan Road, Shanghai 200240, China", "university", "", "https://sjtu.edu.cn", "", 1896),
    ("Zhejiang University", "浙江大学", "Asia", "China", "Hangzhou", "38 Zheda Road, Hangzhou 310027, China", "university", "", "https://zju.edu.cn", "", 1897),
    ("University of Tokyo", "东京大学", "Asia", "Japan", "Tokyo", "7-3-1 Hongo, Bunkyo-ku, Tokyo 113-8654, Japan", "university", "", "https://u-tokyo.ac.jp", "", 1877),
    ("Kyoto University", "京都大学", "Asia", "Japan", "Kyoto", "Yoshida-honmachi, Sakyo-ku, Kyoto 606-8501, Japan", "university", "", "https://kyoto-u.ac.jp", "", 1897),
    ("National University of Singapore", "新加坡国立大学", "Asia", "Singapore", "Singapore", "21 Lower Kent Ridge Road, Singapore 119077", "university", "", "https://nus.edu.sg", "", 1905),
    ("Nanyang Technological University", "南洋理工大学", "Asia", "Singapore", "Singapore", "50 Nanyang Avenue, Singapore 639798", "university", "", "https://ntu.edu.sg", "", 1981),
    ("Chinese University of Hong Kong", "香港中文大学", "Asia", "Hong Kong", "Hong Kong", "Shatin, New Territories, Hong Kong", "university", "", "https://cuhk.edu.hk", "", 1963),
    ("Hong Kong University of Science and Technology", "香港科技大学", "Asia", "Hong Kong", "Hong Kong", "Clear Water Bay, Kowloon, Hong Kong", "university", "", "https://hkust.edu.hk", "", 1991),
    ("National Taiwan University", "国立台湾大学", "Asia", "Taiwan", "Taipei", "No. 1, Sec. 4, Roosevelt Road, Taipei 10617, Taiwan", "university", "", "https://ntu.edu.tw", "", 1928),
    ("Indian Institute of Technology Bombay", "印度理工学院孟买分校", "Asia", "India", "Mumbai", "Powai, Mumbai 400076, India", "university", "", "https://iitb.ac.in", "", 1958),
    ("Indian Institute of Technology Delhi", "印度理工学院德里分校", "Asia", "India", "New Delhi", "Hauz Khas, New Delhi 110016, India", "university", "", "https://iitd.ac.in", "", 1961),
]

added_count = 0
for school in schools_batch_133:
    try:
        cursor.execute("""
            INSERT INTO schools (name, name_cn, region, country, city, address, level, description, website, badge_url, founded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (school[0], school[1], school[2], school[3], school[4], school[5], school[6], school[7], school[8], school[9], school[10]))
        added_count += 1
    except sqlite3.IntegrityError as e:
        print(f"学校已存在，跳过: {school[0]} - {e}")

conn.commit()

# 验证
cursor.execute("SELECT COUNT(*) FROM schools WHERE region='Asia'")
total_asian = cursor.fetchone()[0]

cursor.execute("SELECT MAX(id) FROM schools")
new_max_id = cursor.fetchone()[0]

print(f"\n完成!")
print(f"本批次添加: {added_count} 所学校")
print(f"亚洲学校总数: {total_asian}")
print(f"新最大ID: {new_max_id}")

conn.close()
