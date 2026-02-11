#!/usr/bin/env python3
"""
完整重新解析EDB HTML，提取所有字段
"""

import sqlite3
import re
from datetime import datetime
import os

def parse_school_block_v2(block):
    """完整解析学校块"""
    school = {}
    
    # 1. 提取英文名称
    eng_name_match = re.search(r'<tr><td colspan="2" class="bodytxt">([A-Z][A-Za-z\s\.\,\'\(\)\&\-]+)</td></tr>', block)
    if eng_name_match:
        school['name'] = eng_name_match.group(1).strip()
    
    # 2. 提取学校编号
    code_match = re.search(r'School No\./Location ID:\s*([^\s<]+)\s*/\s*(\d+)', block)
    if code_match:
        school['school_code'] = f"{code_match.group(1)} / {code_match.group(2)}"
    
    # 3. 提取电话
    phone_match = re.search(r'Tel\. 電話:\s*<br>\s*([\d\s\-]+)', block)
    if phone_match:
        school['phone'] = phone_match.group(1).strip()
    
    # 4. 提取传真
    fax_match = re.search(r'Fax 傳真:\s*<br>\s*([\d\s\-]+)', block)
    if fax_match:
        school['fax'] = fax_match.group(1).strip()
    
    # 5. 提取中文名称 (在英文名后面的<tr>)
    eng_name = school.get('name', '')
    if eng_name:
        # 找到英文名位置，然后找后面的中文名
        eng_pos = block.find(f'>{eng_name}<')
        if eng_pos > 0:
            # 在英文名后面找中文
            cn_part = block[eng_pos+len(eng_name)+2:]
            cn_match = re.search(r'<tr><td colspan="2" class="bodytxt">([^\<\n]+)</td></tr>', cn_part[:200])
            if cn_match:
                cn_text = cn_match.group(1).strip()
                if re.search(r'[\u4e00-\u9fff]', cn_text):
                    school['name_cn'] = cn_text
    
    # 6. 提取中文地址
    if school.get('name_cn'):
        cn_pos = block.find(school['name_cn'])
        if cn_pos > 0:
            addr_part = block[cn_pos+len(school['name_cn'])+2:]
            addr_match = re.search(r'<tr><td width="5%">&nbsp;</td>\s*<td class="bodytxt">([^<]+)</td></tr>', addr_part[:150])
            if addr_match:
                school['address_cn'] = addr_match.group(1).strip().replace('&nbsp;', ' ')
    
    # 7. 提取校长 (多行)
    principal_match = re.search(r'Head of School 校長:\s*<br>\s*([^\n<]+)', block)
    if principal_match:
        school['principal'] = principal_match.group(1).strip()
    
    # 8. 提取校监
    supervisor_match = re.search(r'Chairman of SMC<br>學校管理委員會主席:\s*<br>\s*([^\n<]+)', block)
    if supervisor_match:
        school['supervisor'] = supervisor_match.group(1).strip()
    
    # 9. 提取官网
    website_match = re.search(r'>Website 網址</td>\s*<td[^>]*>:?</td>\s*<td[^>]*>.*?<a[^>]*href="([^"]+)"', block)
    if website_match:
        school['website'] = website_match.group(1).strip()
    else:
        # 备用模式
        website_match = re.search(r'<a href="(http[^"]+)"[^>]*>http', block)
        if website_match:
            school['website'] = website_match.group(1).strip()
    
    # 10. 提取性别
    gender_match = re.search(r'</table>\s*(GIRLS|CO-ED|BOYS)', block)
    if gender_match:
        school['gender'] = gender_match.group(1)
    elif 'GIRLS' in block or '女' in block:
        school['gender'] = 'GIRLS'
    elif 'BOYS' in block or '男' in block:
        school['gender'] = 'BOYS'
    else:
        school['gender'] = 'CO-ED'
    
    # 11. 确定办学类型
    name_lower = school.get('name', '').lower()
    if 'government' in name_lower:
        school['finance_type'] = 'Government'
    elif 'direct' in name_lower:
        school['finance_type'] = 'Direct'
    elif 'private' in name_lower:
        school['finance_type'] = 'Private'
    else:
        school['finance_type'] = 'Aided'
    
    return school

def process_file(filepath, district_en):
    """处理单个HTML文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按学校编号分割
    split_pattern = r'(School No\./Location ID:\s*[^\s<]+\s*/\s*\d+.*?)(?=School No\./Location ID:\s*[^\s<]+\s*/\s*\d+|$)'
    blocks = re.findall(split_pattern, content, re.DOTALL)
    
    # 提取所有英文名称
    eng_pattern = r'<tr><td colspan="2" class="bodytxt">([A-Z][A-Za-z\s\.\,\'\(\)\&\-]+)</td></tr>'
    eng_names = re.findall(eng_pattern, content)
    
    schools = []
    for i, block in enumerate(blocks):
        if i < len(eng_names):
            school = parse_school_block_v2(block)
            school['name'] = eng_names[i].strip()
            if school.get('name') and school.get('school_code'):
                schools.append(school)
    
    return schools

def import_to_db(district_en, schools):
    """导入学校数据"""
    if not schools:
        return 0, 0
    
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    updated = 0
    
    for school in schools:
        # 构建更新语句
        cursor.execute("""
            UPDATE schools SET
                name_cn = ?, address = ?, phone = ?, fax = ?,
                supervisor = ?, principal = ?, school_code = ?,
                gender = ?, finance_type = ?, website = ?,
                source = 'edb', updated_at = ?
            WHERE name = ? AND district = ?
        """, (
            school.get('name_cn', ''),
            school.get('address_cn', ''),
            school.get('phone', ''),
            school.get('fax', ''),
            school.get('supervisor', ''),
            school.get('principal', ''),
            school.get('school_code', ''),
            school.get('gender', ''),
            school.get('finance_type', ''),
            school.get('website', ''),
            now,
            school['name'],
            district_en
        ))
        if cursor.rowcount > 0:
            updated += 1
    
    conn.commit()
    conn.close()
    
    return len(schools), updated

def main():
    """主函数"""
    print("=" * 70)
    print("完整重新解析EDB数据")
    print("=" * 70)
    
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
    
    total_schools = 0
    total_updated = 0
    
    for html_file, district_en in districts.items():
        filepath = f"/tmp/edb_{html_file}"
        
        if not os.path.exists(filepath):
            print(f"\n跳过: {html_file} (文件不存在)")
            continue
        
        print(f"\n处理: {html_file} ({district_en})")
        
        schools = process_file(filepath, district_en)
        _, updated = import_to_db(district_en, schools)
        
        total_schools += len(schools)
        total_updated += updated
        
        # 显示样本
        if schools:
            s = schools[0]
            print(f"  样本: {s.get('name', '?')}")
            print(f"    中文: {s.get('name_cn', '?')[:30]}")
            print(f"    电话: {s.get('phone', '?')}")
            print(f"    校长: {s.get('principal', '?')[:20]}")
            print(f"    官网: {s.get('website', '?')[:40]}")
    
    print(f"\n{'='*70}")
    print(f"完成! 处理 {total_schools} 所, 更新 {total_updated} 条")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
