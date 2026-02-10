#!/usr/bin/env python3
import urllib.request
from html.parser import HTMLParser
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# 尝试多个可能的URL
urls_to_try = [
    "https://www.edb.gov.hk/en/sch-admin/school-information/school-list/index.html",
    "https://www.edb.gov.hk/en/sch-admin/school-information.html",
    "https://www.edb.gov.hk/en/sch-admin.html",
    "https://schools.edb.gov.hk/",
]

for url in urls_to_try:
    print(f"\n{'='*60}")
    print(f"Trying: {url}")
    print(f"{'='*60}")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            print(f"Status: {response.status}")
            print(f"Content length: {len(content)}")

            if response.status == 200:
                # 查找所有链接
                links = re.findall(r'href="([^"]*)"', content)
                school_links = [link for link in links if 'school' in link.lower()]

                print(f"\nLinks containing 'school':")
                for link in set(school_links)[:20]:
                    print(f"  {link}")

                # 查找可能的学校数据（JSON格式）
                json_data = re.findall(r'(\{[^{}]*school[^{}]*\})', content, re.IGNORECASE)
                if json_data:
                    print(f"\nFound potential JSON data with 'school':")
                    for data in json_data[:5]:
                        print(f"  {data[:200]}")

    except Exception as e:
        print(f"Error: {e}")