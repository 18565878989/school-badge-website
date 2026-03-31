#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDB 香港教育局数据抓取 v2
直接解析HTML结构，提取所有字段包括supervisor
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time

# 数据库路径
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

# EDB 区域URL列表
DISTRICT_URLS = {
    'cw': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-cw.html',
    'hke': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-hke.html',
    'i': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-i.html',
    'sou': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-sou.html',
    'wch': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-wch.html',
    'kc': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-kc.html',
    'kt': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-kt.html',
    'sk': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-sk.html',
    'ssp': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-ssp.html',
    'wts': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-wts.html',
    'ytm': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-ytm.html',
    'n': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-n.html',
    'st': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-st.html',
    'tp': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-tp.html',
    'tw': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-tw.html',
    'tm': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-tm.html',
    'yl': 'https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-yl.html',
}

DISTRICT_NAMES = {
    'cw': 'Central & Western',
    'hke': 'Hong Kong Eastern',
    'i': 'Islands',
    'sou': 'Southern',
    'wch': 'Wan Chai',
    'kc': 'Kowloon City',
    'kt': 'Kwun Tong',
    'sk': 'Sai Kung',
    'ssp': 'Sham Shui Po',
    'wts': 'Wong Tai Sin',
    'ytm': 'Yau Tsim Mong',
    'n': 'Northern',
    'st': 'Sha Tin',
    'tp': 'Tai Po',
    'tw': 'Tsuen Wan',
    'tm': 'Tuen Mun',
    'yl': 'Yuen Long',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


def fetch_page(url):
    """获取网页内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=90)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None


def get_text(element):
    """获取元素的文本内容"""
    if element is None:
        return ''
    return element.get_text(strip=True)


def parse_school_from_row(row, district):
    """从一行数据解析学校信息"""
    school = {
        'district': district,
        'name': '',
        'name_cn': '',
        'address': '',
        'phone': '',
        'fax': '',
        'school_code': '',
        'principal': '',
        'supervisor': '',
        'website': '',
        'gender': '',
    }
    
    cells = row.find_all('td', class_='bodytxt')
    if not cells:
        return None
    
    # 获取整行文本用于模式匹配
    row_text = row.get_text(' ', strip=True)
    
    # 跳过标题行
    skip_patterns = ['GOVERNMENT SECONDARY', 'AIDED SECONDARY', 'DIRECT SUBSIDY',
                     'ENGLISH SCHOOLS FOUNDATION', 'PRIVATE SECONDARY',
                     'GOVERNMENT PRIMARY', 'AIDED PRIMARY', 'PRIVATE PRIMARY',
                     'AIDED SPECIAL', 'KINDERGARTEN', 'KINDERGARTEN-CUM-CHILD',
                     'OTHERS', 'PRIMARY AND SECONDARY']
    for pattern in skip_patterns:
        if pattern in row_text.upper():
            return None
    
    # 查找学校编号
    code_match = re.search(r'School No\./Location ID:\s*(\d{6})', row_text)
    if code_match:
        school['school_code'] = code_match.group(1)
    
    # 查找电话
    phone_match = re.search(r'Tel\.\s*電話:\s*\D*(\d{8})', row_text)
    if phone_match:
        school['phone'] = phone_match.group(1)
    
    # 查找传真
    fax_match = re.search(r'Fax\s*傳真:\s*\D*(\d{8}|NIL)', row_text)
    if fax_match:
        fax = fax_match.group(1)
        school['fax'] = '' if fax == 'NIL' else fax
    
    # 查找校长/校监 - 使用更精确的模式
    # 校长
    principal_match = re.search(r'Head of School\s*校長:\s*(.+?)(?=\s*(?:AM|PM|WD|Website|$))', row_text, re.DOTALL)
    if principal_match:
        school['principal'] = re.sub(r'\s+', ' ', principal_match.group(1)).strip()
        # 清理多余的空白和<br>标签
        school['principal'] = school['principal'].replace('\n', ' ').replace('  ', ' ').strip()
    
    # 校监/学校管理委员会主席
    supervisor_patterns = [
        r'Chairman of SMC\s*學校管理委員會主席:\s*(.+?)(?=\s*(?:Head of School|Tel|Website|$))',
        r'Supervisor\s*校監:\s*(.+?)(?=\s*(?:Head of School|Tel|Website|$))',
    ]
    for pattern in supervisor_patterns:
        supervisor_match = re.search(pattern, row_text, re.DOTALL)
        if supervisor_match:
            school['supervisor'] = re.sub(r'\s+', ' ', supervisor_match.group(1)).strip()
            school['supervisor'] = school['supervisor'].replace('\n', ' ').replace('  ', ' ').strip()
            break
    
    # 查找学校名称 - 从包含学校编号的cell中提取
    for cell in cells:
        cell_text = get_text(cell)
        # 查找School No.所在的cell，它前面的cell应该包含学校名
        if 'School No./Location ID' in cell_text or '學校編號' in cell_text:
            # 获取父tr中的第一个td（学校名称）
            parent_table = cell.find_parent('table')
            if parent_table:
                name_cell = parent_table.find('td', class_='bodytxt')
                if name_cell:
                    name_text = get_text(name_cell)
                    # 第一行是英文名
                    lines = [l.strip() for l in name_text.split('\n') if l.strip()]
                    if lines:
                        school['name'] = lines[0]
                        # 查找中文名（通常在英文名后面）
                        for line in lines[1:]:
                            if re.search(r'[\u4e00-\u9fff]', line):  # 包含中文字符
                                school['name_cn'] = line
                                break
    
    # 查找性别
    if 'BOYS' in row_text.upper():
        school['gender'] = 'BOYS'
    elif 'GIRLS' in row_text.upper():
        school['gender'] = 'GIRLS'
    elif 'CO-ED' in row_text.upper() or '男女' in row_text:
        school['gender'] = 'CO-ED'
    
    # 查找网站
    website_match = re.search(r'Website\s*網址:\s*(.+?)(?:\s|$)', row_text)
    if website_match:
        website = website_match.group(1).strip()
        # 提取URL
        url_match = re.search(r'http[s]?://[^\s<>"]+', website)
        if url_match:
            school['website'] = url_match.group(0)
    
    return school if school['name'] or school['school_code'] else None


def parse_district_html(html, district):
    """解析整个区域页面"""
    soup = BeautifulSoup(html, 'html.parser')
    schools = []
    
    # 找到所有学校行 - 包含School No.的行
    for row in soup.find_all('tr'):
        row_text = row.get_text(strip=True)
        if 'School No./Location ID' in row_text or '學校編號' in row_text:
            school = parse_school_from_row(row, district)
            if school:
                schools.append(school)
    
    return schools


def update_database(schools, district):
    """更新数据库"""
    if not schools:
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    updated = 0
    
    for school in schools:
        school_code = school.get('school_code', '')
        phone = school.get('phone', '')
        
        db_school_id = None
        
        # 1. 用school_code匹配
        if school_code:
            cursor.execute(
                "SELECT id FROM schools WHERE school_code = ? AND (country = 'Hong Kong' OR city LIKE '%Hong Kong%')",
                (school_code,)
            )
            result = cursor.fetchone()
            if result:
                db_school_id = result[0]
        
        # 2. 用电话匹配
        if not db_school_id and phone and len(phone) == 8:
            cursor.execute(
                "SELECT id FROM schools WHERE phone = ? AND (country = 'Hong Kong' OR city LIKE '%Hong Kong%')",
                (phone,)
            )
            result = cursor.fetchone()
            if result:
                db_school_id = result[0]
        
        # 3. 用学校名称匹配
        if not db_school_id and school.get('name'):
            name = school['name']
            cursor.execute(
                "SELECT id FROM schools WHERE (country = 'Hong Kong' OR city LIKE '%Hong Kong%') AND (name LIKE ? OR name_cn LIKE ?)",
                (f'%{name}%', f'%{name}%')
            )
            result = cursor.fetchone()
            if result:
                db_school_id = result[0]
        
        if db_school_id:
            # 构建更新语句
            updates = []
            values = []
            
            if school.get('phone') and len(school['phone']) == 8:
                updates.append('phone = ?')
                values.append(school['phone'])
            if school.get('fax') and len(school['fax']) == 8:
                updates.append('fax = ?')
                values.append(school['fax'])
            if school.get('principal') and school['principal'] not in ['-', '']:
                updates.append('principal = ?')
                values.append(school['principal'])
            if school.get('supervisor') and school['supervisor'] not in ['-', '']:
                updates.append('supervisor = ?')
                values.append(school['supervisor'])
            if school.get('school_code'):
                updates.append('school_code = ?')
                values.append(school['school_code'])
            if school.get('website'):
                updates.append('website = ?')
                values.append(school['website'])
            if school.get('gender'):
                updates.append('gender = ?')
                values.append(school['gender'])
            
            if updates:
                values.append(db_school_id)
                query = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, values)
                updated += 1
    
    conn.commit()
    conn.close()
    return updated


def main():
    """主函数"""
    print("=" * 70)
    print("EDB 香港教育局数据抓取 v2")
    print("=" * 70)
    
    total_schools = 0
    total_updated = 0
    
    for district_code, url in DISTRICT_URLS.items():
        district_name = DISTRICT_NAMES.get(district_code, district_code)
        print(f"\n📍 处理 {district_name} ({district_code})...")
        
        html = fetch_page(url)
        if html:
            schools = parse_district_html(html, district_name)
            print(f"  解析到 {len(schools)} 所学校")
            total_schools += len(schools)
            
            updated = update_database(schools, district_name)
            print(f"  更新 {updated} 条记录")
            total_updated += updated
        else:
            print(f"  ❌ 无法获取页面")
        
        time.sleep(2)  # 礼貌性延迟
    
    print(f"\n" + "=" * 70)
    print(f"完成!")
    print(f"解析学校总数: {total_schools}")
    print(f"更新数据库记录: {total_updated}")
    print("=" * 70)
    
    # 数据质量检查
    print("\n📊 数据质量检查:")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source = 'edb'")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source = 'edb' AND supervisor IS NOT NULL AND supervisor != '' AND supervisor != '-'")
    with_supervisor = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source = 'edb' AND phone IS NOT NULL AND phone != ''")
    with_phone = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source = 'edb' AND principal IS NOT NULL AND principal != '' AND principal != '-'")
    with_principal = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source = 'edb' AND website IS NOT NULL AND website != ''")
    with_website = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"  总EDB学校: {total}")
    print(f"  有supervisor: {with_supervisor} ({100*with_supervisor/total:.1f}%)")
    print(f"  有phone: {with_phone} ({100*with_phone/total:.1f}%)")
    print(f"  有principal: {with_principal} ({100*with_principal/total:.1f}%)")
    print(f"  有website: {with_website} ({100*with_website/total:.1f}%)")


if __name__ == '__main__':
    main()
