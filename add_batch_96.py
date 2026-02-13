#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 96: 添加第96批亚洲学校（21所）
ID范围: 13215-13235
新增国家/地区: 日本、韩国、中国、巴基斯坦、孟加拉、斯里兰卡、尼泊尔
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第96批学校数据 (21所)
schools_batch_96 = [
    # 日本大学 (4所)
    (13215, "University of Tokyo", "东京大学", "Asia", "Japan", "Tokyo", None, "university", None, "https://www.u-tokyo.ac.jp", None, None, None),
    (13216, "Kyoto University", "京都大学", "Asia", "Japan", "Kyoto", None, "university", None, "https://www.kyoto-u.ac.jp", None, None, None),
    (13217, "Osaka University", "大阪大学", "Asia", "Japan", "Osaka", None, "university", None, "https://www.osaka-u.ac.jp", None, None, None),
    (13218, "Tohoku University", "东北大学", "Asia", "Japan", "Sendai", None, "university", None, "https://www.tohoku.ac.jp", None, None, None),
    
    # 韩国大学 (4所)
    (13219, "Seoul National University", "首尔国立大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.snu.ac.kr", None, None, None),
    (13220, "Korea Advanced Institute of Science and Technology (KAIST)", "韩国科学技术院", "Asia", "South Korea", "Daejeon", None, "university", None, "https://www.kaist.ac.kr", None, None, None),
    (13221, "Yonsei University", "延世大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.yonsei.ac.kr", None, None, None),
    (13222, "Korea University", "高丽大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.korea.ac.kr", None, None, None),
    
    # 中国大学 (4所)
    (13223, "Tsinghua University", "清华大学", "Asia", "China", "Beijing", None, "university", None, "https://www.tsinghua.edu.cn", None, None, None),
    (13224, "Peking University", "北京大学", "Asia", "China", "Beijing", None, "university", None, "https://www.pku.edu.cn", None, None, None),
    (13225, "Fudan University", "复旦大学", "Asia", "China", "Shanghai", None, "university", None, "https://www.fudan.edu.cn", None, None, None),
    (13226, "Zhejiang University", "浙江大学", "Asia", "China", "Hangzhou", None, "university", None, "https://www.zju.edu.cn", None, None, None),
    
    # 巴基斯坦大学 (3所)
    (13227, "University of Karachi", "卡拉奇大学", "Asia", "Pakistan", "Karachi", None, "university", None, "https://www.uok.edu.pk", None, None, None),
    (13228, "Lahore University of Management Sciences (LUMS)", "拉合尔管理科学大学", "Asia", "Pakistan", "Lahore", None, "university", None, "https://www.lums.edu.pk", None, None, None),
    (13229, "Pakistan Institute of Engineering and Applied Sciences", "巴基斯坦工程技术学院", "Asia", "Pakistan", "Islamabad", None, "university", None, "https://www.pieas.edu.pk", None, None, None),
    
    # 孟加拉大学 (2所)
    (13230, "University of Dhaka", "达卡大学", "Asia", "Bangladesh", "Dhaka", None, "university", None, "https://www.du.ac.bd", None, None, None),
    (13231, "Bangladesh University of Engineering and Technology", "孟加拉工程技术大学", "Asia", "Bangladesh", "Dhaka", None, "university", None, "https://www.buet.ac.bd", None, None, None),
    
    # 斯里兰卡大学 (2所)
    (13232, "University of Moratuwa", "莫拉图瓦大学", "Asia", "Sri Lanka", "Moratuwa", None, "university", None, "https://www.uom.lk", None, None, None),
    (13233, "University of Peradeniya", "佩拉德尼亚大学", "Asia", "Sri Lanka", "Peradeniya", None, "university", None, "https://www.pdn.ac.lk", None, None, None),
    
    # 尼泊尔大学 (2所)
    (13234, "Kathmandu University", "加德满都大学", "Asia", "Nepal", "Dhulikhel", None, "university", None, "https://www.ku.edu.np", None, None, None),
    (13235, "Pokhara University", "博卡拉大学", "Asia", "Nepal", "Pokhara", None, "university", None, "https://www.pu.edu.np", None, None, None),
]

# 插入数据
added_count = 0
skipped_count = 0
for school in schools_batch_96:
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

print(f"\n🎉 Batch 96 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   跳过(已存在): {skipped_count} 所")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")
print(f"   最大ID: {max_id}")

conn.close()
