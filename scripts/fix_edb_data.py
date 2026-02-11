#!/usr/bin/env python3
"""
重新解析EDB HTML并修复数据
"""

import sqlite3
import re
from datetime import datetime

def parse_school_block(block):
    """解析单个学校块"""
    school = {}
    
    # 提取英文名称
    name_match = re.search(r'<tr><td colspan="2" class="bodytxt">([A-Z][A-Za-z\s\.\,\'\(\)\&\-]+)</td></tr>', block)
    if name_match:
        school['name'] = name_match.group(1).strip()
    
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
    
    # 提取校长 (多行匹配)
    principal_match = re.search(r'Head of School 校長:\s*<br>\s*([^\n<]+)', block)
    if principal_match:
        school['principal'] = principal_match.group(1).strip()
    
    # 提取校监 (多行匹配)
    supervisor_match = re.search(r'Chairman of SMC<br>學校管理委員會主席:<br>\s*([^\n<]+)', block)
    if supervisor_match:
        school['supervisor'] = supervisor_match.group(1).strip()
    
    # 提取性别 (在表格后面的文本)
    gender_match = re.search(r'</table>\s*(GIRLS|CO-ED|BOYS)', block)
    if gender_match:
        gender = gender_match.group(1)
        if gender == 'GIRLS':
            school['gender'] = 'GIRLS'
        elif gender == 'BOYS':
            school['gender'] = 'BOYS'
        else:
            school['gender'] = 'CO-ED'
    else:
        # 检查中文
        if '女' in block:
            school['gender'] = 'GIRLS'
        elif '男' in block:
            school['gender'] = 'BOYS'
        else:
            school['gender'] = 'CO-ED'
    
    return school

def fix_and_import(filepath, district_en):
    """修复数据并导入"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按学校编号分割
    split_pattern = r'(School No\./Location ID:\s*[^\s<]+\s*/\s*\d+.*?)(?=School No\./Location ID:\s*[^\s<]+\s*/\s*\d+|$)'
    blocks = re.findall(split_pattern, content, re.DOTALL)
    
    # 提取所有名称
    name_pattern = r'<tr><td colspan="2" class="bodytxt">([A-Z][A-Za-z\s\.\,\'\(\)\&\-]+)</td></tr>'
    names = re.findall(name_pattern, content)
    
    schools = []
    for i, block in enumerate(blocks):
        if i < len(names):
            school = parse_school_block(block)
            school['name'] = names[i].strip()
            if school.get('name') and school.get('school_code'):
                schools.append(school)
    
    # 导入到数据库
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    fixed = 0
    
    for school in schools:
        # 确定办学类型
        finance_type = 'Aided'
        name_lower = school.get('name', '').lower()
        if 'government' in name_lower:
            finance_type = 'Government'
        elif 'direct' in name_lower:
            finance_type = 'Direct'
        elif 'private' in name_lower:
            finance_type = 'Private'
        
        # 更新记录
        cursor.execute("""
            UPDATE schools SET
                phone = ?, fax = ?, supervisor = ?, principal = ?,
                school_code = ?, gender = ?, finance_type = ?, 
                source = 'edb', updated_at = ?
            WHERE name = ? AND district = ?
        """, (
            school.get('phone', ''), school.get('fax', ''),
            school.get('supervisor', ''), school.get('principal', ''),
            school.get('school_code', ''), school.get('gender', ''),
            finance_type, now, school['name'], district_en
        ))
        if cursor.rowcount > 0:
            fixed += 1
    
    conn.commit()
    conn.close()
    
    return len(schools), fixed

def main():
    """主函数"""
    print("=" * 70)
    print("修复EDB数据 (校长/校监/性别)")
    print("=" * 70)
    
    districts = {
        'test_hke.html': 'Eastern',
    }
    
    for filepath, district_en in districts.items():
        if not filepath.startswith('/'):
            filepath = f"/tmp/{filepath}"
        
        print(f"\n处理: {filepath}")
        
        total, fixed = fix_and_import(filepath, district_en)
        print(f"  解析: {total} 所")
        print(f"  修复: {fixed} 条记录")

if __name__ == '__main__':
    main()
