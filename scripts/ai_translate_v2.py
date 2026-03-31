#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高效的 AI 翻译脚本 - name_cn
优化策略：
1. 预先获取所有缺失数据
2. 控制调用频率（每批间隔 10 秒）
3. 每 10 批后休息 30 秒
4. 失败自动重试（最多 3 次）
"""

import sqlite3
import urllib.request
import json
import re
import time
import os
from datetime import datetime

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
MINIMAX_API_KEY = 'sk-api-PqND1VcFMy4oQakns0ifJ3bIO1Q9fAT8P5sF2D2V1JfN4DSJYP3T7aFrNCPlWu5eKBZuAqgtWDxAGUS6P-0dYg7yqeSWk4NvgbTahYKdjLJmphXIOfHTIAU'
MINIMAX_BASE_URL = 'https://api.minimaxi.com/anthropic/v1'

LOG_FILE = '/tmp/translate_v2.log'

def log(msg):
    """带时间的日志"""
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{ts}] {msg}\n")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_name_cn_exists(name_cn, country, exclude_id=None):
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
    except sqlite3.IntegrityError:
        conn.close()
        return False, None

def call_minimax_translate(texts, retries=3):
    """带重试的翻译，失败时等待更长时间"""
    names_str = ', '.join(texts)
    
    prompt = f"""Translate these school names to Simplified Chinese. Return ONLY a JSON array.
Example: ["哈佛大学", "斯坦福大学"]

Names: {names_str}

Respond with ONLY the JSON array."""

    for attempt in range(retries):
        try:
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
            
            with urllib.request.urlopen(req, timeout=90) as response:
                result = json.loads(response.read().decode('utf-8'))
                content = result.get('content', [])
                
                text = ""
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text = block.get('text', '')
                        break
                
                if text and text.strip().startswith('['):
                    match = re.search(r'\[.*\]', text, re.DOTALL)
                    if match:
                        translations = json.loads(match.group(0))
                        if isinstance(translations, list) and len(translations) == len(texts):
                            return translations
                        elif isinstance(translations, list):
                            log(f"    长度不匹配: got {len(translations)}, expected {len(texts)}")
            
            # 失败，等待后重试
            if attempt < retries - 1:
                wait = (attempt + 1) * 15  # 15, 30, 45 秒
                log(f"    等待 {wait} 秒后重试...")
                time.sleep(wait)
                
        except Exception as e:
            if attempt < retries - 1:
                wait = (attempt + 1) * 15
                log(f"    错误: {e}, 等待 {wait} 秒...")
                time.sleep(wait)
    
    return None

def get_all_missing_schools():
    """一次性获取所有缺失 name_cn 的学校"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, name_cn, country 
        FROM schools 
        WHERE (name_cn IS NULL OR name_cn = '')
        ORDER BY country, id
    """)
    schools = [{'id': r['id'], 'name': r['name'], 'country': r['country']} for r in cur.fetchall()]
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
    global LOG_FILE
    
    # 初始化日志
    LOG_FILE = f'/tmp/translate_v2_{os.getpid()}.log'
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    log("=" * 60)
    log("AI 翻译学校名称 - name_cn (高效版)")
    log("=" * 60)
    
    # 一次性获取所有缺失数据
    log("正在获取所有缺失 name_cn 的学校...")
    all_schools = get_all_missing_schools()
    total_missing = len(all_schools)
    log(f"共需翻译: {total_missing} 所")
    
    if total_missing == 0:
        log("✓ 所有学校已有名!")
        return
    
    # 分批处理
    batch_size = 20
    total_updated = 0
    total_batches = (total_missing + batch_size - 1) // batch_size
    
    # 失败重试队列
    failed_batches = []
    
    for i in range(0, total_missing, batch_size):
        batch_num = i // batch_size + 1
        batch = all_schools[i:i + batch_size]
        
        log(f"\n[Batch {batch_num}/{total_batches}] 翻译 {len(batch)} 所...")
        
        texts = [s['name'] for s in batch]
        translations = call_minimax_translate(texts, retries=3)
        
        if translations:
            success_count = 0
            for j, school in enumerate(batch):
                if translations[j] and translations[j].strip():
                    success, final_name = update_name_cn(school['id'], translations[j].strip(), school['country'])
                    if success:
                        success_count += 1
                        total_updated += 1
                        log(f"  ✓ {school['name'][:30]} → {final_name[:20]}")
            
            if success_count < len(batch):
                log(f"    部分成功: {success_count}/{len(batch)}")
        else:
            log(f"    翻译失败，加入重试队列")
            failed_batches.append((batch_num, batch))
        
        remaining = count_remaining()
        log(f"  剩余: {remaining} 所")
        
        # 控制频率：每批间隔 10 秒，每 10 批休息 30 秒
        if batch_num % 10 == 0:
            log(f"\n[每 10 批休息 30 秒...]")
            time.sleep(30)
        else:
            time.sleep(10)
    
    # 重试失败的批次
    if failed_batches:
        log(f"\n{'=' * 60}")
        log(f"开始重试失败的 {len(failed_batches)} 个批次...")
        log(f"{'=' * 60}")
        
        for batch_num, batch in failed_batches:
            texts = [s['name'] for s in batch]
            log(f"\n[Retry Batch {batch_num}]")
            
            translations = call_minimax_translate(texts, retries=5)
            
            if translations:
                for j, school in enumerate(batch):
                    if translations[j] and translations[j].strip():
                        success, final_name = update_name_cn(school['id'], translations[j].strip(), school['country'])
                        if success:
                            total_updated += 1
                            log(f"  ✓ {school['name'][:30]} → {final_name[:20]}")
                time.sleep(15)
            else:
                log(f"    重试失败")
    
    log(f"\n{'=' * 60}")
    log(f"完成! 共更新 {total_updated} 所学校")
    log(f"剩余缺失: {count_remaining()} 所")
    log(f"{'=' * 60}")

if __name__ == '__main__':
    main()
