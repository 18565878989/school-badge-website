#!/usr/bin/env python3
"""
香港学校历年数据同步脚本
从 schooland.hk 抓取学校历年数据
"""
import re
import sqlite3
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
SCHOOLAND_BASE_URL = 'https://www.schooland.hk'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_school_mapping():
    """获取学校的source_school_id映射"""
    conn = get_db_connection()
    schools = conn.execute("""
        SELECT id, source_school_id, name, name_cn 
        FROM schools 
        WHERE country = 'Hong Kong' 
        AND source = 'schooland.hk'
    """).fetchall()
    conn.close()
    return {str(s['source_school_id']): s['id'] for s in schools}

def parse_yearly_table(html, school_name):
    """解析历年数据表格"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找包含数字表格的文本
    data = {
        'teacher_count': {},
        'class_count': {},
        'student_count': {}
    }
    
    # 解析教學人員數 (教师数量)
    teacher_pattern = r'(\d{4})\s*(\d+)\s*(\d+)'
    # 解析班級結構 (班级数量)
    class_pattern = r'(\d{4})\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)'
    # 解析學生總數 (学生数量)
    student_pattern = r'(\d{4})\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)'
    
    text = soup.get_text()
    
    # 尝试从表格中提取数据
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = [c.get_text(strip=True) for c in row.find_all(['td', 'th'])]
            if len(cells) >= 8:
                try:
                    year = int(cells[0])
                    if 2015 <= year <= 2026:
                        # 解析教师数据: year, total, approved
                        if '教學人員' in row.get_text() or '教師' in row.get_text():
                            if len(cells) >= 3:
                                data['teacher_count'][year] = {
                                    'total': int(cells[1]) if cells[1].isdigit() else None,
                                    'approved': int(cells[2]) if len(cells) > 2 and cells[2].isdigit() else None
                                }
                        # 解析班级数据: year, s1-s6
                        elif '班級結構' in row.get_text() or '班數' in row.get_text():
                            if len(cells) >= 7:
                                data['class_count'][year] = {
                                    's1': int(cells[1]) if cells[1].isdigit() else 0,
                                    's2': int(cells[2]) if len(cells) > 2 and cells[2].isdigit() else 0,
                                    's3': int(cells[3]) if len(cells) > 3 and cells[3].isdigit() else 0,
                                    's4': int(cells[4]) if len(cells) > 4 and cells[4].isdigit() else 0,
                                    's5': int(cells[5]) if len(cells) > 5 and cells[5].isdigit() else 0,
                                    's6': int(cells[6]) if len(cells) > 6 and cells[6].isdigit() else 0,
                                }
                        # 解析学生数据
                        elif '學生總數' in row.get_text():
                            if len(cells) >= 7:
                                total = sum(int(cells[i]) if cells[i].isdigit() else 0 for i in range(1, 7))
                                data['student_count'][year] = {'total': total}
                except (ValueError, IndexError):
                    continue
    
    return data

def parse_school_info(html):
    """解析学校基本信息"""
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    info = {
        'teaching_language': None,
        'feeder_school': None,
        'school_type': None,
    }
    
    # 教学语言
    if '以中文為主要教學語言' in text:
        info['teaching_language'] = '中文'
    elif '以英文為主要教學語言' in text:
        info['teaching_language'] = '英文'
    elif '主要教學語言' in text:
        lang_match = re.search(r'主要教學語言[：:]\s*([^\n]+)', text)
        if lang_match:
            info['teaching_language'] = lang_match.group(1).strip()
    
    # 学校类型
    type_patterns = [
        r'([^\n]+學校)',
        r'(資助|官立|直資|私立|國際)',
    ]
    for pattern in type_patterns:
        match = re.search(pattern, text)
        if match and len(match.group(1)) < 20:
            info['school_type'] = match.group(1)
            break
    
    # 直属小学
    feeder_match = re.search(r'直屬小學[：:]\s*([^\n]+)', text)
    if feeder_match:
        info['feeder_school'] = feeder_match.group(1).strip()
    
    return info

def fetch_school_data(school_id, source_school_id):
    """抓取单个学校的数据"""
    try:
        # 构建URL
        url = f"{SCHOOLAND_BASE_URL}/ss/{source_school_id}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        yearly_data = parse_yearly_table(response.text, source_school_id)
        basic_info = parse_school_info(response.text)
        
        return {
            'school_id': school_id,
            'source_school_id': source_school_id,
            'yearly_data': yearly_data,
            'basic_info': basic_info,
            'success': True
        }
    except Exception as e:
        return {
            'school_id': school_id,
            'source_school_id': source_school_id,
            'error': str(e),
            'success': False
        }

def save_yearly_stats(school_id, yearly_data):
    """保存历年统计数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for year, data in yearly_data['teacher_count'].items():
        cursor.execute("""
            INSERT OR REPLACE INTO school_yearly_stats 
            (school_id, year, teacher_count, approved_teacher_count, source)
            VALUES (?, ?, ?, ?, 'schooland.hk')
        """, (school_id, year, 
              data.get('total'), 
              data.get('approved')))
    
    for year, data in yearly_data['class_count'].items():
        cursor.execute("""
            INSERT OR REPLACE INTO school_yearly_stats 
            (school_id, year, class_s1, class_s2, class_s3, class_s4, class_s5, class_s6, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'schooland.hk')
        """, (school_id, year,
              data.get('s1', 0),
              data.get('s2', 0),
              data.get('s3', 0),
              data.get('s4', 0),
              data.get('s5', 0),
              data.get('s6', 0)))
    
    for year, data in yearly_data['student_count'].items():
        cursor.execute("""
            INSERT OR REPLACE INTO school_yearly_stats 
            (school_id, year, student_count, source)
            VALUES (?, ?, ?, 'schooland.hk')
        """, (school_id, year, data.get('total')))
    
    conn.commit()
    conn.close()

