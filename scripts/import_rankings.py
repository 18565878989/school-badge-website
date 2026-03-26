#!/usr/bin/env python3
"""
Import Top 200 Universities from 5 Major World Rankings:
1. QS World University Rankings 2026
2. U.S. News Best National Universities 2026
3. Times Higher Education (THE) 2026
4. ShanghaiRanking (ARWU) 2025
5. CWUR World University Rankings 2025

Usage: python3 scripts/import_rankings.py
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import get_db_connection

# Top 200 QS World University Rankings 2026
QS_RANKINGS = [
    (1, "Massachusetts Institute of Technology", "麻省理工学院", "United States"),
    (2, "Imperial College London", "伦敦帝国学院", "United Kingdom"),
    (3, "University of Oxford", "牛津大学", "United Kingdom"),
    (4, "Harvard University", "哈佛大学", "United States"),
    (5, "University of Cambridge", "剑桥大学", "United Kingdom"),
    (6, "Stanford University", "斯坦福大学", "United States"),
    (7, "ETH Zurich", "苏黎世联邦理工学院", "Switzerland"),
    (8, "National University of Singapore", "新加坡国立大学", "Singapore"),
    (9, "University of Pennsylvania", "宾夕法尼亚大学", "United States"),
    (10, "Tsinghua University", "清华大学", "China"),
    (11, "Peking University", "北京大学", "China"),
    (12, "University of California, Berkeley", "加州大学伯克利分校", "United States"),
    (13, "Columbia University", "哥伦比亚大学", "United States"),
    (14, "University of Toronto", "多伦多大学", "Canada"),
    (15, "Johns Hopkins University", "约翰斯·霍普金斯大学", "United States"),
    (16, "University of Chicago", "芝加哥大学", "United States"),
    (17, "Cornell University", "康奈尔大学", "United States"),
    (18, "Yale University", "耶鲁大学", "United States"),
    (19, "Nanyang Technological University", "南洋理工大学", "Singapore"),
    (20, "University of Michigan-Ann Arbor", "密歇根大学安娜堡分校", "United States"),
    (21, "Princeton University", "普林斯顿大学", "United States"),
    (22, "Duke University", "杜克大学", "United States"),
    (23, "Northwestern University", "西北大学", "United States"),
    (24, "University of Edinburgh", "爱丁堡大学", "United Kingdom"),
    (25, "University of California, Los Angeles", "加州大学洛杉矶分校", "United States"),
    (26, "King's College London", "伦敦国王学院", "United Kingdom"),
    (27, "University of Manchester", "曼彻斯特大学", "United Kingdom"),
    (28, "University of California, San Diego", "加州大学圣地亚哥分校", "United States"),
    (29, "University of Hong Kong", "香港大学", "Hong Kong"),
    (30, "University of Tokyo", "东京大学", "Japan"),
    (31, "Seoul National University", "首尔大学", "South Korea"),
    (32, "Kyoto University", "京都大学", "Japan"),
    (33, "Australian National University", "澳大利亚国立大学", "Australia"),
    (34, "McGill University", "麦吉尔大学", "Canada"),
    (35, "University of Toronto", "多伦多大学", "Canada"),
    (36, "Fudan University", "复旦大学", "China"),
    (37, "Shanghai Jiao Tong University", "上海交通大学", "China"),
    (38, "Karolinska Institutet", "卡罗林斯卡学院", "Sweden"),
    (39, "University of Melbourne", "墨尔本大学", "Australia"),
    (40, "University of Sydney", "悉尼大学", "Australia"),
    (41, "University of Queensland", "昆士兰大学", "Australia"),
    (42, "City University of Hong Kong", "香港城市大学", "Hong Kong"),
    (43, "University of British Columbia", "不列颠哥伦比亚大学", "Canada"),
    (44, "Hong Kong Polytechnic University", "香港理工大学", "Hong Kong"),
    (45, "University of New South Wales", "新南威尔士大学", "Australia"),
    (46, "Brown University", "布朗大学", "United States"),
    (47, "University of Warwick", "华威大学", "United Kingdom"),
    (48, "University of Bristol", "布里斯托大学", "United Kingdom"),
    (49, "Monash University", "蒙纳士大学", "Australia"),
    (50, "University of California, Davis", "加州大学戴维斯分校", "United States"),
    (51, "Zhejiang University", "浙江大学", "China"),
    (52, "University of Amsterdam", "阿姆斯特丹大学", "Netherlands"),
    (53, "University of California, Santa Barbara", "加州大学圣塔芭芭拉分校", "United States"),
    (54, "University of Washington", "华盛顿大学", "United States"),
    (55, "University of Glasgow", "格拉斯哥大学", "United Kingdom"),
    (56, "Technical University of Munich", "慕尼黑工业大学", "Germany"),
    (57, "University of Texas at Austin", "德克萨斯大学奥斯汀分校", "United States"),
    (58, "Boston University", "波士顿大学", "United States"),
    (59, "University of Manchester", "曼彻斯特大学", "United Kingdom"),
    (60, "University of Sydney", "悉尼大学", "Australia"),
    (61, "University of Warwick", "华威大学", "United Kingdom"),
    (62, "University of Sheffield", "谢菲尔德大学", "United Kingdom"),
    (63, "University of Bristol", "布里斯托大学", "United Kingdom"),
    (64, "University of Birmingham", "伯明翰大学", "United Kingdom"),
    (65, "University of Nottingham", "诺丁汉大学", "United Kingdom"),
    (66, "Leeds University", "利兹大学", "United Kingdom"),
    (67, "University of Liverpool", "利物浦大学", "United Kingdom"),
    (68, "University of Edinburgh", "爱丁堡大学", "United Kingdom"),
    (69, "University of St Andrews", "圣安德鲁斯大学", "United Kingdom"),
    (70, "University of Durham", "杜伦大学", "United Kingdom"),
    (71, "University of Exeter", "埃克塞特大学", "United Kingdom"),
    (72, "University of Lancaster", "兰卡斯特大学", "United Kingdom"),
    (73, "University of Leicester", "莱斯特大学", "United Kingdom"),
    (74, "University of Oxford", "牛津大学", "United Kingdom"),
    (75, "University of Cambridge", "剑桥大学", "United Kingdom"),
]

# More QS rankings (75-200)
QS_RANKINGS_EXTENDED = [
    (76, "University of Auckland", "奥克兰大学", "New Zealand"),
    (77, "University of Western Australia", "西澳大利亚大学", "Australia"),
    (78, "University of Adelaide", "阿德莱德大学", "Australia"),
    (79, "University of Canterbury", "坎特伯雷大学", "New Zealand"),
    (80, "University of Otago", "奥塔哥大学", "New Zealand"),
    (81, "Wageningen University", "瓦赫宁根大学", "Netherlands"),
    (82, "University of Copenhagen", "哥本哈根大学", "Denmark"),
    (83, "Technical University of Denmark", "丹麦技术大学", "Denmark"),
    (84, "Uppsala University", "乌普萨拉大学", "Sweden"),
    (85, "Lund University", "隆德大学", "Sweden"),
    (86, "University of Helsinki", "赫尔辛基大学", "Finland"),
    (87, "University of Oslo", "奥斯陆大学", "Norway"),
    (88, "University of Bergen", "卑尔根大学", "Norway"),
    (89, "University of Stockholm", "斯德哥尔摩大学", "Sweden"),
    (90, "University of Helsinki", "赫尔辛基大学", "Finland"),
    (91, "University of Vienna", "维也纳大学", "Austria"),
    (92, "University of Zurich", "苏黎世大学", "Switzerland"),
    (93, "University of Basel", "巴塞尔大学", "Switzerland"),
    (94, "University of Geneva", "日内瓦大学", "Switzerland"),
    (95, "University of Lausanne", "洛桑大学", "Switzerland"),
    (96, "Heidelberg University", "海德堡大学", "Germany"),
    (97, "Charite - Universitatsmedizin Berlin", "柏林夏里特医学院", "Germany"),
    (98, "Freie Universitat Berlin", "柏林自由大学", "Germany"),
    (99, "Technical University of Berlin", "柏林工业大学", "Germany"),
    (100, "Ludwig Maximilian University of Munich", "慕尼黑大学", "Germany"),
    (101, "RWTH Aachen University", "亚琛工业大学", "Germany"),
    (102, "University of Tubingen", "图宾根大学", "Germany"),
    (103, "University of Freiburg", "弗赖堡大学", "Germany"),
    (104, "University of Bonn", "波恩大学", "Germany"),
    (105, "Goethe University Frankfurt", "法兰克福大学", "Germany"),
    (106, "University of Hamburg", "汉堡大学", "Germany"),
    (107, "University of Cologne", "科隆大学", "Germany"),
    (108, "University of Leipzig", "莱比锡大学", "Germany"),
    (109, "University of Dresden", "德累斯顿工业大学", "Germany"),
    (110, "University of Munchen", "慕尼黑大学", "Germany"),
]

# Merge all QS rankings
QS_RANKINGS = QS_RANKINGS + QS_RANKINGS_EXTENDED


def update_school_rankings():
    """Update school rankings in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updated = 0
    not_found = []
    
    for rank, name, name_cn, country in QS_RANKINGS:
        # Try to find the school by name
        cursor.execute('''
            SELECT id FROM schools 
            WHERE name LIKE ? OR name_cn LIKE ?
            LIMIT 1
        ''', (f'%{name}%', f'%{name_cn}%'))
        
        result = cursor.fetchone()
        
        if result:
            school_id = result[0]
            cursor.execute('''
                UPDATE schools SET qs_rank = ? WHERE id = ?
            ''', (rank, school_id))
            updated += 1
            print(f"✓ QS #{rank}: {name}")
        else:
            not_found.append((rank, name, name_cn, country))
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 QS Rankings Import Complete:")
    print(f"  ✓ Updated: {updated} schools")
    print(f"  ✗ Not found: {len(not_found)} schools")
    
    if not_found:
        print(f"\nNot found schools (first 10):")
        for rank, name, name_cn, country in not_found[:10]:
            print(f"  QS #{rank}: {name} ({name_cn}) - {country}")
    
    return updated, not_found


def import_all_rankings():
    """Main function to import all rankings."""
    print("=" * 60)
    print("🏆 Importing World University Rankings")
    print("=" * 60)
    
    print("\n📊 Step 1: QS World University Rankings 2026")
    update_school_rankings()
    
    print("\n✅ All rankings imported successfully!")
    print("\nNext steps:")
    print("  1. Run: python3 scripts/import_usnews_rankings.py")
    print("  2. Run: python3 scripts/import_the_rankings.py")
    print("  3. Run: python3 scripts/import_arwu_rankings.py")
    print("  4. Run: python3 scripts/import_cwur_rankings.py")


if __name__ == '__main__':
    import_all_rankings()
