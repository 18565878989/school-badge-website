#!/usr/bin/env python3
"""
定时任务脚本：持续添加欧洲和美洲院校数据
用法: python3 add_schools_cron.py
"""

import sqlite3
import os
import sys

# 数据库路径
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def add_schools(schools):
    """批量添加学校"""
    conn = get_connection()
    cursor = conn.cursor()
    
    count = 0
    for school in schools:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO schools 
                (name, name_cn, region, country, city, address, level, description, badge_url, website, motto, founded, principal, source, is_top_university)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'manual', 1)
            """, school)
            if cursor.rowcount > 0:
                count += 1
        except Exception as e:
            pass
    
    conn.commit()
    conn.close()
    return count

def get_current_stats():
    """获取当前统计"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT region, COUNT(*) as count 
        FROM schools 
        WHERE region IN ('Europe', 'North America', 'South America') 
        GROUP BY region 
        ORDER BY count DESC
    """)
    results = cursor.fetchall()
    conn.close()
    return dict(results)

if __name__ == "__main__":
    print("=" * 50)
    print("开始添加欧洲和美洲院校...")
    print("=" * 50)
    
    # 获取添加前的统计
    stats_before = get_current_stats()
    print(f"添加前: {stats_before}")
    
    # 添加学校
    added = add_schools([])
    print(f"本次添加: {added} 所学校")
    
    # 获取添加后的统计
    stats_after = get_current_stats()
    print(f"添加后: {stats_after}")
    
    print("=" * 50)
    print("完成!")
    print("=" * 50)
