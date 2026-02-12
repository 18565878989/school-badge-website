#!/usr/bin/env python3
"""
从schooland.hk获取学校校园照片
"""

import sqlite3
import urllib.request
import urllib.parse
import re
from datetime import datetime
import time

def fetch_url(url):
    """获取URL内容"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        return None

def fetch_campus_image(school_name, city='', country=''):
    """尝试获取学校校园照片URL"""
    # 清理学校名称，创建URL slug
    name_slug = school_name.lower().replace(' ', '-').replace("'", '').replace('&', 'and')
    name_slug = re.sub(r'[^a-z0-9\-]', '', name_slug)
    
    urls_to_try = [
        f"https://www.schooland.hk/ss/{name_slug}",
        f"https://www.schooland.hk/ps/{name_slug}",
    ]
    
    for url in urls_to_try:
        content = fetch_url(url)
        
        if content:
            # 查找学校图片URL（优先级：校门 > 校园全景 > 建筑）
            # schooland.hk的图片格式: https://www.schooland.hk/img/ss/{id}.jpg 或 /img/ps/{id}.jpg
            img_matches = re.findall(r'https://www\.schooland\.hk/img/(ss|ps)/[^"]+\.jpg', content)
            
            if img_matches:
                # 取第一张图片作为校园照片
                first_img = img_matches[0]
                campus_url = f"https://www.schooland.hk/img/{first_img[0]}/{first_img[1]}.jpg"
                return campus_url
    
    return None

def verify_url(url):
    """验证URL是否存在"""
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except:
        return False

def update_campus_images(limit=100):
    """更新学校校园照片"""
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取没有校园照片的前limit所学校
    cursor.execute("""
        SELECT id, name, name_cn, city, country 
        FROM schools 
        WHERE (campus_image IS NULL OR campus_image = '')
        AND source = 'schooland.hk'
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    
    print(f"需要获取校园照片的学校: {len(schools)}")
    
    success = 0
    failed = 0
    checked = 0
    
    for school_id, name, name_cn, city, country in schools:
        checked += 1
        
        # 尝试用英文名获取
        campus_url = fetch_campus_image(name, city, country)
        
        if campus_url and verify_url(campus_url):
            cursor.execute("UPDATE schools SET campus_image=? WHERE id=?", (campus_url, school_id))
            success += 1
            print(f"{checked}. ✓ {name[:50]}")
        else:
            failed += 1
            if checked <= 15:
                print(f"{checked}. ✗ {name[:50]}")
        
        time.sleep(0.5)
    
    conn.commit()
    
    # 统计更新后的数据
    cursor.execute("SELECT COUNT(*) FROM schools WHERE campus_image IS NOT NULL AND campus_image != ''")
    total_with_campus = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n完成! 成功: {success}, 失败: {failed}")
    print(f"有校园照片的学校总数: {total_with_campus}")
    return success

def main():
    """主函数"""
    print("=" * 70)
    print("从schooland.hk获取学校校园照片")
    print("=" * 70)
    
    success = update_campus_images(limit=100)
    
    print(f"\n成功获取 {success} 张校园照片")

if __name__ == '__main__':
    main()
