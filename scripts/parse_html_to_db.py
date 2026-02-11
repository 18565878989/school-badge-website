#!/usr/bin/env python3
"""
完整解析EDB HTML文件并导入学校数据
"""

import sqlite3
import re
from datetime import datetime
import os

def parse_school_block(block, name):
    """解析单个学校块"""
    school = {'name': name}
    
    # 提取学校编号
    code_match = re.search(r'School No\./Location ID:\s*([^\s<]+)\s*/\s*(\d+)', block)
    if code_match:
        school['school_code'] = f"{code_match.group(1)} / {code_match.group(2)}"
    
    # 提取电话
    phone_match = re.search(r'Tel\. 電話:\s*<br>\s*([\d\s\-]+)', block)
    if phone_match:
        school['phone'] = phone_match.group(1).strip()
    
    # 提取传真
    fax_match = re.search(r'Fax 傳真:\s*<br>\s*([\d\s\-]+)', block)
    if fax_match:
        school['fax'] = fax_match.group(1).strip()
    
    # 提取校长
    principal_match = re.search(r'Head of School 校長:\s*<br>([^<\n]+)', block)
    if principal_match:
        school['principal'] = principal_match.group(1).strip()
    
    # 提取校监
    supervisor_match = re.search(r'Chairman of SMC<br>學校管理委員會主席:<br>([^<\n]+)', block)
    if supervisor_match:
        school['supervisor'] = supervisor_match.group(1).strip()
    
    # 提取性别
    if 'GIRLS' in block or '女' in block:
        school['gender'] = 'GIRLS'
    elif 'BOYS' in block or '男' in block:
        school['gender'] = 'BOYS'
    else:
        school['gender'] = 'CO-ED'
    
    return school

def process_file(filepath, district_en):
    """处理单个HTML文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有学校名称
    name_pattern = r'<tr><td colspan="2" class="bodytxt">([A-Z][A-Za-z\s\.\,\'\(\)\&\-]+)</td></tr>'
    names = re.findall(name_pattern, content)
    
    # 按学校编号分割内容
    split_pattern = r'(School No\./Location ID:\s*[^\s<]+\s*/\s*\d+.*?)(?=School No\./Location ID:\s*[^\s<]+\s*/\s*\d+|$)'
    blocks = re.findall(split_pattern, content, re.DOTALL)
    
    schools = []
    for i, block in enumerate(blocks):
        if i < len(names):
            school = parse_school_block(block, names[i].strip())
            if school.get('name') and school.get('school_code'):
                schools.append(school)
    
    return schools

def import_to_db(district_en, schools):
    """导入学校到数据库"""
    if not schools:
        return 0, 0
    
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0
    
    for school in schools:
        name = school.get('name', '').strip()
        if not name:
            continue
        
        # 确定办学类型
        finance_type = 'Aided'
        name_lower = name.lower()
        if 'government' in name_lower:
            finance_type = 'Government'
        elif 'direct' in name_lower:
            finance_type = 'Direct'
        elif 'private' in name_lower:
            finance_type = 'Private'
        
        # 检查是否已存在
        cursor.execute("SELECT id FROM schools WHERE name = ? AND district = ?", 
                     (name, district_en))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE schools SET
                    phone = ?, fax = ?, supervisor = ?, principal = ?,
                    school_code = ?, gender = ?, finance_type = ?, 
                    source = 'edb', updated_at = ?
                WHERE id = ?
            """, (
                school.get('phone', ''), school.get('fax', ''),
                school.get('supervisor', ''), school.get('principal', ''),
                school.get('school_code', ''), school.get('gender', ''),
                finance_type, now, existing[0]
            ))
            updated += 1
        else:
            # 确定学校级别
            level = 'middle'
            if 'primary' in name_lower:
                level = 'primary'
            elif 'kindergarten' in name_lower:
                level = 'kindergarten'
            
            cursor.execute("""
                INSERT INTO schools (
                    name, region, country, city, phone, fax,
                    supervisor, principal, gender, level, finance_type, district,
                    school_code, source, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, 'Hong Kong', 'China', 'Hong Kong',
                school.get('phone', ''), school.get('fax', ''),
                school.get('supervisor', ''), school.get('principal', ''),
                school.get('gender', ''), level, finance_type, district_en,
                school.get('school_code', ''), 'edb', now, now
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    return inserted, updated

def main():
    """主函数"""
    print("=" * 70)
    print("解析EDB HTML文件并导入学校数据")
    print("=" * 70)
    
    # 区域映射
    districts = {
        'school-list-cw.html': 'Central & Western',
        'school-list-hke.html': 'Eastern',
        'school-list-i.html': 'Islands',
        'school-list-kc.html': 'Kowloon City',
        'school-list-kt.html': 'Kwun Tong',
        'school-list-kwt.html': 'Kwai Tsing',
        'school-list-n.html': 'Northern',
        'school-list-sk.html': 'Sai Kung',
        'school-list-sou.html': 'Southern',
        'school-list-ssp.html': 'Sham Shui Po',
        'school-list-st.html': 'Sha Tin',
        'school-list-tm.html': 'Tuen Mun',
        'school-list-tp.html': 'Tai Po',
        'school-list-tw.html': 'Tsuen Wan',
        'school-list-wch.html': 'Wan Chai',
        'school-list-wts.html': 'Wong Tai Sin',
        'school-list-yl.html': 'Yuen Long',
        'school-list-ytm.html': 'Yau Tsim Mong',
    }
    
    total_inserted = 0
    total_updated = 0
    
    for html_file, district_en in districts.items():
        filepath = f"/tmp/edb_{html_file}"
        
        if not os.path.exists(filepath):
            print(f"\n跳过: {html_file} (文件不存在)")
            continue
        
        print(f"\n{'='*70}")
        print(f"处理: {html_file} ({district_en})")
        print(f"{'='*70}")
        
        schools = process_file(filepath, district_en)
        print(f"解析到 {len(schools)} 所学校")
        
        # 显示前2所
        for s in schools[:2]:
            print(f"  - {s.get('name', '?')} ({s.get('gender', '?')})")
        
        if schools:
            inserted, updated = import_to_db(district_en, schools)
            total_inserted += inserted
            total_updated += updated
            print(f"导入: {inserted} 新增, {updated} 更新")
    
    print(f"\n{'='*70}")
    print(f"完成! 总共新增 {total_inserted}, 更新 {total_updated}")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
