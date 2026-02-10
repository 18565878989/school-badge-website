#!/usr/bin/env python3
"""
从 schooland.hk 批量抓取香港学校数据
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sqlite3
import time
import os
from urllib.parse import urljoin

BASE_URL = "https://www.schooland.hk"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def get_page(url):
    """获取页面内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'utf-8'
        return response.text if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_school_page(html, url, category):
    """解析学校页面"""
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    data = {
        'url': url,
        'level': category,  # ps, ss, is
        'region': 'Hong Kong',
        'country': 'Hong Kong'
    }
    
    # 从标题提取学校名称
    title = soup.find('title')
    if title:
        full_title = title.get_text().strip()
        # 通常格式: "學校名稱 English Name - Schooland.hk"
        if ' - ' in full_title:
            parts = full_title.split(' - ')
            data['name_cn'] = parts[0].strip()
            data['name'] = parts[1].strip() if len(parts) > 1 else data['name_cn']
        else:
            data['name_cn'] = full_title
            data['name'] = full_title
    
    # 创办年份
    founded_match = re.search(r'(\d{4})\s*年創立', text)
    if founded_match:
        data['founded'] = int(founded_match.group(1))
    
    # 校训
    motto_match = re.search(r'校訓[：:]\s*([^\n。]+)', text)
    if motto_match:
        data['motto'] = motto_match.group(1).strip()
    
    # 地址
    addr_match = re.search(r'學校位置[：:]\s*([^。\n]+)', text)
    if addr_match:
        address = addr_match.group(1).strip()
        # 提取地区
        if '›' in address:
            parts = address.split('›')
            data['city'] = parts[-1].strip() if len(parts) > 1 else 'Hong Kong'
            data['address'] = address
        else:
            data['city'] = 'Hong Kong'
            data['address'] = address
    
    # 学校类型
    if '私立' in text:
        data['school_type'] = 'private'
    elif '官立' in text:
        data['school_type'] = 'government'
    elif '資助' in text:
        data['school_type'] = 'aided'
    elif '直資' in text:
        data['school_type'] = 'direct_subsidized'
    
    # 性别
    if '女校' in text:
        data['gender'] = 'girls'
    elif '男校' in text:
        data['gender'] = 'boys'
    else:
        data['gender'] = 'coed'
    
    # 宗教
    if '天主教' in text:
        data['religion'] = 'catholic'
    elif '基督教' in text:
        data['religion'] = 'christian'
    elif '佛教' in text:
        data['religion'] = 'buddhist'
    
    # 官网
    website_match = re.search(r'官網[：:]\s*(https?://[^\s]+)', text)
    if website_match:
        data['website'] = website_match.group(1).strip()
    
    # 简介
    desc_match = re.search(r'辦學宗旨[：:]\s*([^。]+)', text)
    if desc_match:
        data['description'] = desc_match.group(1).strip()[:200]
    
    return data

def get_all_school_urls(category):
    """获取某个分类下所有学校URL"""
    urls = []
    
    # 分页获取学校列表
    page = 1
    while True:
        if category == 'ps':
            list_url = f"{BASE_URL}/ps?page={page}"
        elif category == 'ss':
            list_url = f"{BASE_URL}/ss?page={page}"
        else:
            list_url = f"{BASE_URL}/{category}?page={page}"
        
        html = get_page(list_url)
        if not html:
            break
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找学校链接
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if f'/{category}/' in href and len(href.split('/')) > 2:
                full_url = urljoin(BASE_URL, href)
                if full_url not in urls:
                    urls.append(full_url)
        
        # 检查是否还有下一页
        if '下一頁' not in text if (text := soup.get_text()) else '' and '下一頁' not in html:
            break
        
        page += 1
        time.sleep(0.5)
    
    return list(set(urls))

def scrape_category(category, max_schools=100):
    """抓取某个分类的学校数据"""
    print(f"\n{'='*60}")
    print(f"开始抓取 {category.upper()} (最多 {max_schools} 所)")
    print(f"{'='*60}")
    
    schools = []
    
    # 尝试获取学校列表页面
    if category == 'ps':
        list_url = f"{BASE_URL}/ps"
    elif category == 'ss':
        list_url = f"{BASE_URL}/ss"
    else:
        list_url = f"{BASE_URL}/{category}"
    
    html = get_page(list_url)
    if not html:
        print(f"无法获取列表页面: {list_url}")
        return schools
    
    # 从主页获取学校链接
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    
    school_urls = set()
    for link in links:
        href = link['href']
        # 匹配 /ps/xxx, /ss/xxx, /is/xxx 格式
        if re.match(f'/({category})/[^/]+$', href):
            full_url = urljoin(BASE_URL, href)
            school_urls.add(full_url)
    
    print(f"找到 {len(school_urls)} 个学校链接")
    
    # 抓取每个学校
    for i, url in enumerate(list(school_urls)[:max_schools], 1):
        print(f"  [{i}/{min(len(school_urls), max_schools)}] {url}")
        
        html = get_page(url)
        if html:
            school = parse_school_page(html, url, category)
            schools.append(school)
        
        time.sleep(0.3)
    
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
            name_check = school.get('name_cn', '') or school.get('name', '')
            cursor.execute(
                'SELECT id FROM schools WHERE name_cn = ? AND level = ?',
                (name_check, school.get('level', ''))
            )
            if cursor.fetchone():
                continue
            
            # 插入
            cursor.execute('''
                INSERT INTO schools (
                    name, name_cn, region, country, city, address, level,
                    description, website, badge_url, motto, founded
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school.get('name', name_check),
                school.get('name_cn', ''),
                school.get('region', 'Hong Kong'),
                school.get('country', 'Hong Kong'),
                school.get('city', 'Hong Kong'),
                school.get('address', ''),
                school.get('level', 'middle'),
                school.get('description', ''),
                school.get('website', ''),
                '',  # badge_url
                school.get('motto', ''),
                school.get('founded', 0)
            ))
            imported += 1
            
        except Exception as e:
            print(f"    错误: {e}")
    
    conn.commit()
    conn.close()
    return imported

def main():
    """主函数"""
    print("=" * 60)
    print("Schooland.hk 香港学校数据抓取工具")
    print("=" * 60)
    
    all_schools = []
    
    # 抓取小学
    ps_schools = scrape_category('ps', max_schools=500)
    all_schools.extend(ps_schools)
    
    # 抓取中学
    ss_schools = scrape_category('ss', max_schools=500)
    all_schools.extend(ss_schools)
    
    # 抓取国际学校
    is_schools = scrape_category('is', max_schools=100)
    all_schools.extend(is_schools)
    
    # 保存到JSON
    output_file = 'data/schooland_hk_schools.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_schools, f, ensure_ascii=False, indent=2)
    print(f"\n已保存 {len(all_schools)} 所学校到 {output_file}")
    
    # 导入数据库
    imported = import_to_database(all_schools)
    print(f"\n成功导入数据库: {imported} 所")
    
    return all_schools

if __name__ == '__main__':
    main()
