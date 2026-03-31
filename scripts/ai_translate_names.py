#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 翻译学校名称脚本 - 补充 name_cn
使用 MiniMax API 进行批量翻译
"""

import sqlite3
import os
import time
import re
import json
import urllib.request
import urllib.error
from datetime import datetime

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
MINIMAX_API_KEY = 'sk-api-PqND1VcFMy4oQakns0ifJ3bIO1Q9fAT8P5sF2D2V1JfN4DSJYP3T7aFrNCPlWu5eKBZuAqgtWDxAGUS6P-0dYg7yqeSWk4NvgbTahYKdjLJmphXIOfHTIAU'
MINIMAX_BASE_URL = 'https://api.minimaxi.com/anthropic/v1'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_name_cn_exists(name_cn, country, exclude_id=None):
    """检查 name_cn 是否已存在"""
    conn = get_db_connection()
    cur = conn.cursor()
    if exclude_id:
        cur.execute("SELECT id FROM schools WHERE name_cn = ? AND country = ? AND id != ? LIMIT 1",
                   (name_cn, country, exclude_id))
    else:
        cur.execute("SELECT id FROM schools WHERE name_cn = ? AND country = ? LIMIT 1",
                   (name_cn, country))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def update_name_cn(school_id, name_cn, country):
    """更新学校的中文名，处理冲突"""
    base_name_cn = name_cn
    suffix = 1
    while check_name_cn_exists(name_cn, country, school_id):
        name_cn = f"{base_name_cn} ({suffix})"
        suffix += 1
        if suffix > 100:
            break
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE schools SET name_cn = ?, updated_at = ? WHERE id = ?",
                    (name_cn, datetime.now().isoformat(), school_id))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        return affected > 0, name_cn
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, None

def call_minimax_translate(texts):
    """调用 MiniMax API 翻译"""
    names_str = ', '.join(texts)
    
    prompt = f"""Translate these school names to Simplified Chinese. Return ONLY a JSON array.
Example: ["哈佛大学", "斯坦福大学"]

Names: {names_str}

Respond with ONLY the JSON array."""

    payload = {
        "model": "MiniMax-M2.7",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    req = urllib.request.Request(
        f"{MINIMAX_BASE_URL}/messages",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {MINIMAX_API_KEY}'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result.get('content', [])
            text = ""
            # 找到 type='text' 的 block，忽略 'thinking' block
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    text = block.get('text', '')
                    break
            
            if text and text.strip().startswith('['):
                # 先尝试精确匹配 JSON 数组
                match = re.search(r'\[.*?\]', text, re.DOTALL)
                if match:
                    try:
                        translations = json.loads(match.group(0))
                        if isinstance(translations, list) and len(translations) == len(texts):
                            return translations
                        elif isinstance(translations, list):
                            print(f"    长度不匹配: got {len(translations)}, expected {len(texts)}", flush=True)
                    except json.JSONDecodeError as e:
                        print(f"    JSON解析失败: {e}", flush=True)
                else:
                    print(f"    未找到JSON数组", flush=True)
    except Exception as e:
        print(f"API Error: {e}", flush=True)
    return None

def get_missing_schools(limit=20):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, name_cn, country 
        FROM schools 
        WHERE (name_cn IS NULL OR name_cn = '')
        ORDER BY country, id
        LIMIT ?
    """, (limit,))
    schools = cur.fetchall()
    conn.close()
    return schools

def count_remaining():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM schools WHERE name_cn IS NULL OR name_cn = ''")
    remaining = cur.fetchone()[0]
    conn.close()
    return remaining

def main():
    print("=" * 60)
    print("AI 翻译学校名称 - 补充 name_cn")
    print("=" * 60)
    
    remaining = count_remaining()
    print(f"当前缺失 name_cn: {remaining} 所")
    
    if remaining == 0:
        print("✓ 所有学校已有名!")
        return
    
    total_updated = 0
    batch_num = 0
    
    while remaining > 0:
        batch_num += 1
        schools = get_missing_schools(20)
        if not schools:
            break
        
        texts = [s['name'] for s in schools]
        print(f"\n[Batch {batch_num}] 翻译 {len(texts)} 所 ({texts[0][:20]}...)", flush=True)
        
        translations = call_minimax_translate(texts)
        
        if translations:
            for i, school in enumerate(schools):
                if translations[i] and translations[i].strip():
                    success, final_name = update_name_cn(school['id'], translations[i].strip(), school['country'])
                    if success:
                        total_updated += 1
                        print(f"  ✓ {school['name'][:30]} → {final_name[:20]}", flush=True)
        else:
            print(f"  翻译失败，跳过此批次", flush=True)
        
        remaining = count_remaining()
        print(f"  剩余: {remaining} 所", flush=True)
        time.sleep(5)  # 等待一下避免API限制
    
    print("\n" + "=" * 50)
    print(f"完成! 共更新 {total_updated} 所学校")
    print(f"剩余缺失: {count_remaining()} 所")

if __name__ == '__main__':
    main()
