#!/usr/bin/env python3
"""
从 Wikipedia 抓取世界大学排名数据
使用 Wikipedia API 获取排名表格
"""

import sqlite3
import os
import time
import re
import json
import requests
from urllib.parse import urlencode

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
}

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_wikipedia_table(table_url, year):
    """从 Wikipedia 页面提取排名表格"""
    rankings = []
    
    # Extract page title from URL
    match = re.search(r'/wiki/([^#?]+)', table_url)
    if not match:
        return rankings
    
    page_title = match.group(1)
    
    # Use Wikipedia API to get parsed content
    api_url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': page_title,
        'format': 'json',
        'prop': 'wikitext'
    }
    
    try:
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            data = response.json()
            wikitext = data.get('parse', {}).get('wikitext', {}).get('*', '')
            
            # Parse the wikitable
            lines = wikitext.split('\n')
            in_table = False
            headers = []
            
            for line in lines:
                if '|-' in line or '|+' in line:  # Table row
                    in_table = True
                elif line.startswith('|}'):  # End of table
                    break
                elif in_table and line.startswith('|'):
                    # Parse table cell
                    cells = [c.strip() for c in line.split('||')[1:]]
                    if len(cells) >= 2:
                        # First cell is usually rank, second is university name
                        rank_str = re.sub(r'\[.*?\]', '', cells[0]).strip()
                        name = re.sub(r'\[.*?\]', '', cells[1]).strip()
                        
                        # Clean up name
                        name = re.sub(r'\([^)]*\)', '', name).strip()
                        name = name.replace('"', '').replace("'", "")
                        
                        # Extract rank number
                        rank_match = re.search(r'(\d+)', rank_str)
                        if rank_match and name:
                            rank = int(rank_match.group(1))
                            if rank <= 2000:  # Only top 2000
                                rankings.append({
                                    'name': name,
                                    'rank': rank,
                                    'source': f'wikipedia_{year}'
                                })
                                
    except Exception as e:
        print(f"Error fetching {table_url}: {e}")
    
    return rankings

def update_database(rankings, rank_field, year_field, year):
    """更新数据库"""
    if not rankings:
        return 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updated = 0
    
    for school in rankings:
        name = school['name']
        rank = school['rank']
        
        # Try to match by name
        # Clean name for matching
        name_clean = re.sub(r'[,\.\-\'\"\(\)]', '', name.lower()).strip()
        
        # Try exact match first
        cursor.execute(f'''
            SELECT id, {rank_field} FROM schools 
            WHERE LOWER(name) = ? OR LOWER(name_cn) = ?
        ''', (name.lower(), name.lower()))
        result = cursor.fetchone()
        
        if not result:
            # Try partial match
            cursor.execute(f'''
                SELECT id, {rank_field} FROM schools 
                WHERE LOWER(name) LIKE ? OR LOWER(name_cn) LIKE ?
                AND ({rank_field} IS NULL OR {rank_field} > ?)
                LIMIT 1
            ''', (f'%{name_clean[:20]}%', f'%{name_clean[:20]}%', rank))
            result = cursor.fetchone()
        
        if result and (result[1] is None or result[1] > rank):
            cursor.execute(f'''
                UPDATE schools 
                SET {rank_field} = ?, {year_field} = ?
                WHERE id = ?
            ''', (rank, year, result[0]))
            updated += 1
    
    conn.commit()
    conn.close()
    
    return updated

def main():
    print("=" * 60)
    print("从 Wikipedia 抓取世界大学排名")
    print("=" * 60)
    
    # Wikipedia pages with ranking tables
    ranking_sources = [
        # QS Rankings
        ("https://en.wikipedia.org/wiki/QS_World_University_Rankings", "qs", 2026),
        
        # THE Rankings
        ("https://en.wikipedia.org/wiki/Times_Higher_Education_World_University_Rankings", "the", 2024),
        
        # ARWU (Shanghai Ranking)
        ("https://en.wikipedia.org/wiki/Academic_Ranking_of_World_Universities", "arwu", 2023),
        
        # US News Rankings (Best Global Universities)
        ("https://en.wikipedia.org/wiki/2023_2024_Best_Universities_Rankings", "usnews", 2024),
    ]
    
    total_updated = 0
    
    for url, rank_type, year in ranking_sources:
        print(f"\n{'=' * 40}")
        print(f"抓取 {rank_type.upper()} 排名 ({year})...")
        print(f"URL: {url}")
        
        rankings = get_wikipedia_table(url, year)
        print(f"找到 {len(rankings)} 条排名数据")
        
        if rankings:
            rank_field = f"{rank_type}_rank"
            year_field = f"{rank_type}_year"
            updated = update_database(rankings, rank_field, year_field, year)
            total_updated += updated
            print(f"更新了 {updated} 所大学")
        
        time.sleep(1)  # Be polite
    
    print(f"\n{'=' * 60}")
    print(f"总共更新了 {total_updated} 所大学")
    
    # Print final statistics
    print("\n最终统计:")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for field, name in [('qs_rank', 'QS'), ('usnews_rank', 'US News'),
                         ('the_rank', 'THE'), ('arwu_rank', 'ARWU'), 
                         ('cwur_rank', 'CWUR')]:
        cursor.execute(f'SELECT COUNT(*) FROM schools WHERE {field} IS NOT NULL')
        count = cursor.fetchone()[0]
        
        # Only count universities (not schools, middle, elementary, kindergarten)
        cursor.execute(f'''
            SELECT COUNT(*) FROM schools 
            WHERE {field} IS NOT NULL 
            AND level = 'university'
        ''')
        uni_count = cursor.fetchone()[0]
        
        print(f"  {name}: {count} (大学: {uni_count})")
    
    conn.close()
    
    print("\n注意: 排名数据主要来自 Wikipedia，可能不完全准确")
    print("建议参考官方排名网站获取最新数据")


if __name__ == '__main__':
    main()
