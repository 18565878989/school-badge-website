#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 58: 添加第58批亚洲学校（21所）
ID范围: 11582-11602
新增国家/地区: 日本、韩国、中国大陆、台湾、缅甸、柬埔寨、老挝
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第58批学校数据 (21所)
schools_batch_58 = [
    # 日本大学 (4所)
    (11582, "University of Tokyo", "东京大学", "Asia", "Japan", "Tokyo", None, "university", None, "https://www.u-tokyo.ac.jp", None, None, None),
    (11583, "Kyoto University", "京都大学", "Asia", "Japan", "Kyoto", None, "university", None, "https://www.kyoto-u.ac.jp", None, None, None),
    (11584, "Osaka University", "大阪大学", "Asia", "Japan", "Osaka", None, "university", None, "https://www.osaka-u.ac.jp", None, None, None),
    (11585, "Tohoku University", "东北大学", "Asia", "Japan", "Sendai", None, "university", None, "https://www.tohoku.ac.jp", None, None, None),
    
    # 韩国大学 (4所)
    (11586, "Seoul National University", "首尔国立大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.snu.ac.kr", None, None, None),
    (11587, "Korea University", "高丽大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.korea.ac.kr", None, None, None),
    (11588, "Yonsei University", "延世大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.yonsei.ac.kr", None, None, None),
    (11589, "Sungkyunkwan University", "成均馆大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.skku.edu", None, None, None),
    
    # 中国大陆大学 (4所)
    (11590, "Tsinghua University", "清华大学", "Asia", "China", "Beijing", None, "university", None, "https://www.tsinghua.edu.cn", None, None, None),
    (11591, "Peking University", "北京大学", "Asia", "China", "Beijing", None, "university", None, "https://www.pku.edu.cn", None, None, None),
    (11592, "Fudan University", "复旦大学", "Asia", "China", "Shanghai", None, "university", None, "https://www.fudan.edu.cn", None, None, None),
    (11593, "Zhejiang University", "浙江大学", "Asia", "China", "Hangzhou", None, "university", None, "https://www.zju.edu.cn", None, None, None),
    
    # 台湾大学 (3所)
    (11594, "National Taiwan University", "台湾大学", "Asia", "Taiwan", "Taipei", None, "university", None, "https://www.ntu.edu.tw", None, None, None),
    (11595, "National Tsing Hua University", "清华大学", "Asia", "Taiwan", "Hsinchu", None, "university", None, "https://www.nthu.edu.tw", None, None, None),
    (11596, "National Cheng Kung University", "成功大学", "Asia", "Taiwan", "Tainan", None, "university", None, "https://www.ncku.edu.tw", None, None, None),
    
    # 东南亚大学 (6所)
    (11597, "Yangon University", "仰光大学", "Asia", "Myanmar", "Yangon", None, "university", None, "https://www.yu.edu.mm", None, None, None),
    (11598, "Royal University of Phnom Penh", "金边皇家大学", "Asia", "Cambodia", "Phnom Penh", None, "university", None, "https://www.rupp.edu.kh", None, None, None),
    (11599, "National University of Laos", "老挝国立大学", "Asia", "Laos", "Vientiane", None, "university", None, "https://www.nuol.edu.la", None, None, None),
    (11600, "Chulalongkorn University", "朱拉隆功大学", "Asia", "Thailand", "Bangkok", None, "university", None, "https://www.chula.ac.th", None, None, None),
    (11601, "Mahidol University", "马希隆大学", "Asia", "Thailand", "Bangkok", None, "university", None, "https://www.mahidol.ac.th", None, None, None),
    (11602, "University of Malaya", "马来亚大学", "Asia", "Malaysia", "Kuala Lumpur", None, "university", None, "https://www.um.edu.my", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_58:
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

print(f"\n🎉 Batch 58 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
