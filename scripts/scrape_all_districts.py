#!/usr/bin/env python3
"""
从香港教育局网站抓取所有区域的学校数据
"""

import urllib.request
import ssl
import re
import json
import time

def fetch_url(url):
    """获取URL内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_school_table(html, district_en, district_cn):
    """解析学校表格数据"""
    schools = []

    # 提取表格行
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)

    for row in rows:
        # 跳过表头
        if 'School No.' in row or '<th' in row:
            continue

        # 提取学校编号
        school_no_match = re.search(r'<td[^>]*>(\d+)[A-Z]?</td>', row)
        if not school_no_match:
            continue

        school_no = school_no_match.group(1)

        # 提取英文名称
        name_en_match = re.search(r'>([^<]+(?:School|College|Primary|Kindergarten|Secondary)[^<]*)</a>', row)
        if not name_en_match:
            name_en_match = re.search(r'>([A-Z][A-Za-z\s\-\'\.]+)</td>', row)

        name_en = name_en_match.group(1).strip() if name_en_match else ''

        # 提取中文名称
        name_cn_match = re.search(r'([\u4e00-\u9fff]+(?:小學|中學|學校|書院|幼兒園|幼稚園)[^\n<]*)', row)
        name_cn = name_cn_match.group(1).strip() if name_cn_match else ''

        # 如果没有找到中文名，尝试其他方式
        if not name_cn:
            name_cn_match = re.search(r'([\u4e00-\u9fff]{2,10})', row)
            name_cn = name_cn_match.group(1).strip() if name_cn_match else ''

        # 提取地址（英文）
        address_en_match = re.search(r'>([A-Z][A-Za-z\s,\d\-\.]+\d+\s+(?:ROAD|STREET|AVENUE|LANE|DRIVE|WAY|PATH|CENTRE|BUILDING|HK|HONG\s*KONG|WESTERN|KENNEDY|PRINCE|QUEEN|CHATHAM|CITY|TOWN|VILLAGE|ESTATE|HOUSE|PLAZA)])', row)
        address_en = address_en_match.group(1).strip() if address_en_match else ''

        # 提取地址（中文）
        address_cn_match = re.search(r'([\u4e00-\u9fff]+[\u4e00-\u9fff0-9號]+)', row)
        address_cn = address_cn_match.group(1).strip() if address_cn_match else ''

        # 提取电话
        phone_match = re.search(r'Tel[^:]*[:\s]*(\d{8})', row)
        if not phone_match:
            phone_match = re.search(r'(\d{8})', row)
        phone = phone_match.group(1) if phone_match else ''

        # 提取传真
        fax_match = re.search(r'Fax[^:]*[:\s]*(\d{8})', row)
        fax = fax_match.group(1) if fax_match else ''

        # 提取校长
        principal_match = re.search(r'Principal[:\s]*([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', row)
        if not principal_match:
            principal_match = re.search(r'校長[:\s]*([\u4e00-\u9fff]+女士|[\u4e00-\u9fff]+先生|[\u4e00-\u9fff]+博士)', row)
        principal = principal_match.group(1).strip() if principal_match else ''

        # 提取校监/主席
        supervisor_match = re.search(r'(?:Chairman of SMC|Supervisor|校監|學校管理委員會主席)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[\u4e00-\u9fff]+女士|[\u4e00-\u9fff]+先生|[\u4e00-\u9fff]+博士|[\u4e00-\u9fff]+牧師)', row)
        supervisor = supervisor_match.group(1).strip() if supervisor_match else ''

        # 提取性别类型
        gender = ''
        if "BOYS" in row or "男校" in row or "男" in row:
            gender = 'BOYS'
        elif "GIRLS" in row or "女校" in row or "女" in row:
            gender = 'GIRLS'
        elif "CO-ED" in row or "男女" in row:
            gender = 'CO-ED'

        # 提取授课时间
        session_type = ''
        if "AM" in row and "WD" in row:
            session_type = 'WD'
        elif "AM" in row:
            session_type = 'AM'
        elif "PM" in row:
            session_type = 'PM'

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

        # 判断学校等级
        level = 'elementary'  # 默认小学
        if name_en:
            if 'COLLEGE' in name_en.upper() or 'SECONDARY' in name_en.upper():
                level = 'middle'
            elif 'KINDERGARTEN' in name_en.upper() or 'KG' in name_en.upper():
                level = 'kindergarten'

        # 只添加有效的学校记录
        if name_en and len(name_en) > 2:
            schools.append({
                'name_en': name_en,
                'name_cn': name_cn,
                'address_en': address_en,
                'address_cn': address_cn,
                'phone': phone,
                'fax': fax,
                'supervisor': supervisor,
                'principal': principal,
                'gender': gender,
                'session_type': session_type,
                'finance_type': finance_type,
                'level': level,
                'district_en': district_en,
                'district_cn': district_cn,
                'school_no': school_no,
                'region': 'Hong Kong',
                'country': 'Hong Kong',
            })

    return schools

def scrape_district(url, district_en, district_cn):
    """抓取单个区域的学校"""
    print(f"\n抓取 {district_cn} ({district_en})...")

    html = fetch_url(url)
    if not html:
        print(f"  无法获取页面")
        return []

    # 提取表格内容
    table_match = re.search(r'<table[^>]*class="[^"]*table[^"]*"[^>]*>(.*?)</table>', html, re.DOTALL)
    if not table_match:
        # 尝试其他表格
        tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
        for table in tables:
            if 'School No.' in table or len(table) > 500:
                table_match = {'html': table}
                break

    if not table_match:
        print(f"  未找到学校表格")
        return []

    schools = parse_school_table(table_match.group(1) if hasattr(table_match, 'group') else tables[0], district_en, district_cn)
    print(f"  找到 {len(schools)} 所学校")

    return schools

def main():
    """主函数"""
    print("=" * 60)
    print("香港教育局学校数据抓取")
    print("=" * 60)

    # 区域列表（按用户要求的顺序，跳过前2个已完成的）
    districts = [
        # ('URL', '英文名', '中文名')
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

    all_schools = {}
    total = 0

    for i, (url, district_en, district_cn) in enumerate(districts, 1):
        schools = scrape_district(url, district_en, district_cn)
        all_schools[district_en] = {
            'district_cn': district_cn,
            'status': 'completed',
            'schools': schools,
            'count': len(schools)
        }
        total += len(schools)
        print(f"  进度: {i}/{len(districts)} 区域完成")
        time.sleep(1)  # 礼貌性延迟

    # 添加已完成的区域
    all_schools['Islands'] = {'district_cn': '離島區', 'status': 'completed', 'schools': [], 'count': 0}
    all_schools['Southern'] = {'district_cn': '南區', 'status': 'completed', 'schools': [], 'count': 0}

    # 保存到JSON文件
    output_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/scripts/edb_districts.json'

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_schools, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"完成! 共抓取 {total} 所学校")
    print(f"数据已保存到: {output_path}")
    print(f"{'='*60}")

    # 打印摘要
    print("\n各区域统计:")
    for district, data in all_schools.items():
        status = '✓' if data['status'] == 'completed' else '○'
        print(f"  {status} {data['district_cn']} ({district}): {data['count']} 所学校")

    return all_schools

if __name__ == '__main__':
    main()