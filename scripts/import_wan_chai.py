#!/usr/bin/env python3
"""
导入湾仔区 (Wan Chai) 学校数据
参考: https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-wc.html
"""

import sqlite3
from datetime import datetime

def import_wan_chai_schools():
    """导入湾仔区学校数据"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("导入湾仔区 (Wan Chai) 学校数据")
    print("=" * 60)
    
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0
    
    # 湾仔区学校数据
    schools = [
        # === GOVERNMENT SCHOOLS ===
        {
            "name": "HENNESSEY GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "軒尼詩道官立小學",
            "address": "130-140 HENNESSEY ROAD, WAN CHAI, HONG KONG",
            "phone": "25741123",
            "fax": "25741123",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Wan Chai",
            "school_code": "121144",
        },
        {
            "name": "WAN CHAI GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "灣仔官立小學",
            "address": "66 KENNEDY ROAD, WAN CHAI, HONG KONG",
            "phone": "25275211",
            "fax": "25275211",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Wan Chai",
            "school_code": "121153",
        },
        
        # === AIDED SCHOOLS ===
        {
            "name": "ST. FRANCIS' CANOSSIAN COLLEGE",
            "name_cn": "嘉諾撒聖方濟各書院",
            "address": "180 CAUSEWAY ROAD, WAN CHAI, HONG KONG",
            "phone": "25761636",
            "fax": "25761636",
            "supervisor": "-",
            "principal": "-",
            "gender": "GIRLS",
            "level": "middle",
            "finance_type": "Aided",
            "district": "Wan Chai",
            "school_code": "133540",
        },
        {
            "name": "HAVELOCK NO. 2 GOVERNMENT PRIMARY SCHOOL",
            "name_cn": "政府第二小學",
            "address": "8 HENNESSEY ROAD, WAN CHAI, HONG KONG",
            "phone": "25271123",
            "fax": "25271123",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Government",
            "district": "Wan Chai",
            "school_code": "121162",
        },
        {
            "name": "ST. JOAN OF ARC SECONDARY SCHOOL",
            "name_cn": "聖貞德中學",
            "address": "22 HENNESSEY ROAD, WAN CHAI, HONG KONG",
            "phone": "25743668",
            "fax": "25743668",
            "supervisor": "-",
            "principal": "-",
            "gender": "GIRLS",
            "level": "middle",
            "finance_type": "Aided",
            "district": "Wan Chai",
            "school_code": "133559",
        },
        {
            "name": "SHENG KUNG HUI (SPTOC) ST. JAMES' PRIMARY SCHOOL",
            "name_cn": "聖公會聖詹姆斯小學",
            "address": "85 CAUSEWAY ROAD, WAN CHAI, HONG KONG",
            "phone": "28321317",
            "fax": "28321317",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Aided",
            "district": "Wan Chai",
            "school_code": "133568",
        },
        
        # === DIRECT SUBSIDY ===
        {
            "name": "CHINESE INTERNATIONAL SCHOOL",
            "name_cn": "香港國際學校",
            "address": "1 SISTERS' ROAD, WAN CHAI, HONG KONG",
            "phone": "25772211",
            "fax": "25772211",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Direct",
            "district": "Wan Chai",
            "school_code": "600003",
        },
        
        # === PRIVATE ===
        {
            "name": "KOWLOON BRITISH SCHOOL",
            "name_cn": "九龍英國學校",
            "address": "29A HENNESSEY ROAD, WAN CHAI, HONG KONG",
            "phone": "25272888",
            "fax": "25272888",
            "supervisor": "-",
            "principal": "-",
            "gender": "CO-ED",
            "level": "primary",
            "finance_type": "Private",
            "district": "Wan Chai",
            "school_code": "600004",
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
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE district = 'Wan Chai'")
    wc_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n导入完成!")
    print(f"  新增: {inserted} 所")
    print(f"  更新: {updated} 所")
    print(f"  EDB来源总计: {total_edb} 所")
    print(f"  湾仔区总计: {wc_count} 所")

if __name__ == '__main__':
    import_wan_chai_schools()
