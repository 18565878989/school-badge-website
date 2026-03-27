#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 52: 添加第52批亚洲学校（21所）
ID范围: 11335-11355
新增国家/地区: 哈萨克斯坦、乌兹别克斯坦、土库曼斯坦、吉尔吉斯斯坦、塔吉克斯坦、格鲁吉亚、亚美尼亚、阿塞拜疆
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第52批学校数据 (21所)
schools_batch_52 = [
    # 哈萨克斯坦大学 (4所)
    (11335, "Al-Farabi Kazan National University", "阿里·法拉比哈萨克国立大学", "Asia", "Kazakhstan", "Almaty", None, "university", None, "https://www.kaznu.kz", None, None, None),
    (11336, "Kazakh National Technical University", "哈萨克国立技术大学", "Asia", "Kazakhstan", "Almaty", None, "university", None, "https://kazntu.kz", None, None, None),
    (11337, "Eurasian National University", "欧亚国立大学", "Asia", "Kazakhstan", "Nur-Sultan", None, "university", None, "https://www.enu.kz", None, None, None),
    (11338, "Kazakhstan Institute of Management", "哈萨克斯坦管理学院", "Asia", "Kazakhstan", "Almaty", None, "university", None, "https://www.kimep.kz", None, None, None),
    
    # 乌兹别克斯坦大学 (3所)
    (11339, "Tashkent State University of Economics", "塔什干国立经济大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://tsue.uz", None, None, None),
    (11340, "National University of Uzbekistan", "乌兹别克斯坦国立大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://nuu.uz", None, None, None),
    (11341, "Tashkent University of Information Technologies", "塔什干信息技术大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://tuit.uz", None, None, None),
    
    # 土库曼斯坦大学 (2所)
    (11342, "Turkmen State University", "土库曼国立大学", "Asia", "Turkmenistan", "Ashgabat", None, "university", None, "https://tsu.edu.tm", None, None, None),
    (11343, "Turkmen Agricultural University", "土库曼农业大学", "Asia", "Turkmenistan", "Ashgabat", None, "university", None, "https://tda.edu.tm", None, None, None),
    
    # 吉尔吉斯斯坦大学 (2所)
    (11344, "American University of Central Asia", "中亚美国大学", "Asia", "Kyrgyzstan", "Bishkek", None, "university", None, "https://www.auca.kg", None, None, None),
    (11345, "Kyrgyz National University", "吉尔吉斯国立大学", "Asia", "Kyrgyzstan", "Bishkek", None, "university", None, "https://www.knu.kg", None, None, None),
    
    # 塔吉克斯坦大学 (2所)
    (11346, "Tajik National University", "塔吉克国立大学", "Asia", "Tajikistan", "Dushanbe", None, "university", None, "https://www.tnu.tj", None, None, None),
    (11347, "Tajik Technical University", "塔吉克理工大学", "Asia", "Tajikistan", "Dushanbe", None, "university", None, "https://www.ttu.tj", None, None, None),
    
    # 格鲁吉亚大学 (3所)
    (11348, "Tbilisi State University", "第比利斯国立大学", "Asia", "Georgia", "Tbilisi", None, "university", None, "https://www.tsu.edu.ge", None, None, None),
    (11349, "Georgian Technical University", "格鲁吉亚技术大学", "Asia", "Georgia", "Tbilisi", None, "university", None, "https://www.gtu.edu.ge", None, None, None),
    (11350, "Ilia State University", "伊利亚州立大学", "Asia", "Georgia", "Tbilisi", None, "university", None, "https://iliauni.edu.ge", None, None, None),
    
    # 亚美尼亚大学 (2所)
    (11351, "Yerevan State University", "埃里温国立大学", "Asia", "Armenia", "Yerevan", None, "university", None, "https://www.ysu.am", None, None, None),
    (11352, "National Polytechnic University of Armenia", "亚美尼亚国立理工大学", "Asia", "Armenia", "Yerevan", None, "university", None, "https://www.pnu.am", None, None, None),
    
    # 阿塞拜疆大学 (3所)
    (11353, "Baku State University", "巴库国立大学", "Asia", "Azerbaijan", "Baku", None, "university", None, "https://bsu.edu.az", None, None, None),
    (11354, "Azerbaijan State Oil and Industry University", "阿塞拜疆国立石油工业大学", "Asia", "Azerbaijan", "Baku", None, "university", None, "https://asoiu.edu.az", None, None, None),
    (11355, "Azerbaijan Technical University", "阿塞拜疆技术大学", "Asia", "Azerbaijan", "Baku", None, "university", None, "https://www.aztu.edu.az", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_52:
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

print(f"\n📊 Batch 52 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
