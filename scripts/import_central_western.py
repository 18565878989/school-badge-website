#!/usr/bin/env python3
"""
导入中西区 (Central & Western) 学校数据
参考: https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-hkw.html
"""

import sqlite3
from datetime import datetime

def import_central_western_schools():
    """导入中西区学校数据"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("导入中西区 (Central & Western) 学校数据")
    print("=" * 60)
    
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0
    
    # 中西区学校数据
    schools = [
        # === GOVERNMENT SCHOOLS ===
        {
            "name": "CENTRAL GOVERNMENT OFFICES SCHOOL",
            "name_cn": "政府學校",
            "address": "2 G/F, CENTRAL GOVERNMENT OFFICES, TAI MING LANE, HONG KONG",
            "phone": "28100207",
            "fax": "28459193",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Central & Western",
            "school_code": "121117",
        },
        {
            "name": "HK CHINESE WOMEN'S GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "官立嘉道理女子小學",
            "address": "36 KENNEDY ROAD, HONG KONG",
            "phone": "25256309",
            "fax": "25256309",
            "supervisor": "MS WONG YUK LING (黃玉玲女士)",
            "principal": "MS LEUNG WAI LING (梁慧玲女士)",
            "gender": "GIRLS",
            "level": "primary",
            "finance_type": "Government",
            "district": "Central & Western",
            "school_code": "121126",
        },
        {
            "name": "BONHAM ROAD GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "般咸道官立小學",
            "address": "9-13 BONHAM ROAD, HONG KONG",
            "phone": "25462443",
            "fax": "25469583",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Central & Western",
            "school_code": "121135",
        },
        
        # === AIDED SCHOOLS ===
        {
            "name": "ST. CLARE'S PRIMARY SCHOOL",
            "name_cn": "聖嘉勒小學",
            "address": "15 CANTON ROAD, CENTRAL, HONG KONG",
            "phone": "25235211",
            "fax": "25236111",
            "supervisor": "MS CHOW CHING YUEN (周晴媛女士)",
            "principal": "MS WONG MARY (黃曼瓊女士)",
            "gender": "GIRLS",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Central & Western",
            "school_code": "133471",
        },
        {
            "name": "DIOCESAN GIRLS' SCHOOL",
            "name_cn": "拔萃女書院",
            "address": "130-138 GORDON ROAD, HONG KONG",
            "phone": "25224467",
            "fax": "25294443",
            "supervisor": "DR TING YUE CHIU (丁饒秋博士)",
            "principal": "MS CHOW AGNES (周胡靄文女士)",
            "gender": "GIRLS",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Central & Western",
            "school_code": "133480",
        },
        {
            "name": "ST. ANTHONY'S SCHOOL",
            "name_cn": "聖安東尼小學",
            "address": "139-141 CANTON ROAD, HONG KONG",
            "phone": "25255615",
            "fax": "25255615",
            "supervisor": "-",
            "principal": "-",
            "gender": "BOYS",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Central & Western",
            "school_code": "133499",
        },
        {
            "name": "LA SALLE COLLEGE",
            "name_cn": "喇沙書院",
            "address": "18 LA SALLE ROAD, HONG KONG",
            "phone": "25776187",
            "fax": "28828615",
            "supervisor": "DR SIMON YAM (任達賢博士)",
            "principal": "MR PAUL TONG (湯啟文先生)",
            "gender": "BOYS",
            "level": "middle",
            "finance_type": "Aided",
            "district": "Central & Western",
            "school_code": "133504",
        },
        {
            "name": "ST. JOSEPH'S COLLEGE",
            "name_cn": "聖若瑟書院",
            "address": "26 KENNEDY ROAD, HONG KONG",
            "phone": "25228169",
            "fax": "25228169",
            "supervisor": "-",
            "principal": "-",
            "gender": "BOYS",
            "level": "middle",
            "finance_type": "Aided",
            "district": "Central & Western",
            "school_code": "133513",
        },
        {
            "name": "ST. STEPHEN'S GIRLS' COLLEGE",
            "name_cn": "聖士提反女子書院",
            "address": "18 LYTTELTON ROAD, HONG KONG",
            "phone": "25228027",
            "fax": "25228027",
            "supervisor": "MRS YUEN WONG YIN FUN (源黃燕歡女士)",
            "principal": "MS WONG WAI HUNG (黃惠紅女士)",
            "gender": "GIRLS",
            "level": "middle",
            "finance_type": "Aided",
            "district": "Central & Western",
            "school_code": "133522",
        },
        {
            "name": "MARYKNOLL CONVENT SCHOOL",
            "name_cn": "瑪利諾修院學校",
            "address": "150 GORDON ROAD, HONG KONG",
            "phone": "25592201",
            "fax": "25592201",
            "supervisor": "-",
            "principal": "-",
            "gender": "GIRLS",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Central & Western",
            "school_code": "133531",
        },
    ]
    
    for school in schools:
        # 检查是否已存在
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
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE district = 'Central & Western'")
    cw_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n导入完成!")
    print(f"  新增: {inserted} 所")
    print(f"  更新: {updated} 所")
    print(f"  EDB来源总计: {total_edb} 所")
    print(f"  中西区总计: {cw_count} 所")

if __name__ == '__main__':
    import_central_western_schools()
