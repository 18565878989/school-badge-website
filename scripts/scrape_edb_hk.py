#!/usr/bin/env python3
"""
从香港教育局网站抓取学校详细信息
来源: https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/
"""

import sqlite3
import urllib.request
import urllib.error
import ssl
import re
import time
import json
from html import unescape
from datetime import datetime

# 配置
BASE_URL = "https://www.edb.gov.hk"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

DISTRICTS = [
    'central-western',      # 中西區
    'eastern',              # 東區
    'southern',             # 南區
    'wan-chai',            # 灣仔區
    'kowloon-city',        # 九龍城區
    'kwun-tong',          # 觀塘區
    'sham-shui-po',       # 深水埗區
    'wong-tai-sin',       # 黃大仙區
    'yau-tsim-mong',      # 油尖旺區
    'sha-tin',            # 沙田區
    'north',              # 北區
    'tai-po',             # 大埔區
    'yuen-long',          # 元朗區
    'tuen-mun',          # 屯門區
    'tung-chung',        # 東涌區
    'sai-ku',             # 西貢區
    'islands',            # 離島區
]

# 学校类型映射
FINANCE_TYPES = {
    'GOVERNMENT': 'Government',
    'AIDED': 'Aided',
    'DIRECT SUBSIDY': 'Direct Subsidy',
    'PRIVATE': 'Private',
    'ESF': 'ESF (English Schools Foundation)',
    'NPM': 'Private (Non-Profit Making)',
}

