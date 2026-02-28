#!/usr/bin/env python3
"""
学校校徽和校园风光定时抓取脚本
每天6次（每4小时）自动从各学校官网抓取校徽和校园图片并更新数据库
优先抓取全球顶尖大学的图片
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import sqlite3
import random
import re
from datetime import datetime
import time

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
BADGE_DIR = os.path.join(BASE_DIR, 'static/images/badges')
CAMPUS_DIR = os.path.join(BASE_DIR, 'static/images/campus')

# 确保目录存在
os.makedirs(BADGE_DIR, exist_ok=True)
os.makedirs(CAMPUS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 每次任务抓取学校数量
BATCH_SIZE = 30


def log(message):
    """日志输出"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def get_schools_without_badge(limit=BATCH_SIZE):
    """获取没有校徽的学校（优先顶尖大学）"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    
    # 优先获取顶尖大学
    schools = conn.execute("""
        SELECT id, name, name_cn, website, country
        FROM schools 
        WHERE website IS NOT NULL 
        AND website != ''
        AND (badge_url IS NULL OR badge_url = '')
        AND is_top_university = 1
        ORDER BY RANDOM()
        LIMIT ?
    """, (limit,)).fetchall()
    
    # 如果没有足够的顶尖大学，再获取其他的
    if len(schools) < limit:
        remaining = limit - len(schools)
        other_schools = conn.execute("""
            SELECT id, name, name_cn, website, country
            FROM schools 
            WHERE website IS NOT NULL 
            AND website != ''
            AND (badge_url IS NULL OR badge_url = '')
            AND is_top_university = 0
            ORDER BY RANDOM()
            LIMIT ?
        """, (remaining,)).fetchall()
        schools = schools + other_schools
    
    conn.close()
    return [dict(s) for s in schools]


def get_schools_without_campus(limit=BATCH_SIZE):
    """获取没有校园图片的学校（优先顶尖大学）"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    
    # 优先获取顶尖大学
    schools = conn.execute("""
        SELECT id, name, name_cn, website, country
        FROM schools 
        WHERE website IS NOT NULL 
        AND website != ''
        AND (campus_image IS NULL OR campus_image = '')
        AND is_top_university = 1
        ORDER BY RANDOM()
        LIMIT ?
    """, (limit,)).fetchall()
    
    # 如果没有足够的顶尖大学，再获取其他的
    if len(schools) < limit:
        remaining = limit - len(schools)
        other_schools = conn.execute("""
            SELECT id, name, name_cn, website, country
            FROM schools 
            WHERE website IS NOT NULL 
            AND website != ''
            AND (campus_image IS NULL OR campus_image = '')
            AND is_top_university = 0
            ORDER BY RANDOM()
            LIMIT ?
        """, (remaining,)).fetchall()
        schools = schools + other_schools
    
    conn.close()
    return [dict(s) for s in schools]


def clean_url(url):
    """清理URL"""
    if not url:
        return None
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.split('?')[0]


def make_url(base, path):
    """将相对路径转换为完整URL"""
    from urllib.parse import urljoin
    if not path:
        return None
    return urljoin(base, path)


def download_favicon(school_id, name, website):
    """从学校官网下载favicon作为校徽"""
    url = clean_url(website)
    if not url:
        return None
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 方法1: 查找favicon
        links = soup.find_all('link', rel=re.compile(r'icon'))
        for link in links:
            href = link.get('href')
            if href:
                full_url = make_url(url, href)
                try:
                    resp2 = requests.get(full_url, headers=HEADERS, timeout=10)
                    if resp2.status_code == 200 and len(resp2.content) > 500:
                        if resp2.content[:4] in [b'\x89PNG', b'\xff\xd8', b'GIF8', b'RIFF']:
                            ext = '.png' if '.png' in full_url.lower() else '.ico'
                            filename = f"school_{school_id}{ext}"
                            filepath = os.path.join(BADGE_DIR, filename)
                            with open(filepath, 'wb') as f:
                                f.write(resp2.content)
                            return f'/static/images/badges/{filename}'
                except:
                    continue
        
        # 方法2: 查找logo
        logo_elements = soup.find_all('a', class_=re.compile(r'logo'))
        for logo_elem in logo_elements:
            img = logo_elem.find('img')
            if img:
                src = img.get('src')
                if src:
                    full_url = make_url(url, src)
                    try:
                        resp2 = requests.get(full_url, headers=HEADERS, timeout=10)
                        if resp2.status_code == 200 and len(resp2.content) > 500:
                            ext = '.png' if '.png' in full_url.lower() else '.jpg'
                            filename = f"school_{school_id}{ext}"
                            filepath = os.path.join(BADGE_DIR, filename)
                            with open(filepath, 'wb') as f:
                                f.write(resp2.content)
                            return f'/static/images/badges/{filename}'
                    except:
                        continue
        
        # 方法3: 查找第一个大图作为校徽
        images = soup.find_all('img')
        for img in images[:5]:
            src = img.get('src', '')
            if any(kw in src.lower() for kw in ['logo', 'brand', 'emblem']):
                full_url = make_url(url, src)
                try:
                    resp2 = requests.get(full_url, headers=HEADERS, timeout=10)
                    if resp2.status_code == 200 and len(resp2.content) > 1000:
                        ext = '.png' if '.png' in full_url.lower() else '.jpg'
                        filename = f"school_{school_id}{ext}"
                        filepath = os.path.join(BADGE_DIR, filename)
                        with open(filepath, 'wb') as f:
                            f.write(resp2.content)
                        return f'/static/images/badges/{filename}'
                except:
                    continue
                    
    except Exception as e:
        log(f"  ⚠️ 抓取失败: {e}")
    
    return None


