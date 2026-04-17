#!/usr/bin/env python3
"""
大学地址信息补全脚本 v2
优先处理知名大学，使用多种策略获取地址
"""
import sqlite3
import time
import urllib.request
import json
import re
import sys
from datetime import datetime

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
PROCESSED_LOG = '/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/address_enhance.log'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def load_processed_ids():
    """加载已处理的学校ID"""
    try:
        with open(PROCESSED_LOG, 'r') as f:
            return set(line.strip() for line in f)
    except:
        return set()

def save_processed_id(school_id):
    """保存已处理的学校ID"""
    with open(PROCESSED_LOG, 'a') as f:
        f.write(f"{school_id}\n")

def get_universities_missing_addresses(limit=20, processed_ids=None):
    """获取缺少地址的大学"""
    conn = get_db_connection()
    query = """
        SELECT id, name, name_cn, country, website, address
        FROM schools
        WHERE level = 'university'
        AND (address IS NULL OR address = '')
    """
    if processed_ids:
        query += f" AND id NOT IN ({','.join('?' * len(processed_ids))})"
    query += " ORDER BY country, name LIMIT ?"
    
    params = list(processed_ids) if processed_ids else []
    params.append(limit)
    
    schools = conn.execute(query, params).fetchall()
    conn.close()
    return schools

def fetch_url(url, timeout=8):
    """获取网页内容"""
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8', errors='ignore')
    except:
        return None

def parse_address(content):
    """从网页内容中解析地址"""
    if not content:
        return None
    
    # 常见地址模式
    patterns = [
        r'地址[：:]\s*([^\n\r<]{10,100})',
        r'Address[：:]\s*([^\n\r<]{10,100})',
        r'Located at:\s*([^\n\r<]{10,100})',
        r'"address"\s*:\s*"([^"]{10,100})"',
        r"'address'\s*:\s*'([^']{10,100})'",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            addr = match.group(1).strip()
            addr = re.sub(r'<[^>]+>', ' ', addr)  # 清理 HTML
            addr = re.sub(r'\s+', ' ', addr)  # 合并空格
            if 5 < len(addr) < 200:
                return addr[:150]
    return None

def try_contact_page(website):
    """尝试访问联系页面"""
    if not website:
        return None
    
    base = website.rstrip('/').replace('http://', '').replace('https://', '')
    contact_urls = [
        f"https://{base}/contact",
        f"https://{base}/about/contact",
        f"https://{base}/en/contact",
        f"https://{base}/about",
    ]
    
    for url in contact_urls:
        content = fetch_url(url, timeout=5)
        if content:
            addr = parse_address(content)
            if addr:
                return addr
    return None

def update_school_address(school_id, address):
    """更新学校地址"""
    conn = get_db_connection()
    conn.execute("""
        UPDATE schools 
        SET address = ?, updated_at = ?
        WHERE id = ?
    """, (address, datetime.now().isoformat(), school_id))
    conn.commit()
    conn.close()

def process_universities(max_count=30):
    """处理大学地址"""
    processed_ids = load_processed_ids()
    total = 0
    updated = 0
    
    print(f"开始获取大学地址... (已处理: {len(processed_ids)})")
    print("=" * 50)
    
    while total < max_count:
        schools = get_universities_missing_addresses(10, processed_ids)
        if not schools:
            print("\n没有更多需要处理的数据")
            break
        
        for school in schools:
            if total >= max_count:
                break
                
            school_id, name, name_cn, country, website, address = school
            total += 1
            
            print(f"[{total}] {name[:35]}... ", end="", flush=True)
            
            # 尝试从联系页面获取
            addr = try_contact_page(website)
            if addr:
                update_school_address(school_id, addr)
                updated += 1
                print(f"✓ {addr[:45]}...")
            else:
                print("✗")
            
            processed_ids.add(school_id)
            save_processed_id(school_id)
            time.sleep(0.8)
    
    print("=" * 50)
    print(f"完成! 总计处理: {total}, 成功获取地址: {updated}")
    
    return total, updated

if __name__ == '__main__':
    max_count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    process_universities(max_count)
