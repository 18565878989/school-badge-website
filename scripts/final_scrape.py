#!/usr/bin/env python3
"""
最终的香港教育局学校数据抓取脚本
"""

import urllib.request
import ssl
import re
import json
import time

def fetch_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_school_block(block):
    school = {}
    
    # 学校编号
    no_match = re.search(r'(\d+)', block)
    if no_match:
        school['school_no'] = no_match.group(1)

    # 英文名称
    name_en_match = re.search(r'class="bodytxt"[^>]*>([A-Z][A-Za-z\s\-\'\.]+(?:SCHOOL|COLLEGE|PRIMARY|KINDERGARTEN|SECONDARY)[^<]*)', block)
    if name_en_match:
        school['name_en'] = name_en_match.group(1).strip()

    # 中文名称
    name_cn_match = re.search(r'([\u4e00-\u9fff]+(?:中學|小學|學校|書院|幼兒園|幼稚園)[^\n<]*)', block)
    if name_cn_match:
        school['name_cn'] = name_cn_match.group(1).strip()
    if not school.get('name_cn'):
        name_cn_match = re.search(r'([\u4e00-\u9fff]{2,10})', block)
        if name_cn_match:
            school['name_cn'] = name_cn_match.group(1).strip()

    # 英文地址
    addr_en_match = re.search(r'([A-Z][A-Za-z\s,\d\-\.]+(?:ROAD|STREET|AVENUE|LANE|DRIVE|WAY|PATH|CENTRE|BUILDING|HK|HONG\s*KONG)[^<]*)', block)
    if addr_en_match:
        school['address_en'] = addr_en_match.group(1).strip().replace('&nbsp;', ' ')

    # 中文地址
    addr_cn_match = re.search(r'([\u4e00-\u9fff]+[\u4e00-\u9fff0-9號]+)', block)
    if addr_cn_match:
        school['address_cn'] = addr_cn_match.group(1).strip()

    # 电话
    tel_match = re.search(r'Tel[^<]*<[^>]*>\s*(\d{8})', block)
    if tel_match:
        school['phone'] = tel_match.group(1)

    # 传真
    fax_match = re.search(r'Fax[^<]*<[^>]*>\s*(\d{8})', block)
    if fax_match:
        school['fax'] = fax_match.group(1)

    # 校长 - 格式: Head of School 校長: <br>NAME<br>
    principal_pattern = r'Head of School 校長:\s*<br>\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*(?:\s+[A-Z][A-Za-z]+)*)\s*<br>'
    principal_match = re.search(principal_pattern, block)
    if principal_match:
        school['principal'] = principal_match.group(1).strip()

    # 校监 - 格式: Chairman of SMC<br>學校管理委員會主席:<br>NAME<br>
    supervisor_pattern = r'(?:Chairman of SMC|學校管理委員會主席):\s*<br>\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*(?:\s+[A-Z][A-Za-z]+)*)\s*<br>'
    supervisor_match = re.search(supervisor_pattern, block)
    if supervisor_match:
        school['supervisor'] = supervisor_match.group(1).strip()

    # 性别
    if 'GIRLS' in block or '女' in block:
        school['gender'] = 'GIRLS'
    elif 'BOYS' in block or '男' in block:
        school['gender'] = 'BOYS'
    elif 'CO-ED' in block or '男女' in block:
        school['gender'] = 'CO-ED'

    # 授课时间
    if 'WD' in block and '*' in block:
        school['session_type'] = 'WD'
    elif 'PM' in block and '*' in block:
        school['session_type'] = 'PM'
    elif 'AM' in block and '*' in block:
        school['session_type'] = 'AM'

    # 学校ID
    school_id_match = re.search(r'School No[./Location ID]*:\s*([^<\n]+)', block)
    if school_id_match:
        school['school_id'] = school_id_match.group(1).strip()

    return school

def extract_schools(html, district_en, district_cn):
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    school_blocks = re.split(r'(<td[^>]*align="center"[^>]*>\s*\d+\s*<)', html)
    
    schools = []
    seen_schools = set()
    
    for block in school_blocks[1:]:
        school = parse_school_block(block)
        
        if school.get('name_en') and school['name_en'] not in seen_schools:
            seen_schools.add(school['name_en'])
            school['district_en'] = district_en
            school['district_cn'] = district_cn
            school['region'] = 'Hong Kong'
            school['country'] = 'Hong Kong'
            schools.append(school)
    
    return schools

# 抓取所有区域
districts = [
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-wch.html', 'Wan Chai', '灣仔區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-kc.html', 'Kowloon City', '九龍城區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-kt.html', 'Kwun Tong', '觀塘區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-sk.html', 'Sai Kung', '西貢區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-ssp.html', 'Sham Shui Po', '深水埗區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-wts.html', 'Wong Tai Sin', '黃大仙區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-ytm.html', 'Yau Tsim Mong', '油尖旺區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-n.html', 'Northern', '北區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-st.html', 'Sha Tin', '沙田區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-tp.html', 'Tai Po', '大埔區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-kwt.html', 'Kwai Chung & Tsing Yi', '葵涌及青衣區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-tw.html', 'Tsuen Wan', '荃灣區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-tm.html', 'Tuen Mun', '屯門區'),
    ('https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-yl.html', 'Yuen Long', '元朗區'),
]

print("=" * 60)
print("香港教育局学校数据抓取")
print("=" * 60)

all_data = {}
total = 0

for i, (url, district_en, district_cn) in enumerate(districts, 1):
    print(f"\n抓取 {district_cn} ({district_en})...", end=" ")
    
    html = fetch_url(url)
    if not html:
        print("无法获取页面")
        all_data[district_en] = {'district_cn': district_cn, 'status': 'failed', 'schools': [], 'count': 0}
        continue
    
    schools = extract_schools(html, district_en, district_cn)
    all_data[district_en] = {
        'district_cn': district_cn,
        'status': 'completed',
        'schools': schools,
        'count': len(schools)
    }
    total += len(schools)
    print(f"找到 {len(schools)} 所学校")
    time.sleep(1)

# 添加已完成的区域
all_data['Islands'] = {'district_cn': '離島區', 'status': 'completed', 'schools': [], 'count': 0}
all_data['Southern'] = {'district_cn': '南區', 'status': 'completed', 'schools': [], 'count': 0}

# 保存
output_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/scripts/edb_districts.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 60}")
print(f"完成! 共抓取 {total} 所学校")
print(f"数据已保存到: {output_path}")
print(f"{'=' * 60}")
