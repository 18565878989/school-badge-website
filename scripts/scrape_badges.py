#!/usr/bin/env python3
"""
学校高清校徽抓取脚本
从学校官网抓取高清校徽/图标
"""

import sqlite3
import os
import subprocess
import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time

# 配置
BADGES_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/badges'
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

os.makedirs(BADGES_DIR, exist_ok=True)

def get_domain(url):
    """提取域名"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return None

def try_download_favicon(domain, school_id):
    """尝试下载favicon"""
    # 方式1: 直接获取favicon.ico
    favicon_url = f"https://{domain}/favicon.ico"
    try:
        response = requests.get(favicon_url, headers=HEADERS, timeout=5)
        if response.status_code == 200 and len(response.content) > 500:
            filename = f"{school_id}.ico"
            filepath = os.path.join(BADGES_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return f"/static/images/badges/{filename}", len(response.content)
    except:
        pass
    return None, 0

def try_extract_from_html(url, domain, school_id):
    """从HTML中提取校徽链接"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找各种logo/favicon链接
        selectors = [
            ('link', 'rel', 'icon'),
            ('link', 'rel', 'shortcut icon'),
            ('link', 'rel', 'apple-touch-icon'),
            ('link', 'rel', 'apple-touch-icon-precomposed'),
            ('img', 'class', 'logo'),
            ('img', 'id', 'logo'),
            ('img', 'src', 'logo'),
        ]
        
        for tag, attr, value in selectors:
            for img in soup.find_all(tag):
                if img.get(attr) and value in str(img.get(attr)):
                    src = img.get('src') or img.get('href')
                    if src and not src.startswith('data:'):
                        full_url = urljoin(url, src)
                        # 下载图片
                        img_response = requests.get(full_url, headers=HEADERS, timeout=10)
                        if img_response.status_code == 200 and len(img_response.content) > 1000:
                            # 判断文件类型
                            content_type = img_response.headers.get('Content-Type', '')
                            ext = 'png'
                            if 'image/jpeg' in content_type:
                                ext = 'jpg'
                            elif 'image/svg' in content_type:
                                ext = 'svg'
                            elif 'image/x-icon' in content_type:
                                ext = 'ico'
                            
                            filename = f"{school_id}.{ext}"
                            filepath = os.path.join(BADGES_DIR, filename)
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                            return f"/static/images/badges/{filename}", len(img_response.content)
        return None
    except Exception as e:
        return None

def process_school(school_id, name, website, country):
    """处理单个学校"""
    domain = get_domain(website)
    if not domain:
        return None
    
    print(f"  尝试抓取: {name} ({domain})")
    
    # 方式1: 尝试favicon.ico
    badge_url, size = try_download_favicon(domain, school_id)
    if badge_url and size > 500:
        print(f"    ✓ favicon.ico 获取成功 ({size} bytes)")
        return badge_url
    
    # 方式2: 从HTML提取
    badge_url = try_extract_from_html(website, domain, school_id)
    if badge_url:
        print(f"    ✓ HTML中提取成功: {badge_url}")
        return badge_url
    
    print(f"    ✗ 未能获取校徽")
    return None

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取需要抓取校徽的学校
    cursor.execute("""
        SELECT id, name, website, country
        FROM schools 
        WHERE region IN ('Asia', 'North America', 'Europe')
        AND website IS NOT NULL 
        AND website != ''
        AND website NOT LIKE '%example.com%'
        AND website NOT LIKE '%wikipedia.org%'
        AND (badge_url IS NULL OR badge_url = '' OR badge_url LIKE '%example.com%')
        LIMIT 50
    """)
    
    schools = cursor.fetchall()
    print(f"开始抓取校徽，共 {len(schools)} 所学校\n")
    
    success_count = 0
    for school in schools:
        school_id, name, website, country = school
        
        # 清理旧的可能无效的badge_url
        cursor.execute("SELECT badge_url FROM schools WHERE id = ?", (school_id,))
        current = cursor.fetchone()
        if current and current[0] and 'example.com' in current[0]:
            # 先尝试获取新的
            result = process_school(school_id, name, website, country)
            if result:
                cursor.execute("UPDATE schools SET badge_url = ? WHERE id = ?", (result, school_id))
                success_count += 1
                time.sleep(0.5)  # 避免请求过快
        
        conn.commit()
    
    print(f"\n完成! 成功更新 {success_count} 所学校的校徽")
    conn.close()

if __name__ == '__main__':
    main()
