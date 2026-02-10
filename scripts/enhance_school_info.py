#!/usr/bin/env python3
"""
补充香港学校的详细信息
基于香港教育局官方数据
"""

import sqlite3
import csv
import json

# 香港中西区学校详细信息（从教育局网站获取）
HK_SCHOOLS_DATA = [
    # 中学 - 官立/资助
    {
        'name_cn': '英皇書院',
        'data': {
            'name': "KING'S COLLEGE",
            'phone': '25470310',
            'fax': '25406908',
            'supervisor': 'MS CHAN KIT LING 陳潔玲女士',
            'principal': 'MS WONG CHAU LING FIONA 黃秋玲女士',
            'gender': 'BOYS',
            'finance_type': 'Government',
            'district': 'Central and Western',
            'address': '63A BONHAM ROAD HONG KONG',
            'address_cn': '香港西環般咸道６３號Ａ',
        }
    },
    {
        'name_cn': '聖若瑟書院',
        'data': {
            'name': "ST JOSEPH'S COLLEGE",
            'phone': '36524888',
            'fax': '28770232',
            'supervisor': 'MR CHAN KOK KEONG 陳國強先生',
            'principal': 'MR KWOK TIK MAN 郭廸民先生',
            'gender': 'BOYS',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '7 KENNEDY ROAD CENTRAL HONG KONG',
            'address_cn': '香港中環堅尼地道７號',
        }
    },
    {
        'name_cn': '聖保羅書院',
        'data': {
            'name': "ST PAUL'S COLLEGE",
            'phone': '25462241',
            'fax': '25597075',
            'supervisor': 'MR PONG YUEN SUN LOUIS 龐元燊先生',
            'principal': 'MR MAK CHI HO MICHAEL 麥志豪先生',
            'gender': 'BOYS',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '67-69 BONHAM ROAD HONG KONG',
            'address_cn': '香港般咸道６７－６９號',
        }
    },
    {
        'name_cn': '英華女學校',
        'data': {
            'name': "YING WA GIRLS' SCHOOL",
            'phone': '25463151',
            'fax': '28588669',
            'supervisor': 'REV SO SHING YIT ERIC 蘇成溢牧師',
            'principal': 'MS CHUK WAI KAN 祝慧勤女士',
            'gender': 'GIRLS',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '76 ROBINSON ROAD CENTRAL HONG KONG',
            'address_cn': '香港中環羅便臣道７６號',
        }
    },
    {
        'name_cn': '聖士提反女子中學',
        'data': {
            'name': "ST STEPHEN'S GIRLS' COLLEGE",
            'phone': '25492522',
            'fax': '25596994',
            'supervisor': 'REV. CANON KOON HO MING PETER DOUGLAS 管浩鳴法政牧師',
            'principal': 'MS LAM LAI YUNG 林麗容女士',
            'gender': 'GIRLS',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '2 LYTTELTON ROAD HONG KONG',
            'address_cn': '香港列堤頓道２號',
        }
    },
    {
        'name_cn': '聖嘉勒女書院',
        'data': {
            'name': "ST CLARE'S GIRLS' SCHOOL",
            'phone': '28171764',
            'fax': '28558420',
            'supervisor': 'MS WONG SHE LAI SHIRLEY 黃詩麗女士',
            'principal': 'MS WONG PIK YU 黃碧瑜女士',
            'gender': 'GIRLS',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '50 MOUNT DAVIS ROAD HONG KONG',
            'address_cn': '香港摩星嶺道５０號',
        }
    },
    {
        'name_cn': '聖類斯中學',
        'data': {
            'name': "ST LOUIS SCHOOL",
            'phone': '25460117',
            'fax': '25407341',
            'supervisor': 'FR CHAN HUNG KEE 陳鴻基神父',
            'principal': 'DR YICK HO KUEN 易浩權博士',
            'gender': 'BOYS',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '179 THIRD STREET HONG KONG',
            'address_cn': '香港第三街１７９號',
        }
    },
    {
        'name_cn': '樂善堂梁銶琚書院',
        'data': {
            'name': "LOK SIN TONG LEUNG KAU KUI COLLEGE",
            'phone': '28587002',
            'fax': '28572705',
            'supervisor': 'MR MOK MICHAEL MAN TOO 莫文韜先生',
            'principal': 'MR CHUNG YIU KEE 鍾耀基先生',
            'gender': 'CO-ED',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '28 HOSPITAL ROAD SAI YING POON HONG KONG',
            'address_cn': '香港西營盤醫院道２８號',
        }
    },
    {
        'name_cn': '高主教書院',
        'data': {
            'name': "RAIMONDI COLLEGE",
            'phone': '25222159',
            'fax': '25256725',
            'supervisor': 'MS LO WING KUM 盧詠琴女士',
            'principal': 'MR HO TAI ON 何泰安先生',
            'gender': 'CO-ED',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '2 ROBINSON ROAD MID-LEVEL HONG KONG',
            'address_cn': '香港半山羅便臣道二號',
        }
    },
    {
        'name_cn': '聖士提反堂中學',
        'data': {
            'name': "ST STEPHEN'S CHURCH COLLEGE",
            'phone': '25466111',
            'fax': '25407518',
            'supervisor': 'REV IP KAM FAI 葉錦輝牧師',
            'principal': 'MR MAK WAI LUN 麥偉麟先生',
            'gender': 'CO-ED',
            'finance_type': 'Aided',
            'district': 'Central and Western',
            'address': '62 POKFULAM ROAD HONG KONG',
            'address_cn': '香港薄扶林道６２號',
        }
    },
    {
        'name_cn': '聖保羅男女中學',
        'data': {
            'name': "ST PAUL'S CO-EDUCATIONAL COLLEGE",
            'phone': '25231123',
            'fax': '28770442',
            'supervisor': 'MR LEE CHIEN 利乾先生',
            'principal': 'MR POON SIU CHI 潘紹慈先生',
            'gender': 'CO-ED',
            'finance_type': 'Direct Subsidy',
            'district': 'Central and Western',
            'address': '33 MACDONNELL ROAD CENTRAL HONG KONG',
            'address_cn': '香港中環麥當勞道',
        }
    },
    # 小学
    {
        'name_cn': '般咸道官立小學',
        'data': {
            'name': "BONHAM RD GOVERNMENT PRI SCH",
            'phone': '25171216',
            'fax': '28576743',
            'supervisor': 'MR LAM YU HANG 林雨恒先生',
            'principal': 'MR LEE MING KAI LOUIE 李明佳先生',
            'gender': 'CO-ED',
            'finance_type': 'Government',
            'level': 'elementary',
            'district': 'Central and Western',
            'address': '9A BONHAM ROAD HONG KONG',
            'address_cn': '香港般咸道９號Ａ',
        }
    },
    {
        'name_cn': '李陞小學',
        'data': {
            'name': "LI SING PRIMARY SCHOOL",
            'phone': '25408966',
            'fax': '25405819',
            'supervisor': 'MS SHEK WAN HAAN KITTY 石慧嫻女士',
            'principal': 'MS YU WINI 余詠莉女士',
            'gender': 'CO-ED',
            'finance_type': 'Government',
            'level': 'elementary',
            'district': 'Central and Western',
            'address': '119 HIGH STREET SAI YING PUN HONG KONG',
            'address_cn': '香港西營盤高街１１９號',
        }
    },
    {
        'name_cn': '天主教總堂區學校',
        'data': {
            'name': "CATHOLIC MISSION SCHOOL",
            'phone': '25477618',
            'fax': '25591595',
            'supervisor': 'REV LI CHI YUEN 李志源神父',
            'principal': 'MS CHUNG OI MAN 宗藹雯女士',
            'gender': 'CO-ED',
            'finance_type': 'Aided',
            'level': 'elementary',
            'district': 'Central and Western',
            'address': 'RUTTER STREET CENTRAL HONG KONG',
            'address_cn': '香港中環律打街',
        }
    },
    {
        'name_cn': '嘉諾撒聖心學校',
        'data': {
            'name': "SACRED HEART CANOSSIAN SCHOOL",
            'phone': '25248679',
            'fax': '28698154',
            'supervisor': 'MS LEE YUK SHAN ROSSETTI 李玉珊女士',
            'principal': 'MS HO KA YEE MARTINA 何嘉儀女士',
            'gender': 'GIRLS',
            'finance_type': 'Aided',
            'level': 'elementary',
            'district': 'Central and Western',
            'address': '26 CAINE ROAD CENTRAL HONG KONG',
            'address_cn': '香港中環堅道',
        }
    },
]

