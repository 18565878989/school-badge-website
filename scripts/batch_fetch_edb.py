#!/usr/bin/env python3
"""
抓取香港教育局各区域学校数据
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sqlite3
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 区域映射
districts = {
    'school-list-cw.html': ('Central & Western', '中西区'),
    'school-list-hke.html': ('Eastern', '东区'),
    'school-list-i.html': ('Islands', '离岛区'),
    'school-list-kc.html': ('Kowloon City', '九龙城区'),
    'school-list-kt.html': ('Kwun Tong', '观塘区'),
    'school-list-kwt.html': ('Kwai Tsing', '葵青区'),
    'school-list-n.html': ('Northern', '北区'),
    'school-list-sk.html': ('Sai Kung', '西贡区'),
    'school-list-sou.html': ('Southern', '南区'),
    'school-list-ssp.html': ('Sham Shui Po', '深水埗区'),
    'school-list-st.html': ('Sha Tin', '沙田区'),
    'school-list-tm.html': ('Tuen Mun', '屯门区'),
    'school-list-tp.html': ('Tai Po', '大埔区'),
    'school-list-tw.html': ('Tsuen Wan', '荃湾区'),
    'school-list-wch.html': ('Wan Chai', '湾仔区'),
    'school-list-wts.html': ('Wong Tai Sin', '黄大仙区'),
    'school-list-yl.html': ('Yuen Long', '元朗区'),
    'school-list-ytm.html': ('Yau Tsim Mong', '油尖旺区'),
}

def parse_school_info(school_div):
    """解析单个学校信息"""
    school = {}
    
    try:
        # 获取学校名称
        name_elem = school_div.find('h3')
        if name_elem:
            school['name'] = name_elem.get_text(strip=True)
        
        # 获取中文名称
        cn_elem = school_div.find('span', class_='title_cn')
        if cn_elem:
            school['name_cn'] = cn_elem.get_text(strip=True)
        
        # 获取地址
        addr_elem = school_div.find('div', class_='address')
        if addr_elem:
            school['address'] = addr_elem.get_text(strip=True)
        
        # 获取其他信息
        text = school_div.get_text(separator='|')
        
        # 电话
        phone_match = re.search(r'Phone[:\s]*([\d\s-]+)', text)
        if phone_match:
            school['phone'] = phone_match.group(1).strip()
        
        # 传真
        fax_match = re.search(r'Fax[:\s]*([\d\s-]+)', text)
        if fax_match:
            school['fax'] = fax_match.group(1).strip()
        
        # 校长
        principal_match = re.search(r'Principal[:\s]*([^\|]+)', text)
        if principal_match:
            school['principal'] = principal_match.group(1).strip()
        
        # 校监
        supervisor_match = re.search(r'Supervisor[:\s]*([^\|]+)', text)
        if supervisor_match:
            school['supervisor'] = supervisor_match.group(1).strip()
        
        # 学校编号
        code_match = re.search(r'School No[./Location ID]*[:\s]*([^\|]+)', text)
        if code_match:
            school['school_code'] = code_match.group(1).strip()
        
    except Exception as e:
        print(f"  解析错误: {e}")
    
    return school

def fetch_district_schools(filename):
    """抓取单个区域的学校数据"""
    url = f"http://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/{filename}"
    
    print(f"\n{'='*60}")
    print(f"正在抓取: {filename}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有学校条目
            school_divs = soup.find_all('div', class_='school-item')
            
            if not school_divs:
                # 尝试其他选择器
                school_divs = soup.find_all('div', class_='school')
            
            if not school_divs:
                # 尝试查找表格
                tables = soup.find_all('table')
                print(f"  找到 {len(tables)} 个表格")
            
            print(f"  找到 {len(school_divs)} 个学校条目")
            
            schools = []
            for div in school_divs[:50]:  # 限制数量
                school = parse_school_info(div)
                if school.get('name'):
                    schools.append(school)
            
            return schools
        else:
            print(f"  抓取失败: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"  错误: {e}")
        return []

def import_schools_to_db(district_name, schools):
    """导入学校数据到数据库"""
    if not schools:
        return 0
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0
    
    for school in schools:
        # 检查是否已存在
        cursor.execute("SELECT id FROM schools WHERE name = ? AND district = ?", 
                     (school.get('name', ''), district_name))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE schools SET
                    name_cn = ?, address = ?, phone = ?, fax = ?,
                    supervisor = ?, principal = ?, school_code = ?,
                    source = 'edb', updated_at = ?
                WHERE id = ?
            """, (
                school.get('name_cn', ''), school.get('address', ''),
                school.get('phone', ''), school.get('fax', ''),
                school.get('supervisor', ''), school.get('principal', ''),
                school.get('school_code', ''), now, existing[0]
            ))
            updated += 1
        else:
            # 确定学校类型
            level = 'middle'
            if 'primary' in school.get('name', '').lower() or '小學' in school.get('name_cn', ''):
                level = 'primary'
            elif 'kindergarten' in school.get('name', '').lower() or '幼兒園' in school.get('name_cn', ''):
                level = 'kindergarten'
            
            # 确定办学类型
            finance_type = 'Aided'
            name_lower = school.get('name', '').lower()
            if 'government' in name_lower or '官立' in school.get('name_cn', ''):
                finance_type = 'Government'
            elif 'direct' in name_lower or '直資' in school.get('name_cn', ''):
                finance_type = 'Direct'
            elif 'private' in name_lower or '私立' in school.get('name_cn', ''):
                finance_type = 'Private'
            
            cursor.execute("""
                INSERT INTO schools (
                    name, name_cn, region, country, city, address, phone, fax,
                    supervisor, principal, level, finance_type, district,
                    school_code, source, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                school.get('name', ''), school.get('name_cn', ''),
                'Hong Kong', 'China', 'Hong Kong',
                school.get('address', ''), school.get('phone', ''), school.get('fax', ''),
                school.get('supervisor', ''), school.get('principal', ''),
                level, finance_type, district_name,
                school.get('school_code', ''), 'edb', now, now
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"  导入: {inserted} 新增, {updated} 更新")
    return inserted + updated

def main():
    """主函数"""
    print("=" * 60)
    print("开始批量抓取香港教育局学校数据")
    print("=" * 60)
    
    total_imported = 0
    
    for filename, (en_name, cn_name) in districts.items():
        schools = fetch_district_schools(filename)
        if schools:
            imported = import_schools_to_db(en_name, schools)
            total_imported += imported
        time.sleep(1)  # 礼貌性延迟
    
    print(f"\n{'='*60}")
    print(f"抓取完成! 总共导入 {total_imported} 条记录")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
