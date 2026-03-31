#!/usr/bin/env python3
"""
从香港教育局抓取缺失的字段数据：session_type, gender, supervisor, principal
并更新到数据库 - 改进版：按学校名称匹配
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import sqlite3
from datetime import datetime
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 区域映射
districts = {
    'school-list-cw.html': ('Central & Western', '中西区'),
    'school-list-hke.html': ('Eastern', '东区'),
    'school-list-i.html': ('Islands', '离岛区'),
    'school-list-kc.html': ('Kowloon City', '九龙城区'),
    'school-list-kt.html': ('Kwun Tong', '观塘区'),
    'school-list-kwt.html': ('Kwai Tsing', '葵青区'),
    'school-list-n.html': ('Northern', '北区'),
    'school-list-sk.html': ('Sai Kung', '西贡区'),
    'school-list-sou.html': ('Southern', '南区'),
    'school-list-ssp.html': ('Sham Shui Po', '深水埗区'),
    'school-list-st.html': ('Sha Tin', '沙田区'),
    'school-list-tm.html': ('Tuen Mun', '屯门区'),
    'school-list-tp.html': ('Tai Po', '大埔区'),
    'school-list-tw.html': ('Tsuen Wan', '荃湾区'),
    'school-list-wch.html': ('Wan Chai', '湾仔区'),
    'school-list-wts.html': ('Wong Tai Sin', '黄大仙区'),
    'school-list-yl.html': ('Yuen Long', '元朗区'),
    'school-list-ytm.html': ('Yau Tsim Mong', '油尖旺区'),
}

def normalize_name(name):
    """标准化学校名称用于匹配"""
    if not name:
        return ""
    # 转小写，移除常见后缀
    name = name.lower().strip()
    name = re.sub(r'\s+(college|school|primary|secondary|kindergarten|kg|ps|gs)$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[^\w\u4e00-\u9fff]', '', name)
    return name

def fetch_district_schools(filename):
    """抓取单个区域的学校数据"""
    url = f"https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/{filename}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        schools = []
        
        # 获取所有文本内容并按学校分割
        full_text = soup.get_text()
        school_blocks = re.split(r'(?=School No[./]|Location ID:)', full_text)
        
        for block in school_blocks[1:]:
            school_info = {'source': 'edb'}
            
            # 提取 School No
            id_match = re.search(r'School No[./]*\s*Location ID:*\s*(\d+)', block)
            if not id_match:
                id_match = re.search(r'(\d{6})', block[:100])
            if id_match:
                school_info['school_code'] = id_match.group(1)
            
            # 提取英文名称 - 改进匹配
            lines = block.split('\n')
            for i, line in enumerate(lines[:10]):
                line = line.strip()
                # 跳过空行和短行
                if len(line) < 5:
                    continue
                # 跳过明显的非名称行
                if any(x in line.upper() for x in ['TEL', 'FAX', 'EMAIL', 'HTTP', 'WWW']):
                    continue
                # 如果行以大写字母开头且包含字母
                if re.match(r'^[A-Z][A-Za-z\s\'\-\.]+', line):
                    # 清理名称
                    clean_name = re.sub(r'\s+', ' ', line).strip()
                    # 移除末尾的特殊字符
                    clean_name = re.sub(r'[\*\#]+$', '', clean_name)
                    if len(clean_name) > 3:
                        school_info['name'] = clean_name
                        break
            
            # 提取中文名称
            cn_match = re.search(r'([\u4e00-\u9fff]{2,}(?:小學|中學|書院|學校|學院|堂|園|幼稚|幼兒))', block)
            if cn_match:
                school_info['name_cn'] = cn_match.group(1)
            
            # 提取 Supervisor/Chairman
            supervisor_match = re.search(r'(?:Supervisor|Chairman of SMC)[^\w]*([^\*]+)', block, re.IGNORECASE)
            if supervisor_match:
                sup = supervisor_match.group(1).strip()
                if sup and sup not in ['-', '']:
                    school_info['supervisor'] = re.sub(r'\s+', ' ', sup)
            
            # 提取 Principal/Head of School
            principal_match = re.search(r'(?:Head of School|Principal)[^\w]*([^\*]+)', block, re.IGNORECASE)
            if principal_match:
                prin = principal_match.group(1).strip()
                if prin and prin not in ['-', '']:
                    school_info['principal'] = re.sub(r'\s+', ' ', prin)
            
            # 提取 Gender
            gender_match = re.search(r'\*\s*(BOYS|GIRLS|CO-ED)', block, re.IGNORECASE)
            if gender_match:
                school_info['gender'] = gender_match.group(1).upper()
            
            # 提取 Session Type
            asterisk_sections = re.findall(r'\*[ \*\n]*(?:(AM)|(PM)|(WD)|(上午)|(下午)|(全日))', block, re.IGNORECASE)
            
            session_type = None
            for section in asterisk_sections:
                if section:
                    if section.upper() in ['WD', '全日']:
                        session_type = 'WD'
                        break
                    elif section.upper() in ['PM', '下午']:
                        session_type = 'PM'
                    elif session_type is None and section.upper() in ['AM', '上午']:
                        session_type = 'AM'
            
            if session_type is None:
                session_type = 'WD'  # 默认值
            
            school_info['session_type'] = session_type
            
            # 至少要有名称或编号才加入
            if school_info.get('name') or school_info.get('school_code'):
                schools.append(school_info)
        
        return schools
        
    except Exception as e:
        print(f"抓取错误: {e}")
        return []

def update_database(schools_data):
    """更新数据库 - 使用多种匹配策略"""
    if not schools_data:
        return 0, 0
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    updated = 0
    not_found = 0
    
    # 按 school_code 建立索引
    cursor.execute("SELECT id, name, name_cn, school_code, district FROM schools WHERE country = 'Hong Kong'")
    db_schools = cursor.fetchall()
    
    # 建立匹配索引
    by_code = {}
    by_name_en = {}
    by_name_cn = {}
    
    for row in db_schools:
        sid, name, name_cn, code, district = row
        if code:
            by_code[code] = (sid, name, name_cn)
        if name:
            by_name_en[normalize_name(name)] = (sid, name_cn)
        if name_cn:
            by_name_cn[name_cn] = (sid, name)
    
    for school in schools_data:
        school_code = school.get('school_code')
        name = school.get('name')
        name_cn = school.get('name_cn')
        
        matched_id = None
        match_method = None
        
        # 策略1: school_code 匹配
        if school_code and school_code in by_code:
            matched_id, _, _ = by_code[school_code]
            match_method = 'code'
        # 策略2: 英文名称匹配
        elif name:
            norm_name = normalize_name(name)
            if norm_name in by_name_en:
                matched_id, _ = by_name_en[norm_name]
                match_method = 'name_en'
        # 策略3: 中文名称匹配
        elif name_cn and name_cn in by_name_cn:
            matched_id, _ = by_name_cn[name_cn]
            match_method = 'name_cn'
        
        if matched_id:
            # 构建更新
            updates = []
            params = []
            
            if school.get('supervisor'):
                updates.append("supervisor = ?")
                params.append(school['supervisor'])
            
            if school.get('principal'):
                updates.append("principal = ?")
                params.append(school['principal'])
            
            if school.get('session_type'):
                updates.append("session_type = ?")
                params.append(school['session_type'])
            
            if school.get('gender'):
                updates.append("gender = ?")
                params.append(school['gender'])
            
            if updates:
                updates.append("updated_at = ?")
                params.append(now)
                params.append(matched_id)
                
                sql = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                updated += 1
        else:
            not_found += 1
    
    conn.commit()
    conn.close()
    
    return updated, not_found

def main():
    print("=" * 60)
    print("开始从香港教育局抓取缺失数据")
    print("=" * 60)
    
    all_schools = []
    
    # 抓取所有区域
    for filename, (en_name, cn_name) in districts.items():
        print(f"抓取 {en_name}...", end=" ")
        schools = fetch_district_schools(filename)
        print(f"{len(schools)} 所")
        all_schools.extend(schools)
        time.sleep(0.3)
    
    print(f"\n共抓取 {len(all_schools)} 条记录")
    
    # 更新数据库
    print("\n更新数据库...")
    updated, not_found = update_database(all_schools)
    
    print(f"\n更新完成:")
    print(f"  - 成功更新: {updated}")
    print(f"  - 未匹配: {not_found}")
    
    # 验证更新结果
    print("\n验证更新结果...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN session_type IS NOT NULL AND session_type != '' THEN 1 ELSE 0 END) as with_session,
            SUM(CASE WHEN gender IS NOT NULL AND gender != '' THEN 1 ELSE 0 END) as with_gender,
            SUM(CASE WHEN supervisor IS NOT NULL AND supervisor != '' THEN 1 ELSE 0 END) as with_supervisor,
            SUM(CASE WHEN principal IS NOT NULL AND principal != '' THEN 1 ELSE 0 END) as with_principal
        FROM schools WHERE country = 'Hong Kong'
    """)
    
    result = cursor.fetchone()
    total, with_session, with_gender, with_supervisor, with_principal = result
    
    print(f"\n香港学校数据完整性 ({total} 所):")
    print(f"  Session Type: {with_session}/{total} ({with_session*100//total}%)")
    print(f"  Gender: {with_gender}/{total} ({with_gender*100//total}%)")
    print(f"  Supervisor: {with_supervisor}/{total} ({with_supervisor*100//total}%)")
    print(f"  Principal: {with_principal}/{total} ({with_principal*100//total}%)")
    
    conn.close()

if __name__ == '__main__':
    main()