def update_schools():
    """更新学校信息"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    updated = 0
    not_found = []
    
    for item in HK_SCHOOLS_DATA:
        name_cn = item['name_cn']
        data = item['data']
        
        # 查找学校
        cursor.execute(
            'SELECT id, name FROM schools WHERE name_cn = ? AND region = "Hong Kong"',
            (name_cn,)
        )
        school = cursor.fetchone()
        
        if school:
            school_id = school[0]
            
            # 构建更新语句
            updates = []
            params = []
            
            for field, value in data.items():
                if value:
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            if updates:
                params.append(school_id)
                sql = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                updated += 1
                print(f"✓ {name_cn}")
        else:
            not_found.append(name_cn)
            print(f"✗ {name_cn} - 未找到")
    
    conn.commit()
    conn.close()
    
    return updated, not_found

def export_template():
    """导出学校信息模板CSV"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取所有香港学校
    cursor.execute("""
        SELECT id, name, name_cn, level
        FROM schools 
        WHERE region = 'Hong Kong'
        ORDER BY level, name_cn
    """)
    
    with open('scripts/supplement/hk_schools_info_template.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'name', 'name_cn', 'level',
            'phone', 'fax', 'supervisor', 'principal',
            'gender', 'finance_type', 'district',
            'address_en', 'address_cn'
        ])
        
        for row in cursor.fetchall():
            writer.writerow([row[0], row[1], row[2], row[3], '', '', '', '', '', '', '', ''])
    
    conn.close()
    print("\n已导出模板到 scripts/supplement/hk_schools_info_template.csv")

def main():
    """主函数"""
    print("=" * 60)
    print("补充香港学校详细信息")
    print("=" * 60)
    
    # 更新学校信息
    updated, not_found = update_schools()
    
    print("\n" + "=" * 60)
    print(f"更新结果: {updated} 所学校")
    print(f"未找到: {len(not_found)} 所")
    
    if not_found:
        print("\n未找到的学校:")
        for name in not_found:
            print(f"  - {name}")
    
    # 导出模板供手动补充
    export_template()
    
    print("\n下一步:")
    print("1. 编辑 CSV 文件补充更多学校信息")
    print("2. 运行 python scripts/import_school_info.py import hk_schools_info_template.csv")

if __name__ == '__main__':
    main()
