#!/usr/bin/env python3
"""
批量获取学校校园照片 - 从Wikipedia下载到本地
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import os
import time

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
CAMPUS_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/campus'

def download_image(url, save_path):
    """下载图片到本地，返回实际保存路径"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            content_type = resp.headers.get('Content-Type', '').lower()
            
            if 'image/webp' in content_type:
                ext = '.webp'
            elif 'image/png' in content_type:
                ext = '.png'
            elif 'image/gif' in content_type:
                ext = '.gif'
            else:
                ext = '.jpg'
            
            # 检查文件头
            if content[:3] == b'\xff\xd8\xff':
                ext = '.jpg'
            elif content[:4] == b'\x89PNG':
                ext = '.png'
            elif content[:4] == b'RIFF' and b'WEBP' in content[:12]:
                ext = '.webp'
            
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

def fetch_wikipedia_images(school_name, school_id, max_images=6):
    """从Wikipedia API下载学校多张图片到本地"""
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
        
        if not data.get('query', {}).get('search'):
            return []
        
        title = data['query']['search'][0]['title']
        
        # 获取页面所有图片
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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        pages = data.get('query', {}).get('pages', {})
        image_urls = []
        for page_id, page_info in pages.items():
            if page_id != '-1' and 'thumbnail' in page_info:
                image_urls.append(page_info['thumbnail']['source'])
        
        if not image_urls:
            return []
        
        # 创建目录
        school_dir = os.path.join(CAMPUS_DIR, f"school_{school_id}")
        os.makedirs(school_dir, exist_ok=True)
        
        # 已有图片数
        existing = [f for f in os.listdir(school_dir) if f.startswith(f"school_{school_id}_")]
        start_idx = len(existing) + 1
        
        saved = []
        for i, img_url in enumerate(image_urls):
            if len(saved) >= max_images:
                break
            save_path = os.path.join(school_dir, f"school_{school_id}_{start_idx + i}.jpg")
            result = download_image(img_url, save_path)
            if result:
                saved.append(result)
                time.sleep(0.3)
        
        return saved
        
    except Exception as e:
        return []

def process_school(school_data):
    """处理单个学校"""
    school_id, name, name_cn, city, country = school_data
    
    search_name = name_cn if name_cn else name
    if not search_name:
        return (school_id, [], False)
    
    saved = fetch_wikipedia_images(search_name, school_id, max_images=6)
    
    if saved:
        return (school_id, saved, True)
    
    if name_cn:
        saved = fetch_wikipedia_images(name, school_id, max_images=6)
        if saved:
            return (school_id, saved, True)
    
    return (school_id, [], False)

def update_campus_images(limit=200):
    """批量更新学校校园照片（下载到本地）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, name_cn, city, country 
        FROM schools 
        WHERE campus_reviewed = 0
        AND (campus_image IS NULL OR campus_image = '')
        AND name_cn IS NOT NULL AND name_cn != ''
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    print(f"需要获取校园照片的学校: {len(schools)}")
    start_time = time.time()
    
    success = 0
    failed = 0
    
    for school_data in schools:
        school_id, saved, ok = process_school(school_data)
        
        if ok and saved:
            # 转换为URL相对路径
            url_paths = []
            for p in saved:
                url_path = p.replace('/Users/wangfeng/.openclaw/workspace/school-badge-website', '')
                url_paths.append(url_path)
            
            cursor.execute("UPDATE schools SET campus_image=? WHERE id=?", (','.join(url_paths), school_id))
            success += 1
            print(f"  ✓ ID={school_id} 下载了 {len(saved)} 张")
        else:
            failed += 1
        
        time.sleep(0.2)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE campus_image IS NOT NULL AND campus_image != ''")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    elapsed = time.time() - start_time
    print(f"\n完成! 耗时: {elapsed:.1f}秒")
    print(f"成功: {success}, 跳过/失败: {failed}")
    print(f"有校园照片的学校总数: {total}")
    return success

if __name__ == '__main__':
    print("=" * 70)
    print("批量获取学校校园照片 - 从Wikipedia下载到本地")
    print("=" * 70)
    
    update_campus_images(limit=200)
