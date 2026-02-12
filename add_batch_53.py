#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 53: 添加第53批亚洲学校（21所）
ID范围: 11356-11376
新增国家/地区: 孟加拉、印度、巴基斯坦、斯里兰卡、尼泊尔、不丹、马尔代夫、缅甸、柬埔寨、老挝
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第53批学校数据 (21所)
schools_batch_53 = [
    # 孟加拉大学 (3所)
    (11356, "Bangladesh University of Engineering and Technology", "孟加拉工程技术大学", "Asia", "Bangladesh", "Dhaka", None, "university", None, "https://www.buet.ac.bd", None, None, None),
    (11357, "University of Dhaka", "达卡大学", "Asia", "Bangladesh", "Dhaka", None, "university", None, "https://www.univdhaka.edu", None, None, None),
    (11358, "Jahangirnagar University", "贾汉吉尔诺尔大学", "Asia", "Bangladesh", "Savar", None, "university", None, "https://www.juniv.edu", None, None, None),
    
    # 印度大学 (5所)
    (11359, "Indian Institute of Technology Bombay", "印度理工学院孟买分校", "Asia", "India", "Mumbai", None, "university", None, "https://www.iitb.ac.in", None, None, None),
    (11360, "Indian Institute of Technology Delhi", "印度理工学院德里分校", "Asia", "India", "New Delhi", None, "university", None, "https://home.iitd.ac.in", None, None, None),
    (11361, "Indian Institute of Technology Madras", "印度理工学院马德拉斯分校", "Asia", "India", "Chennai", None, "university", None, "https://www.iitm.ac.in", None, None, None),
    (11362, "Jawaharlal Nehru University", "贾瓦哈拉尔·尼赫鲁大学", "Asia", "India", "New Delhi", None, "university", None, "https://www.jnu.ac.in", None, None, None),
    (11363, "Delhi University", "德里大学", "Asia", "India", "New Delhi", None, "university", None, "https://www.du.ac.in", None, None, None),
    
    # 巴基斯坦大学 (3所)
    (11364, "University of Punjab", "旁遮普大学", "Asia", "Pakistan", "Lahore", None, "university", None, "https://www.pu.edu.pk", None, None, None),
    (11365, "Pakistan Institute of Engineering and Applied Sciences", "巴基斯坦工程与应用科学学院", "Asia", "Pakistan", "Islamabad", None, "university", None, "https://www.pieas.edu.pk", None, None, None),
    (11366, "Lahore University of Management Sciences", "拉合尔管理科学大学", "Asia", "Pakistan", "Lahore", None, "university", None, "https://www.lums.edu.pk", None, None, None),
    
    # 斯里兰卡大学 (2所)
    (11367, "University of Colombo", "科伦坡大学", "Asia", "Sri Lanka", "Colombo", None, "university", None, "https://www.cmb.ac.lk", None, None, None),
    (11368, "University of Peradeniya", "佩拉德尼亚大学", "Asia", "Sri Lanka", "Peradeniya", None, "university", None, "https://www.pdn.ac.lk", None, None, None),
    
    # 尼泊尔大学 (2所)
    (11369, "Tribhuvan University", "特里布文大学", "Asia", "Nepal", "Kirtipur", None, "university", None, "https://www.tribhuvan-university.edu.np", None, None, None),
    (11370, "Kathmandu University", "加德满都大学", "Asia", "Nepal", "Dhulikhel", None, "university", None, "https://www.ku.edu.np", None, None, None),
    
    # 不丹大学 (1所)
    (11371, "Royal University of Bhutan", "不丹皇家大学", "Asia", "Bhutan", "Thimphu", None, "university", None, "https://www.rub.edu.bt", None, None, None),
    
    # 马尔代夫大学 (1所)
    (11372, "Maldives National University", "马尔代夫国立大学", "Asia", "Maldives", "Male", None, "university", None, "https://www.mnu.edu.mv", None, None, None),
    
    # 缅甸大学 (2所)
    (11373, "University of Yangon", "仰光大学", "Asia", "Myanmar", "Yangon", None, "university", None, "https://www.yangonuniversity.edu.mm", None, None, None),
    (11374, " Mandalay", "曼德勒大学", "Asia", "Myanmar", "Mandalay", None, "university", None, "https://www.mandayuniversity.edu.mm", None, None, None),
    
    # 柬埔寨大学 (1所)
    (11375, "Royal University of Phnom Penh", "金边皇家大学", "Asia", "Cambodia", "Phnom Penh", None, "university", None, "https://www.rupp.edu.kh", None, None, None),
    
    # 老挝大学 (1所)
    (11376, "National University of Laos", "老挝国立大学", "Asia", "Laos", "Vientiane", None, "university", None, "https://www.nuol.edu.la", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_53:
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

print(f"\n📊 Batch 53 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
