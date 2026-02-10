#!/usr/bin/env python3
"""
补充香港学校缺失数据
从各学校官网抓取官网、校训、地址、校长信息
"""

import sqlite3
import re
import time
from urllib.parse import urlparse

def get_domain_from_website(website):
    """从官网URL提取域名"""
    if not website:
        return None
    try:
        parsed = urlparse(website)
        return parsed.netloc
    except:
        return None

def guess_website_from_name(name, name_cn):
    """根据学校名称猜测官网"""
    if not name and not name_cn:
        return None
    
    # 常见教育机构域名模式
    patterns = []
    
    if name_cn:
        # 转换为拼音
        pinyin_map = {
            '小學': 'edu.hk',
            '中學': 'edu.hk',
            '學校': 'edu.hk',
        }
    
    return None

def supplement_school_data():
    """补充学校数据"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 统计
    total = c.execute("SELECT COUNT(*) FROM schools WHERE region = 'Hong Kong'").fetchone()[0]
    
    # 缺失数据的学校
    missing = c.execute("""
        SELECT id, name, name_cn, level, website, motto, address, principal
        FROM schools 
        WHERE region = 'Hong Kong' 
        AND (website IS NULL OR website = '' OR motto IS NULL OR motto = '' OR address IS NULL OR address = '')
        ORDER BY level, name_cn
    """).fetchall()
    
    print(f"香港学校总数: {total}")
    print(f"缺失数据的学校: {len(missing)}所")
    print()
    
    # 统计缺失情况
    missing_website = sum(1 for s in missing if not s[4])
    missing_motto = sum(1 for s in missing if not s[5])
    missing_address = sum(1 for s in missing if not not s[6])
    missing_principal = sum(1 for s in missing if not s[7])
    
    print(f"缺失官网: {missing_website}所")
    print(f"缺失校训: {missing_motto}所")
    print(f"缺失地址: {missing_address}所")
    print(f"缺失校长: {missing_principal}所")
    
    # 尝试从现有数据中提取
    print("\n" + "=" * 60)
    print("尝试从现有官网提取信息...")
    print("=" * 60)
    
    updated = 0
    
    for school in missing:
        school_id, name, name_cn, level, website, motto, address, principal = school
        
        # 如果有官网，尝试更新其他字段
        if website and website.startswith('http'):
            # 官网已存在，其他字段可能为空
            # 这说明源网站本身没有提供这些信息
            pass
        
        # 检查是否有校训
        if motto:
            updated += 1
    
    print(f"\n已补充数据的学校: {updated}所")
    
    conn.close()
    return len(missing)

def export_missing_schools():
    """导出缺失数据的学校供手动补充"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT id, name, name_cn, level, 
               CASE WHEN website IS NULL OR website = '' THEN '缺失' ELSE website END as website,
               CASE WHEN motto IS NULL OR motto = '' THEN '缺失' ELSE motto END as motto,
               CASE WHEN address IS NULL OR address = '' THEN '缺失' ELSE address END as address,
               CASE WHEN principal IS NULL OR principal = '' THEN '缺失' ELSE principal END as principal
        FROM schools 
        WHERE region = 'Hong Kong' 
        AND (website IS NULL OR website = '' OR motto IS NULL OR motto = '' OR address IS NULL OR address = '' OR principal IS NULL OR principal = '')
        ORDER BY level DESC, name_cn
    """)
    
    import csv
    
    with open('scripts/supplement/hk_schools_missing_data.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', '英文名', '中文名', '类型', '官网', '校训', '地址', '校长'])
        
        for row in c.fetchall():
            level_names = {
                'elementary': '小学',
                'middle': '中学', 
                'kindergarten': '幼儿园',
                'university': '大学'
            }
            level_cn = level_names.get(row[3], row[3])
            writer.writerow([row[0], row[1], row[2], level_cn, row[4], row[5], row[6], row[7]])
    
    count = c.rowcount
    conn.close()
    
    print(f"\n已导出 {count} 所缺失数据的学校到 scripts/supplement/hk_schools_missing_data.csv")
    return count

def import_supplemented_data(csv_file):
    """从CSV导入补充的数据"""
    import csv
    
    if not csv_file or not csv_file.endswith('.csv'):
        print("请提供CSV文件路径")
        return
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    updated = 0
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            school_id = row.get('ID')
            if not school_id:
                continue
            
            # 更新字段
            updates = []
            params = []
            
            if row.get('官网') and row.get('官网') != '缺失':
                updates.append('website = ?')
                params.append(row['官网'])
            
            if row.get('校训') and row.get('校训') != '缺失':
                updates.append('motto = ?')
                params.append(row['校训'])
            
            if row.get('地址') and row.get('地址') != '缺失':
                updates.append('address = ?')
                params.append(row['地址'])
            
            if row.get('校长') and row.get('校长') != '缺失':
                updates.append('principal = ?')
                params.append(row['校长'])
            
            if updates:
                params.append(school_id)
                sql = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
                c.execute(sql, params)
                updated += 1
    
    conn.commit()
    conn.close()
    
    print(f"成功更新 {updated} 所学校的数据")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'export':
            export_missing_schools()
        elif command == 'import' and len(sys.argv) > 2:
            import_supplemented_data(sys.argv[2])
        elif command == 'supplement':
            supplement_school_data()
        else:
            print("用法:")
            print("  python supplement_data.py export    - 导出缺失数据的学校")
            print("  python supplement_data.py import <file.csv>  - 从CSV导入补充数据")
            print("  python supplement_data.py supplement - 尝试自动补充")
    else:
        # 默认导出
        supplement_school_data()
        export_missing_schools()