def save_school_relation(school_id, feeder_school_name):
    """保存学校关系"""
    if not feeder_school_name:
        return
    
    conn = get_db_connection()
    
    # 查找 feeder 学校
    feeder = conn.execute("""
        SELECT id FROM schools 
        WHERE country = 'Hong Kong' 
        AND (name LIKE ? OR name_cn LIKE ?)
        LIMIT 1
    """, (f'%{feeder_school_name}%', f'%{feeder_school_name}%')).fetchone()
    
    if feeder:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO school_relations 
            (school_id, related_school_id, relation_type, direction)
            VALUES (?, ?, 'feeder', 'primary_to_secondary')
        """, (school_id, feeder['id']))
        conn.commit()
        print(f"  ↳ 关联直属小学: {feeder_school_name} -> {feeder['id']}")
    
    conn.close()

def main():
    print("=" * 60)
    print("香港学校历年数据同步工具")
    print("=" * 60)
    
    # 获取学校映射
    school_mapping = get_school_mapping()
    print(f"\n找到 {len(school_mapping)} 所学校需要同步")
    
    if not school_mapping:
        print("没有找到需要同步的学校，请先运行数据导入")
        return
    
    success_count = 0
    fail_count = 0
    
    # 限制并发数
    max_workers = 3
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_school_data, school_id, source_id): (school_id, source_id)
            for source_id, school_id in list(school_mapping.items())[:50]  # 限制每次处理50所
        }
        
        for future in as_completed(futures):
            school_id, source_id = futures[future]
            try:
                result = future.result()
                
                if result['success']:
                    # 保存数据
                    save_yearly_stats(result['school_id'], result['yearly_data'])
                    
                    # 保存关系
                    if result['basic_info'].get('feeder_school'):
                        save_school_relation(result['school_id'], result['basic_info']['feeder_school'])
                    
                    success_count += 1
                    print(f"✅ [{success_count}] school_id={school_id}: {result['source_school_id']}")
                else:
                    fail_count += 1
                    print(f"❌ school_id={school_id}: {result.get('error', 'Unknown error')}")
                
                # 避免请求过快
                time.sleep(0.5)
                
            except Exception as e:
                fail_count += 1
                print(f"❌ school_id={school_id}: {e}")
    
    print("\n" + "=" * 60)
    print(f"同步完成: ✅ {success_count} 所 | ❌ {fail_count} 所")
    print("=" * 60)

if __name__ == '__main__':
    main()
