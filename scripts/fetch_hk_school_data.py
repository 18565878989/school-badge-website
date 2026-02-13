#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 schooland.hk 抓取香港学校的校训和简介
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import re

# 数据库路径
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_school_data(url):
    """从单个学校页面抓取数据"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            text = soup.get_text()
            
            # 提取校训
            motto = None
            motto_match = re.search(r'校訓[：:]\s*([^\n\r（）()]+)', text)
            if motto_match:
                motto = motto_match.group(1).strip()[:200]
            
            # 提取办学宗旨
            description = None
            desc_match = re.search(r'辦學宗旨[：:]\s*([^\n\r（）()]+)', text)
            if desc_match:
                description = desc_match.group(1).strip()[:500]
            
            return motto, description
    except Exception as e:
        print(f"  抓取失败: {e}")
    return None, None

def get_all_school_urls():
    """获取所有学校URL"""
    urls = []
    
    # 需要抓取的学校（从数据库中提取）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, name_cn FROM schools WHERE country = 'Hong Kong' AND level = 'middle'")
    schools = cursor.fetchall()
    conn.close()
    
    print(f"数据库中有 {len(schools)} 所香港中学")
    
    # 直接构建URL（schooland.hk 使用学校名称作为路径）
    # 例如：英華書院 -> /ss/yingwa
    # 我们需要转换学校名称为URL格式
    
    return schools

def update_school_data(name, motto, description):
    """更新学校数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 尝试通过名称匹配
    cursor.execute(
        "SELECT id, name, name_cn FROM schools WHERE country = 'Hong Kong' AND (name = ? OR name_cn = ?)",
        (name, name)
    )
    school = cursor.fetchone()
    
    if school:
        if motto:
            cursor.execute("UPDATE schools SET motto = ? WHERE id = ?", (motto, school[0]))
        if description:
            cursor.execute("UPDATE schools SET description = ? WHERE id = ?", (description, school[0]))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def main():
    """主函数"""
    print("=" * 60)
    print("从 schooland.hk 抓取香港学校校训和简介")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取需要处理的学校列表（已有校训的优先处理）
    cursor.execute("""
        SELECT id, name, name_cn 
        FROM schools 
        WHERE country = 'Hong Kong' 
        ORDER BY 
            CASE WHEN motto IS NULL OR motto = '' THEN 0 ELSE 1 END,
            id
        LIMIT 30
    """)
    
    schools = cursor.fetchall()
    conn.close()
    
    print(f"将处理 {len(schools)} 所学校\n")
    
    updated = 0
    failed = 0
    
    for i, school in enumerate(schools, 1):
        school_id, name, name_cn = school
        print(f"[{i}/{len(schools)}] {name_cn or name}")
        
        # 构建URL
        # schooland.hk URL 格式需要转换
        url_name = name.lower().replace(' ', '-').replace("'", '') if name else name_cn
        url = f'https://www.schooland.hk/ss/{url_name}'
        
        motto, description = fetch_school_data(url)
        
        if motto or description:
            # 更新数据库
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if motto:
                cursor.execute("UPDATE schools SET motto = ? WHERE id = ?", (motto, school_id))
            if description:
                cursor.execute("UPDATE schools SET description = ? WHERE id = ?", (description, school_id))
            
            conn.commit()
            conn.close()
            
            print(f"  ✅ 校训: {motto[:30] if motto else '无'}...")
            print(f"  ✅ 简介: {description[:30] if description else '无'}...")
            updated += 1
        else:
            print(f"  ❌ 未能获取数据")
            failed += 1
        
        time.sleep(1.5)  # 礼貌爬取
    
    print("\n" + "=" * 60)
    print(f"完成! 更新: {updated}, 失败: {failed}")
    print("=" * 60)

if __name__ == '__main__':
    main()
