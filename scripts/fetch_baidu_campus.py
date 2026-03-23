#!/usr/bin/env python3
"""
从百度图片获取校园风光
"""

import sqlite3
import os
import requests
import time
import json
import re

# 配置
CAMPUS_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/campus'
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://image.baidu.com/'
}

os.makedirs(CAMPUS_DIR, exist_ok=True)

def search_baidu_image(school_name):
    """从百度图片搜索获取校园风光"""
    try:
        # 百度图片搜索API
        url = f"https://image.baidu.com/search/acjson?tn=resultjson_com&word={requests.utils.quote(school_name + ' 校园风光')}&pn=0&rn=1"
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            for item in data['data']:
                if 'thumbURL' in item:
                    return item['thumbURL'], item.get('middleURL', '')
        return None, None
    except Exception as e:
        print(f"  百度搜索失败: {e}")
        return None, None

def download_image(url, filepath):
    """下载图片"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200 and len(response.content) > 5000:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return len(response.content)
    except Exception as e:
        print(f"  下载失败: {e}")
    return 0

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取需要校园风光的学校
    cursor.execute("""
        SELECT id, name, country
        FROM schools 
        WHERE (campus_image IS NULL OR campus_image = '')
        AND name IS NOT NULL
        AND name != ''
        AND country IN ('China', 'Hong Kong', 'Taiwan', 'Macau')
        ORDER BY RANDOM()
        LIMIT 20
    """)
    
    schools = cursor.fetchall()
    print(f"从百度图片获取校园风光，共 {len(schools)} 所学校\n")
    
    success_count = 0
    for school in schools:
        school_id, name, country = school
        print(f"处理: {name}")
        
        # 从百度图片搜索
        thumb_url, full_url = search_baidu_image(name)
        if full_url:
            print(f"  找到图片")
            
            # 下载图片
            filename = f"{school_id}.jpg"
            filepath = os.path.join(CAMPUS_DIR, filename)
            size = download_image(full_url, filepath)
            
            if size > 5000:
                campus_image = f"/static/images/campus/{filename}"
                cursor.execute("UPDATE schools SET campus_image = ? WHERE id = ?", (campus_image, school_id))
                print(f"  ✓ 保存成功 ({size} bytes)")
                success_count += 1
                time.sleep(0.5)
            else:
                print(f"  ✗ 下载失败")
        else:
            print(f"  ✗ 未找到图片")
        
        conn.commit()
    
    print(f"\n完成! 成功获取 {success_count} 所学校的校园风光")
    conn.close()

if __name__ == '__main__':
    main()
