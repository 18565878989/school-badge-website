#!/usr/bin/env python3
"""
尝试从新的香港教育局网站抓取学校数据
"""

import urllib.request
import urllib.error
import ssl
import re
import json
import time

def fetch_url(url):
    """获取URL内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
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

def find_school_lists(content):
    """查找页面中学校列表相关的链接"""
    links = re.findall(r'href="([^"]*)"', content)
    school_links = []

    keywords = ['school', 'sch', 'list', 'district', '查找', '學校']

    for link in links:
        if any(kw in link.lower() for kw in keywords):
            if link.startswith('http'):
                school_links.append(link)
            elif link.startswith('/'):
                school_links.append('https://www.edb.gov.hk' + link)

    return list(set(school_links))

def scrape_edb():
    """尝试从EDB网站抓取学校数据"""

    # 尝试多个可能的入口点
    base_urls = [
        "https://www.edb.gov.hk",
        "https://www.edb.gov.hk/en",
        "https://www.edb.gov.hk/tc",
    ]

    all_schools = []

    for base_url in base_urls:
        print(f"\n{'='*60}")
        print(f"Scanning: {base_url}")
        print(f"{'='*60}")

        content = fetch_url(base_url)
        if not content:
            print(f"Cannot fetch {base_url}")
            continue

        # 查找学校相关的链接
        school_links = find_school_lists(content)
        print(f"\nFound {len(school_links)} potential school-related links:")
        for link in school_links[:10]:
            print(f"  {link}")

        # 尝试访问一些链接
        for link in school_links[:5]:
            print(f"\nTrying: {link}")
            link_content = fetch_url(link)
            if link_content and len(link_content) > 1000:
                print(f"  Content length: {len(link_content)}")

                # 查找是否有学校数据
                if 'school' in link_content.lower() or '學校' in link_content:
                    print(f"  Contains school data!")

                    # 尝试提取学校信息
                    schools = extract_schools_from_content(link_content)
                    if schools:
                        all_schools.extend(schools)
                        print(f"  Extracted {len(schools)} schools")

    return all_schools

def extract_schools_from_content(content):
    """从页面内容中提取学校信息"""
    schools = []

    # 尝试多种模式提取学校名称
    patterns = [
        # English names
        r'([A-Z][A-Za-z\s\-\'\.]+(?:School|College|Primary|Kindergarten)[A-Za-z\s\-\'\.]*)',
        # 中文名称
        r'([\u4e00-\u9fff]+(?:小學|中學|學校|書院|幼兒園|幼稚園)[\u4e00-\u9fff]*)',
    ]

    # 查找学校表格或列表
    tables = re.findall(r'<table[^>]*>(.*?)</table>', content, re.DOTALL)
    for table in tables[:5]:  # 只检查前5个表格
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
        for row in rows[:10]:  # 每表检查前10行
            # 尝试提取学校信息
            school_info = extract_school_from_row(row)
            if school_info:
                schools.append(school_info)

    return schools

def extract_school_from_row(row):
    """从表格行中提取学校信息"""
    # 提取各种字段
    name = None
    name_cn = None
    address = None
    phone = None

    # 提取学校名
    name_match = re.search(r'>([^<]+(?:School|College|Primary|Kindergarten)[^<]*)<', row)
    if name_match:
        name = name_match.group(1).strip()

    # 提取中文名
    name_cn_match = re.search(r'([\u4e00-\u9fff]+(?:小學|中學|學校|書院|幼兒園|幼稚園)[^\n<]*)', row)
    if name_cn_match:
        name_cn = name_cn_match.group(1).strip()

    # 提取电话
    phone_match = re.search(r'(\d{8})', row)
    if phone_match:
        phone = phone_match.group(1)

    if name or name_cn:
        return {
            'name': name,
            'name_cn': name_cn,
            'address': address,
            'phone': phone,
        }

    return None

def save_to_json(schools, filename):
    """保存学校数据到JSON文件"""
    filepath = f"/Users/wangfeng/.openclaw/workspace/school-badge-website/scripts/{filename}"

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(schools, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(schools)} schools to {filepath}")

def main():
    """主函数"""
    print("=" * 60)
    print("Hong Kong EDB School Data Scraper (New Website)")
    print("=" * 60)

    schools = scrape_edb()

    if schools:
        print(f"\n{'='*60}")
        print(f"Total schools found: {len(schools)}")
        print(f"{'='*60}")

        save_to_json(schools, 'edb_districts.json')
    else:
        print("\nNo schools found. Website structure may have changed.")
        print("Please check the EDB website manually.")

        # 创建空的JSON文件结构
        districts = {
            "Islands": {"status": "completed", "schools": []},
            "Southern": {"status": "completed", "schools": []},
            "Wan Chai": {"status": "pending", "schools": []},
            "Kowloon City": {"status": "pending", "schools": []},
            "Kwun Tong": {"status": "pending", "schools": []},
            "Sai Kung": {"status": "pending", "schools": []},
            "Sham Shui Po": {"status": "pending", "schools": []},
            "Wong Tai Sin": {"status": "pending", "schools": []},
            "Yau Tsim Mong": {"status": "pending", "schools": []},
            "Northern": {"status": "pending", "schools": []},
            "Sha Tin": {"status": "pending", "schools": []},
            "Tai Po": {"status": "pending", "schools": []},
            "Tsuen Wan": {"status": "pending", "schools": []},
            "Tuen Mun": {"status": "pending", "schools": []},
            "Yuen Long": {"status": "pending", "schools": []},
        }

        save_to_json(districts, 'edb_districts.json')
        print("\nCreated edb_districts.json with pending status for all districts")

    return schools

if __name__ == '__main__':
    main()