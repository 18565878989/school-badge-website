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
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "database.db"
LOG_FILE = '/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/enhance_school_info.log'
REPORT_FILE = '/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/enhance_school_info_report.log'

def log(msg):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def get_schools_without_details(limit=20):
    """获取缺少详细信息的学校"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
        response = requests.get(website, headers=headers, timeout=15, verify=False)
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
        
    except Exception as e:
        log(f"解析失败: {e}")
    
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

def main():
    start_time = datetime.now()
    log("=" * 50)
    log("学校信息完善任务开始")
    log("=" * 50)
    
    schools = get_schools_without_details(limit=20)
    log(f"目标: {len(schools)} 所学校")
    
    updated = 0
    updated_details = {'phone': 0, 'email': 0}
    
    for school in schools:
        school_id, name, name_cn, country, website = school
        
        if not website:
            continue
        
        log(f"处理: {name} ({country})")
        
        # 解析网站
        info = parse_school_website(school_id, name_cn or name, website)
        
        if info:
            update_school_info(school_id, info)
            updated += 1
            for k in info.keys():
                updated_details[k] = updated_details.get(k, 0) + 1
            log(f"  ✓ 更新: {info}")
        else:
            log(f"  ✗ 未找到新信息")
        
        time.sleep(1)
    
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    
    # 生成报告
    log("=" * 50)
    log("任务完成 - 执行报告")
    log("=" * 50)
    log(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"执行时长: {duration} 秒")
    log("-" * 50)
    log(f"处理学校: {len(schools)}")
    log(f"更新学校: {updated}")
    for k, v in updated_details.items():
        if v > 0:
            log(f"  {k}: +{v}")
    log("=" * 50)
    
    # 写入报告文件
    with open(REPORT_FILE, 'a') as f:
        f.write("\n" + "=" * 50 + "\n")
        f.write(f"学校信息完善报告 - {end_time.strftime('%Y-%m-%d')}\n")
        f.write("=" * 50 + "\n")
        f.write(f"处理: {len(schools)} 所学校\n")
        f.write(f"更新: {updated} 所学校\n")
        for k, v in updated_details.items():
            if v > 0:
                f.write(f"  {k}: +{v}\n")

if __name__ == "__main__":
    main()
