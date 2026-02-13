#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 CHSC (chsc.hk) 抓取香港学校详细数据
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time

# 数据库路径
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

def fetch_school_detail(sch_id):
    """获取单个学校详情"""
    url = f'https://www.chsc.hk/ssp2025/sch_detail.php?lang_id=2&sch_id={sch_id}'
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        pass
    return None

def parse_school_detail(html, school_name):
    """解析学校详情页"""
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'lxml')
    data = {}
    
    # 查找所有表格
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # 获取这一行的所有文本
                cell_texts = [c.get_text().strip() for c in cells]
                
                # 提取地址
                if '地址:' in cell_texts:
                    idx = cell_texts.index('地址:')
                    if idx + 1 < len(cell_texts):
                        addr = cell_texts[idx + 1].strip()
                        if addr and len(addr) > 5:
                            data['address'] = addr
                
                # 提取电话
                if '電話:' in cell_texts:
                    idx = cell_texts.index('電話:')
                    if idx + 1 < len(cell_texts):
                        phone = cell_texts[idx + 1].strip()
                        if phone and len(phone) < 20:
                            data['phone'] = phone
                
                # 提取传真
                if '傳真:' in cell_texts:
                    idx = cell_texts.index('傳真:')
                    if idx + 1 < len(cell_texts):
                        fax = cell_texts[idx + 1].strip()
                        if fax and len(fax) < 20:
                            data['fax'] = fax
                
                # 提取电邮
                if '電郵:' in cell_texts:
                    idx = cell_texts.index('電郵:')
                    if idx + 1 < len(cell_texts):
                        email = cell_texts[idx + 1].strip()
                        if '@' in email:
                            data['email'] = email
                
                # 提取网址
                if '網址:' in cell_texts:
                    idx = cell_texts.index('網址:')
                    if idx + 1 < len(cell_texts):
                        website = cell_texts[idx + 1].strip()
                        if website.startswith('http'):
                            data['website'] = website
                
                # 提取校长
                if '校長' in cell_texts[0] and len(cells) >= 3:
                    principal = cells[2].get_text().strip()
                    if principal and len(principal) < 80:
                        # 清理校长名字（移除学历信息）
                        principal = re.sub(r'[（(].*$', '', principal).strip()
                        data['principal'] = principal
                
                # 提取校监
                if '校監' in cell_texts[0] and len(cells) >= 3:
                    supervisor = cells[2].get_text().strip()
                    if supervisor and len(supervisor) < 80 and supervisor != '不適用':
                        data['supervisor'] = supervisor
                
                # 提取校训
                if '校訓' in cell_texts[0] and len(cells) >= 3:
                    motto = cells[2].get_text().strip()
                    if motto and len(motto) < 100:
                        data['motto'] = motto
                
                # 提取学校类别
                if '學校類別' in cell_texts[0] and len(cells) >= 3:
                    category = cells[2].get_text().strip()
                    if category:
                        data['school_type'] = category
                
                # 提取办学团体
                if '辦學團體' in cell_texts[0] and len(cells) >= 3:
                    sponsor = cells[2].get_text().strip()
                    if sponsor and len(sponsor) < 100:
                        data['sponsor'] = sponsor
    
    return data if data else None

def update_database(school_name, data):
    """更新数据库"""
    if not data:
        return False
    
    # 只保留数据库中存在的字段
    allowed_fields = {
        'address', 'phone', 'fax', 'website', 'principal', 
        'supervisor', 'motto', 'school_type', 'description'
    }
    filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not filtered_data:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 模糊匹配学校
    parts = re.split(r'[書院中學小學大學]', school_name)
    if parts[0]:
        cursor.execute(
            "SELECT id, name, name_cn FROM schools WHERE country = 'Hong Kong' AND (name LIKE ? OR name_cn LIKE ?)",
            (f'%{parts[0]}%', f'%{parts[0]}%')
        )
        school = cursor.fetchone()
    
    if school:
        updates = []
        values = []
        for key, value in filtered_data.items():
            updates.append(f"{key} = ?")
            values.append(value)
        
        if updates:
            values.append(school[0])
            query = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
    
    conn.close()
    return False

def main():
    """主函数"""
    print("="*60)
    print("从 CHSC 抓取香港学校详细数据")
    print("="*60)
    
    # 已知的部分学校ID（从CHSC网站获取）
    known_ids = {
        418: '英華書院',
        515: '拔萃男書院',
        433: '喇沙書院',
        419: '皇仁書院',
        411: '聖保羅書院',
        427: '聖芳濟書院',
        408: '嘉諾撒聖方濟各書院',
        430: '瑪利曼中學',
        423: '庇理羅士女子中學',
        424: '皇仁書院',
    }
    
    updated = 0
    
    for sch_id, name in known_ids.items():
        print(f"\n[{sch_id}] {name}")
        html = fetch_school_detail(sch_id)
        if html:
            data = parse_school_detail(html, name)
            if data:
                print(f"  数据: {list(data.keys())}")
                if update_database(name, data):
                    updated += 1
                    print(f"  ✅ 已更新")
            else:
                print(f"  ❌ 未解析到数据")
        time.sleep(0.5)
    
    print(f"\n" + "="*60)
    print(f"完成! 更新: {updated}")
    print("="*60)

if __name__ == '__main__':
    main()
