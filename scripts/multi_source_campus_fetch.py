#!/usr/bin/env python3
"""
多来源校园图片抓取脚本
支持来源：学校官网、高考派、留学平台、Flickr
"""

import sqlite3
import os
import time
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
CAMPUS_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/campus'

os.makedirs(CAMPUS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def download_image(url, save_path, timeout=15):
    """下载图片到本地"""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            content_type = resp.headers.get('Content-Type', '').lower()
            
            # 确定扩展名
            if 'webp' in content_type or content[:4] == b'RIFF':
                ext = '.webp'
            elif 'png' in content_type or content[:4] == b'\x89PNG':
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                ext = '.jpg'
                if content[:3] != b'\xff\xd8\xff':
                    ext = '.jpg'
            
            final_path = save_path.rsplit('.', 1)[0] + ext
            
            # 检查文件大小
            if len(content) < 5000:
                return None
                
            with open(final_path, 'wb') as f:
                f.write(content)
            
            size = os.path.getsize(final_path)
            print(f"    ✓ 下载成功: {os.path.basename(final_path)} ({size/1024:.1f}KB)")
            return final_path
    except Exception as e:
        print(f"    ✗ 下载失败: {e}")
        return None


def fetch_from_school_website(school_name, school_id):
    """从学校官网抓取校园图片"""
    print(f"  [学校官网] {school_name}")
    
    # 常见官网URL模式
    domains = [
        f"https://www.{school_name.replace(' ', '').lower()}.edu.cn",
        f"https://www.{school_name.replace(' ', '')}.edu.cn",
    ]
    
    for url in domains:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            # 搜索图片
            img_patterns = [
                r'src=["\']([^"\']*campus[^"\']*\.(jpg|png|webp))["\']',
                r'src=["\']([^"\']*photo[^"\']*\.(jpg|png|webp))["\']',
                r'src=["\']([^"\']*banner[^"\']*\.(jpg|png|webp))["\']',
            ]
            
            for pattern in img_patterns:
                matches = re.findall(pattern, html, re.I)
                for img_url in matches[:3]:
                    if img_url.startswith('http'):
                        save_path = f"{CAMPUS_DIR}/school_{school_id}_0.jpg"
                        result = download_image(img_url, save_path)
                        if result:
                            return result
                        break
        except:
            continue
    
    return None


def fetch_from_bing(school_name, school_id):
    """从 Bing 图片抓取"""
    print(f"  [Bing图片] {school_name}")
    
    try:
        search_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(school_name + ' campus')}&first=0&count=5"
        req = urllib.request.Request(search_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # 提取图片URL (多种格式)
        patterns = [
            r'mediaurl=([^&\s]+)',  # mediaurl=格式
            r'src="(https?://[^"]*\.(?:jpg|png|jpeg))"',  # src=jpg格式
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.I)
            for img_url in matches[:3]:
                img_url = urllib.parse.unquote(img_url)
                if img_url.startswith('http') and ('bing' in img_url or 'jpg' in img_url.lower()):
                    save_path = f"{CAMPUS_DIR}/school_{school_id}_bing.jpg"
                    result = download_image(img_url, save_path)
                    if result:
                        return result
    except Exception as e:
        print(f"    ✗ Bing图片失败: {e}")
    
    return None


def fetch_from_liuxue86(school_name, school_id):
    """从留学86网站抓取"""
    print(f"  [留学平台] {school_name}")
    
    try:
        # 搜索页面
        search_url = f"https://www.liuxue86.com/school/search?keyword={urllib.parse.quote(school_name)}"
        req = urllib.request.Request(search_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # 提取学校链接
        school_links = re.findall(r'href="(/school/[^"]+)"[^>]*>([^<]+)<', html)
        for link, name in school_links[:5]:
            if school_name.lower() in name.lower():
                try:
                    school_url = f"https://www.liuxue86.com{link}"
                    req = urllib.request.Request(school_url, headers=HEADERS)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        school_html = resp.read().decode('utf-8', errors='ignore')
                    
                    # 提取校园图片
                    img_matches = re.findall(r'src="([^"]*photo[^"]*\.(jpg|png))"', school_html, re.I)
                    for img_url, _ in img_matches[:3]:
                        if img_url.startswith('http'):
                            save_path = f"{CAMPUS_DIR}/school_{school_id}_liuxue.jpg"
                            result = download_image(img_url, save_path)
                            if result:
                                return result
                except:
                    continue
    except Exception as e:
        print(f"    ✗ 留学平台失败: {e}")
    
    return None


def fetch_from_flickr(school_name, school_id):
    """从 Flickr 抓取 CC 授权图片"""
    print(f"  [Flickr] {school_name}")
    
    try:
        # Flickr API (公开，无需 key 但有限流)
        search_url = f"https://www.flickr.com/search/?text={urllib.parse.quote(school_name + ' campus')}&license=4,5,6"
        req = urllib.request.Request(search_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # 提取图片
        matches = re.findall(r'src="([^"]*\.staticflickr\.com[^"]*\.(jpg|png))"', html)
        for img_url, _ in matches[:3]:
            save_path = f"{CAMPUS_DIR}/school_{school_id}_flickr.jpg"
            result = download_image(img_url, save_path)
            if result:
                return result
    except Exception as e:
        print(f"    ✗ Flickr 失败: {e}")
    
    return None


def fetch_from_gaoxiaobang(school_name, school_id):
    """从高考帮抓取"""
    print(f"  [高考帮] {school_name}")
    
    try:
        search_url = f"https://www.gaoxiaobang.com/search?keyword={urllib.parse.quote(school_name)}"
        req = urllib.request.Request(search_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # 提取图片
        matches = re.findall(r'src="([^"]*campus[^"]*\.(jpg|png))"', html, re.I)
        for img_url, _ in matches[:3]:
            if img_url.startswith('http'):
                save_path = f"{CAMPUS_DIR}/school_{school_id}_gx.jpg"
                result = download_image(img_url, save_path)
                if result:
                    return result
    except Exception as e:
        print(f"    ✗ 高考帮失败: {e}")
    
    return None


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取需要校园图片的学校
    cursor.execute("""
        SELECT id, name, website 
        FROM schools 
        WHERE campus_image IS NULL OR campus_image = '' OR campus_image = '[]'
        AND name IS NOT NULL
        ORDER BY RANDOM() 
        LIMIT 50
    """)
    
    schools = cursor.fetchall()
    print(f"=== 多来源校园图片抓取 ===")
    print(f"待处理学校: {len(schools)} 所\n")
    
    success = 0
    fail = 0
    
    for school_id, name, website in schools:
        print(f"\n[{school_id}] {name}")
        
        result = None
        
        # 按优先级尝试各来源
        sources = [
            lambda: fetch_from_school_website(name, school_id),
            lambda: fetch_from_bing(name, school_id),
            lambda: fetch_from_liuxue86(name, school_id),
            lambda: fetch_from_gaoxiaobang(name, school_id),
            lambda: fetch_from_flickr(name, school_id),
        ]
        
        for fetch_func in sources:
            result = fetch_func()
            if result:
                # 更新数据库
                cursor.execute(
                    "UPDATE schools SET campus_image = ? WHERE id = ?",
                    (f"/static/images/campus/{os.path.basename(result)}", school_id)
                )
                conn.commit()
                success += 1
                break
        
        if not result:
            fail += 1
        
        time.sleep(1)  # 礼貌性延迟
    
    conn.close()
    
    print(f"\n=== 完成 ===")
    print(f"成功: {success}")
    print(f"失败: {fail}")


if __name__ == '__main__':
    main()
