#!/usr/bin/env python3
"""
学校详细信息完善任务
从学校官网抓取详细信息
"""
import sqlite3
import requests
from pathlib import Path
from urllib.parse import quote
from bs4 import BeautifulSoup
import time
import re

DB_PATH = Path(__file__).parent.parent / "database.db"

def get_schools_without_details(limit=20):
    """获取缺少详细信息的学校"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 优先获取有网站但信息不完整的学校
    cursor.execute("""
        SELECT id, name, name_cn, country, website 
        FROM schools 
        WHERE website IS NOT NULL 
        AND website != ''
        AND (phone IS NULL OR phone = '' OR principal IS NULL OR principal = '')
        ORDER BY RANDOM()
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    conn.close()
    return schools

def parse_school_website(school_id, name, website):
    """解析学校官网获取信息"""
    info = {}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(website, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取电话
        phone_pattern = re.compile(r'(\+?86)?[-.\s]?1[3-9]\d[-.\s]?\d{4}[-.\s]?\d{4}')
        text = soup.get_text()
        phone_match = phone_pattern.search(text)
        if phone_match:
            info['phone'] = phone_match.group()
        
        # 提取邮箱
        email_pattern = re.compile(r'[\w.-]+@[\w.-]+\.\w+')
        emails = email_pattern.findall(text)
        if emails:
            info['email'] = emails[0]
        
        # 提取地址 (简单处理)
        address_keywords = ['地址', 'Address', 'location']
        for kw in address_keywords:
            elements = soup.find_all(string=re.compile(kw, re.I))
            if elements:
                parent = elements[0].parent
                if parent:
                    info['address'] = parent.get_text(strip=True)[:200]
                    break
        
    except Exception as e:
        print(f"解析失败: {e}")
    
    return info

def update_school_info(school_id, info):
    """更新学校信息"""
    if not info:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    set_clauses = []
    params = []
    
    for key, value in info.items():
        set_clauses.append(f"{key} = ?")
        params.append(value)
    
    if set_clauses:
        params.append(school_id)
        cursor.execute(f"""
            UPDATE schools 
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """, params)
        conn.commit()
    
    conn.close()
    return True

def enhance_school_details(limit=20):
    """完善学校详细信息"""
    schools = get_schools_without_details(limit)
    
    print(f"开始完善学校信息，目标: {len(schools)} 所学校")
    
    updated = 0
    for school in schools:
        school_id, name, name_cn, country, website = school
        
        if not website:
            continue
        
        print(f"处理: {name} ({country})")
        print(f"  网站: {website}")
        
        # 解析网站
        info = parse_school_website(school_id, name_cn or name, website)
        
        if info:
            update_school_info(school_id, info)
            updated += 1
            print(f"  ✓ 更新: {info}")
        else:
            print(f"  ✗ 未找到新信息")
        
        # 避免请求过快
        time.sleep(1)
    
    print(f"\n完成! 成功更新 {updated}/{len(schools)} 所学校")
    return updated

if __name__ == "__main__":
    enhance_school_details(limit=20)
