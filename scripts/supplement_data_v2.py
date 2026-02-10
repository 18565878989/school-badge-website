#!/usr/bin/env python3
"""
从各学校官网抓取缺失的数据
官网、校训、地址、校长
使用urllib
"""

import sqlite3
import urllib.request
import urllib.error
from html import unescape
import re
import time
import json

def get_page(url, timeout=10):
    """获取页面内容"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return html
    except Exception as e:
        print(f"  错误: {type(e).__name__}")
        return None

def extract_school_info(html, url):
    """从学校官网提取信息"""
    data = {
        'website': url,
        'motto': None,
        'principal': None,
        'address': None
    }
    
    # 提取校训
    motto_patterns = [
        r'校訓[：:]\s*([^\n。]+)',
        r'办学宗旨[：:]\s*([^\n。]+)',
        r'校训[：:]\s*([^\n。]+)',
    ]
    for pattern in motto_patterns:
        match = re.search(pattern, html)
        if match:
            motto = match.group(1).strip()[:100]
            if len(motto) > 3:
                data['motto'] = motto
                break
    
    # 提取校长
    principal_patterns = [
        r'校长[：:]\s*([^\n。]+)',
        r'校監[：:]\s*([^\n。]+)',
        r'校長[：:]\s*([^\n。]+)',
        r'Principal[：:]\s*([^\n。]+)',
        r'Headmaster[：:]\s*([^\n。]+)',
    ]
    for pattern in principal_patterns:
        match = re.search(pattern, html)
        if match:
            principal = match.group(1).strip()[:50]
            if len(principal) > 1 and len(principal) < 30:
                data['principal'] = principal
                break
    
    # 提取地址
    address_patterns = [
        r'地址[：:]\s*([^\n。]+)',
        r'校址[：:]\s*([^\n。]+)',
        r'Address[：:]\s*([^\n。]+)',
    ]
    for pattern in address_patterns:
        match = re.search(pattern, html)
        if match:
            address = match.group(1).strip()[:100]
            if len(address) > 5:
                data['address'] = address
                break
    
    return data

def scrape_schools_with_websites(limit=50):
    """抓取有官网的学校数据"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 获取有官网的香港学校
    c.execute(f"""
        SELECT id, name, name_cn, level, website
        FROM schools 
        WHERE region = 'Hong Kong' 
        AND website IS NOT NULL 
        AND website != ''
        AND website LIKE 'http%'
        ORDER BY RANDOM()
        LIMIT {limit}
    """)
    
    schools = c.fetchall()
    print(f"找到 {len(schools)} 所有官网的香港学校 (限制{limit}所)")
    
    results = []
    updated = 0
    
    for i, school in enumerate(schools, 1):
        school_id, name, name_cn, level, website = school
        
        print(f"[{i}/{len(schools)}] {name_cn or name}")
        print(f"  → {website}")
        
        html = get_page(website)
        if not html:
            print(f"  ❌ 无法访问")
            continue
        
        info = extract_school_info(html, website)
        
        # 更新数据库
        updates = []
        params = []
        
        if info['motto']:
            updates.append('motto = ?')
            params.append(info['motto'])
            print(f"  ✓ 校训: {info['motto'][:30]}...")
        
        if info['principal']:
            updates.append('principal = ?')
            params.append(info['principal'])
            print(f"  ✓ 校长: {info['principal']}")
        
        if info['address']:
            updates.append('address = ?')
            params.append(info['address'])
            print(f"  ✓ 地址: {info['address'][:30]}...")
        
        if updates:
            params.append(school_id)
            sql = f"UPDATE schools SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            c.execute(sql, params)
            updated += 1
        
        results.append({
            'id': school_id,
            'name': name,
            'name_cn': name_cn,
            'website': website,
            **info
        })
        
        time.sleep(0.3)
    
    conn.commit()
    conn.close()
    
    # 保存结果
    with open('scripts/supplement/scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成!")
    print(f"更新: {updated}所")
    print(f"结果: scripts/supplement/scraped_data.json")
    
    return results

if __name__ == '__main__':
    scrape_schools_with_websites(limit=100)
