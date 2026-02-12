#!/usr/bin/env python3
"""
从Wikipedia和Unsplash获取学校校园照片
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import re
import time

def fetch_url(url):
    """获取URL内容"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return json.loads(resp.read().decode('utf-8'))
            else:
                return resp.read().decode('utf-8')
    except Exception as e:
        return None

def fetch_from_wikipedia(school_name):
    """从Wikipedia API获取学校图片"""
    # 搜索学校
    search_url = f"https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': school_name,
        'format': 'json',
        'origin': '*'
    }
    
    url = f"{search_url}?{urllib.parse.urlencode(params)}"
    data = fetch_url(url)
    
    if data and 'query' in data and 'search' in data and data['search']:
        # 获取第一个搜索结果
        title = data['search'][0]['title']
        
        # 获取页面图片
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'pageimages|extracts',
            'pithumbsize': 800,
            'explaintext': True,
            'format': 'json',
            'origin': '*'
        }
        
        url = f"{search_url}?{urllib.parse.urlencode(params)}"
        data = fetch_url(url)
        
        if data and 'query' in data and 'pages' in data:
            pages = data['query']['pages']
            for page_id, page_info in pages.items():
                if page_id != '-1' and 'thumbnail' in page_info:
                    return page_info['thumbnail']['source']
    
    return None

def fetch_from_unsplash(query, city='', country=''):
    """从Unsplash获取校园照片"""
    # 如果有 Unsplash API Key，可以使用
    # 这里使用Unsplash的直接搜索URL（可能需要API）
    
    # 尝试使用 Unsplash Source（已弃用，改用直接搜索）
    search_query = f"{query} university campus"
    if city:
        search_query += f" {city}"
    if country:
        search_query += f" {country}"
    
    # 返回Unsplash搜索链接（实际使用时需要API）
    return None

def update_campus_images(limit=100):
    """更新学校校园照片"""
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取没有校园照片的学校（优先处理有中文名的学校）
    cursor.execute("""
        SELECT id, name, name_cn, city, country 
        FROM schools 
        WHERE (campus_image IS NULL OR campus_image = '')
        AND name_cn IS NOT NULL AND name_cn != ''
        ORDER BY RANDOM()
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    
    print(f"需要获取校园照片的学校: {len(schools)}")
    
    success = 0
    failed = 0
    checked = 0
    
    for school_id, name, name_cn, city, country in schools:
        checked += 1
        
        # 优先用中文名搜索
        search_name = name_cn if name_cn else name
        
        # 尝试Wikipedia
        campus_url = fetch_from_wikipedia(search_name)
        
        if campus_url:
            cursor.execute("UPDATE schools SET campus_image=? WHERE id=?", (campus_url, school_id))
            success += 1
            print(f"{checked}. ✓ {name_cn[:40]} ({name[:30]})")
        else:
            failed += 1
            if checked <= 15:
                print(f"{checked}. ✗ {name_cn[:40]} ({name[:30]})")
        
        time.sleep(0.3)
    
    conn.commit()
    
    # 统计更新后的数据
    cursor.execute("SELECT COUNT(*) FROM schools WHERE campus_image IS NOT NULL AND campus_image != ''")
    total_with_campus = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n完成! 成功: {success}, 失败: {failed}")
    print(f"有校园照片的学校总数: {total_with_campus}")
    return success

def main():
    """主函数"""
    print("=" * 70)
    print("从Wikipedia获取学校校园照片")
    print("=" * 70)
    
    success = update_campus_images(limit=50)
    
    print(f"\n成功获取 {success} 张校园照片")

if __name__ == '__main__':
    main()