def download_campus_images(school_id, name, website):
    """从学校官网下载校园图片"""
    url = clean_url(website)
    if not url:
        return []
    
    downloaded = []
    school_dir = os.path.join(CAMPUS_DIR, f"school_{school_id}")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 查找所有图片
        images = soup.find_all('img')
        
        # 过滤出可能是校园风景的图片
        campus_images = []
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            
            # 跳过图标、logo等小图片
            if any(kw in src.lower() for kw in ['icon', 'logo', 'button', 'avatar', 'thumb', 'nav', 'menu', 'banner']):
                continue
            if any(kw in alt for kw in ['icon', 'logo', 'button', 'avatar']):
                continue
            
            full_url = make_url(url, src)
            if full_url and full_url.startswith('http') and full_url not in campus_images:
                campus_images.append(full_url)
        
        # 下载前几张图片
        os.makedirs(school_dir, exist_ok=True)
        
        for i, img_url in enumerate(campus_images[:6]):
            try:
                resp2 = requests.get(img_url, headers=HEADERS, timeout=15)
                if resp2.status_code == 200 and len(resp2.content) > 5000:
                    ext = '.jpg' if '.jpg' in img_url.lower() else '.png'
                    filename = f"school_{school_id}_{i+1}{ext}"
                    filepath = os.path.join(school_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(resp2.content)
                    
                    downloaded.append(f'/static/images/campus/school_{school_id}/{filename}')
            except Exception as e:
                continue
            
            time.sleep(0.3)
            
    except Exception as e:
        log(f"  ⚠️ 抓取失败: {e}")
    
    return downloaded


def update_school_badge(school_id, badge_url):
    """更新学校校徽"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("UPDATE schools SET badge_url = ? WHERE id = ?", (badge_url, school_id))
    conn.commit()
    conn.close()


def update_school_campus(school_id, campus_images):
    """更新学校校园图片"""
    if not campus_images:
        return
    campus_str = ','.join(campus_images)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("UPDATE schools SET campus_image = ? WHERE id = ?", (campus_str, school_id))
    conn.commit()
    conn.close()


def process_badge_batch():
    """处理一批学校的校徽抓取"""
    log("=" * 50)
    log("开始校徽抓取任务（优先顶尖大学）")
    log("=" * 50)
    
    schools = get_schools_without_badge(BATCH_SIZE)
    log(f"找到 {len(schools)} 所需要校徽的学校")
    
    success_count = 0
    for school in schools:
        log(f"处理: {school['name']} ({school.get('name_cn', '')}) - {school.get('country', '')}")
        
        badge_url = download_favicon(school['id'], school['name'], school.get('website'))
        if badge_url:
            update_school_badge(school['id'], badge_url)
            success_count += 1
            log(f"  ✅ 校徽已更新")
        else:
            log(f"  ❌ 校徽获取失败")
        
        time.sleep(0.5)
    
    log(f"校徽任务完成: 成功 {success_count}/{len(schools)}")
    return success_count


def process_campus_batch():
    """处理一批学校的校园图片抓取"""
    log("=" * 50)
    log("开始校园图片抓取任务（优先顶尖大学）")
    log("=" * 50)
    
    schools = get_schools_without_campus(BATCH_SIZE)
    log(f"找到 {len(schools)} 所需要校园图片的学校")
    
    success_count = 0
    for school in schools:
        log(f"处理: {school['name']} ({school.get('name_cn', '')}) - {school.get('country', '')}")
        
        campus_images = download_campus_images(school['id'], school['name'], school.get('website'))
        if campus_images:
            update_school_campus(school['id'], campus_images)
            success_count += 1
            log(f"  ✅ 校园图片已更新 ({len(campus_images)} 张)")
        else:
            log(f"  ❌ 校园图片获取失败")
        
        time.sleep(0.5)
    
    log(f"校园图片任务完成: 成功 {success_count}/{len(schools)}")
    return success_count


def main():
    log("=" * 60)
    log("开始学校校徽和校园风光抓取任务（优先顶尖大学）")
    log("=" * 60)
    
    # 1. 抓取校徽
    process_badge_batch()
    
    # 2. 抓取校园图片
    process_campus_batch()
    
    log("=" * 60)
    log("任务完成")
    log("=" * 60)


if __name__ == '__main__':
    main()
