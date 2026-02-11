#!/usr/bin/env python3
"""
正确解析学校类型 - 基于区域标题
"""

import sqlite3
import re
from datetime import datetime

def extract_schools(filepath, district_en):
    """提取学校数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    schools = []
    
    # 定义区域标题模式（按优先级排序）
    # 越具体的标题应该越靠前
    title_patterns = [
        (r'GOVERNMENT SECONDARY SCHOOLS', 'middle'),
        (r'AIDED SECONDARY SCHOOLS', 'middle'),
        (r'DIRECT SUBSIDY SCHEME SECONDARY SCHOOLS', 'middle'),
        (r'PRIVATE SECONDARY SCHOOLS', 'middle'),
        (r'GOVERNMENT PRIMARY SCHOOLS', 'primary'),
        (r'AIDED PRIMARY SCHOOLS', 'primary'),
        (r'DIRECT SUBSIDY SCHEME PRIMARY SCHOOLS', 'primary'),
        (r'PRIVATE PRIMARY SCHOOLS', 'primary'),
        (r'KINDERGARTENS?', 'kindergarten'),
    ]
    
    # 找到每个学校编号
    school_pattern = r'School No\./Location ID:\s*([^\s<]+)\s*/\s*(\d+)'
    
    for match in re.finditer(school_pattern, content):
        school = {}
        
        school['school_code'] = f"{match.group(1)} / {match.group(2)}"
        school_pos = match.start()
        
        # 找到学校块
        block_start = content.rfind('<td align="center" class="bodytxt" rowspan=2>', 0, school_pos)
        if block_start == -1:
            continue
        
        block_end = content.find('</tr>', school_pos)
        if block_end == -1:
            continue
        
        full_block = content[block_start:block_end + 5]
        
        # 提取英文名称
        eng_match = re.search(r'<tr><td colspan="2" class="bodytxt">([A-Z][A-Za-z0-9\s\.\,\'\(\)\&\-]+)</td></tr>', full_block)
        if not eng_match:
            continue
        
        school['name'] = eng_match.group(1).strip()
        
        # 提取中文名称
        cn_match = re.search(r'<tr><td colspan="2" class="bodytxt">([^\x00-\x7F]+)</td></tr>', full_block)
        if cn_match:
            school['name_cn'] = cn_match.group(1).strip()
        
        # 提取电话
        phone_match = re.search(r'Tel\. 電話:\s*<br>\s*([\d\s\-]+)', full_block)
        if phone_match:
            school['phone'] = phone_match.group(1).strip()
        
        # 提取传真
        fax_match = re.search(r'Fax 傳真:\s*<br>\s*([\d\s\-]+)', full_block)
        if fax_match:
            school['fax'] = fax_match.group(1).strip()
        
        # 提取英文地址
        addr_match = re.search(r'<tr><td width="5%">&nbsp;</td>\s*<td class="bodytxt">([^<]+)</td></tr>', full_block)
        if addr_match:
            school['address'] = addr_match.group(1).strip().replace('&nbsp;', ' ')
        
        # 提取校长
        principal_match = re.search(r'Head of School 校長:\s*<br>\s*([^\n<]+)', full_block)
        if principal_match:
            school['principal'] = principal_match.group(1).strip()
        
        # 提取校监
        supervisor_match = re.search(r'Chairman of SMC<br>學校管理委員會主席:\s*<br>\s*([^\n<]+)', full_block)
        if supervisor_match:
            school['supervisor'] = supervisor_match.group(1).strip()
        
        # 提取官网
        website_match = re.search(r'<a href="(http[^"]+)"[^>]*>http', full_block)
        if website_match:
            school['website'] = website_match.group(1).strip()
        
        # 提取性别
        if 'GIRLS' in full_block or '女' in full_block:
            school['gender'] = 'GIRLS'
        elif 'BOYS' in full_block or '男' in full_block:
            school['gender'] = 'BOYS'
        else:
            school['gender'] = 'CO-ED'
        
        # 确定办学类型
        name_lower = school.get('name', '').lower()
        if 'government' in name_lower:
            school['finance_type'] = 'Government'
        elif 'direct' in name_lower:
            school['finance_type'] = 'Direct'
        elif 'private' in name_lower:
            school['finance_type'] = 'Private'
        else:
            school['finance_type'] = 'Aided'
        
        # 确定学校级别 - 找到最近的上方区域标题
        before = content[:school_pos]
        school_level = 'middle'  # 默认
        closest_dist = float('inf')
        
        for pattern, level in title_patterns:
            title_pos = before.rfind(pattern)
            if title_pos != -1:
                dist = school_pos - title_pos
                if dist < closest_dist:
                    closest_dist = dist
                    school_level = level
        
        school['level'] = school_level
        
        schools.append(school)
    
    return schools

def import_to_db(district_en, schools):
    """导入数据库"""
    if not schools:
        return 0, 0
    
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    updated = 0
    
    # 统计级别
    levels = {}
    
    for school in schools:
        lvl = school.get('level', 'middle')
        levels[lvl] = levels.get(lvl, 0) + 1
        
        cursor.execute("""
            UPDATE schools SET
                name_cn = ?, address = ?, phone = ?, fax = ?,
                supervisor = ?, principal = ?, school_code = ?,
                gender = ?, finance_type = ?, website = ?, level = ?,
                source = 'edb', updated_at = ?
            WHERE name = ? AND district = ?
        """, (
            school.get('name_cn', ''),
            school.get('address', ''),
            school.get('phone', ''),
            school.get('fax', ''),
            school.get('supervisor', ''),
            school.get('principal', ''),
            school.get('school_code', ''),
            school.get('gender', ''),
            school.get('finance_type', ''),
            school.get('website', ''),
            lvl,
            now,
            school['name'],
            district_en
        ))
        if cursor.rowcount > 0:
            updated += 1
    
    conn.commit()
    conn.close()
    
    return len(schools), updated, levels

# 测试
print("=" * 70)
print("测试中西区解析")
print("=" * 70)

schools = extract_schools('/tmp/edb_cw_test.html', 'Central & Western')

levels = {}
for s in schools:
    lvl = s.get('level', 'unknown')
    levels[lvl] = levels.get(lvl, 0) + 1

print(f"\n中西区学校级别分布:")
for lvl, cnt in sorted(levels.items()):
    print(f"  {lvl}: {cnt}")

print("\n各级别样本:")
for lvl in ['middle', 'primary', 'kindergarten']:
    if lvl in levels:
        print(f"\n{lvl}:")
        for s in schools:
            if s.get('level') == lvl:
                print(f"  - {s.get('name', '?')[:40]}")
                if sum(1 for x in schools if x.get('level') == lvl) <= 5:
                    break
PYEOF