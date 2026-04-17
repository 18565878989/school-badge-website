#!/usr/bin/env python3
"""
学校地理坐标批量获取脚本
使用 OpenStreetMap Nominatim API 批量获取学校坐标
"""
import sqlite3
import time
import urllib.request
import json
import sys
from datetime import datetime

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
RATE_LIMIT = 1  # Nominatim 要求每秒最多1个请求

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def get_schools_needing_coordinates(limit=100):
    """获取需要坐标的学校（优先处理有地址的）"""
    conn = get_db_connection()
    schools = conn.execute("""
        SELECT id, name, name_cn, address, city, district, country, region
        FROM schools
        WHERE latitude IS NULL OR latitude = ''
        AND (address IS NOT NULL AND address != '')
        ORDER BY 
            CASE WHEN level = 'university' THEN 0 ELSE 1 END,
            country
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return schools

def geocode_address(query):
    """使用 Nominatim API 获取坐标"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={urllib.request.quote(query)}&format=json&limit=1"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'SchoolBadgeWebsite/1.0 (educational project)'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"  Geocoding error: {e}", file=sys.stderr)
    return None, None

def update_school_coordinates(school_id, lat, lng):
    """更新学校坐标"""
    conn = get_db_connection()
    conn.execute("""
        UPDATE schools 
        SET latitude = ?, longitude = ?, updated_at = ?
        WHERE id = ?
    """, (lat, lng, datetime.now().isoformat(), school_id))
    conn.commit()
    conn.close()

def process_schools(batch_size=50):
    """批量处理学校"""
    total = 0
    updated = 0
    failed = 0
    
    print(f"开始获取学校坐标... (每批 {batch_size} 所)")
    print("=" * 50)
    
    while True:
        schools = get_schools_needing_coordinates(batch_size)
        if not schools:
            break
            
        for school in schools:
            school_id, name, name_cn, address, city, district, country, region = school
            total += 1
            
            # 构建查询字符串
            parts = []
            if address:
                parts.append(address)
            if city:
                parts.append(city)
            if country:
                parts.append(country)
            query = ', '.join(parts)
            
            if not query:
                failed += 1
                continue
            
            print(f"[{total}] {name[:40]}...", end=" ", flush=True)
            
            lat, lng = geocode_address(query)
            if lat and lng:
                update_school_coordinates(school_id, lat, lng)
                updated += 1
                print(f"✓ ({lat:.4f}, {lng:.4f})")
            else:
                failed += 1
                print("✗")
            
            time.sleep(RATE_LIMIT)
    
    print("=" * 50)
    print(f"完成! 总计: {total}, 成功: {updated}, 失败: {failed}")
    
    return total, updated, failed

if __name__ == '__main__':
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    process_schools(batch_size)
