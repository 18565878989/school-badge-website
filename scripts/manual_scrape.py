#!/usr/bin/env python3
"""
从学校官网手动抓取数据
你需要在Chrome浏览器中手动打开每个学校官网
然后复制页面中的信息
"""

import sqlite3
import json

def export_missing_schools():
    """导出需要补充数据的学校"""
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 获取有官网但缺失数据的中学
    c.execute("""
        SELECT id, name, name_cn, website, motto, address, principal
        FROM schools 
        WHERE region = 'Hong Kong' 
        AND level = 'middle'
        AND website IS NOT NULL 
        AND website != ''
        AND website LIKE 'http%'
        ORDER BY name_cn
    """)
    
    schools = []
    for row in c.fetchall():
        schools.append({
            'id': row[0],
            'name': row[1],
            'name_cn': row[2],
            'website': row[3],
            'motto': row[4] or '',
            'address': row[5] or '',
            'principal': row[6] or ''
        })
    
    conn.close()
    
    # 保存到JSON
    with open('scripts/supplement/manual_scrape.json', 'w', encoding='utf-8') as f:
        json.dump(schools, f, ensure_ascii=False, indent=2)
    
    print(f"导出 {len(schools)} 所学校到 scripts/supplement/manual_scrape.json")
    print("\n使用说明:")
    print("1. 在Chrome中打开 https://www.school106.edu.hk")
    print("2. 查找页面中的校训、校长、地址信息")
    print("3. 将信息填入CSV文件")
    print("4. 运行 python scripts/supplement_data.py import missing_manual.csv")
    
    return schools

def import_manual_data(csv_file):
    """从CSV导入手动补充的数据"""
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    updated = 0
    
    # 读取CSV
    import csv
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            school_id = row.get('ID')
            if not school_id:
                continue
            
            updates = []
            params = []
            
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
    
    print(f"更新 {updated} 所学校的数据")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'export':
            export_missing_schools()
        elif command == 'import' and len(sys.argv) > 2:
            import_manual_data(sys.argv[2])
    else:
        export_missing_schools()