def get_page(url):
    """获取页面内容"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  错误: {e}")
        return None

def parse_school_info(html, district, url):
    """解析学校信息"""
    schools = []
    
    # 按学校编号提取
    school_pattern = re.compile(
        r'<tr[^>]*>\s*<td[^>]*>(\d+)</td>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>',
        re.DOTALL
    )
    
    # 更精确的解析 - 使用多行匹配
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    
    for row in rows:
        # 提取学校编号
        no_match = re.search(r'<td[^>]*>(\d+)[A-Z]?</td>', row)
        if not no_match:
            continue
        
        school_no = no_match.group(1)
        
        # 提取英文名
        name_match = re.search(r'>([^<]+KING\'?S\s+COLLEGE|[^<]+COLLEGE|[^<]+SCHOOL|[^<]+PRIMARY|[^<]+SECONDARY|[^<]+KINDERGARTEN)[^<]*</a>', row)
        if not name_match:
            name_match = re.search(r'>([A-Z][A-Za-z\s\-\'\.]+?)\s*</td>', row)
        
        name = name_match.group(1).strip() if name_match else ''
        
        # 提取中文名
        name_cn_match = re.search(r'([\u4e00-\u9fff]+[^\n<]*)', row)
        name_cn = name_cn_match.group(1).strip() if name_cn_match else ''
        
        # 提取地址（英文）
        address_match = re.search(r'([A-Z][A-Za-z\s,\d\-\.]+\d+\s+(?:ROAD|STREET|AVENUE|LANE|DRIVE|WAY|PATH|CENTRE|BUILDING|HK|HONG\s*KONG|WESTERN|KENNEDY|PRINCE|QUEEN|CHATHAM|CITY|TOWN|VILLAGE)])', row)
        address_en = address_match.group(1).strip() if address_match else ''
        
        # 提取地址（中文）
        address_cn_match = re.search(r'([\u4e00-\u9fff]+[\u4e00-\u9fff0-9號]+)', row)
        address_cn = address_cn_match.group(1).strip() if address_cn_match else ''
        
        # 提取电话
        tel_match = re.search(r'Tel[^:]*[:\s]*(\d{8})', row)
        if not tel_match:
            tel_match = re.search(r'(\d{8})', row)
        phone = tel_match.group(1) if tel_match else ''
        
        # 提取传真
        fax_match = re.search(r'Fax[^:]*[:\s]*(\d{8})', row)
        fax = fax_match.group(1) if fax_match else ''
        
        # 提取校长
        principal_match = re.search(r'Head of School[^:]*[:\s]*([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', row)
        if not principal_match:
            principal_match = re.search(r'校長[:\s]*([\u4e00-\u9fff]+女士|[\u4e00-\u9fff]+先生|[\u4e00-\u9fff]+博士)', row)
        principal = principal_match.group(1).strip() if principal_match else ''
        
        # 提取校监/主席
        supervisor_match = re.search(r'(?:Chairman of SMC|Supervisor|校監|學校管理委員會主席)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[\u4e00-\u9fff]+女士|[\u4e00-\u9fff]+先生|[\u4e00-\u9fff]+博士|[\u4e00-\u9fff]+牧師)', row)
        supervisor = supervisor_match.group(1).strip() if supervisor_match else ''
        
        # 提取性别
        gender = ''
        if "BOYS" in row or "男" in row:
            gender = 'BOYS'
        elif "GIRLS" in row or "女" in row:
            gender = 'GIRLS'
        elif "CO-ED" in row or "男女" in row:
            gender = 'CO-ED'
        
        # 提取授课时间
        session = ''
        if "AM" in row and "WD" in row:
            session = 'WD'  # 全日
        elif "AM" in row:
            session = 'AM'  # 上午
        elif "PM" in row:
            session = 'PM'  # 下午
        
        # 判断学校类型
        finance_type = ''
        if "GOVERNMENT" in row or '官立' in row:
            finance_type = 'Government'
        elif "AIDED" in row or '資助' in row:
            finance_type = 'Aided'
        elif "DIRECT SUBSIDY" in row or '直接資助' in row:
            finance_type = 'Direct Subsidy'
        elif "PRIVATE" in row or '私立' in row:
            finance_type = 'Private'
        elif "ESF" in row:
            finance_type = 'ESF'
        elif "NPM" in row:
            finance_type = 'Private (Non-Profit Making)'
        
        # 判断学校等级
        level = 'elementary'  # 默认小学
        if 'COLLEGE' in name.upper() or 'SECONDARY' in name.upper():
            level = 'middle'
        elif 'KINDERGARTEN' in name.upper() or 'KG' in name.upper():
            level = 'kindergarten'
        elif 'UNIVERSITY' in name.upper():
            level = 'university'
        
        # 只添加有学校名的记录
        if name and len(name) > 3:
            schools.append({
                'name': name.strip(),
                'name_cn': name_cn,
                'address': address_en,
                'address_cn': address_cn,
                'phone': phone,
                'fax': fax,
                'principal': principal,
                'supervisor': supervisor,
                'gender': gender,
                'session_type': session,
                'finance_type': finance_type,
                'level': level,
                'district': district,
                'region': 'Hong Kong',
                'country': 'Hong Kong',
                'city': 'Hong Kong',
                'source': 'edb.gov.hk',
            })
    
    return schools

def scrape_district(district):
    """抓取单个区域的所有学校"""
    url = f"{BASE_URL}/en/student-parents/sch-info/sch-search/schlist-by-district/{district}.html"
    
    district_cn = {
        'central-western': '中西區',
        'eastern': '東區',
        'southern': '南區',
        'wan-chai': '灣仔區',
        'kowloon-city': '九龍城區',
        'kwun-tong': '觀塘區',
        'sham-shui-po': '深水埗區',
        'wong-tai-sin': '黃大仙區',
        'yau-tsim-mong': '油尖旺區',
        'sha-tin': '沙田區',
        'north': '北區',
        'tai-po': '大埔區',
        'yuen-long': '元朗區',
        'tuen-mun': '屯門區',
        'tung-chung': '東涌區',
        'sai-ku': '西貢區',
        'islands': '離島區',
    }
    
    print(f"\n抓取 {district_cn.get(district, district)}...")
    
    html = get_page(url)
    if not html:
        print(f"  无法获取页面")
        return []
    
    schools = parse_school_info(html, district, url)
    print(f"  找到 {len(schools)} 所学校")
    
    return schools

def import_to_database(schools):
    """导入到数据库"""
    if not schools:
        return 0
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    imported = 0
    for school in schools:
        try:
            # 检查是否已存在
            cursor.execute(
                'SELECT id FROM schools WHERE name = ? AND name_cn = ? AND region = ?',
                (school['name'], school['name_cn'], 'Hong Kong')
            )
            if cursor.fetchone():
                continue
            
            # 插入新学校
            cursor.execute('''
                INSERT INTO schools (
                    name, name_cn, region, country, city, address, level,
                    phone, fax, principal, supervisor, gender, session_type,
                    finance_type, district, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school['name'],
                school['name_cn'],
                school['region'],
                school['country'],
                school['city'],
                school['address'],
                school['level'],
                school.get('phone', ''),
                school.get('fax', ''),
                school.get('principal', ''),
                school.get('supervisor', ''),
                school.get('gender', ''),
                school.get('session_type', ''),
                school.get('finance_type', ''),
                school.get('district', ''),
                school.get('source', '')
            ))
            imported += 1
            
        except Exception as e:
            print(f"  错误: {e}")
    
    conn.commit()
    conn.close()
    return imported

def main():
    """主函数"""
    print("=" * 60)
    print("香港教育局学校数据抓取")
    print("=" * 60)
    
    all_schools = []
    
    # 抓取各区域
    for district in DISTRICTS[:2]:  # 先抓取前2个区域测试
        schools = scrape_district(district)
        all_schools.extend(schools)
        time.sleep(1)
    
    # 保存到JSON
    with open('scripts/supplement/edb_hk_schools.json', 'w', encoding='utf-8') as f:
        json.dump(all_schools, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存 {len(all_schools)} 所学校到 scripts/supplement/edb_hk_schools.json")
    
    # 导入数据库
    imported = import_to_database(all_schools)
    print(f"成功导入数据库: {imported} 所")
    
    return all_schools

if __name__ == '__main__':
    main()
