#!/usr/bin/env python3
"""
改进的香港教育局学校数据解析器
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

def extract_schools_from_html(html, district_en, district_cn):
    """从HTML中提取学校数据"""
    schools = []

    # 移除脚本和样式
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

    # 找到表格
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)

    for table in tables:
        # 只处理包含学校数据的表格
        if 'School List by District' not in table and 'tablestyleA' not in table:
            continue

        # 找到表格内的行
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)

        current_school = {}

        for row in rows:
            # 跳过表头行
            if 'Name & Address of School' in row or 'No.' in row or row.strip().startswith('<th'):
                continue

            # 提取学校编号
            no_match = re.search(r'<td[^>]*[^>]*>(\d+)\s*<', row)
            if no_match and 'rowspan=' not in row:
                # 保存之前的学校
                if current_school and current_school.get('name_en'):
                    schools.append(current_school)
                    print(f"  找到学校: {current_school.get('name_en', 'Unknown')}")

                current_school = {
                    'district_en': district_en,
                    'district_cn': district_cn,
                }

                school_no = no_match.group(1)
                current_school['school_no'] = school_no

            # 提取英文名称
            name_en_match = re.search(r'class="bodytxt"[^>]*>([A-Z][A-Za-z\s\-\'\.]+(?:SCHOOL|COLLEGE|PRIMARY|KINDERGARTEN|SECONDARY)[^<]*)', row)
            if name_en_match:
                current_school['name_en'] = name_en_match.group(1).strip()

            # 提取中文名称
            name_cn_match = re.search(r'([\u4e00-\u9fff]+(?:中學|小學|學校|書院|幼兒園|幼稚園)[^\n<]*)', row)
            if name_cn_match:
                current_school['name_cn'] = name_cn_match.group(1).strip()

            # 如果没有中文名，尝试其他方式
            if not current_school.get('name_cn'):
                name_cn_match = re.search(r'([\u4e00-\u9fff]{2,10})', row)
                if name_cn_match:
                    current_school['name_cn'] = name_cn_match.group(1).strip()

            # 提取英文地址
            address_en_match = re.search(r'>\s*([A-Z][A-Za-z\s,\d\-\.]+(?:ROAD|STREET|AVENUE|LANE|DRIVE|WAY|PATH|CENTRE|BUILDING|HK|HONG\s*KONG|WESTERN|KENNEDY|PRINCE|QUEEN|CHATHAM|CITY|TOWN|VILLAGE|ESTATE|HOUSE|PLAZA|TOWER)[^<]*)', row)
            if address_en_match:
                current_school['address_en'] = address_en_match.group(1).strip()

            # 提取中文地址
            address_cn_match = re.search(r'([\u4e00-\u9fff]+[\u4e00-\u9fff0-9號]+)', row)
            if address_cn_match:
                current_school['address_cn'] = address_cn_match.group(1).strip()

            # 提取电话
            tel_match = re.search(r'Tel[.\s]*電話[:\s]*<br>\s*(\d{8})', row)
            if tel_match:
                current_school['phone'] = tel_match.group(1)

            # 如果没找到，尝试其他格式
            if not current_school.get('phone'):
                tel_match = re.search(r'Tel[.\s]*電話:\s*<br>\s*(\d{8})', row)
                if tel_match:
                    current_school['phone'] = tel_match.group(1)

            # 提取传真
            fax_match = re.search(r'Fax[.\s]*傳真[:\s]*<br>\s*(\d{8})', row)
            if fax_match:
                current_school['fax'] = fax_match.group(1)

            # 提取校长
            principal_match = re.search(r'Head of School 校長:\s*<br>\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z][a-z]+)*)', row)
            if principal_match:
                current_school['principal'] = principal_match.group(1).strip()

            # 如果没找到，尝试中文格式
            if not current_school.get('principal'):
                principal_match = re.search(r'Head of School 校長:\s*<br>\s*([\u4e00-\u9fff]+女士|[\u4e00-\u9fff]+先生|[\u4e00-\u9fff]+博士)', row)
                if principal_match:
                    current_school['principal'] = principal_match.group(1).strip()

            # 提取校监/主席
            supervisor_match = re.search(r'(?:Chairman of SMC|學校管理委員會主席)[:\s]*<br>\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+女士|\s+先生|\s+博士)?)', row)
            if supervisor_match:
                current_school['supervisor'] = supervisor_match.group(1).strip()

            # 提取性别
            if 'GIRLS' in row or '女' in row:
                current_school['gender'] = 'GIRLS'
            elif 'BOYS' in row or '男' in row:
                current_school['gender'] = 'BOYS'
            elif 'CO-ED' in row or '男女' in row:
                current_school['gender'] = 'CO-ED'

            # 提取授课时间
            if 'WD' in row and '*' in row:
                current_school['session_type'] = 'WD'
            elif 'PM' in row and '*' in row:
                current_school['session_type'] = 'PM'
            elif 'AM' in row and '*' in row:
                current_school['session_type'] = 'AM'

            # 提取学校编号/Location ID
            school_id_match = re.search(r'School No[./Location ID]*:\s*([^<\n]+)', row)
            if school_id_match:
                current_school['school_id'] = school_id_match.group(1).strip()

        # 保存最后一个学校
        if current_school and current_school.get('name_en'):
            schools.append(current_school)
            print(f"  找到学校: {current_school.get('name_en', 'Unknown')}")

    return schools

def scrape_district(url, district_en, district_cn):
    """抓取单个区域的学校"""
    print(f"\n抓取 {district_cn} ({district_en})...")

    html = fetch_url(url)
    if not html:
        print(f"  无法获取页面")
        return []

    schools = extract_schools_from_html(html, district_en, district_cn)
    print(f"  共找到 {len(schools)} 所学校")

    return schools

def main():
    """主函数"""
    print("=" * 60)
    print("香港教育局学校数据抓取（改进版）")
    print("=" * 60)

    # 区域列表
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
        time.sleep(1)

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