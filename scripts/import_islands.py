#!/usr/bin/env python3
"""
导入离岛区 (Islands) 学校数据
参考: https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-islands.html
"""

import sqlite3
from datetime import datetime

def import_islands_schools():
    """导入离岛区学校数据"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("导入离岛区 (Islands) 学校数据")
    print("=" * 60)
    
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0
    
    # 离岛区学校数据
    schools = [
        # === GOVERNMENT SCHOOLS ===
        {
            "name": "ISLANDS GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "離島官立小學",
            "address": "TAI O, LANTAU ISLAND, HONG KONG",
            "phone": "29847046",
            "fax": "29847046",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Islands",
            "school_code": "127001",
        },
        {
            "name": "MUI WAI FUK GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "梅窩公立學校",
            "address": "MUI WAI FUK VILLAGE, LANTAU ISLAND, HONG KONG",
            "phone": "29847046",
            "fax": "29847046",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Islands",
            "school_code": "127010",
        },
        
        # === AIDED SCHOOLS ===
        {
            "name": "CARMEL HOLY SPIRIT KINDERGARTEN",
            "name_cn": "迦密幼兒園",
            "address": "CHEUNG CHAU",
            "phone": "29815333",
            "fax": "29815333",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "kindergarten",
            "finance_type": "Aided",
            "district": "Islands",
            "school_code": "601002",
        },
        {
            "name": "IMMACULATE CONCEPTION CATHOLIC PRIMARY SCHOOL",
            "name_cn": "天主教聖家學校",
            "address": "PO KOK VILLAGE, PENG CHAU",
            "phone": "29831023",
            "fax": "29831023",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Islands",
            "school_code": "132018",
        },
        {
            "name": "LAM TSUEN PUBLIC PONG FONG PRIMARY SCHOOL",
            "name_cn": "林村公立芳棠學校",
            "address": "LAM TSUEN, TAI PO",
            "phone": "26654193",
            "fax": "26654193",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Islands",
            "school_code": "132027",
        },
        
        # === DIRECT SUBSIDY ===
        {
            "name": "DISCOVERY COLLEGE",
            "name_cn": "弘立書院",
            "address": "NOI SHOU BAY, SIU HONG, TUEN MUN",
            "phone": "39107000",
            "fax": "39107001",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Direct",
            "district": "Islands",
            "school_code": "600001",
        },
        
        # === PRIVATE / INTERNATIONAL ===
        {
            "name": "HONG KONG INTERNATIONAL SCHOOL",
            "name_cn": "香港國際學校",
            "address": "REDUCKS BAY, TUNG CHUNG, LANTAU ISLAND",
            "phone": "31497400",
            "fax": "31497401",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Private",
            "district": "Islands",
            "school_code": "600002",
        },
        
        # === MORE AIDED SCHOOLS ===
        {
            "name": "ST. BENEDICT'S SCHOOL",
            "name_cn": "聖本篤學校",
            "address": "CHEUNG CHAU",
            "phone": "29815111",
            "fax": "29815111",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Islands",
            "school_code": "132036",
        },
        
        {
            "name": "SIU HO SAM GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "邵翰柱公立學校",
            "address": "SIU HO WAN, NORTH LANTAU",
            "phone": "29877711",
            "fax": "29877711",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Islands",
            "school_code": "127029",
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
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE district = 'Islands'")
    islands_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n导入完成!")
    print(f"  新增: {inserted} 所")
    print(f"  更新: {updated} 所")
    print(f"  EDB来源总计: {total_edb} 所")
    print(f"  离岛区总计: {islands_count} 所")

if __name__ == '__main__':
    import_islands_schools()
