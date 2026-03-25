#!/usr/bin/env python3
"""
从Wikipedia下载学校校园照片（直接存本地）
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import os
import time

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
CAMPUS_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/campus'

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

def download_image(url, save_path):
    """下载图片到本地"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            content_type = resp.headers.get('Content-Type', '').lower()
            
            # 根据Content-Type确定扩展名
            if 'image/webp' in content_type:
                ext = '.webp'
            elif 'image/png' in content_type:
                ext = '.png'
            elif 'image/gif' in content_type:
                ext = '.gif'
            else:
                ext = '.jpg'
            
            # 检查文件头
            if not ext:
                if content[:3] == b'\xff\xd8\xff':
                    ext = '.jpg'
                elif content[:4] == b'\x89PNG':
                    ext = '.png'
                elif content[:4] == b'RIFF' and b'WEBP' in content[:12]:
                    ext = '.webp'
                else:
                    ext = '.jpg'
            
            final_path = save_path.rsplit('.', 1)[0] + ext
            with open(final_path, 'wb') as f:
                f.write(content)
            
            size = os.path.getsize(final_path)
            if size > 5000:
                return final_path
            else:
                os.remove(final_path)
                return None
    except Exception as e:
        return None

def fetch_from_wikipedia(school_name, school_id):
    """从Wikipedia下载学校图片到本地"""
    # 搜索学校
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': school_name,
        'format': 'json',
        'origin': '*'
    }
    
    url = f"{search_url}?{urllib.parse.urlencode(params)}"
    data = fetch_url(url)
    
    if not data or 'query' not in data or 'search' not in data or not data['search']:
        return None
    
    title = data['search'][0]['title']
    
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
    data = fetch_url(url)
    
    if not data or 'query' not in data or 'pages' not in data:
        return None
    
    pages = data['query']['pages']
    for page_id, page_info in pages.items():
        if page_id != '-1' and 'thumbnail' in page_info:
            image_url = page_info['thumbnail']['source']
            
            # 创建本地目录
            school_dir = os.path.join(CAMPUS_DIR, f"school_{school_id}")
            os.makedirs(school_dir, exist_ok=True)
            
            # 下载第一张图片
            save_path = os.path.join(school_dir, f"school_{school_id}_1.jpg")
            result = download_image(image_url, save_path)
            
            if result:
                return result
    
    return None

def update_campus_images(limit=50):
    """更新学校校园照片（下载到本地）"""
    conn = sqlite3.connect(DB_PATH)
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
    
    for school_id, name, name_cn, city, country in schools:
        search_name = name_cn if name_cn else name
        if not search_name:
            continue
        
        local_path = fetch_from_wikipedia(search_name, school_id)
        
        if local_path:
            # 转换为URL相对路径
            url_path = local_path.replace('/Users/wangfeng/.openclaw/workspace/school-badge-website', '')
            cursor.execute("UPDATE schools SET campus_image=? WHERE id=?", (url_path, school_id))
            success += 1
            print(f"  ✓ {name_cn[:40]} -> {os.path.basename(local_path)}")
        else:
            failed += 1
            print(f"  ✗ {name_cn[:40]}")
        
        time.sleep(0.3)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE campus_image IS NOT NULL AND campus_image != ''")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n完成! 成功: {success}, 失败: {failed}")
    print(f"有校园照片的学校总数: {total}")
    return success

if __name__ == '__main__':
    print("=" * 70)
    print("从Wikipedia下载学校校园照片（存本地）")
    print("=" * 70)
    
    update_campus_images(limit=50)
