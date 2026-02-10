#!/usr/bin/env python3
"""
香港教育局学校数据导入脚本
处理已抓取的区域数据
"""

import sqlite3
import json
from datetime import datetime
import re

def parse_school_data(raw_text):
    """解析原始抓取的网页数据"""
    schools = []
    
    # 解析学校数据
    pattern = r"(\d+)\s+([A-Z][A-Z\s&'()-]+?)\s*\n\s*\n\s*([\s\S]*?)School No\./Location ID:\s*([^/]+)/(\d+)"
    
    return schools

def import_district_data(district_name, schools_data):
    """导入区域数据到数据库"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    added = 0
    updated = 0
    
    for school in schools_data:
        # 检查是否已存在
        cursor.execute("SELECT id FROM schools WHERE name = ? AND district = ?", 
                     (school['name'], school.get('district', '')))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE schools SET
                    name_cn = ?, address = ?, phone = ?, fax = ?,
                    supervisor = ?, principal = ?, gender = ?, level = ?,
                    finance_type = ?, district = ?, school_code = ?,
                    source = 'edb', updated_at = ?
                WHERE id = ?
            """, (
                school['name_cn'], school['address'], school.get('phone', ''), school.get('fax', ''),
                school.get('supervisor', ''), school.get('principal', ''),
                school.get('gender', ''), school.get('level', 'middle'),
                school.get('finance_type', ''), school.get('district', district_name),
                school.get('school_code', ''), now, existing[0]
            ))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO schools (
                    name, name_cn, region, country, city, address,
                    phone, fax, supervisor, principal, gender, level,
                    finance_type, district, school_code, source,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                school['name'], school.get('name_cn', ''), 'Hong Kong', 'China', 'Hong Kong',
                school.get('address', ''), school.get('phone', ''), school.get('fax', ''),
                school.get('supervisor', ''), school.get('principal', ''),
                school.get('gender', ''), school.get('level', 'middle'),
                school.get('finance_type', ''), school.get('district', district_name),
                school.get('school_code', ''), 'edb', now, now
            ))
            added += 1
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source = 'edb'")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"{district_name}: 新增 {added}, 更新 {updated}, EDB总计 {total}")
    return added + updated

def main():
    """主函数"""
    print("=" * 60)
    print("香港教育局学校数据导入")
    print("=" * 60)
    
    # 这里处理已抓取的数据
    # 实际使用时，需要解析网页抓取的原始数据
    
    print("\n等待数据抓取完成...")
    print("请稍后使用导入脚本处理已收集的区域数据")

if __name__ == '__main__':
    main()
