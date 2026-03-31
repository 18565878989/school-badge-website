#!/usr/bin/env python3
"""
从香港教育局抓取缺失的字段数据：session_type, gender, supervisor, principal
并更新到数据库
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import sqlite3
from datetime import datetime
import concurrent.futures
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

def parse_session_type(text):
    """从文本中解析 AM/PM/WD session type"""
    text = text.upper().replace(' ', '')
    
    # 检查 WD (Whole Day 全日) 优先
    if 'WD' in text or '全日' in text:
        return 'WD'
    # 检查 PM (下午)
    if 'PM' in text or '下午' in text:
        return 'PM'
    # 检查 AM (上午)
    if 'AM' in text or '上午' in text:
        return 'AM'
    
    # 备用：从星号位置判断
    if '*' in text:
        if 'CO-ED' in text or '男女' in text:
            # 需要更精确的判断
            return 'WD' if 'WD' in text else ('PM' if 'PM' in text else 'AM')
    
    return None

def parse_gender(text):
    """从文本中解析性别"""
    text_upper = text.upper()
    
    if 'BOYS' in text_upper or '男' in text:
        return 'BOYS'
    if 'GIRLS' in text_upper or '女' in text:
        return 'GIRLS'
    if 'CO-ED' in text_upper or '男女' in text:
        return 'CO-ED'
    
    return None

def parse_school_from_text(text, school_name):
    """从文本块中解析学校信息"""
    result = {
        'session_type': None,
        'gender': None,
        'supervisor': None,
        'principal': None,
    }
    
    # 分割文本
    lines = text.split('\n')
    
    # 查找 Supervisor/Chairman of SMC
    supervisor_pattern = r'(?:Supervisor|Chairman of SMC)[^\w]*([^\*]+)'
    supervisor_match = re.search(supervisor_pattern, text, re.IGNORECASE)
    if supervisor_match:
        supervisor = supervisor_match.group(1).strip()
        supervisor = re.sub(r'\s+', ' ', supervisor)
        if supervisor and supervisor != '-':
            result['supervisor'] = supervisor
    
    # 查找 Head of School/Principal
    principal_pattern = r'(?:Head of School|Principal)[^\w]*([^\*]+)'
    principal_match = re.search(principal_pattern, text, re.IGNORECASE)
    if principal_match:
        principal = principal_match.group(1).strip()
        principal = re.sub(r'\s+', ' ', principal)
        if principal and principal != '-':
            result['principal'] = principal
    
    # 查找 Gender 和 Session
    # 常见模式：* BOYS 男 或 * CO-ED 男女
    gender_session_pattern = r'\*\s*(BOYS|GIRLS|CO-ED|男女|男|女)'
    matches = re.findall(gender_session_pattern, text, re.IGNORECASE)
    
    if matches:
        for match in matches:
            if result['gender'] is None:
                result['gender'] = parse_gender(match)
    
    # 解析 session type
    # 检查 AM/PM/WD 标记
    am_match = re.search(r'(?:AM|上午)', text, re.IGNORECASE)
    pm_match = re.search(r'(?:PM|下午)', text, re.IGNORECASE)
    wd_match = re.search(r'(?:WD|全日)', text, re.IGNORECASE)
    
    # 检查星号行附近的 session 标记
    asterisk_lines = [line.strip() for line in lines if '*' in line]
    
    # 优先判断 WD（全日）
    for line in asterisk_lines:
        line_upper = line.upper()
        if 'WD' in line_upper or '全日' in line:
            result['session_type'] = 'WD'
            break
        if 'PM' in line_upper or '下午' in line:
            result['session_type'] = 'PM'
        elif 'AM' in line_upper or '上午' in line:
            if result['session_type'] is None:
                result['session_type'] = 'AM'
    
    # 如果还是没找到，根据 gender 和学校类型推断
    if result['session_type'] is None:
        # 对于幼儿园，通常是 AM/PM/WD 都有
        # 对于中小学，通常是全日
        if 'KINDERGARTEN' in text.upper() or '幼稚園' in text or 'KG' in school_name.upper():
            result['session_type'] = 'WD'  # 幼儿园通常是全日
        else:
            result['session_type'] = 'WD'  # 中小学默认全日
    
    return result

def fetch_and_parse_district(filename):
    """抓取并解析单个区域的数据"""
    url = f"https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/{filename}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取所有文本内容
            text = soup.get_text()
            
            # 按学校分割 - 找到 School No. 或 Location ID
            schools_data = []
            
            # 使用正则表达式按学校分割
            school_pattern = r'(?:School No[./]|Location ID:)'
            parts = re.split(school_pattern, text)
            
            for i, part in enumerate(parts[1:], 1):  # 跳过第一部分（标题）
                # 提取学校编号
                school_id_match = re.match(r'[:\s]*(\d+)[/\s]', part)
                school_id = school_id_match.group(1) if school_id_match else None
                
                if school_id:
                    # 提取学校名称（英文）
                    name_match = re.search(r'([A-Z][A-Z\s\'\-\.]+?)(?:\n|幼|http|$)', part[:500], re.IGNORECASE)
                    name_en = name_match.group(1).strip() if name_match else None
                    
                    # 提取中文名称
                    cn_match = re.search(r'([\u4e00-\u9fff]+(?:校|學|院|堂|幼))', part[:800])
                    name_cn = cn_match.group(1) if cn_match else None
                    
                    # 解析 session, gender, supervisor, principal
                    parsed = parse_school_from_text(part[:2000], name_en or '')
                    
                    schools_data.append({
                        'school_code': school_id,
                        'name': name_en,
                        'name_cn': name_cn,
                        **parsed
                    })
            
            return schools_data, district
        else:
            print(f"  失败: {response.status_code}")
            return [], None
            
    except Exception as e:
        print(f"  错误: {e}")
        return [], None

def fetch_district_schools_v2(filename):
    """使用HTML结构抓取单个区域的学校数据 - 改进版"""
    url = f"https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/{filename}"
    
    print(f"\n抓取: {filename}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"  HTTP错误: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        schools = []
        
        # 获取所有文本内容并按学校分割
        full_text = soup.get_text()
        
        # 找到所有学校条目（通过 School No./Location ID 定位）
        school_blocks = re.split(r'(?=School No[./]|Location ID:)', full_text)
        
        for block in school_blocks[1:]:  # 跳过第一个空块
            school_info = {}
            
            # 提取 School No
            id_match = re.search(r'School No[./]*\s*Location ID:*\s*(\d+)', block)
            if not id_match:
                id_match = re.search(r'(\d{6})', block[:100])
            if id_match:
                school_info['school_code'] = id_match.group(1)
            
            # 提取英文名称
            name_match = re.search(r'^([A-Z][A-Za-z\s\'\-\.]+?)(?:\n|[\u4e00-\u9fff]|$)', block, re.MULTILINE)
            if name_match:
                school_info['name'] = name_match.group(1).strip()
            
            # 提取中文名称
            cn_match = re.search(r'([\u4e00-\u9fff]{2,}(?:小學|中學|書院|學校|學院|堂|園|幼稚園|幼兒園))', block)
            if cn_match:
                school_info['name_cn'] = cn_match.group(1)
            
            # 提取 Supervisor/Chairman
            supervisor_match = re.search(r'(?:Supervisor|Chairman of SMC)[^\w]*([^\*]+)', block, re.IGNORECASE)
            if supervisor_match:
                sup = supervisor_match.group(1).strip()
                if sup and sup != '-':
                    school_info['supervisor'] = re.sub(r'\s+', ' ', sup)
            
            # 提取 Principal/Head of School
            principal_match = re.search(r'(?:Head of School|Principal)[^\w]*([^\*]+)', block, re.IGNORECASE)
            if principal_match:
                prin = principal_match.group(1).strip()
                if prin and prin != '-':
                    school_info['principal'] = re.sub(r'\s+', ' ', prin)
            
            # 提取 Gender
            gender_match = re.search(r'\*\s*(BOYS|GIRLS|CO-ED)', block, re.IGNORECASE)
            if gender_match:
                school_info['gender'] = gender_match.group(1).upper()
            else:
                # 备用：从文字中查找
                if 'BOYS' in block.upper() or '男' in block:
                    school_info['gender'] = 'BOYS'
                elif 'GIRLS' in block.upper() or '女' in block:
                    school_info['gender'] = 'GIRLS'
                elif 'CO-ED' in block.upper() or '男女' in block:
                    school_info['gender'] = 'CO-ED'
            
            # 提取 Session Type (AM/PM/WD)
            # 检查星号标记
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
            
            # 备用判断
            if session_type is None:
                if 'WHOLE DAY' in block.upper() or 'WD' in block.upper() or '全日' in block:
                    session_type = 'WD'
                elif 'PM' in block.upper() or '下午' in block:
                    session_type = 'PM'
                elif 'AM' in block.upper() or '上午' in block:
                    session_type = 'AM'
                else:
                    # 默认值
                    session_type = 'WD'
            
            school_info['session_type'] = session_type
            
            if school_info.get('school_code'):
                schools.append(school_info)
        
        print(f"  解析到 {len(schools)} 所学校")
        return schools
        
    except Exception as e:
        print(f"  错误: {e}")
        return []

def update_database(schools_data, district_name):
    """更新数据库"""
    if not schools_data:
        return 0, 0
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    updated = 0
    not_found = 0
    
    for school in schools_data:
        school_code = school.get('school_code')
        if not school_code:
            continue
        
        # 通过 school_code 查找学校
        cursor.execute("""
            SELECT id, name, name_cn FROM schools 
            WHERE school_code = ? AND country = 'Hong Kong'
        """, (school_code,))
        
        existing = cursor.fetchone()
        
        if existing:
            school_id, name, name_cn = existing
            
            # 构建更新语句
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
                params.append(school_id)
                
                sql = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                updated += 1
        else:
            not_found += 1
    
    conn.commit()
    conn.close()
    
    return updated, not_found

def main():
    """主函数"""
    print("=" * 60)
    print("开始从香港教育局抓取缺失数据")
    print("目标字段: session_type, gender, supervisor, principal")
    print("=" * 60)
    
    all_schools = []
    
    # 抓取所有区域数据
    for filename, (en_name, cn_name) in districts.items():
        print(f"\n处理区域: {en_name} ({cn_name})")
        schools = fetch_district_schools_v2(filename)
        all_schools.extend(schools)
        time.sleep(0.5)  # 礼貌性延迟
    
    print(f"\n\n共抓取 {len(all_schools)} 条学校记录")
    
    # 统计
    stats = {
        'with_session': sum(1 for s in all_schools if s.get('session_type')),
        'with_gender': sum(1 for s in all_schools if s.get('gender')),
        'with_supervisor': sum(1 for s in all_schools if s.get('supervisor')),
        'with_principal': sum(1 for s in all_schools if s.get('principal')),
    }
    
    print("\n数据完整性:")
    print(f"  - Session Type: {stats['with_session']}/{len(all_schools)}")
    print(f"  - Gender: {stats['with_gender']}/{len(all_schools)}")
    print(f"  - Supervisor: {stats['with_supervisor']}/{len(all_schools)}")
    print(f"  - Principal: {stats['with_principal']}/{len(all_schools)}")
    
    # 更新数据库
    print("\n开始更新数据库...")
    total_updated = 0
    total_not_found = 0
    
    for filename, (en_name, cn_name) in districts.items():
        # 找出该区域的学校
        region_schools = all_schools  # 简化处理
        updated, not_found = update_database(region_schools, en_name)
        total_updated += updated
        total_not_found += not_found
    
    print(f"\n数据库更新完成:")
    print(f"  - 更新记录: {total_updated}")
    print(f"  - 未匹配记录: {total_not_found}")

if __name__ == '__main__':
    main()
