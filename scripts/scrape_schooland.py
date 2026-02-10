#!/usr/bin/env python3
"""
从 schooland.hk 抓取香港学校数据
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sqlite3

BASE_URL = "https://www.schooland.hk"

# 小学列表
PS_URLS = [
    "https://www.schooland.hk/ps/scps",
    "https://www.schooland.hk/ps/salesian",
    "https://www.schooland.hk/ps/stmatthew",
    # ... 更多学校
]

def get_school_data(url):
    """获取单个学校页面数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取学校信息
        data = {'url': url}
        
        # 学校名称
        title = soup.find('title')
        if title:
            name_match = re.search(r'^(.+?)\s*[-|]\s*.+', title.text)
            if name_match:
                data['name'] = name_match.group(1).strip()
            else:
                data['name'] = title.text.strip()
        
        # 尝试从页面提取更多信息
        # 这是一个简化的版本，实际需要根据页面结构调整
        
        return data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_school_page(html):
    """解析学校详情页面"""
    soup = BeautifulSoup(html, 'html.parser')
    
    data = {}
    
    # 提取学校名称
    title = soup.find('title')
    if title:
        title_text = title.get_text().strip()
        # 格式通常是: 學校名稱 - Schooland.hk
        parts = title_text.split(' - ')
        if parts:
            data['name_cn'] = parts[0].strip()
    
    # 提取学校类型 (ps=小学, ss=中学, is=国际学校)
    url = soup.find('link', rel='canonical')
    if url and 'ps/' in url.get('href', ''):
        data['level'] = 'elementary'
    elif url and 'ss/' in url.get('href', ''):
        data['level'] = 'middle'
    elif url and 'is/' in url.get('href', ''):
        data['level'] = 'international'
    
    return data

def scrape_schools():
    """抓取所有学校数据"""
    all_schools = []
    
    # 抓取小学
    print("抓取小学数据...")
    ps_response = requests.get(f"{BASE_URL}/ps/", headers={'User-Agent': 'Mozilla/5.0'})
    if ps_response.status_code == 200:
        # 解析小学列表页面
        pass
    
    # 抓取中学
    print("抓取中学数据...")
    ss_response = requests.get(f"{BASE_URL}/ss/", headers={'User-Agent': 'Mozilla/5.0'})
    if ss_response.status_code == 200:
        pass
    
    return all_schools

def save_to_database(schools):
    """保存到数据库"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    for school in schools:
        try:
            cursor.execute('''
                INSERT INTO schools (name, name_cn, region, country, city, level, website, motto, founded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school.get('name', ''),
                school.get('name_cn', ''),
                'Hong Kong',
                'Hong Kong',
                school.get('district', 'Hong Kong'),
                school.get('level', 'middle'),
                school.get('website', ''),
                school.get('motto', ''),
                school.get('founded', 0)
            ))
        except Exception as e:
            print(f"Error inserting {school.get('name_cn')}: {e}")
    
    conn.commit()
    conn.close()
    print(f"已保存 {len(schools)} 所学校到数据库")

if __name__ == '__main__':
    print("=" * 60)
    print("香港学校数据抓取工具")
    print("=" * 60)
    print(f"数据来源: {BASE_URL}")
    print("=" * 60)
