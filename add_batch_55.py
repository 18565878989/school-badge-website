#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch 55: 添加第55批亚洲学校（21所）
ID范围: 11393-11413
新增国家/地区: 中国大陆、台湾、香港、澳门、日本、韩国
"""

import sqlite3
import uuid

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 第55批学校数据 (21所)
schools_batch_55 = [
    # 中国大陆大学 (3所)
    (11393, "Fudan University", "复旦大学", "Asia", "China", "Shanghai", None, "university", None, "https://www.fudan.edu.cn", None, None, None),
    (11394, "Zhejiang University", "浙江大学", "Asia", "China", "Hangzhou", None, "university", None, "https://www.zju.edu.cn", None, None, None),
    (11395, "Nanjing University", "南京大学", "Asia", "China", "Nanjing", None, "university", None, "https://www.nju.edu.cn", None, None, None),
    
    # 台湾大学 (3所)
    (11396, "National Taiwan University", "台湾大学", "Asia", "Taiwan", "Taipei", None, "university", None, "https://www.ntu.edu.tw", None, None, None),
    (11397, "National Tsing Hua University", "清华大学", "Asia", "Taiwan", "Hsinchu", None, "university", None, "https://www.nthu.edu.tw", None, None, None),
    (11398, "National Chiao Tung University", "交通大学", "Asia", "Taiwan", "Hsinchu", None, "university", None, "https://www.nctu.edu.tw", None, None, None),
    
    # 香港大学 (3所)
    (11399, "The University of Hong Kong", "香港大学", "Asia", "Hong Kong", "Hong Kong", None, "university", None, "https://www.hku.hk", None, None, None),
    (11400, "Chinese University of Hong Kong", "香港中文大学", "Asia", "Hong Kong", "Hong Kong", None, "university", None, "https://www.cuhk.edu.hk", None, None, None),
    (11401, "Hong Kong University of Science and Technology", "香港科技大学", "Asia", "Hong Kong", "Hong Kong", None, "university", None, "https://www.hkust.edu.hk", None, None, None),
    
    # 澳门大学 (2所)
    (11402, "University of Macau", "澳门大学", "Asia", "Macau", "Macau", None, "university", None, "https://www.um.edu.mo", None, None, None),
    (11403, "Macau University of Science and Technology", "澳门科技大学", "Asia", "Macau", "Macau", None, "university", None, "https://www.must.edu.mo", None, None, None),
    
    # 日本大学 (3所)
    (11404, "Osaka University", "大阪大学", "Asia", "Japan", "Osaka", None, "university", None, "https://www.osaka-u.ac.jp", None, None, None),
    (11405, "Tohoku University", "东北大学", "Asia", "Japan", "Sendai", None, "university", None, "https://www.tohoku.ac.jp", None, None, None),
    (11406, "Nagoya University", "名古屋大学", "Asia", "Japan", "Nagoya", None, "university", None, "https://www.nagoya-u.ac.jp", None, None, None),
    
    # 韩国大学 (3所)
    (11407, "Yonsei University", "延世大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.yonsei.ac.kr", None, None, None),
    (11408, "Korea University", "高丽大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.korea.ac.kr", None, None, None),
    (11409, "Sungkyunkwan University", "成均馆大学", "Asia", "South Korea", "Seoul", None, "university", None, "https://www.skku.edu", None, None, None),
    
    # 新加坡大学 (2所)
    (11410, "Singapore Management University", "新加坡管理大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.smu.edu.sg", None, None, None),
    (11411, "Singapore University of Technology and Design", "新加坡科技设计大学", "Asia", "Singapore", "Singapore", None, "university", None, "https://www.sutd.edu.sg", None, None, None),
    
    # 马来西亚大学 (2所)
    (11412, "Multimedia University", "多媒体大学", "Asia", "Malaysia", "Cyberjaya", None, "university", None, "https://www.mmu.edu.my", None, None, None),
    (11413, "International Islamic University Malaysia", "马来西亚国际伊斯兰大学", "Asia", "Malaysia", "Kuala Lumpur", None, "university", None, "https://www.iium.edu.my", None, None, None),
]

# 插入数据
added_count = 0
for school in schools_batch_55:
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

print(f"\n🎉 Batch 55 完成!")
print(f"   本批添加: {added_count}/21 所学校")
print(f"   亚洲学校总数: {asia_count} 所")
print(f"   数据库总数: {total_count} 所")

conn.close()
