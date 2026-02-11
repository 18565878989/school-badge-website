#!/usr/bin/env python3
import urllib.request
import re

def fetch_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# 搜索香港教育局网站上的学校列表
base_url = "https://www.edb.gov.hk"

# 首先获取主页
print("Fetching main page...")
main_content = fetch_url(base_url)
if main_content:
    print(f"Main page length: {len(main_content)}")

    # 查找所有链接
    all_links = re.findall(r'href="([^"]*)"', main_content)

    # 打印一些示例链接看看结构
    print(f"\nSample links found ({len(all_links)} total):")
    for link in list(all_links)[:20]:
        print(f"  {link}")

    # 筛选可能的学校相关链接
    school_keywords = ['school', 'sch-admin', 'school-list', 'education']
    potential_links = []

    for link in set(all_links):
        for keyword in school_keywords:
            if keyword in link.lower():
                potential_links.append(link)
                break

    print(f"\nFound {len(potential_links)} potential school-related links:")
    for link in potential_links[:30]:
        print(f"  {link}")

# 尝试一些已知的可能路径
possible_paths = [
    '/en/sch-admin/',
    '/en/sch-admin/school-information/',
    '/tc/sch-admin/',
    '/sc/sch-admin/',
    '/en/sch-info/',
    '/sch-info/',
    '/en/school/',
    '/school-list/',
    '/en/edu-school/',
]

print(f"\n{'='*60}")
print("Trying common paths...")
print(f"{'='*60}")

for path in possible_paths:
    url = base_url + path
    content = fetch_url(url)
    if content and len(content) > 1000 and '404' not in content[:500]:
        print(f"✓ Found: {url} (length: {len(content)})")
    else:
        print(f"✗ Not found or empty: {url}")

# 尝试一些外部可能的数据源
external_urls = [
    "https://data.gov.hk/api/3/action/package_show?id=edb-school-list",
    "https://www.gov.hk/en/residents/",
]

print(f"\n{'='*60}")
print("Trying external data sources...")
print(f"{'='*60}")

for url in external_urls:
    content = fetch_url(url)
    if content and len(content) > 100:
        print(f"✓ Found: {url} (length: {len(content)})")
        print(f"  Content preview: {content[:200]}...")
    else:
        print(f"✗ Not found: {url}")