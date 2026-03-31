#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多语言数据填充脚本
1. 补充缺失的 name_cn (中文名)
2. 补充 motto_cn (中文校训)
3. 补充 description_cn (中文简介)
"""

import sqlite3
import time
import re
from datetime import datetime

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_school_name(name):
    """标准化学校名称"""
    if not name:
        return ""
    name = name.strip()
    # 移除常见后缀
    name = re.sub(r'\s+(College|School|Academy|Institute|University|High School|Primary School)$', '', name, flags=re.IGNORECASE)
    return name

def get_schools_needing_translation(limit=100):
    """获取需要翻译的 schools"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, name, name_cn, country, region
        FROM schools 
        WHERE (name_cn IS NULL OR name_cn = '')
        ORDER BY country, name
        LIMIT ?
    """, (limit,))
    
    schools = cur.fetchall()
    conn.close()
    return schools

def get_schools_with_motto_not_cn(limit=100):
    """获取有 motto 但没有 motto_cn 的学校"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, name, name_cn, motto, country
        FROM schools 
        WHERE motto IS NOT NULL AND motto != ''
          AND (motto_cn IS NULL OR motto_cn = '')
        ORDER BY country, name
        LIMIT ?
    """, (limit,))
    
    schools = cur.fetchall()
    conn.close()
    return schools

def add_multilingual_columns():
    """添加多语言字段"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 检查字段是否存在
    cur.execute("PRAGMA table_info(schools)")
    columns = [row[1] for row in cur.fetchall()]
    
    if 'motto_cn' not in columns:
        cur.execute("ALTER TABLE schools ADD COLUMN motto_cn TEXT")
        print("✓ 添加 motto_cn 字段")
    
    if 'description_cn' not in columns:
        cur.execute("ALTER TABLE schools ADD COLUMN description_cn TEXT")
        print("✓ 添加 description_cn 字段")
    
    conn.commit()
    conn.close()

def count_missing_data():
    """统计缺失数据"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("\n=== 多语言数据统计 ===")
    
    cur.execute("SELECT COUNT(*) FROM schools")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM schools WHERE name_cn IS NULL OR name_cn = ''")
    missing_name_cn = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM schools WHERE motto IS NOT NULL AND motto != ''")
    has_motto = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM schools WHERE motto_cn IS NULL OR motto_cn = ''")
    missing_motto_cn = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM schools WHERE description IS NOT NULL AND description != ''")
    has_desc = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM schools WHERE description_cn IS NULL OR description_cn = ''")
    missing_desc_cn = cur.fetchone()[0]
    
    print(f"学校总数: {total}")
    print(f"name_cn 缺失: {missing_name_cn} ({missing_name_cn*100//total}%)")
    print(f"有 motto: {has_motto}, 缺失 motto_cn: {missing_motto_cn}")
    print(f"有 description: {has_desc}, 缺失 description_cn: {missing_desc_cn}")
    
    conn.close()

def main():
    print("=" * 60)
    print("多语言数据填充脚本")
    print("=" * 60)
    
    # 添加新字段
    add_multilingual_columns()
    
    # 统计当前数据
    count_missing_data()
    
    print("\n=== 需要翻译的示例数据 ===")
    schools = get_schools_needing_translation(10)
    for s in schools:
        print(f"  [{s['id']}] {s['name']} ({s['country']})")

if __name__ == '__main__':
    main()
