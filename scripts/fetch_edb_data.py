#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 EDB 香港教育局网站抓取所有区域学校数据
网址: https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time
import json

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

# 区域名称映射
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
        response = requests.get(url, headers=HEADERS, timeout=60)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def parse_school_data(html, district):
    """解析学校数据"""
    soup = BeautifulSoup(html, 'lxml')
    
    schools = []
    
    # 查找所有表格行
    rows = soup.find_all('tr')
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        
        # 跳过标题行
        if len(cells) < 3:
            continue
        
        # 提取学校数据
        school_data = {
            'district': district,
            'school_code': '',
            'name': '',
            'name_cn': '',
            'address': '',
            'phone': '',
            'fax': '',
            'supervisor': '',
            'principal': '',
            'gender': '',
            'session_type': '',
        }
        
        # 解析表格
        for i, cell in enumerate(cells):
            text = cell.get_text().strip()
            
            # 查找学校编号
            if 'School No./Location ID' in text or '學校編號/學校位置編號' in text:
                code_match = re.search(r'(\d{6})', text)
                if code_match:
                    school_data['school_code'] = code_match.group(1)
            
            # 查找学校名称
            if school_data['name'] == '' and i < len(cells) - 1:
                # 尝试获取学校名称
                name_text = cells[i].get_text().strip()
                # 跳过编号行
                if not re.match(r'^\d+$', name_text) and len(name_text) > 2:
                    if name_text not in ['GOVERNMENT', 'AIDED', 'DIRECT', 'ENGLISH', 'PRIVATE', 
                                         'GOVERNMENT SECONDARY SCHOOLS', 'AIDED SECONDARY SCHOOLS',
                                         'DIRECT SUBSIDY SCHEME SECONDARY SCHOOLS',
                                         'ENGLISH SCHOOLS FOUNDATION (SECONDARY)',
                                         'PRIVATE SECONDARY SCHOOLS (DAY/EVENING)',
                                         'GOVERNMENT PRIMARY SCHOOLS', 'AIDED PRIMARY SCHOOLS',
                                         'ENGLISH SCHOOLS FOUNDATION (PRIMARY)',
                                         'PRIMARY SCHOOLS', 'AIDED SPECIAL SCHOOLS',
                                         'KINDERGARTENS', 'KINDERGARTEN-CUM-CHILD CARE CENTRES']:
                        school_data['name'] = name_text
        
        # 尝试从HTML结构中提取更详细的信息
        # 查找包含学校信息的表格
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # 检查是否包含学校名称
                    cell_text = cells[0].get_text().strip()
                    
                    # 跳过分类标题
                    categories = ['GOVERNMENT', 'AIDED', 'DIRECT', 'ENGLISH', 'PRIVATE', 
                                 'GOVERNMENT SECONDARY', 'AIDED SECONDARY', 
                                 'DIRECT SUBSIDY SCHEME', 'ENGLISH SCHOOLS FOUNDATION',
                                 'PRIVATE SECONDARY', 'GOVERNMENT PRIMARY',
                                 'AIDED PRIMARY', 'ENGLISH SCHOOLS FOUNDATION (PRIMARY)',
                                 'PRIMARY SCHOOLS', 'SPECIAL SCHOOLS',
                                 'KINDERGARTENS', 'KINDERGARTEN-CUM-CHILD']
                    
                    if any(cat in cell_text.upper() for cat in categories):
                        continue
                    
                    # 提取学校名称
                    if not school_data['name'] or school_data['name'] in cell_text:
                        # 尝试从链接获取学校名
                        link = cells[0].find('a')
                        if link:
                            school_data['name'] = link.get_text().strip()
                    
                    # 提取地址
                    if '地址' in cell_text or 'Address' in cell_text:
                        if len(cells) > 1:
                            addr = cells[1].get_text().strip()
                            addr = re.sub(r'\s+', ' ', addr)
                            school_data['address'] = addr
        
        # 如果有学校名，添加到列表
        if school_data['name'] and len(school_data['name']) > 3:
            schools.append(school_data)
    
    return schools

