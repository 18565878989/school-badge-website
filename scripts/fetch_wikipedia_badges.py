#!/usr/bin/env python3
"""
从Wikipedia获取学校校徽
"""

import sqlite3
import os
import requests
import time
import re
from urllib.parse import quote

# 配置
BADGES_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/badges'
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

os.makedirs(BADGES_DIR, exist_ok=True)

def get_wikipedia_logo_url(school_name):
    """从Wikipedia获取学校校徽URL"""
    try:
        # 搜索Wikipedia
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={quote(school_name)}&limit=1&namespace=0&format=json"
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        data = response.json()
        
        if len(data) > 1 and data[1]:
            title = data[1][0]
            # 获取页面信息
            info_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={quote(title)}&prop=pageimages&format=json&pithumbsize=500"
            response = requests.get(info_url, headers=HEADERS, timeout=10)
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'thumbnail' in page_data:
                    return page_data['thumbnail']['source']
        return None
    except Exception as e:
        print(f"  Wikipedia搜索失败: {e}")
        return None

def download_image(url, filepath):
    """下载图片"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return len(response.content)
    except Exception as e:
        print(f"  下载失败: {e}")
    return 0

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取需要抓取校徽的学校
    cursor.execute("""
        SELECT id, name, country
        FROM schools 
        WHERE (badge_url IS NULL OR badge_url = '' OR badge_url LIKE '%example.com%')
        AND website IS NOT NULL 
        AND website != ''
        AND website NOT LIKE '%example.com%'
        AND website NOT LIKE '%wikipedia.org%'
        ORDER BY RANDOM()
        LIMIT 30
    """)
    
    schools = cursor.fetchall()
    print(f"从Wikipedia获取校徽，共 {len(schools)} 所学校\n")
    
    success_count = 0
    for school in schools:
        school_id, name, country = school
        print(f"处理: {name} ({country})")
        
        # 从Wikipedia获取校徽
        logo_url = get_wikipedia_logo_url(name)
        if logo_url:
            print(f"  找到校徽: {logo_url[:80]}...")
            
            # 下载图片
            ext = 'png' if '.png' in logo_url else 'jpg'
            filename = f"{school_id}.{ext}"
            filepath = os.path.join(BADGES_DIR, filename)
            size = download_image(logo_url, filepath)
            
            if size > 1000:
                badge_url = f"/static/images/badges/{filename}"
                cursor.execute("UPDATE schools SET badge_url = ? WHERE id = ?", (badge_url, school_id))
                print(f"  ✓ 保存成功 ({size} bytes)")
                success_count += 1
                time.sleep(1)
            else:
                print(f"  ✗ 下载失败")
        else:
            print(f"  ✗ 未找到校徽")
        
        conn.commit()
    
    print(f"\n完成! 成功获取 {success_count} 所学校的校徽")
    conn.close()

if __name__ == '__main__':
    main()
