#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 60: 添加第60批亚洲学校（21所）
ID范围: 11624-11644
新增国家/地区: 斯里兰卡、尼泊尔、不丹、马尔代夫、蒙古、哈萨克斯坦、乌兹别克斯坦
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第60批学校数据 (21所)
schools_batch_60 = [
    # 斯里兰卡大学 (3所)
    (11624, "University of Colombo", "科伦坡大学", "Asia", "Sri Lanka", "Colombo", None, "university", None, "https://www.cmb.ac.lk", None, None, None),
    (11625, "University of Peradeniya", "佩拉德尼亚大学", "Asia", "Sri Lanka", "Peradeniya", None, "university", None, "https://www.pdn.ac.lk", None, None, None),
    (11626, "University of Moratuwa", "莫拉图瓦大学", "Asia", "Sri Lanka", "Moratuwa", None, "university", None, "https://www.mrt.ac.lk", None, None, None),
    
    # 尼泊尔大学 (3所)
    (11627, "Tribhuvan University", "特里布万大学", "Asia", "Nepal", "Kirtipur", None, "university", None, "https://www.tribhuvanuniversity.edu.np", None, None, None),
    (11628, "Kathmandu University", "加德满都大学", "Asia", "Nepal", "Dhulikhel", None, "university", None, "https://www.ku.edu.np", None, None, None),
    (11629, "Pokhara University", "博卡拉大学", "Asia", "Nepal", "Pokhara", None, "university", None, "https://www.pu.edu.np", None, None, None),
    
    # 不丹、马尔代夫大学 (2所)
    (11630, "Royal University of Bhutan", "不丹皇家大学", "Asia", "Bhutan", "Thimphu", None, "university", None, "https://www.rub.edu.bt", None, None, None),
    (11631, "Maldives National University", "马尔代夫国立大学", "Asia", "Maldives", "Malé", None, "university", None, "https://www.mnu.edu.mv", None, None, None),
    
    # 蒙古大学 (3所)
    (11632, "National University of Mongolia", "蒙古国立大学", "Asia", "Mongolia", "Ulaanbaatar", None, "university", None, "https://www.num.edu.mn", None, None, None),
    (11633, "Mongolian University of Science and Technology", "蒙古科学技术大学", "Asia", "Mongolia", "Ulaanbaatar", None, "university", None, "https://www.must.edu.mn", None, None, None),
    (11634, "Mongolian State University", "蒙古国立大学", "Asia", "Mongolia", "Ulaanbaatar", None, "university", None, "https://www.msu.edu.mn", None, None, None),
    
    # 中亚大学 (10所)
    (11635, "Al-Farabi Nazarbayev University", "阿尔法拉比纳扎尔巴耶夫大学", "Asia", "Kazakhstan", "Almaty", None, "university", None, "https://www.nu.edu.kz", None, None, None),
    (11636, "Kazakh National University", "哈萨克斯坦国立大学", "Asia", "Kazakhstan", "Almaty", None, "university", None, "https://www.kaznu.edu.kz", None, None, None),
    (11637, "Kazakhstan Institute of Management", "哈萨克斯坦管理学院", "Asia", "Kazakhstan", "Almaty", None, "university", None, "https://www.kimep.kz", None, None, None),
    (11638, "Tashkent State University of Uzbek", "塔什干国立大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://www.uzswlu.uz", None, None, None),
    (11639, "Westminster International University in Tashkent", "威斯敏斯特塔什干国际大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://www.wiut.uz", None, None, None),
    (11640, "National University of Uzbekistan", "乌兹别克斯坦国立大学", "Asia", "Uzbekistan", "Tashkent", None, "university", None, "https://www.nuu.uz", None, None, None),
    (11641, "Kyrgyz National University", "吉尔吉斯斯坦国立大学", "Asia", "Kyrgyzstan", "Bishkek", None, "university", None, "https://www.knu.kg", None, None, None),
    (11642, "American University of Central Asia", "中亚美国大学", "Asia", "Kyrgyzstan", "Bishkek", None, "university", None, "https://www.auca.kg", None, None, None),
    (11643, "Turkmen State University", "土库曼斯坦国立大学", "Asia", "Turkmenistan", "Ashgabat", None, "university", None, "https://www.tsu.edu.tm", None, None, None),
    (11644, "Tajik National University", "塔吉克斯坦国立大学", "Asia", "Tajikistan", "Dushanbe", None, "university", None, "https://www.tnu.tj", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_60:
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

print(f"\n🎉 Batch 60 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