def extract_schools_from_html(html, district_name):
    """从HTML直接提取学校数据"""
    soup = BeautifulSoup(html, 'lxml')
    
    schools = []
    
    # 查找所有学校数据行
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            
            # 需要至少包含学校编号和名称
            if len(cells) < 2:
                continue
            
            # 跳过标题行
            first_text = cells[0].get_text().strip()
            if first_text in ['', 'No.', 'GOVERNMENT SECONDARY SCHOOLS', 'AIDED SECONDARY SCHOOLS',
                             'DIRECT SUBSIDY SCHEME SECONDARY SCHOOLS', 
                             'ENGLISH SCHOOLS FOUNDATION (SECONDARY)',
                             'PRIVATE SECONDARY SCHOOLS (DAY/EVENING)',
                             'GOVERNMENT PRIMARY SCHOOLS', 'AIDED PRIMARY SCHOOLS',
                             'ENGLISH SCHOOLS FOUNDATION (PRIMARY)', 'PRIVATE PRIMARY SCHOOLS',
                             'AIDED SPECIAL SCHOOLS', 'KINDERGARTENS',
                             'KINDERGARTEN-CUM-CHILD CARE CENTRES']:
                continue
            
            # 检查是否是学校数据行（包含学校编号）
            has_school_code = False
            for cell in cells:
                if 'School No./Location ID' in cell.get_text() or '學校編號/學校位置編號' in cell.get_text():
                    has_school_code = True
                    break
            
            if has_school_code:
                school = parse_school_row(cells, district_name)
                if school:
                    schools.append(school)
    
    return schools

def parse_school_row(cells, district):
    """解析单行学校数据"""
    try:
        school = {}
        
        # 初始化
        school['district'] = district
        school['name'] = ''
        school['name_cn'] = ''
        school['address'] = ''
        school['phone'] = ''
        school['fax'] = ''
        school['supervisor'] = ''
        school['principal'] = ''
        school['gender'] = ''
        school['session_type'] = ''
        school['school_code'] = ''
        
        # 解析每个单元格
        for i, cell in enumerate(cells):
            text = cell.get_text().strip()
            
            # 提取学校编号
            if 'School No./Location ID' in text or '學校編號/學校位置編號' in text:
                code_match = re.search(r'(\d{6})', text)
                if code_match:
                    school['school_code'] = code_match.group(1)
            
            # 提取学校名称
            if i == 0 and text and not re.match(r'^\d+$', text):
                if len(text) > 3 and text not in ['GOVERNMENT', 'AIDED', 'DIRECT', 'ENGLISH', 'PRIVATE']:
                    school['name'] = text
            
            # 提取地址
            if 'HONG KONG' in text.upper() or '九龍' in text or '新界' in text:
                addr = re.sub(r'\s+', ' ', text)
                if len(addr) > 10:
                    school['address'] = addr
            
            # 提取中文名
            if '中文名' in text or '學校名稱' in text:
                if len(text) > 5:
                    school['name_cn'] = re.sub(r'中文名|學校名稱|：:', '', text).strip()
            
            # 提取电话
            if 'Tel.' in text or '電話' in text:
                phone_match = re.search(r'(\d{8})', text)
                if phone_match:
                    school['phone'] = phone_match.group(1)
            
            # 提取传真
            if 'Fax' in text or '傳真' in text:
                fax_match = re.search(r'(\d{8})', text)
                if fax_match:
                    school['fax'] = fax_match.group(1)
            
            # 提取校长
            if 'Head of School' in text or '校長' in text:
                principal = re.sub(r'Head of School|校長|：:', '', text).strip()
                if principal and principal != '-':
                    school['principal'] = principal
            
            # 提取校监
            if 'Supervisor' in text or '校監' in text:
                supervisor = re.sub(r'Supervisor|校監|：:', '', text).strip()
                if supervisor and supervisor not in ['-', 'English Schools Foundation']:
                    school['supervisor'] = supervisor
            
            # 提取学校管理委员会主席
            if 'Chairman of SMC' in text or '學校管理委員會主席' in text:
                chairman = re.sub(r'Chairman of SMC|學校管理委員會主席|：:', '', text).strip()
                if chairman and chairman != '-':
                    school['supervisor'] = chairman
            
            # 提取性别
            if 'BOYS' in text.upper():
                school['gender'] = 'BOYS'
            elif 'GIRLS' in text.upper():
                school['gender'] = 'GIRLS'
            elif 'CO-ED' in text.upper():
                school['gender'] = 'CO-ED'
            
            # 提取授课时间
            if 'AM' in text.upper() and school['session_type'] == '':
                school['session_type'] = 'AM'
            elif 'PM' in text.upper() and school['session_type'] == '':
                school['session_type'] = 'PM'
            elif 'WD' in text.upper():
                school['session_type'] = 'WD'
        
        # 清理数据
        school['name'] = school['name'].strip()
        school['name_cn'] = school['name_cn'].strip()
        school['address'] = re.sub(r'\s+', ' ', school['address']).strip()
        school['phone'] = school['phone'].strip()
        school['fax'] = school['fax'].strip()
        school['principal'] = school['principal'].strip()
        school['supervisor'] = school['supervisor'].strip()
        
        # 只有当有学校名称时才返回
        if school['name'] and len(school['name']) > 3:
            return school
        
    except Exception as e:
        print(f"Error parsing row: {e}")
    
    return None

