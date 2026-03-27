#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 63: 添加第63批亚洲学校（21所）
ID范围: 11929-11949
新增国家/地区: 巴勒斯坦、亚美尼亚、阿塞拜疆、不丹、马尔代夫、乌兹别克斯坦、土库曼斯坦、吉尔吉斯斯坦、塔吉克斯坦
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第63批学校数据 (21所)
schools_batch_63 = [
    # 巴勒斯坦大学 (3所)
    (11929, "Al-Quds University", "圣城大学", "Asia", "Palestine", "Jerusalem", None, "university", None, "https://www.alquds.edu", None, None, None),
    (11930, "An-Najah National University", "安纳贾国立大学", "Asia", "Palestine", "Nablus", None, "university", None, "https://www.najah.edu", None, None, None),
    (11931, "Hebron University", "希伯伦大学", "Asia", "Palestine", "Hebron", None, "university", None, "https://www.hebron.edu", None, None, None),
    
    # 亚美尼亚大学 (2所)
    (11932, "American University of Armenia", "亚美尼亚美国大学", "Asia", "Armenia", "Yerevan", None, "university", None, "https://www.aua.am", None, None, None),
    (11933, "Yerevan State Medical University", "埃里温国立医科大学", "Asia", "Armenia", "Yerevan", None, "university", None, "https://www.ysmu.am", None, None, None),
    
    # 阿塞拜疆大学 (2所)
    (11934, "Azerbaijan State Oil and Industry University", "阿塞拜疆国立石油工业大学", "Asia", "Azerbaijan", "Baku", None, "university", None, "https://www.asoiu.edu.az", None, None, None),
    (11935, "Baku State University", "巴库国立大学", "Asia", "Azerbaijan", "Baku", None, "university", None, "https://www.bsu.edu.az", None, None, None),
    
    # 不丹大学 (3所)
    (11936, "Royal University of Bhutan", "不丹皇家大学", "Asia", "Bhutan", "Thimphu", None, "university", None, "https://www.rub.edu.bt", None, None, None),
    (11937, "College of Science and Technology", "科学技术学院", "Asia", "Bhutan", "Phuentsholing", None, "university", None, "https://www.cst.edu.bt", None, None, None),
    (11938, "Gyalpozhing College of Information Technology", "贾尔波津信息技术学院", "Asia", "Bhutan", "Punakha", None, "university", None, "https://www.gcit.edu.bt", None, None, None),
    
    # 马尔代夫大学 (2所)
    (11939, "Maldives National University", "马尔代夫国立大学", "Asia", "Maldives", "Male", None, "university", None, "https://www.mnu.edu.mv", None, None, None),
    (11940, "Islamic University of Maldives", "马尔代夫伊斯兰大学", "Asia", "Maldives", "Male", None, "university", None, "https://www.ium.edu.mv", None, None, None),
    
    # 乌兹别克斯坦大学 (3所)
    (11941, "Tashkent State Technical University", "塔什干国立技术大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://www.tstu.uz", None, None, None),
    (11942, "National University of Uzbekistan", "乌兹别克斯坦国立大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://www.nuu.uz", None, None, None),
    (11943, "Samarkand State University", "撒马尔罕国立大学", "Asia", "Uzbekistan", "Samarkand", None, "university", None, "https://www.samdu.uz", None, None, None),
    
    # 土库曼斯坦大学 (3所)
    (11944, "Turkmen State University", "土库曼国立大学", "Asia", "Turkmenistan", "Ashgabat", None, "university", None, "https://www.tsu.edu.tm", None, None, None),
    (11945, "Turkmen Polytechnic University", "土库曼理工大学", "Asia", "Turkmenistan", "Ashgabat", None, "university", None, "https://www.tpu.edu.tm", None, None, None),
    (11946, "International University of Turkmenistan", "土库曼国际大学", "Asia", "Turkmenistan", "Ashgabat", None, "university", None, "https://www.intu.edu.tm", None, None, None),
    
    # 吉尔吉斯斯坦大学 (2所)
    (11947, "American University of Central Asia", "中亚美国大学", "Asia", "Kyrgyzstan", "Bishkek", None, "university", None, "https://www.auca.kg", None, None, None),
    (11948, "Kyrgyz National University", "吉尔吉斯斯坦国立大学", "Asia", "Kyrgyzstan", "Bishkek", None, "university", None, "https://www.knu.kg", None, None, None),
    
    # 塔吉克斯坦大学 (1所)
    (11949, "Tajik National University", "塔吉克斯坦国立大学", "Asia", "Tajikistan", "Dushanbe", None, "university", None, "https://www.tnu.tj", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_63:
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

print(f"\n🎉 Batch 63 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
