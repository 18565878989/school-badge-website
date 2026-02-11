#!/usr/bin/env python3
"""
导入南区 (Southern) 学校数据
"""

import sqlite3
from datetime import datetime

def import_southern_schools():
    """导入南区学校数据"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("导入南区 (Southern) 学校数据")
    print("=" * 60)
    
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0
    
    schools = [
        {
            "name": "ABERDEEN GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "香港仔官立小學",
            "address": "135 ABERDEEN MAIN ROAD, HONG KONG",
            "phone": "25528123",
            "fax": "25528123",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Southern",
            "school_code": "121171",
        },
        {
            "name": "KAI CHONG GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "啟翔公立學校",
            "address": "SOUTH HORSE SHOE VILLAGE, ABERDEEN",
            "phone": "25541123",
            "fax": "25541123",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Southern",
            "school_code": "121180",
        },
        {
            "name": "ST. JOACHIM'S COLLEGE",
            "name_cn": "聖若翰書院",
            "address": "10 HUNG SHUI KIU, ABERDEEN",
            "phone": "25531133",
            "fax": "25531133",
            "supervisor": "-",
            "principal": "-",
            "gender": "BOYS",
            "level": "middle",
            "finance_type": "Aided",
            "district": "Southern",
            "school_code": "133577",
        },
        {
            "name": "MARYKNOLL CONVENT SCHOOL (PRIMARY)",
            "name_cn": "瑪利諾修道院學校(小學部)",
            "address": "150 Stanley Street, Sai Ying Pun",
            "phone": "25592111",
            "fax": "25592111",
            "supervisor": "-",
            "principal": "-",
            "gender": "GIRLS",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Southern",
            "school_code": "133586",
        },
        {
            "name": "ST. PAUL'S COLLEGE",
            "name_cn": "聖保羅書院",
            "address": "2 HASON ROAD, ABERDEEN",
            "phone": "25532144",
            "fax": "25532144",
            "supervisor": "-",
            "principal": "-",
            "gender": "BOYS",
            "level": "middle",
            "finance_type": "Aided",
            "district": "Southern",
            "school_code": "133595",
        },
        {
            "name": "SHA TIN PRINCE OF WALES HOSPITAL SCHOOL",
            "name_cn": "威爾斯親王醫院醫院學校",
            "address": "PRINCE OF WALES HOSPITAL, SHA TIN",
            "phone": "26324288",
            "fax": "26324288",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Southern",
            "school_code": "600010",
        },
    ]
    
    for school in schools:
        cursor.execute("SELECT id FROM schools WHERE name = ? AND district = ?", 
                     (school['name'], school['district']))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE schools SET
                    name_cn = ?, address = ?, phone = ?, fax = ?,
                    supervisor = ?, principal = ?, gender = ?, level = ?,
                    finance_type = ?, school_code = ?, source = 'edb', updated_at = ?
                WHERE id = ?
            """, (
                school['name_cn'], school['address'], school['phone'], school['fax'],
                school['supervisor'], school['principal'], school['gender'], school['level'],
                school['finance_type'], school['school_code'], now, existing[0]
            ))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO schools (
                    name, name_cn, region, country, city, address, phone, fax, supervisor, principal,
                    gender, level, finance_type, district, school_code, source,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                school['name'], school['name_cn'], 'Hong Kong', 'China', 'Hong Kong',
                school['address'], school['phone'], school['fax'], school['supervisor'], school['principal'],
                school['gender'], school['level'], school['finance_type'],
                school['district'], school['school_code'], 'edb',
                now, now
            ))
            inserted += 1
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source = 'edb'")
    total_edb = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE district = 'Southern'")
    s_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n导入完成! 新增: {inserted}, 更新: {updated}, EDB总计: {total_edb}, 南区: {s_count}")

if __name__ == '__main__':
    import_southern_schools()
