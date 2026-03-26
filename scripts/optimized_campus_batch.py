#!/usr/bin/env python3
"""
优化版批量校园图片抓取脚本 v2
策略：
1. 从Wikipedia下载校园图片到本地
2. 按学校名字搜索Wikipedia页面
3. 下载多张图片到 static/images/campus/{school_id}/
4. 优先处理还没有校园图片的学校
"""

import sqlite3
import os
import re
import requests
import time
import json
from urllib.parse import urlparse, urljoin, quote
from datetime import datetime

# 配置
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
CAMPUS_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/campus'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}
TIMEOUT = 10

os.makedirs(CAMPUS_DIR, exist_ok=True)

log_file = '/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/campus_batch.log'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(log_file, 'a') as f:
        f.write(line + '\n')


def detect_image_ext(content, content_type=''):
    """检测图片扩展名"""
    if content[:3] == b'\xff\xd8\xff':
        return '.jpg'
    elif content[:4] == b'\x89PNG':
        return '.png'
    elif content[:4] == b'RIFF' and b'WEBP' in content[:12]:
        return '.webp'
    
    ct = content_type.lower()
    if 'jpeg' in ct or 'jpg' in ct:
        return '.jpg'
    elif 'png' in ct:
        return '.png'
    elif 'webp' in ct:
        return '.webp'
    elif 'gif' in ct:
        return '.gif'
    return '.jpg'


def download_image(url, save_path):
    """下载图片，返回路径或None"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if resp.status_code != 200:
            return None
        
        content = resp.content
        if len(content) < 5000:
            return None
        
        ext = detect_image_ext(content, resp.headers.get('Content-Type', ''))
        final_path = save_path.rsplit('.', 1)[0] + ext if '.' not in save_path else save_path
        
        with open(final_path, 'wb') as f:
            f.write(content)
        
        size = os.path.getsize(final_path)
        if size < 5000:
            os.remove(final_path)
            return None
        
        return final_path
    except Exception as e:
        return None


def fetch_wikipedia_images(school_name, school_id, name_cn='', max_images=4):
    """从Wikipedia搜索并下载学校图片"""
    # 优先使用英文名（Wikipedia英文条目更全）
    search_queries = []
    if school_name:
        search_queries.append(school_name)
    if name_cn:
        search_queries.append(name_cn)
    
    for query in search_queries:
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'origin': '*',
                'srlimit': 3
            }
            url = f"https://en.wikipedia.org/w/api.php?{requests.utils.urlencode(params)}"
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT)
            data = resp.json()
            
            results = data.get('query', {}).get('search', [])
            if not results:
                continue
            
            title = results[0]['title']
            
            # 获取页面所有图片（不是thumbnail）
            img_params = {
                'action': 'query',
                'titles': title,
                'prop': 'images',
                'format': 'json',
                'origin': '*',
                'imlimit': 20
            }
            img_url = f"https://en.wikipedia.org/w/api.php?{requests.utils.urlencode(img_params)}"
            img_resp = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT)
            img_data = img_resp.json()
            
            pages = img_data.get('query', {}).get('pages', {})
            image_names = []
            for page_id, page_info in pages.items():
                if page_id != '-1':
                    image_names = [img['title'] for img in page_info.get('images', [])]
                    break
            
            if not image_names:
                # 尝试thumbnail
                thumb_params = {
                    'action': 'query',
                    'titles': title,
                    'prop': 'pageimages',
                    'pithumbsize': 1200,
                    'format': 'json',
                    'origin': '*'
                }
                thumb_url = f"https://en.wikipedia.org/w/api.php?{requests.utils.urlencode(thumb_params)}"
                thumb_resp = requests.get(thumb_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT)
                thumb_data = thumb_resp.json()
                pages = thumb_data.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    if page_id != '-1' and 'thumbnail' in page_info:
                        school_dir = os.path.join(CAMPUS_DIR, f"school_{school_id}")
                        os.makedirs(school_dir, exist_ok=True)
                        
                        # 检查已有图片
                        existing = [f for f in os.listdir(school_dir) if f.startswith(f"school_{school_id}_")]
                        idx = len(existing) + 1
                        
                        save_path = os.path.join(school_dir, f"school_{school_id}_{idx}.jpg")
                        result = download_image(page_info['thumbnail']['source'], save_path)
                        if result:
                            time.sleep(0.3)
                            return [result]
                continue
            
            # 获取图片URL
            school_dir = os.path.join(CAMPUS_DIR, f"school_{school_id}")
            os.makedirs(school_dir, exist_ok=True)
            existing = [f for f in os.listdir(school_dir) if f.startswith(f"school_{school_id}_")]
            idx = len(existing) + 1
            
            saved = []
            for img_name in image_names[:10]:  # 最多试10个
                if len(saved) >= max_images:
                    break
                # 跳过图标等小图
                if any(k in img_name.lower() for k in ['icon', 'logo', 'flag', 'seal', 'coat', 'emblem', 'button', 'svg', 'png']):
                    continue
                
                try:
                    img_info_params = {
                        'action': 'query',
                        'titles': img_name,
                        'prop': 'imageinfo',
                        'iiprop': 'url',
                        'iiurlwidth': 1200,
                        'format': 'json',
                        'origin': '*'
                    }
                    img_info_url = f"https://en.wikipedia.org/w/api.php?{requests.utils.urlencode(img_info_params)}"
                    img_info_resp = requests.get(img_info_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT)
                    img_info_data = img_info_resp.json()
                    
                    pages = img_info_data.get('query', {}).get('pages', {})
                    for page_id, page_info in pages.items():
                        if page_id != '-1' and 'imageinfo' in page_info:
                            img_url = page_info['imageinfo'][0].get('thumburl') or page_info['imageinfo'][0].get('url')
                            if img_url:
                                save_path = os.path.join(school_dir, f"school_{school_id}_{idx}.jpg")
                                result = download_image(img_url, save_path)
                                if result:
                                    saved.append(result)
                                    idx += 1
                                    time.sleep(0.3)
                except:
                    pass
            
            if saved:
                return saved
            
            time.sleep(0.3)
        except Exception as e:
            continue
    
    return []


def update_school_campus(school_id, url_paths):
    """更新学校校园图片"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE schools SET campus_image = ? WHERE id = ?",
        (','.join(url_paths), school_id)
    )
    conn.commit()
    conn.close()


