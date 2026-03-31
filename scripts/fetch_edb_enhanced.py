#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced EDB 香港教育局数据抓取脚本
改进版：完整解析HTML中的所有字段包括supervisor
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from urllib.parse import urljoin

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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
}


def fetch_page(url):
    """获取网页内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None


def parse_text_with_chinese(text):
    """清理文本"""
    if not text:
        return ''
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_fields_from_text(text):
    """从文本块中提取字段"""
    fields = {}
    text = parse_text_with_chinese(text)
    
    # 学校编号
    code_match = re.search(r'School No\./Location ID[:\s]*(\d{6})', text, re.IGNORECASE)
    if code_match:
        fields['school_code'] = code_match.group(1)
    
    # 电话 - 8位数字
    phone_match = re.search(r'Tel\.[:室]?\s*[:\s]*(\d{8})', text, re.IGNORECASE)
    if phone_match:
        fields['phone'] = phone_match.group(1)
    
    # 传真
    fax_match = re.search(r'Fax\s*[:\s]*(\d{8}|NIL)', text, re.IGNORECASE)
    if fax_match:
        fields['fax'] = fax_match.group(1) if fax_match.group(1) != 'NIL' else ''
    
    # 校长
    principal_match = re.search(r'Head of School\s*[校長:]*\s*(.+?)(?=\s*(?:AM|PM|WD|$|\n))', text, re.IGNORECASE | re.DOTALL)
    if principal_match:
        fields['principal'] = parse_text_with_chinese(principal_match.group(1))
    
    # 校监/学校管理委员会主席
    supervisor_match = re.search(r'(?:Chairman of SMC|Supervisor|學校管理委員會主席|校監)[:\s]*(.+?)(?=\s*(?:Head of School|Tel|Fax|AM|PM|WD|$))', text, re.IGNORECASE | re.DOTALL)
    if supervisor_match:
        fields['supervisor'] = parse_text_with_chinese(supervisor_match.group(1))
    
    # 地址
    addr_match = re.search(r'(?:HONG KONG|九龍|九龍|新界|香港)[^\n]{10,}', text, re.IGNORECASE)
    if addr_match:
        fields['address'] = parse_text_with_chinese(addr_match.group(0))
    
    return fields


def parse_school_block(block_text, district):
    """解析学校信息块"""
    fields = {'district': district}
    fields.update(extract_fields_from_text(block_text))
    return fields


def parse_html_enhanced(html, district):
    """增强版HTML解析 - 提取所有学校字段"""
    soup = BeautifulSoup(html, 'html.parser')
    schools = []
    
    # 查找所有表格
    tables = soup.find_all('table')
    
    for table in tables:
        # 获取表格中的所有文本，按行处理
        rows = table.find_all('tr')
        
        current_school = None
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            row_text = ' '.join([cell.get_text() for cell in cells])
            row_text_clean = parse_text_with_chinese(row_text)
            
            # 跳过标题行
            skip_categories = [
                'GOVERNMENT SECONDARY', 'AIDED SECONDARY', 'DIRECT SUBSIDY',
                'ENGLISH SCHOOLS FOUNDATION', 'PRIVATE SECONDARY',
                'GOVERNMENT PRIMARY', 'AIDED PRIMARY', 'PRIVATE PRIMARY',
                'AIDED SPECIAL', 'KINDERGARTEN', 'KINDERGARTEN-CUM-CHILD',
                'OTHERS', 'PRIMARY AND SECONDARY'
            ]
            
            if any(cat in row_text_clean.upper() for cat in skip_categories):
                continue
            
            # 检查是否是学校数据行（包含School No.）
            if 'School No./Location ID' in row_text or '學校編號' in row_text:
                # 保存上一个学校
                if current_school and current_school.get('name'):
                    schools.append(current_school)
                
                # 开始新学校
                current_school = parse_school_block(row_text, district)
            
            elif current_school is not None:
                # 继续补充当前学校的信息
                additional_fields = extract_fields_from_text(row_text)
                
                for key, value in additional_fields.items():
                    if value and (key not in current_school or not current_school[key]):
                        current_school[key] = value
    
    # 保存最后一个学校
    if current_school and current_school.get('name'):
        schools.append(current_school)
    
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
        fax = school.get('fax', '')
        principal = school.get('principal', '')
        supervisor = school.get('supervisor', '')
        address = school.get('address', '')
        
        # 如果有school_code，优先用它匹配
        if school_code:
            cursor.execute(
                "SELECT id, name, name_cn FROM schools WHERE school_code = ? AND (country = 'Hong Kong' OR city LIKE '%Hong Kong%')",
                (school_code,)
            )
            db_school = cursor.fetchone()
        
        # 如果没找到，尝试用电话匹配
        if not db_school and phone:
            cursor.execute(
                "SELECT id, name, name_cn FROM schools WHERE phone = ? AND (country = 'Hong Kong' OR city LIKE '%Hong Kong%')",
                (phone,)
            )
            db_school = cursor.fetchone()
        
        # 如果还没找到，用学校名称关键词匹配
        if not db_school and school.get('name'):
            name = school['name']
            # 尝试多种匹配方式
            for pattern in [name, name.split()[0] if name else '']:
                if pattern and len(pattern) > 3:
                    cursor.execute(
                        "SELECT id, name, name_cn FROM schools WHERE (country = 'Hong Kong' OR city LIKE '%Hong Kong%') AND (name LIKE ? OR name_cn LIKE ?)",
                        (f'%{pattern}%', f'%{pattern}%')
                    )
                    db_school = cursor.fetchone()
                    if db_school:
                        break
        
        if db_school:
            # 更新数据
            updates = []
            values = []
            
            if phone and len(phone) == 8:
                updates.append('phone = ?')
                values.append(phone)
            if fax and len(fax) == 8:
                updates.append('fax = ?')
                values.append(fax)
            if principal and principal != '-':
                updates.append('principal = ?')
                values.append(principal)
            if supervisor and supervisor != '-':
                updates.append('supervisor = ?')
                values.append(supervisor)
            if address and len(address) > 10:
                updates.append('address = ?')
                values.append(address)
            if school_code:
                updates.append('school_code = ?')
                values.append(school_code)
            
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
    print("=" * 70)
    print("EDB 香港教育局数据增强抓取 (supervisor/校长/电话补全)")
    print("=" * 70)
    
    total_schools = 0
    total_updated = 0
    
    for district_code, url in DISTRICT_URLS.items():
        district_name = DISTRICT_NAMES.get(district_code, district_code)
        print(f"\n📍 处理 {district_name} ({district_code})...")
        
        html = fetch_page(url)
        if html:
            schools = parse_html_enhanced(html, district_name)
            print(f"  解析到 {len(schools)} 所学校")
            total_schools += len(schools)
            
            updated = update_database(schools, district_name)
            print(f"  更新 {updated} 条记录")
            total_updated += updated
        else:
            print(f"  ❌ 无法获取页面")
        
        time.sleep(1)  # 礼貌性延迟
    
    print(f"\n" + "=" * 70)
    print(f"完成!")
    print(f"解析学校总数: {total_schools}")
    print(f"更新数据库记录: {total_updated}")
    print("=" * 70)
    
    # 验证结果
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
    
    conn.close()
    
    print(f"  总EDB学校: {total}")
    print(f"  有supervisor: {with_supervisor} ({100*with_supervisor/total:.1f}%)")
    print(f"  有phone: {with_phone} ({100*with_phone/total:.1f}%)")
    print(f"  有principal: {with_principal} ({100*with_principal/total:.1f}%)")


if __name__ == '__main__':
    main()
