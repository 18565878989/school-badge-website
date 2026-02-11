#!/usr/bin/env python3
"""
从schooland.hk获取学校徽标（使用标准库）
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
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        return None

def fetch_badge_url(school_name):
    """尝试获取学校徽标URL"""
    name_slug = school_name.lower().replace(' ', '-').replace("'", '').replace('&', '')
    
    urls_to_try = [
        f"https://www.schooland.hk/ss/{name_slug}",
        f"https://www.schooland.hk/ps/{name_slug}",
    ]
    
    for url in urls_to_try:
        content = fetch_url(url)
        
        if content:
            # 查找徽标URL
            badge_match = re.search(r'https://www\.schooland\.hk/img/(ssb|psb)/[^"]+\.jpg', content)
            if badge_match:
                return badge_match.group(0)
            
            # 查找学校图片
            img_match = re.search(r'https://www\.schooland\.hk/img/(ss|ps)/[^"]+\.jpg', content)
            if img_match:
                return img_match.group(0)
    
    return None

def verify_url(url):
    """验证URL是否存在"""
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except:
        return False

def update_badges(limit=50):
    """更新学校徽标"""
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取没有徽标的前limit所学校
    cursor.execute("""
        SELECT id, name, name_cn 
        FROM schools 
        WHERE badge_url IS NULL OR badge_url=''
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    
    print(f"需要获取徽标的学校: {len(schools)}")
    
    success = 0
    failed = 0
    checked = 0
    
    for school_id, name, name_cn in schools:
        checked += 1
        badge_url = fetch_badge_url(name)
        
        if badge_url and verify_url(badge_url):
            cursor.execute("UPDATE schools SET badge_url=? WHERE id=?", (badge_url, school_id))
            success += 1
            print(f"{checked}. ✓ {name[:40]}: 获取成功")
        else:
            failed += 1
            if checked <= 10:
                print(f"{checked}. ✗ {name[:40]}: 未找到徽标")
        
        time.sleep(0.3)
    
    conn.commit()
    conn.close()
    
    print(f"\n完成! 成功: {success}, 失败: {failed}")
    return success

def main():
    """主函数"""
    print("=" * 70)
    print("从schooland.hk获取学校徽标")
    print("=" * 70)
    
    success = update_badges(limit=50)
    
    print(f"\n成功获取 {success} 个徽标")

if __name__ == '__main__':
    main()
