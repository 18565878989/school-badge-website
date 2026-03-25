#!/usr/bin/env python3
"""
清理失效的Wikipedia校园图片URL，重新下载到本地
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
            
            # 确定扩展名
            if 'webp' in content_type:
                ext = '.webp'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                ext = '.jpg'
            
            # 文件头检查
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
                if os.path.exists(final_path):
                    os.remove(final_path)
                return None
    except Exception as e:
        return None

def redownload_from_wikipedia(school_name, school_id):
    """用学校名重新从Wikipedia搜索并下载图片"""
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': school_name,
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
        
        if not data.get('query', {}).get('search'):
            return []
        
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
        
        saved = []
        for i, img_url in enumerate(image_urls[:6]):
            save_path = os.path.join(school_dir, f"school_{school_id}_{i+1}.jpg")
            result = download_image(img_url, save_path)
            if result:
                saved.append(result)
                time.sleep(0.3)
        
        return saved
        
    except Exception as e:
        return []

def fix_wikipedia_urls():
    """清理所有Wikipedia URL，替换为本地文件"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有有Wikipedia URL的学校
    cursor.execute("""
        SELECT id, name, name_cn, campus_image 
        FROM schools 
        WHERE campus_image LIKE '%wikipedia%' OR campus_image LIKE '%wikimedia%'
    """)
    schools = cursor.fetchall()
    
    print(f"需要修复的学校: {len(schools)}")
    start_time = time.time()
    
    success = 0
    failed = 0
    skipped = 0
    
    for school_id, name, name_cn, old_url in schools:
        search_name = name_cn if name_cn and name_cn.strip() else name
        if not search_name:
            skipped += 1
            continue
        
        print(f"  处理: {search_name[:40]}...", end='', flush=True)
        
        # 重新从Wikipedia下载
        saved = redownload_from_wikipedia(search_name, school_id)
        
        if saved:
            # 转换为URL相对路径
            url_paths = []
            for p in saved:
                url_path = p.replace('/Users/wangfeng/.openclaw/workspace/school-badge-website', '')
                url_paths.append(url_path)
            
            cursor.execute("UPDATE schools SET campus_image=? WHERE id=?", (','.join(url_paths), school_id))
            conn.commit()
            success += 1
            print(f" ✓ {len(saved)}张")
        else:
            # Wikipedia也找不到，清空URL但保留记录
            cursor.execute("UPDATE schools SET campus_image='' WHERE id=?", (school_id,))
            conn.commit()
            failed += 1
            print(f" ✗ (清空)")
        
        time.sleep(0.2)
    
    elapsed = time.time() - start_time
    
    # 统计
    cursor.execute("SELECT COUNT(*) FROM schools WHERE campus_image IS NOT NULL AND campus_image != '' AND campus_image NOT LIKE '%http%'")
    local_only = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE campus_image LIKE '%http%'")
    still_url = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"完成! 耗时: {elapsed:.1f}秒")
    print(f"成功修复: {success} 所学校")
    print(f"修复失败(已清空): {failed} 所学校")
    print(f"跳过: {skipped} 所学校")
    print(f"本地文件图片: {local_only} 所学校")
    print(f"仍为URL: {still_url} 所学校")
    print(f"{'='*50}")

if __name__ == '__main__':
    print("="*50)
    print("清理Wikipedia校园图片URL → 本地文件")
    print("="*50)
    fix_wikipedia_urls()
