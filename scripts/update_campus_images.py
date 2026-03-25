#!/usr/bin/env python3
"""
定时任务：抓取校园风光图片（浏览器自动化版）
- 每小时执行一次
- 使用浏览器自动化从搜索获取图片
"""
import os
import sqlite3
import time
from pathlib import Path

# 配置
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
CAMPUS_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/campus'

def get_browser_images(school_name, max_images=6):
    """使用浏览器获取搜索图片"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 设置视口
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 访问Bing图片搜索
            query = f"{school_name} campus university"
            encoded = query.replace(' ', '+')
            url = f"https://www.bing.com/images/search?q={encoded}&form=HDRSC2&first=0"
            
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=20000)
            
            # 等待图片加载
            page.wait_for_timeout(2000)
            
            # 获取图片 - 使用data-src或者src属性
            images = page.eval_on_selector_all(
                "img.mimg", 
                """els => {
                    return els.map(el => {
                        // 优先使用data-full-src
                        return el.dataset.fullSrc || el.dataset.src || el.src;
                    }).filter(src => src && (src.startsWith('http') || src.startsWith('data:')));
                }"""
            )
            
            browser.close()
            
            # 去重并返回
            seen = set()
            result = []
            for img in images:
                if not img:
                    continue
                # 跳过data URI和太短的URL
                if img.startswith('data:') or len(img) < 30:
                    continue
                    
                # 清理URL
                clean = img.split('?')[0] if '?' in img else img
                
                if clean not in seen:
                    seen.add(clean)
                    result.append(img)
            
            return result[:max_images]
            
    except Exception as e:
        print(f"  浏览器错误: {e}")
        return []

def download_image(url, save_path):
    """下载图片"""
    try:
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.bing.com/',
        }
        
        # 跟随重定向
        resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        if resp.status_code == 200:
            content = resp.content
            
            if len(content) < 100:
                print(f"    内容太短: {len(content)} bytes")
                return False
            
            first_bytes = content[:30]
            
            # 支持多种图片格式
            is_image = False
            content_type = resp.headers.get('Content-Type', '').lower()
            
            # 优先检查Content-Type
            if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                is_image = True
                ext = '.jpg'
            elif 'image/png' in content_type:
                is_image = True
                ext = '.png'
            elif 'image/gif' in content_type:
                is_image = True
                ext = '.gif'
            elif 'image/webp' in content_type:
                is_image = True
                ext = '.webp'
            elif 'image/bmp' in content_type:
                is_image = True
                ext = '.bmp'
            # 然后检查文件头
            elif first_bytes.startswith(b'\xff\xd8\xff') or b'JFIF' in first_bytes[:15]:
                is_image = True
                ext = '.jpg'
            elif first_bytes.startswith(b'\x89PNG'):
                is_image = True
                ext = '.png'
            elif first_bytes.startswith(b'GIF8'):
                is_image = True
                ext = '.gif'
            elif b'RIFF' in first_bytes[:10] and b'WEBP' in first_bytes[8:20]:
                is_image = True
                ext = '.webp'
            elif b'BM' in first_bytes[:10]:
                is_image = True
                ext = '.bmp'
            
            if is_image:
                if not save_path.endswith(ext):
                    save_path = save_path.rsplit('.', 1)[0] + ext
                
                with open(save_path, 'wb') as f:
                    f.write(content)
                
                size = os.path.getsize(save_path)
                if size > 5000:
                    return True
                else:
                    print(f"    文件太小: {size} bytes")
            else:
                print(f"    不是有效图片 (Content-Type: {content_type}, header: {first_bytes[:20]})")
        
        return False
    except Exception as e:
        print(f"    下载错误: {e}")
        return False

def get_current_image_count(campus_image):
    if not campus_image or campus_image.strip() == '':
        return 0
    return len([x for x in campus_image.split(',') if x.strip()])

def process_school(school_id, school_name, name_cn, existing_images):
    current_count = get_current_image_count(existing_images)
    target_count = 6
    
    if current_count >= target_count:
        return None, 0
    
    needed = target_count - current_count
    search_name = name_cn if name_cn else school_name
    
    if not search_name:
        return None, 0
    
    print(f"  处理: {search_name} (当前{current_count}张, 需要{needed}张)")
    
    # 获取图片
    image_urls = get_browser_images(search_name, needed)
    
    if not image_urls:
        print(f"    未找到图片")
        return None, 0
    
    print(f"    找到 {len(image_urls)} 个图片")
    
    # 创建目录
    school_dir = os.path.join(CAMPUS_DIR, f"school_{school_id}")
    os.makedirs(school_dir, exist_ok=True)
    
    # 下载
    saved_paths = []
    for i, url in enumerate(image_urls):
        ext = '.jpg'
        if 'png' in url.lower():
            ext = '.png'
        
        filename = f"school_{school_id}_{current_count + i + 1}{ext}"
        save_path = os.path.join(school_dir, filename)
        
        if download_image(url, save_path):
            saved_paths.append(f"/static/images/campus/school_{school_id}/{filename}")
            print(f"    OK: {filename}")
            time.sleep(0.5)
    
    return saved_paths, len(saved_paths)

def update_campus_images():
    print("=" * 50)
    print("开始抓取校园风光图片 (浏览器版)...")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    os.makedirs(CAMPUS_DIR, exist_ok=True)
    
    # 获取需要处理的学校
    cursor.execute("""
        SELECT id, name, name_cn, campus_image
        FROM schools
        WHERE campus_reviewed = 0
          AND campus_updated != 'Y'
          AND (campus_image IS NULL OR campus_image = '' 
               OR (LENGTH(campus_image) - LENGTH(REPLACE(campus_image, ',', '')) + 1) < 6)
        ORDER BY is_top_university DESC, RANDOM()
        LIMIT 3
    """)
    
    schools = cursor.fetchall()
    
    if not schools:
        print("没有需要处理的学校")
        conn.close()
        return
    
    print(f"找到 {len(schools)} 所需要处理的学校\n")
    
    total_updated = 0
    
    for school_id, name, name_cn, campus_image in schools:
        new_paths, count = process_school(school_id, name, name_cn, campus_image)
        
        if new_paths:
            existing = []
            if campus_image and campus_image.strip():
                existing = [x.strip() for x in campus_image.split(',') if x.strip()]
            
            all_images = existing + new_paths
            new_campus_image = ','.join(all_images[:6])
            
            cursor.execute("""
                UPDATE schools 
                SET campus_image = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_campus_image, school_id))
            
            if len(all_images) >= 6:
                cursor.execute("""
                    UPDATE schools SET campus_updated = 'Y' WHERE id = ?
                """, (school_id,))
                print(f"    完成! (已标记为Y)\n")
            else:
                print(f"    新增 {count} 张图片\n")
            
            total_updated += 1
            conn.commit()
    
    print(f"\n本次更新了 {total_updated} 所学校")
    conn.close()

def main():
    print("\n" + "=" * 50)
    print("定时任务：校园风光图片抓取 (浏览器版)")
    print("=" * 50)
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    update_campus_images()
    
    print("\n" + "=" * 50)
    print("任务完成!")
    print("=" * 50)

if __name__ == '__main__':
    main()