def main(limit=100):
    log("=" * 60)
    log("优化版校园图片批量抓取 v2")
    log("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取需要校园图片的学校（优先有英文名的，因为Wikipedia英文条目更多）
    cursor.execute("""
        SELECT id, name, name_cn, city, country
        FROM schools 
        WHERE campus_reviewed = 0
        AND (campus_image IS NULL OR campus_image = '' OR campus_image = '[]')
        AND name IS NOT NULL AND name != ''
        ORDER BY RANDOM()
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    log(f"需要处理学校: {len(schools)}")
    conn.close()
    
    success = 0
    failed = 0
    
    for i, school_data in enumerate(schools):
        school_id, name, name_cn, city, country = school_data
        
        log(f"[{i+1}/{len(schools)}] 处理: {name_cn or name[:40]} ({country})")
        
        saved = fetch_wikipedia_images(name, school_id, name_cn, max_images=4)
        
        if saved:
            url_paths = [p.replace('/Users/wangfeng/.openclaw/workspace/school-badge-website', '') for p in saved]
            update_school_campus(school_id, url_paths)
            success += 1
            log(f"  ✓ 下载 {len(saved)} 张校园图")
        else:
            failed += 1
            log(f"  ✗ 未找到校园图")
        
        time.sleep(0.3)
        
        if (i + 1) % 20 == 0:
            log(f"--- 进度: {i+1}/{len(schools)} ---")
    
    log("=" * 60)
    log(f"完成! 成功: {success}, 失败: {failed}")
    
    # 统计
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM schools WHERE campus_image IS NOT NULL AND campus_image != '' AND campus_image != '[]'")
    total = c.fetchone()[0]
    conn.close()
    log(f"已有校园图片的学校: {total}")
    log("=" * 60)


if __name__ == '__main__':
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    main(limit=limit)
