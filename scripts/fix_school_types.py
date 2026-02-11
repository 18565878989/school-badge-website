#!/usr/bin/env python3
"""
正确解析EDB HTML，根据表格标题确定学校类型
"""

import sqlite3
import re
from datetime import datetime
import os

def get_school_level(content, position):
    """根据位置确定学校类型"""
    # 定义类型标题和优先级（从后往前找，找到最近的）
    patterns = [
        (r'GOVERNMENT SECONDARY SCHOOLS', 'middle'),
        (r'GOVERNMENT PRIMARY SCHOOLS', 'primary'),
        (r'GOVERNMENT PRIMARY', 'primary'),
        (r'AIDED SECONDARY SCHOOLS', 'middle'),
        (r'AIDED PRIMARY SCHOOLS', 'primary'),
        (r'AIDED PRIMARY', 'primary'),
        (r'DIRECT SUBSIDY SCHEME SECONDARY SCHOOLS', 'middle'),
        (r'DIRECT SUBSIDY SCHEME PRIMARY SCHOOLS', 'primary'),
        (r'PRIVATE SECONDARY SCHOOLS', 'middle'),
        (r'PRIVATE PRIMARY SCHOOLS', 'primary'),
        (r'KINDERGARTENS', 'kindergarten'),
        (r'PRIMARY SCHOOLS', 'primary'),
        (r'SECONDARY SCHOOLS', 'middle'),
    ]
    
    # 向前搜索最近的类型标题
    for pattern, level in patterns:
        pos = content.rfind(pattern, 0, position)
        if pos != -1:
            return level
    
    return 'middle'  # 默认中学

def extract_schools_by_type(content):
    """按类型提取所有学校"""
    schools = []
    
    # 学校块模式
    pattern = r'<td align="center" class="bodytxt" rowspan=2>\d+\s*<br><br><br>.*?(?=<td align="center" class="bodytxt" rowspan=2>\d+|$)'
    blocks = re.findall(pattern, content, re.DOTALL)
    
    for block in blocks:
        school = {}
        
        # 提取英文名称
        eng_match = re.search(r'<tr><td colspan="2" class="bodytxt">([A-Z][A-Za-z0-9\s\.\,\'\(\)\&\-]+)</td></tr>', block)
        if eng_match:
            school['name'] = eng_match.group(1).strip()
        
        # 提取中文名称
        cn_match = re.search(r'<tr><td colspan="2" class="bodytxt">([^\x00-\x7F]+)</td></tr>', block)
        if cn_match:
            school['name_cn'] = cn_match.group(1).strip()
        
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
        
        # 提取英文地址
        addr_match = re.search(r'<tr><td width="5%">&nbsp;</td>\s*<td class="bodytxt">([^<]+)</td></tr>', block)
        if addr_match:
            school['address'] = addr_match.group(1).strip().replace('&nbsp;', ' ')
        
        # 提取校长
        principal_match = re.search(r'Head of School 校長:\s*<br>\s*([^\n<]+)', block)
        if principal_match:
            school['principal'] = principal_match.group(1).strip()
        
        # 提取校监
        supervisor_match = re.search(r'Chairman of SMC<br>學校管理委員會主席:\s*<br>\s*([^\n<]+)', block)
        if supervisor_match:
            school['supervisor'] = supervisor_match.group(1).strip()
        
        # 提取官网
        website_match = re.search(r'<a href="(http[^"]+)"[^>]*>http', block)
        if website_match:
            school['website'] = website_match.group(1).strip()
        
        # 提取性别
        if 'GIRLS' in block or '女' in block:
            school['gender'] = 'GIRLS'
        elif 'BOYS' in block or '男' in block:
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
        
        # 根据HTML位置确定学校级别
        if school.get('name') and school.get('school_code'):
            # 在content中找到这个学校块的位置
            school_pos = content.find(school['name'])
            if school_pos != -1:
                school['level'] = get_school_level(content, school_pos)
            else:
                school['level'] = 'middle'
            
            schools.append(school)
    
    return schools

def process_file(filepath, district_en):
    """处理单个HTML文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    schools = extract_schools_by_type(content)
    
    # 按级别统计
    levels = {}
    for s in schools:
        lvl = s.get('level', 'unknown')
        levels[lvl] = levels.get(lvl, 0) + 1
    
    print(f"  {district_en}: 共{len(schools)}所", end="")
    for lvl, cnt in levels.items():
        print(f", {lvl}: {cnt}", end="")
    print()
    
    return schools

def import_to_db(district_en, schools):
    """导入学校数据"""
    if not schools:
        return 0
    
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    updated = 0
    
    for school in schools:
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
            school.get('level', 'middle'),
            now,
            school['name'],
            district_en
        ))
        if cursor.rowcount > 0:
            updated += 1
    
    conn.commit()
    conn.close()
    
    return updated

def main():
    """主函数"""
    print("=" * 70)
    print("正确解析学校类型 - 根据HTML表格标题")
    print("=" * 70)
    
    districts = {
        'school-list-cw.html': 'Central & Western',
    }
    
    # 先下载并测试中西区
    import urllib.request
    
    print("\n下载并测试中西区...")
    url = "http://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-cw.html"
    with urllib.request.urlopen(url, timeout=30) as resp:
        content = resp.read().decode('utf-8')
    
    with open('/tmp/edb_cw_test.html', 'w') as f:
        f.write(content)
    
    schools = extract_schools_by_type(content)
    
    # 统计
    levels = {}
    for s in schools:
        lvl = s.get('level', 'unknown')
        levels[lvl] = levels.get(lvl, 0) + 1
    
    print(f"\n中西区学校类型分布:")
    for lvl, cnt in sorted(levels.items()):
        print(f"  {lvl}: {cnt}")
    
    print("\n样本数据:")
    for s in schools[:5]:
        print(f"  - {s.get('name', '?')[:40]} ({s.get('level', '?')})")
    
    # 验证一些有问题的学校
    print("\n验证之前有问题的学校:")
    for s in schools:
        if 'DIOCESAN' in s.get('name', '') or 'MARYKNOLL' in s.get('name', ''):
            print(f"  - {s.get('name', '?')} -> {s.get('level', '?')}")

if __name__ == '__main__':
    main()
