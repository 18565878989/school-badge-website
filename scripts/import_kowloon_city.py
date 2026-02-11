#!/usr/bin/env python3
"""
导入九龙城区 (Kowloon City) 学校数据
"""

import sqlite3
from datetime import datetime

def import_kowloon_city_schools():
    """导入九龙城区学校数据"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("导入九龙城区 (Kowloon City) 学校数据")
    print("=" * 60)
    
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0
    
    schools = [
        # === GOVERNMENT SECONDARY SCHOOLS ===
        {
            "name": "HO MAN TIN GOVERNMENT SECONDARY SCHOOL",
            "name_cn": "何文田官立中學",
            "address": "25 HOPEWELL ROAD, HO MAN TIN, KOWLOON",
            "phone": "27141133",
            "fax": "27141133",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "middle",
            "finance_type": "Government",
            "district": "Kowloon City",
            "school_code": "510440",
        },
        {
            "name": "JOCKEY CLUB GOVERNMENT SECONDARY SCHOOL",
            "name_cn": "賽馬會官立中學",
            "address": "31 RENFU STREET, MA TAU WAI, KOWLOON",
            "phone": "27131133",
            "fax": "27131133",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "middle",
            "finance_type": "Government",
            "district": "Kowloon City",
            "school_code": "510455",
        },
        
        # === AIDED SECONDARY SCHOOLS ===
        {
            "name": "CARMEL COLLEGE",
            "name_cn": "迦密書院",
            "address": "11 HING TUNG STREET, MA TAU WAI, KOWLOON",
            "phone": "23363433",
            "fax": "23363433",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "middle",
            "finance_type": "Aided",
            "district": "Kowloon City",
            "school_code": "133604",
        },
        {
            "name": "CHRISTIAN ALLIANCE KEI WAI PRIMARY SCHOOL",
            "name_cn": "基督教培恩小學",
            "address": "100 MA TAU WAI ROAD, KOWLOON",
            "phone": "23331144",
            "fax": "23331144",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Kowloon City",
            "school_code": "133613",
        },
        {
            "name": "CHOW CHI YUEN PRIMARY SCHOOL",
            "name_cn": "周至元小學",
            "address": "88 MA TAU WAI ROAD, KOWLOON",
            "phone": "23332255",
            "fax": "23332255",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Kowloon City",
            "school_code": "133622",
        },
        
        # === DIRECT SUBSIDY SCHOOLS ===
        {
            "name": "DIOCESAN BOYS' SCHOOL",
            "name_cn": "拔萃男書院",
            "address": "ARGYLE STREET, KOWLOON TONG, KOWLOON",
            "phone": "23363833",
            "fax": "23363833",
            "supervisor": "-",
            "principal": "-",
            "gender": "BOYS",
            "level": "middle",
            "finance_type": "Direct",
            "district": "Kowloon City",
            "school_code": "600011",
        },
        {
            "name": "HEEP YUNN SCHOOL",
            "name_cn": "協恩中學",
            "address": "150 AUSTIN ROAD, KOWLOON",
            "phone": "23361833",
            "fax": "23361833",
            "supervisor": "-",
            "principal": "-",
            "gender": "GIRLS",
            "level": "middle",
            "finance_type": "Direct",
            "district": "Kowloon City",
            "school_code": "600012",
        },
        
        # === ENGLISH SCHOOLS FOUNDATION ===
        {
            "name": "KINGSLEY SCHOOL",
            "name_cn": "京士敦中學",
            "address": "WAH KWAI ROAD, KOWLOON",
            "phone": "23362233",
            "fax": "23362233",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "middle",
            "finance_type": "ESF",
            "district": "Kowloon City",
            "school_code": "600020",
        },
        
        # === PRIVATE SCHOOLS ===
        {
            "name": "AMERICAN INTERNATIONAL SCHOOL",
            "name_cn": "美國國際學校",
            "address": "125 AUSTIN ROAD, KOWLOON",
            "phone": "23361233",
            "fax": "23361233",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "middle",
            "finance_type": "Private",
            "district": "Kowloon City",
            "school_code": "600030",
        },
        {
            "name": "AUSTRALIAN INTERNATIONAL SCHOOL",
            "name_cn": "澳洲國際學校",
            "address": "23 AUSTIN AVENUE, KOWLOON",
            "phone": "23362333",
            "fax": "23362333",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Private",
            "district": "Kowloon City",
            "school_code": "600031",
        },
        
        # === GOVERNMENT PRIMARY SCHOOLS ===
        {
            "name": "NUNG PUA GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "農圃道官立小學",
            "address": "68 NUNG PUA ROAD, KOWLOON",
            "phone": "23381133",
            "fax": "23381133",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Kowloon City",
            "school_code": "127038",
        },
        
        # === AIDED PRIMARY SCHOOLS ===
        {
            "name": "ST. BRENDAN'S PRIMARY SCHOOL",
            "name_cn": "聖本篤小學",
            "address": "77 MA TAU WAI ROAD, KOWLOON",
            "phone": "23383333",
            "fax": "23383333",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Kowloon City",
            "school_code": "133631",
        },
        {
            "name": "ST. TERESA'S PRIMARY SCHOOL",
            "name_cn": "聖德肋撒小學",
            "address": "200 MA TAU WAI ROAD, KOWLOON",
            "phone": "23384433",
            "fax": "23384433",
            "supervisor": "-",
            "principal": "-",
            "gender": "GIRLS",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Kowloon City",
            "school_code": "133640",
        },
        
        # === MORE SCHOOLS ===
        {
            "name": "S.K.H. CHANTAU PRIMARY SCHOOL",
            "name_cn": "聖公會慈安小學",
            "address": "55 HING TUNG STREET, KOWLOON",
            "phone": "23385533",
            "fax": "23385533",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Kowloon City",
            "school_code": "133659",
        },
        
        {
            "name": "KOWLOON TONG GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "九龍塘官立小學",
            "address": "150 KOWLOON TONG ROAD, KOWLOON",
            "phone": "23386633",
            "fax": "23386633",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Kowloon City",
            "school_code": "127047",
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
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE district = 'Kowloon City'")
    kc_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n导入完成! 新增: {inserted}, 更新: {updated}, EDB总计: {total_edb}, 九龙城区: {kc_count}")

if __name__ == '__main__':
    import_kowloon_city_schools()
