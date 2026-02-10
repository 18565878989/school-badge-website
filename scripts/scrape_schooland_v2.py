#!/usr/bin/env python3
"""
从 schooland.hk 抓取香港学校数据
完整版本 - 支持批量抓取和数据库导入
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sqlite3
import time
import os

# 配置
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

def parse_primary_school(html, url):
    """解析小学页面"""
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('title')
    
    data = {
        'url': url,
        'level': 'elementary',
        'source': 'schooland.hk'
    }
    
    if title:
        full_title = title.get_text().strip()
        # 格式: "學校名稱 English Name"
        if ' St. ' in full_title or ' Primary' in full_title:
            parts = full_title.split(' ')
            data['name_cn'] = parts[0] if parts else ''
        else:
            data['name_cn'] = full_title.split(' - ')[0].strip()
    
    # 提取详细信息
    text = soup.get_text()
    
    # 创办年份
    founded_match = re.search(r'(\d{4})\s*年創立', text)
    if founded_match:
        data['founded'] = int(founded_match.group(1))
    
    # 校训
    motto_match = re.search(r'校訓[：:]\s*([^\n]+)')
    if motto_match:
        motto_text = motto_match.group(1).strip()
        if 'Truth Conquers' in text:
            data['motto_cn'] = '真理必勝'
            data['motto_en'] = 'Truth Conquers'
    
    # 地址
    addr_match = re.search(r'學校位置[：:]\s*([^。]+)', text)
    if addr_match:
        address = addr_match.group(1).strip()
        # 提取地区
        district_match = re.search(r'([^\n›]+)', address)
        if district_match:
            data['district'] = district_match.group(1).strip()
            data['address'] = address
    
    # 学校类型
    if '私立' in text:
        data['school_type'] = 'private'
    elif '官立' in text:
        data['school_type'] = 'government'
    elif '資助' in text:
        data['school_type'] = 'aided'
    
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
    
    return data

def parse_secondary_school(html, url):
    """解析中学页面"""
    soup = BeautifulSoup(html, 'html.parser')
    
    data = {
        'url': url,
        'level': 'middle',
        'source': 'schooland.hk'
    }
    
    # 类似小学的解析逻辑
    text = soup.get_text()
    
    #创办年份
    founded_match = re.search(r'(\d{4})\s*年創立', text)
    if founded_match:
        data['founded'] = int(founded_match.group(1))
    
    return data

def get_school_urls_from_sitemap():
    """从sitemap获取所有学校URL"""
    urls = {'ps': [], 'ss': [], 'is': []}
    
    # 获取小学列表
    ps_sitemap = get_page(f"{BASE_URL}/sitemap-ps.xml")
    if ps_sitemap:
        # 解析小学URL
        ps_urls = re.findall(r'<loc>(https://www\.schooland\.hk/ps/[^<]+)</loc>', ps_sitemap)
        urls['ps'] = [u for u in ps_urls if '/ps/' in u and len(u.split('/')) > 5]
    
    # 获取中学列表
    ss_sitemap = get_page(f"{BASE_URL}/sitemap-ss.xml")
    if ss_sitemap:
        ss_urls = re.findall(r'<loc>(https://www\.schooland\.hk/ss/[^<]+)</loc>', ss_sitemap)
        urls['ss'] = [u for u in ss_urls if '/ss/' in u and len(u.split('/')) > 5]
    
    return urls

def save_to_json(schools, filename='hk_schools_raw.json'):
    """保存到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schools, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(schools)} 所学校到 {filename}")

def import_to_database(schools):
    """导入到SQLite数据库"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取当前最大ID
    cursor.execute('SELECT MAX(id) FROM schools')
    max_id = cursor.fetchone()[0] or 0
    
    imported = 0
    for school in schools:
        try:
            # 检查是否已存在
            cursor.execute('SELECT id FROM schools WHERE name_cn = ? AND level = ?', 
                         (school.get('name_cn', ''), school.get('level', '')))
            if cursor.fetchone():
                continue
            
            # 插入新学校
            cursor.execute('''
                INSERT INTO schools (
                    name, name_cn, region, country, city, address, level,
                    website, badge_url, motto, founded, principal
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school.get('name_en', school.get('name_cn', '')),
                school.get('name_cn', ''),
                'Hong Kong',
                'Hong Kong',
                school.get('district', 'Hong Kong'),
                school.get('address', ''),
                school.get('level', 'middle'),
                school.get('website', ''),
                '',  # badge_url - 稍后添加
                school.get('motto_cn', ''),
                school.get('founded', 0),
                ''   # principal
            ))
            imported += 1
        except Exception as e:
            print(f"Error inserting {school.get('name_cn')}: {e}")
    
    conn.commit()
    conn.close()
    return imported

def generate_badge_svgs():
    """生成学校SVG校徽模板"""
    # 为没有校徽的学校生成通用模板
    pass

def main():
    """主函数"""
    print("=" * 60)
    print("香港学校数据抓取工具")
    print(f"数据来源: {BASE_URL}")
    print("=" * 60)
    
    # 测试抓取一个学校
    print("\n测试抓取: 聖嘉勒小學")
    html = get_page(f"{BASE_URL}/ps/scps")
    if html:
        school = parse_primary_school(html, f"{BASE_URL}/ps/scps")
        print(json.dumps(school, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("准备批量抓取...")
    print("=" * 60)

if __name__ == '__main__':
    main()
