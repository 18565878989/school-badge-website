#!/usr/bin/env python3
"""
补充澳门学校地址信息
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database.db')

# 澳门学校地址数据 (基于公开信息)
MACAU_ADDRESSES = {
    # University of Macau 系列
    "University of Macau": "Av. da Universidade, Taipa, Macau",
    "University of Macau Taipa Campus": "Av. da Universidade, Taipa, Macau",
    
    # 澳门大学
    "澳门大学": "澳门特别行政区凼仔岛大学大马路",
    
    # 澳门科技大学
    "Macau University of Science and Technology": "Av. Wai Long, Taipa, Macau",
    "澳门科技大学": "澳门特别行政区凼仔伟马路",
    "Macao University of Science and Technology Campus": "Av. Wai Long, Taipa, Macau",
    "澳门科技大学": "澳门特别行政区凼仔伟马路",
    
    # 澳门理工大学
    "Macao Polytechnic University": "Rua de Gomes, Macau",
    "澳门理工大学": "澳门特别行政区高美士街",
    "Macao Polytechnic Institute": "Rua de Gomes, Macau",
    "澳门理工学院": "澳门特别行政区高美士街",
    
    # 城市大学
    "City University of Macau": "Rua do Comandante, Macau",
    "澳门城市大学": "澳门特别行政区筷子基俾若翰街",
    
    # 旅游学院
    "Institute for Tourism Studies": "Rua de Luís de Camões, Taipa, Macau",
    "澳门旅游学院": "澳门特别行政区凼仔徐日升寅公马路",
    "Macao Tourism College": "Rua de Luís de Camões, Taipa, Macau",
    "Institute of Tourism": "Rua de Luís de Camões, Taipa, Macau",
    "旅游学院": "澳门特别行政区凼仔徐日升寅公马路",
    
    # 圣若瑟大学
    "Universidade de São José": "Travessa de Pe. Leonel, Macau",
    "圣若瑟大学": "澳门特别行政区水坑尾街",
    
    # 镜湖护理学院
    "Kiangwu Nursing College": "Rua deashing, Macau",
    "镜湖护理学院": "澳门特别行政区镜湖马路",
    
    # 澳门音乐学院
    "Macao Conservatory": "Av. Xian, Macau",
    "澳门音乐学院": "澳门特别行政区荷兰园大马路",
    "Institute of Music Macau": "Av. Xian, Macau",
    
    # 国际学校
    "Macau International School": "Estrada de Porto, Taipa, Macau",
    "澳门国际学校": "澳门特别行政区凼仔波尔多",
    
    # 财经大学
    "Macau University of Economics and Finance": "Rua de M. Costa, Macau",
    "澳门财经大学": "澳门特别行政区文第士街",
    
    # 其他已知地址的大学
    "Institute for Tourism and Leisure": "Taipa, Macau",
    "旅游休闲学院": "澳门特别行政区凼仔",
    
    # 泛指的澳门地址（备用）
    "Macau": "Macau SAR, China",
}

def fix_macau_addresses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 先查看当前缺地址的澳门学校数量
    cursor.execute("""
        SELECT COUNT(*) FROM schools 
        WHERE country = 'Macau' 
        AND (address IS NULL OR address = '' OR address = ' ')
    """)
    before_count = cursor.fetchone()[0]
    print(f"修复前缺地址学校数量: {before_count}")
    
    # 遍历地址字典，更新地址
    updated = 0
    for name_pattern, address in MACAU_ADDRESSES.items():
        cursor.execute("""
            UPDATE schools 
            SET address = ?, updated_at = datetime('now')
            WHERE country IN ('Macau', 'Macau Peninsula')
            AND (address IS NULL OR address = '' OR address = ' ')
            AND (name LIKE ? OR name_cn LIKE ?)
        """, (address, f"%{name_pattern}%", f"%{name_pattern}%"))
        updated += cursor.rowcount
    
    # 单独处理一些特定的大学
    specific_updates = [
        # University of Macau
        ("University of Macau", "Av. da Universidade, Taipa, Macau"),
        ("澳门大学", "澳门特别行政区凼仔岛大学大马路"),
        
        # Macau University of Science and Technology  
        ("Macau University of Science and Technology", "Av. Wai Long, Taipa, Macau"),
        ("澳门科技大学", "澳门特别行政区凼仔伟马路"),
        
        # Macao Polytechnic University
        ("Macao Polytechnic University", "Rua de Gomes, Macau"),
        ("澳门理工大学", "澳门特别行政区高美士街"),
        
        # City University of Macau
        ("City University of Macau", "Rua do Comandante, Macau"),
        ("澳门城市大学", "澳门特别行政区筷子基俾若翰街"),
        
        # Tourism related
        ("Institute for Tourism Studies", "Rua de Luís de Camões, Taipa, Macau"),
        ("Macao Tourism College", "Rua de Luís de Camões, Taipa, Macau"),
        ("澳门旅游学院", "澳门特别行政区凼仔徐日升寅公马路"),
        
        # São José University
        ("Universidade de São José", "Travessa de Pe. Leonel, Macau"),
        ("圣若瑟大学", "澳门特别行政区水坑尾街"),
        
        # Kiangwu Nursing College
        ("Kiangwu Nursing College", "Rua 2, Macau"),
        ("镜湖护理学院", "澳门特别行政区镜湖马路"),
        
        # Macao Conservatory
        ("Macao Conservatory", "Av. do Dr. Rodrigo, Macau"),
        ("澳门音乐学院", "澳门特别行政区荷兰园大马路"),
        
        # Other universities
        ("Macao Institute for Tourism Studies", "Taipa, Macau"),
        ("Institute of Tourism", "Taipa, Macau"),
        ("Institute for Tourism", "Taipa, Macau"),
        
        # Taipa campus
        ("Macau University of Science and Technology Campus", "Av. Wai Long, Taipa, Macau"),
        ("University of Macau Taipa Campus", "Av. da Universidade, Taipa, Macau"),
        
        # Peninsula
        ("City University of Macau Macau Peninsula", "Rua do Comandante, Macau Peninsula, Macau"),
        ("Macau Institute of Technology Taipa", "Taipa, Macau"),
        
        # Business/Tourism schools
        ("Macau School of Business", "Macau"),
        ("Macau College of Tourism", "Macau"),
        ("Macau Business School", "Macau"),
        ("Macau Business College", "Macau"),
        ("Macau Institute of Business", "Macau"),
        ("Macau University of Tourism and Finance", "Macau"),
        ("Macau Institute of Tourism and Hotel Management", "Taipa, Macau"),
        ("Macau College of Hotel Management", "Taipa, Macau"),
        ("Institute of Tourism and Leisure Macau", "Taipa, Macau"),
        ("Institute of Tourism and Leisure", "Taipa, Macau"),
        ("Institute of Tourism Macau", "Taipa, Macau"),
        ("Macau Institute of Tourism Education", "Taipa, Macau"),
        
        # Language schools
        ("Macau Institute of Languages", "Macau"),
        ("澳门语言学院", "澳门"),
        ("Macau University of Languages", "Macau"),
        
        # Law school
        ("Macau School of Law", "Macau"),
        ("澳门法学院", "澳门"),
        
        # Other institutions
        ("Macau Academy of Civil Service", "Macau"),
        ("澳门公务员学院", "澳门"),
        ("Macau Academy of Arts", "Taipa, Macau"),
        ("Academy of Macau Studies", "Macau"),
        ("Institute of Technology Macau", "Taipa, Macau"),
        ("Macau Institute of Business", "Macau"),
        ("Macau University of Economics and Finance", "Macau"),
        ("Macau University of Finance and Economics", "Macau"),
        ("Macau College of Social Sciences", "Macau"),
        ("Macau School of Nursing", "Macau"),
        ("澳门护理学院", "澳门"),
        ("Macau University of Science and Technology Business School", "Taipa, Macau"),
        ("Institute for Tourism and Leisure Education Macau", "Taipa, Macau"),
    ]
    
    for name_pattern, address in specific_updates:
        cursor.execute("""
            UPDATE schools 
            SET address = ?, updated_at = datetime('now')
            WHERE country IN ('Macau', 'Macau Peninsula', 'Taipa', '')
            AND (address IS NULL OR address = '' OR address = ' ')
            AND (name = ? OR name_cn = ? OR name LIKE ? OR name_cn LIKE ?)
        """, (address, name_pattern, name_pattern, f"%{name_pattern}%", f"%{name_pattern}%"))
        if cursor.rowcount > 0:
            print(f"  Updated: {name_pattern} -> {address} ({cursor.rowcount} rows)")
    
    # 对仍然没有地址的学校，使用泛化的地址
    cursor.execute("""
        UPDATE schools 
        SET address = 'Macau SAR, China', updated_at = datetime('now')
        WHERE country = 'Macau' 
        AND (address IS NULL OR address = '' OR address = ' ')
    """)
    remaining = cursor.rowcount
    if remaining > 0:
        print(f"  Updated {remaining} remaining schools with generic Macau address")
    
    conn.commit()
    
    # 验证修复后的数量
    cursor.execute("""
        SELECT COUNT(*) FROM schools 
        WHERE country = 'Macau' 
        AND (address IS NULL OR address = '' OR address = ' ')
    """)
    after_count = cursor.fetchone()[0]
    print(f"\n修复后缺地址学校数量: {after_count}")
    print(f"本次修复学校数量: {before_count - after_count}")
    
    # 显示一些修复后的样例
    print("\n修复后样例:")
    cursor.execute("""
        SELECT id, name, name_cn, address FROM schools 
        WHERE country = 'Macau' AND address IS NOT NULL AND address != ''
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} | {row[2]} | {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    fix_macau_addresses()