def update_database(schools):
    """更新数据库"""
    if not schools:
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updated = 0
    
    for school in schools:
        # 尝试匹配学校
        cursor.execute(
            "SELECT id, name, name_cn FROM schools WHERE country = 'Hong Kong' AND (name LIKE ? OR name_cn LIKE ?)",
            (f'%{school["name"]}%', f'%{school["name"]}%')
        )
        db_school = cursor.fetchone()
        
        if not db_school:
            # 尝试用中文名匹配
            if school['name_cn']:
                cursor.execute(
                    "SELECT id, name, name_cn FROM schools WHERE country = 'Hong Kong' AND name_cn = ?",
                    (school['name_cn'],)
                )
                db_school = cursor.fetchone()
        
        if db_school:
            # 更新数据
            updates = []
            values = []
            
            if school['address']:
                updates.append('address = ?')
                values.append(school['address'])
            if school['phone']:
                updates.append('phone = ?')
                values.append(school['phone'])
            if school['fax']:
                updates.append('fax = ?')
                values.append(school['fax'])
            if school['principal']:
                updates.append('principal = ?')
                values.append(school['principal'])
            if school['supervisor']:
                updates.append('supervisor = ?')
                values.append(school['supervisor'])
            if school['gender']:
                updates.append('gender = ?')
                values.append(school['gender'])
            if school['district']:
                updates.append('district = ?')
                values.append(school['district'])
            
            if updates:
                values.append(db_school[0])
                query = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, values)
                updated += 1
    
    conn.commit()
    conn.close()
    
    return updated

def main():
    """主函数"""
    print("="*70)
    print("从 EDB 香港教育局网站抓取学校数据")
    print("="*70)
    
    total_updated = 0
    
    for district_code, url in DISTRICT_URLS.items():
        district_name = DISTRICT_NAMES.get(district_code, district_code)
        print(f"\n📍 处理 {district_name} ({district_code})...")
        
        html = fetch_page(url)
        if html:
            schools = extract_schools_from_html(html, district_name)
            print(f"  找到 {len(schools)} 所学校")
            
            updated = update_database(schools)
            print(f"  更新 {updated} 条记录")
            total_updated += updated
        else:
            print(f"  ❌ 无法获取页面")
        
        time.sleep(1)
    
    print(f"\n" + "="*70)
    print(f"完成! 总共更新 {total_updated} 条记录")
    print("="*70)

if __name__ == '__main__':
    main()
