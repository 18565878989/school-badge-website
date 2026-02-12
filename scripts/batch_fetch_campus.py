#!/usr/bin/env python3
"""
批量获取学校校园照片 - 从Wikipedia和学校官网
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import re
import concurrent.futures
import time
from datetime import datetime

def fetch_wikipedia_image(school_name):
    """从Wikipedia API获取学校图片"""
    try:
        # 搜索学校
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': school_name,
            'format': 'json',
            'origin': '*',
            'utf8': ''
        }
        
        url = f"{search_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Accept': 'application/json'
        })
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            if data.get('query', {}).get('search'):
                title = data['query']['search'][0]['title']
                
                # 获取页面图片
                params = {
                    'action': 'query',
                    'titles': title,
                    'prop': 'pageimages',
                    'pithumbsize': 1200,
                    'format': 'json',
                    'origin': '*'
                }
                
                url = f"{search_url}?{urllib.parse.urlencode(params)}"
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                    'Accept': 'application/json'
                })
                
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    pages = data.get('query', {}).get('pages', {})
                    for page_id, page_info in pages.items():
                        if page_id != '-1' and 'thumbnail' in page_info:
                            return page_info['thumbnail']['source']
    except Exception as e:
        pass
    return None

def process_school(school_data):
    """处理单个学校"""
    school_id, name, name_cn, city, country = school_data
    
    # 优先用中文名搜索
    search_name = name_cn if name_cn else name
    if not search_name:
        return (school_id, None, False)
    
    campus_url = fetch_wikipedia_image(search_name)
    
    if campus_url:
        return (school_id, campus_url, True)
    
    # 如果中文名失败，尝试英文名
    if name_cn:
        campus_url = fetch_wikipedia_image(name)
        if campus_url:
            return (school_id, campus_url, True)
    
    return (school_id, None, False)

def update_campus_images(limit=200):
    """批量更新学校校园照片"""
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取没有校园照片的学校（优先处理有中文名的学校）
    cursor.execute("""
        SELECT id, name, name_cn, city, country 
        FROM schools 
        WHERE (campus_image IS NULL OR campus_image = '')
        AND name_cn IS NOT NULL AND name_cn != ''
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    
    print(f"需要获取校园照片的学校: {len(schools)}")
    start_time = time.time()
    
    success = 0
    failed = 0
    
    # 使用线程池并发处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_school, schools))
    
    # 更新数据库
    for school_id, campus_url, is_success in results:
        if is_success and campus_url:
            cursor.execute("UPDATE schools SET campus_image=? WHERE id=?", (campus_url, school_id))
            success += 1
            
    conn.commit()
    
    # 统计更新后的数据
    cursor.execute("SELECT COUNT(*) FROM schools WHERE campus_image IS NOT NULL AND campus_image != ''")
    total_with_campus = cursor.fetchone()[0]
    
    conn.close()
    
    elapsed = time.time() - start_time
    print(f"\n完成! 耗时: {elapsed:.1f}秒")
    print(f"成功: {success}, 跳过/失败: {len(schools) - success}")
    print(f"有校园照片的学校总数: {total_with_campus}")
    return success

if __name__ == '__main__':
    print("=" * 70)
    print("批量获取学校校园照片 - 从Wikipedia")
    print("=" * 70)
    
    success = update_campus_images(limit=200)
    print(f"\n成功获取 {success} 张校园照片")
