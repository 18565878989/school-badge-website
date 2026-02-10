#!/usr/bin/env python3
"""
从已知有官网的香港学校抓取缺失数据
"""

import sqlite3
import urllib.request
import re
import time
import json

def get_page(url, timeout=15):
    """获取页面内容"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

def scrape_known_schools():
    """从已知有官网的学校抓取详细信息"""
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 获取有官网的中学
    c.execute("""
        SELECT id, name, name_cn, website
        FROM schools 
        WHERE region = 'Hong Kong' 
        AND level = 'middle'
        AND website IS NOT NULL 
        AND website != ''
        AND website LIKE 'http%'
        ORDER BY name_cn
        LIMIT 30
    """)
    
    schools = c.fetchall()
    print(f"从 {len(schools)} 所有官网的中学抓取数据")
    
    updated = 0
    results = []
    
    for i, (school_id, name, name_cn, website) in enumerate(schools, 1):
        print(f"[{i}/{len(schools)}] {name_cn or name}")
        
        html = get_page(website)
        if not html:
            print(f"  ❌ 无法访问")
            continue
        
        data = {'id': school_id, 'name': name, 'name_cn': name_cn, 'website': website}
        
        # 提取校长
        principal_match = re.search(r'校長[：:]\s*([^\n<]+)', html)
        if principal_match:
            principal = principal_match.group(1).strip()[:30]
            if principal and len(principal) > 1:
                data['principal'] = principal
                print(f"  ✓ 校长: {principal}")
        
        # 提取地址
        addr_match = re.search(r'地址[：:]\s*([^\n<]+)', html)
        if addr_match:
            addr = addr_match.group(1).strip()[:100]
            if addr and len(addr) > 5:
                data['address'] = addr
                print(f"  ✓ 地址: {addr[:40]}...")
        
        # 提取校训
        motto_match = re.search(r'校訓[：:]\s*([^\n<]+)', html)
        if motto_match:
            motto = motto_match.group(1).strip()[:50]
            if motto and len(motto) > 2:
                data['motto'] = motto
                print(f"  ✓ 校训: {motto}")
        
        results.append(data)
        
        # 更新数据库
        updates = []
        params = []
        
        if data.get('principal'):
            updates.append('principal = ?')
            params.append(data['principal'])
        
        if data.get('address'):
            updates.append('address = ?')
            params.append(data['address'])
        
        if data.get('motto'):
            updates.append('motto = ?')
            params.append(data['motto'])
        
        if updates:
            params.append(school_id)
            sql = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
            c.execute(sql, params)
            updated += 1
        
        time.sleep(0.3)
    
    conn.commit()
    conn.close()
    
    # 保存结果
    with open('scripts/supplement/edb_schools.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n完成! 更新: {updated}所")
    return updated

if __name__ == '__main__':
    scrape_known_schools()
