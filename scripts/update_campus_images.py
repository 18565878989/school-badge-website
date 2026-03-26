#!/usr/bin/env python3
"""
定时任务：抓取校园风光图片（并行加速版）
- 每小时执行一次
- 并行处理，每次处理15所院校
- 浏览器自动化获取高清图片
"""

import os
import sqlite3
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 配置
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
CAMPUS_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/campus'
MAX_WORKERS = 5          # 并行浏览器数
BATCH_SIZE = 15          # 每批处理数量
REQUEST_DELAY = 0.2      # 下载间隔

def get_browser_images(school_name, max_images=6):
    """使用浏览器获取搜索图片"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            query = f"{school_name} campus university"
            encoded = query.replace(' ', '+')
            url = f"https://www.bing.com/images/search?q={encoded}&form=HDRSC2&first=0"
            
            page.goto(url, timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            page.wait_for_timeout(800)
            
            images = page.eval_on_selector_all(
                "img.mimg", 
                """els => {
                    return els.map(el => el.dataset.fullSrc || el.dataset.src || el.src)
                        .filter(src => src && (src.startsWith('http') || src.startsWith('data:')));
                }"""
            )
            
            browser.close()
            
            seen = set()
            result = []
            for img in images:
                if not img or img.startswith('data:') or len(img) < 30:
                    continue
                clean = img.split('?')[0] if '?' in img else img
                if clean not in seen:
                    seen.add(clean)
                    result.append(img)
            
            return result[:max_images]
            
    except Exception as e:
        return []

def download_image(url, save_path):
    """下载图片"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.bing.com/',
        }
        
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        if resp.status_code != 200 or len(resp.content) < 5000:
            return False
        
        ct = resp.headers.get('Content-Type', '').lower()
        content = resp.content
        
        # 确定扩展名
        ext = '.jpg'
        if 'webp' in ct: ext = '.webp'
        elif 'png' in ct: ext = '.png'
        elif 'gif' in ct: ext = '.gif'
        
        # 文件头检查
        if content[:3] == b'\xff\xd8\xff': ext = '.jpg'
        elif content[:4] == b'\x89PNG': ext = '.png'
        elif b'RIFF' in content[:10] and b'WEBP' in content[8:20]: ext = '.webp'
        
        if not save_path.endswith(ext):
            save_path = save_path.rsplit('.', 1)[0] + ext
        
        with open(save_path, 'wb') as f:
            f.write(content)
        
        return os.path.getsize(save_path) > 5000
        
    except Exception:
        return False

def process_school(school_id, school_name, name_cn, existing_images):
    """处理单个学校"""
    current_count = len([x for x in existing_images.split(',') if x.strip()]) if existing_images else 0
    target_count = 6
    
    if current_count >= target_count:
        return None, 0
    
    needed = target_count - current_count
    search_name = name_cn if name_cn else school_name
    if not search_name:
        return None, 0
    
    print(f"  ▶ {search_name[:35]} ({current_count}张 → 需要{needed}张)")
    
    image_urls = get_browser_images(search_name, needed)
    
    if not image_urls:
        return None, 0
    
    school_dir = os.path.join(CAMPUS_DIR, f"school_{school_id}")
    os.makedirs(school_dir, exist_ok=True)
    
    saved = []
    for i, url in enumerate(image_urls):
        ext = '.jpg'
        if 'png' in url.lower(): ext = '.png'
        filename = f"school_{school_id}_{current_count + i + 1}{ext}"
        save_path = os.path.join(school_dir, filename)
        
        if download_image(url, save_path):
            saved.append(filename)
            print(f"    ✓ {filename}")
        time.sleep(REQUEST_DELAY)
    
    return school_id, len(saved)

def update_campus_images():
    """并行更新校园图片"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    os.makedirs(CAMPUS_DIR, exist_ok=True)
    
    # 获取需要处理的学校（未审核 + 未完成）
    cursor.execute("""
        SELECT id, name, name_cn, campus_image
        FROM schools
        WHERE campus_reviewed = 0
          AND (campus_image IS NULL OR campus_image = '' 
               OR (LENGTH(campus_image) - LENGTH(REPLACE(campus_image, ',', '')) + 1) < 6)
        ORDER BY is_top_university DESC, RANDOM()
        LIMIT ?
    """, (BATCH_SIZE,))
    
    schools = cursor.fetchall()
    conn.close()
    
    if not schools:
        print("没有需要处理的学校")
        return 0
    
    print(f"找到 {len(schools)} 所需要处理的学校，并行数={MAX_WORKERS}")
    
    success = 0
    updated_school_ids = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_school, s[0], s[1], s[2], s[3] or ''): s[0]
            for s in schools
        }
        
        for future in as_completed(futures):
            school_id, count = future.result()
            if school_id and count > 0:
                success += 1
                updated_school_ids.append((school_id, count))
    
    # 批量更新数据库
    if updated_school_ids:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for school_id, count in updated_school_ids:
            # 读取完整路径
            cursor.execute('SELECT campus_image FROM schools WHERE id=?', (school_id,))
            row = cursor.fetchone()
            if row and row[0]:
                cursor.execute('''
                    UPDATE schools SET campus_updated='Y', campus_reviewed=0
                    WHERE id=? AND campus_reviewed=0
                ''', (school_id,))
        
        conn.commit()
        conn.close()
    
    return success

if __name__ == '__main__':
    print("=" * 60)
    print("校园风光图片抓取（并行加速版）")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    start = time.time()
    updated = update_campus_images()
    elapsed = time.time() - start
    
    print()
    print(f"完成! 耗时: {elapsed:.1f}秒，更新: {updated} 所学校")
    print("=" * 60)
