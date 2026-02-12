#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 54: 添加第54批亚洲学校（16所）- 完成100所目标
ID范围: 11377-11392
新增国家/地区: 泰国、越南、印尼、菲律宾、马来西亚、新加坡、韩国、日本、中国
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第54批学校数据 (16所，完成100所目标)
schools_batch_54 = [
    # 泰国大学 (2所)
    (11377, "Chulalongkorn University", "朱拉隆功大学", "Asia", "Thailand", "Bangkok", None, "university", None, "https://www.chula.ac.th", None, None, None),
    (11378, "Mahidol University", "玛希隆大学", "Asia", "Thailand", "Bangkok", None, "university", None, "https://www.mahidol.ac.th", None, None, None),
    
    # 越南大学 (2所)
    (11379, "Vietnam National University", "越南国立大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://vnu.edu.vn", None, None, None),
    (11380, "Hanoi University of Science and Technology", "河内科学技术大学", "Asia", "Vietnam", "Hanoi", None, "university", None, "https://www.hust.edu.vn", None, None, None),
    
    # 印尼大学 (2所)
    (11381, "Universitas Indonesia", "印尼大学", "Asia", "Indonesia", "Depok", None, "university", None, "https://www.ui.ac.id", None, None, None),
    (11382, "Bandung Institute of Technology", "万隆理工学院", "Asia", "Indonesia", "Bandung", None, "university", None, "https://www.itb.ac.id", None, None, None),
    
    # 菲律宾大学 (2所)
    (11383, "University of the Philippines", "菲律宾大学", "Asia", "Philippines", "Quezon City", None, "university", None, "https://www.up.edu.ph", None, None, None),
    (11384, "Ateneo de Manila University", "马尼拉雅典耀大学", "Asia", "Philippines", "Quezon City", None, "university", None, "https://www.ateneo.edu", None, None, None),
    
    # 马来西亚大学 (2所)
    (11385, "University of Malaya", "马来亚大学", "Asia", "Malaysia", "Kuala Lumpur", None, "university", None, "https://www.um.edu.my", None, None, None),
    (11386, "National University of Malaysia", "马来西亚国民大学", "Asia", "Malaysia", "Bangi", None, "university", None, "https://www.ukm.my", None, None, None),
    
    # 新加坡大学 (2所)
    (11387, "National University of Singapore", "新加坡国立大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.nus.edu.sg", None, None, None),
    (11388, "Nanyang Technological University", "南洋理工大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.ntu.edu.sg", None, None, None),
    
    # 韩国大学 (2所)
    (11389, "Seoul National University", "首尔国立大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.snu.ac.kr", None, None, None),
    (11390, "Korea Advanced Institute of Science and Technology", "韩国科学技术院", "Asia", "South Korea", "Daejeon", None, "university", None, "https://www.kaist.ac.kr", None, None, None),
    
    # 日本大学 (2所)
    (11391, "University of Tokyo", "东京大学", "Asia", "Japan", "Tokyo", None, "university", None, "https://www.u-tokyo.ac.jp", None, None, None),
    (11392, "Kyoto University", "京都大学", "Asia", "Japan", "Kyoto", None, "university", None, "https://www.kyoto-u.ac.jp", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_54:
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

print(f"\n🎉 Batch 54 完成! (100所目标达成)")
print(f"   本批添加: {added_count}/16 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
