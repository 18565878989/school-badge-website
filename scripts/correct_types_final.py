#!/usr/bin/env python3
"""
正确解析EDB HTML - 根据表格区域标题确定学校类型
"""

import sqlite3
import re
from datetime import datetime
import os

def get_section_type(content, position):
    """获取当前位置所在的区域类型"""
    # 定义区域类型（从当前位置向前找最近的标题）
    sections = [
        (r'KINDERGARTENS?', 'kindergarten'),
        (r'PRIMARY SCHOOLS?', 'primary'),
        (r'SECONDARY SCHOOLS?', 'middle'),
        (r'GOVERNMENT (?:SECONDARY|PRIMARY) SCHOOLS?', 'middle'),
        (r'AIDED (?:SECONDARY|PRIMARY) SCHOOLS?', 'middle'),
        (r'DIRECT SUBSIDY SCHEME (?:SECONDARY|PRIMARY) SCHOOLS?', 'middle'),
        (r'PRIVATE (?:SECONDARY|PRIMARY) SCHOOLS?', 'middle'),
    ]
    
    for pattern, section_type in sections:
        matches = list(re.finditer(pattern, content[:position]))
        if matches:
            return section_type, matches[-1].start()
    
    return 'middle', position

def extract_schools_with_types(filepath, district_en):
    """提取所有学校并正确确定类型"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    schools = []
    
    # 方法：找到每个School No的位置，然后向前找区域类型
    pattern = r'School No\./Location ID:\s*([^\s<]+)\s*/\s*(\d+)'
    
    for match in re.finditer(pattern, content):
        school = {}
        
        # 学校编号
        school['school_code'] = f"{match.group(1)} / {match.group(2)}"
        school_pos = match.start()
        
        # 找到这个学校块的完整内容（从School No向前找到一个学校块）
        # 学校块的起始标记是 rowspan=2>
        block_start = content.rfind('<td align="center" class="bodytxt" rowspan=2>', 0, school_pos)
        if block_start == -1:
            continue
        
        block_end = content.find('</tr>', school_pos)
        if block_end == -1:
            continue
        
        # 扩展块范围（包含更多信息）
        full_block = content[block_start:block_end + 5]
        
        # 提取英文名称
        eng_match = re.search(r'<tr><td colspan="2" class="bodytxt">([A-Z][A-Za-z0-9\s\.\,\'\(\)\&\-]+)</td></tr>', full_block)
        if eng_match:
            school['name'] = eng_match.group(1).strip()
        else:
            continue
        
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
        
        # 根据区域类型确定学校级别
        section_type, _ = get_section_type(content, school_pos)
        school['level'] = section_type
        
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
    
    # 按级别统计
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

def main():
    """主函数"""
    print("=" * 70)
    print("正确解析学校类型 - 根据HTML区域标题")
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
    
    print("\n下载并解析所有区域...")
    
    import urllib.request
    
    all_levels = {}
    
    for html_file, district_en in districts.items():
        filepath = f"/tmp/edb_{html_file}"
        
        # 下载HTML
        url = f"http://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/{html_file}"
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                content = resp.read().decode('utf-8')
            with open(filepath, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"\n下载失败 {html_file}: {e}")
            continue
        
        schools = extract_schools_with_types(filepath, district_en)
        _, updated, levels = import_to_db(district_en, schools)
        
        total_schools += len(schools)
        total_updated += updated
        
        # 统计级别
        for lvl, cnt in levels.items():
            all_levels[lvl] = all_levels.get(lvl, 0) + cnt
        
        print(f"{district_en}: {len(schools)}所", end="")
        for lvl, cnt in sorted(levels.items()):
            print(f", {lvl}: {cnt}", end="")
        print()
    
    print(f"\n{'='*70}")
    print(f"总共处理 {total_schools} 所学校, 更新 {total_updated} 条记录")
    print(f"\n全级别分布:")
    for lvl, cnt in sorted(all_levels.items()):
        print(f"  {lvl}: {cnt}")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
