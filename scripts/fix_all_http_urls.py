#!/usr/bin/env python3
"""
快速修复所有外部HTTP校园图片URL → 本地文件
对每个有HTTP URL的学校，直接尝试下载并保存到本地
"""

import sqlite3
import urllib.request
import os
import time

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
CAMPUS_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/campus'

def try_download(url, save_path):
    """尝试下载URL到本地"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            ct = resp.headers.get('Content-Type', '').lower()
            
            if len(content) < 5000:
                return None
            
            # 确定扩展名
            if 'webp' in ct:
                ext = '.webp'
            elif 'png' in ct:
                ext = '.png'
            elif 'gif' in ct:
                ext = '.gif'
            else:
                ext = '.jpg'
            
            # 文件头
            if content[:3] == b'\xff\xd8\xff':
                ext = '.jpg'
            elif content[:4] == b'\x89PNG':
                ext = '.png'
            elif content[:4] == b'RIFF' and b'WEBP' in content[:12]:
                ext = '.webp'
            
            final = save_path.rsplit('.', 1)[0] + ext
            with open(final, 'wb') as f:
                f.write(content)
            
            if os.path.getsize(final) > 5000:
                return final
            else:
                os.remove(final)
                return None
    except:
        return None

def fix_all_http_urls():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 获取所有有HTTP URL的学校
    cur.execute("""
        SELECT id, name, name_cn, campus_image 
        FROM schools 
        WHERE campus_image LIKE '%http%'
    """)
    schools = cur.fetchall()
    
    print(f"需要修复的HTTP URL学校: {len(schools)}")
    
    success = 0
    failed = 0
    skipped = 0
    
    for school_id, name, name_cn, old_url in schools:
        search_name = name_cn if name_cn and name_cn.strip() else name
        
        # 获取所有URL（可能有多个，逗号分隔）
        urls = [u.strip() for u in old_url.split(',') if u.strip()]
        
        school_dir = os.path.join(CAMPUS_DIR, f"school_{school_id}")
        os.makedirs(school_dir, exist_ok=True)
        
        # 已有本地文件数
        existing = [f for f in os.listdir(school_dir) if f.startswith(f'school_{school_id}_')]
        start_idx = len(existing) + 1
        
        saved = []
        for i, url in enumerate(urls):
            # 跳过已经是本地的
            if '/static/' in url:
                skipped += 1
                continue
            
            save_path = os.path.join(school_dir, f"school_{school_id}_{start_idx + i}.jpg")
            result = try_download(url, save_path)
            
            if result:
                saved.append(result)
            else:
                pass  # 下载失败就跳过这张
        
        if saved:
            url_paths = [p.replace('/Users/wangfeng/.openclaw/workspace/school-badge-website', '') for p in saved]
            # 合并已有本地文件 + 新下载的
            all_paths = []
            for f in sorted(os.listdir(school_dir)):
                if f.startswith(f'school_{school_id}_'):
                    all_paths.append(f'/static/images/campus/school_{school_id}/{f}')
            
            cur.execute("UPDATE schools SET campus_image=? WHERE id=?", (','.join(all_paths), school_id))
            conn.commit()
            success += 1
            print(f"  ✓ ID={school_id} {search_name[:30]}: {len(saved)}张")
        else:
            # 下载全部失败，清空
            cur.execute("UPDATE schools SET campus_image='' WHERE id=?", (school_id,))
            conn.commit()
            failed += 1
            if failed <= 10:
                print(f"  ✗ ID={school_id} {search_name[:30]}")
        
        time.sleep(0.2)
    
    conn.close()
    print(f"\n完成! 成功:{success} 失败:{failed} 跳过(已有本地):{skipped}")

if __name__ == '__main__':
    print("="*50)
    print("修复所有HTTP校园图片URL → 本地文件")
    print("="*50)
    fix_all_http_urls()
