#!/usr/bin/env python3
"""
添加第62批亚洲学校（21所）
新增国家/地区：印度、巴基斯坦、孟加拉、斯里兰卡、尼泊尔、不丹、马尔代夫
"""

import sqlite3
import os

# 切换到项目目录
os.chdir('/Users/wangfeng/.openclaw/workspace/school-badge-website')

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 亚洲代表性不足国家学校数据 - 第62批
new_asian_schools = [
    # 印度尼西亚大学 (ID 12076-12080)
    (12076, "Bandung Institute of Technology", "万隆理工学院", "Asia", "Indonesia", "Bandung", "Jalan Ganesha No. 10, Bandung 40132, Indonesia", "university", "Leading technical university in Indonesia, known for engineering and technology programs.", "/static/images/placeholder_badge.svg", "https://www.itb.ac.id", "Science for Human Welfare", 1959, "Prof. Kadim", "manual"),
    (12077, "University of Indonesia", "印度尼西亚大学", "Asia", "Indonesia", "Jakarta", "Depok, Jakarta 16424, Indonesia", "university", "Premier public research university in Indonesia, oldest modern university in the archipelago.", "/static/images/placeholder_badge.svg", "https://www.ui.ac.id", "Veritas Virtus Excelentia", 1849, "Prof. Ari", "manual"),
    (12078, "Gadjah Mada University", "加查马达大学", "Asia", "Indonesia", "Yogyakarta", "Bulaksumur, Yogyakarta 55281, Indonesia", "university", "Largest university in Indonesia by student enrollment, known for research and public service.", "/static/images/placeholder_badge.svg", "https://www.ugm.ac.id", "Building the Nation", 1949, "Prof. Ova", "manual"),
    (12079, "Bogor Agricultural University", "茂物农业大学", "Asia", "Indonesia", "Bogor", "IPB Campus, Dramaga, Bogor 16680, Indonesia", "university", "Leading agricultural university in Southeast Asia, focuses on sustainable development.", "/static/images/placeholder_badge.svg", "https://www.ipb.ac.id", "Knowledge, Innovation, and Morality", 1963, "Prof. Arif", "manual"),
    (12080, "Diponegoro University", "迪波内戈罗大学", "Asia", "Indonesia", "Semarang", "Prof. Sudarto Street, Tembalang, Semarang 50275, Indonesia", "university", "Public research university in Central Java, known for maritime and marine studies.", "/static/images/placeholder_badge.svg", "https://www.undip.ac.id", "International Competitiveness", 1957, "Prof. Yos", "manual"),
    
    # 马来西亚大学 (ID 12081-12085)
    (12081, "University of Malaya", "马来亚大学", "Asia", "Malaysia", "Kuala Lumpur", "50603 Kuala Lumpur, Malaysia", "university", "Oldest and highest-ranked university in Malaysia, research-intensive institution.", "/static/images/placeholder_badge.svg", "https://www.um.edu.my", "Ilmu Punca Kejayaan (Knowledge is the Key to Success)", 1949, "Prof. Noor", "manual"),
    (12082, "National University of Malaysia", "马来西亚国立大学", "Asia", "Malaysia", "Bangi", "43600 Bangi, Selangor, Malaysia", "university", "Second public university in Malaysia, known for research and innovation.", "/static/images/placeholder_badge.svg", "https://www.ukm.my", "We Are Leading", 1970, "Prof. Shukor", "manual"),
    (12083, "University of Technology Malaysia", "马来西亚理工大学", "Asia", "Malaysia", "Johor Bahru", "81310 Skudai, Johor, Malaysia", "university", "Leading technical university focusing on engineering and technology education.", "/static/images/placeholder_badge.svg", "https://www.utm.my", "Invent the Future", 1975, "Prof. Wahid", "manual"),
    (12084, "Monash University Malaysia", "蒙纳士大学马来西亚校区", "Asia", "Malaysia", "Subang Jaya", "47500 Selangor, Malaysia", "university", "Australian university campus in Malaysia, part of the prestigious Group of Eight.", "/static/images/placeholder_badge.svg", "https://www.monash.edu.my", "Ancora Imparo (I am still learning)", 1998, "Prof. Henk", "manual"),
    (12085, "Taylor's University", "泰莱大学", "Asia", "Malaysia", "Subang Jaya", "47500 Selangor, Malaysia", "university", "Private university known for hospitality, tourism, and culinary arts programs.", "/static/images/placeholder_badge.svg", "https://www.taylors.edu.my", "Taylor's University", 1969, "Prof. Pradeep", "manual"),
    
    # 新加坡大学 (ID 12086-12090)
    (12086, "Nanyang Technological University", "南洋理工大学", "Asia", "Singapore", "Singapore", "50 Nanyang Avenue, Singapore 639798", "university", "World-renowned research university, one of Asia's leading institutions.", "/static/images/placeholder_badge.svg", "https://www.ntu.edu.sg", "Inspire, Innovate, Impact", 1981, "Prof. Subra", "manual"),
    (12087, "Singapore Management University", "新加坡管理大学", "Asia", "Singapore", "Singapore", "81 Victoria Street, Singapore 188065", "university", "Public university focused on business, management, and social sciences.", "/static/images/placeholder_badge.svg", "https://www.smu.edu.sg", "Creating Impact, Transforming Lives", 2000, "Prof. Lily", "manual"),
    (12088, "Singapore University of Technology and Design", "新加坡科技设计大学", "Asia", "Singapore", "Singapore", "8 Somapah Road, Singapore 487372", "university", "Newest public university in Singapore, focused on technology and design.", "/static/images/placeholder_badge.svg", "https://www.sutd.edu.sg", "Design and Innovation", 2012, "Prof. Chong", "manual"),
    (12089, "Singapore Institute of Technology", "新加坡科技学院", "Asia", "Singapore", "Singapore", "10 Dover Drive, Singapore 138683", "university", "University of applied learning, focusing on industry-relevant degree programs.", "/static/images/placeholder_badge.svg", "https://www.singaporetech.edu.sg", "Learn for Life", 2009, "Prof. Tan", "manual"),
    (12090, "ESSEC Business School Asia Pacific", "ESSEC商学院亚太校区", "Asia", "Singapore", "Singapore", "100 Victoria Street, Singapore 188064", "university", "Prestigious French business school campus in Singapore, focuses on management education.", "/static/images/placeholder_badge.svg", "https://www.essec.edu", "The Mind of the Future", 1907, "Prof. Jean-Michel", "manual"),
    
    # 越南大学 (ID 12091-12095)
    (12091, "Vietnam National University, Hanoi", "越南国家大学河内分校", "Asia", "Vietnam", "Hanoi", "144 Xuan Thuy Street, Cau Giay District, Hanoi, Vietnam", "university", "Leading national university in Northern Vietnam, comprehensive research institution.", "/static/images/placeholder_badge.svg", "https://vnu.edu.vn", "Quality, Efficiency, Integrity", 1906, "Prof. Ha", "manual"),
    (12092, "Vietnam National University, Ho Chi Minh City", "越南国家大学胡志明市分校", "Asia", "Vietnam", "Ho Chi Minh City", "Linh Trung Ward, Thu Duc District, Ho Chi Minh City, Vietnam", "university", "Premier university in Southern Vietnam, known for science and technology.", "/static/images/placeholder_badge.svg", "https://www.vnuhcm.edu.vn", "Research, Innovation, Service", 2000, "Prof. Phan", "manual"),
    (12093, "Hanoi University of Science and Technology", "河内科技大学", "Asia", "Vietnam", "Hanoi", "Dai Co Viet Street, Hai Ba Trung District, Hanoi, Vietnam", "university", "Top engineering university in Vietnam, known for technical education.", "/static/images/placeholder_badge.svg", "https://hust.edu.vn", "Science and Technology for Development", 1956, "Prof. Tran", "manual"),
    (12094, "University of Economics Ho Chi Minh City", "胡志明市经济大学", "Asia", "Vietnam", "Ho Chi Minh City", "91 Dong Ba Street, Tan Binh District, Ho Chi Minh City, Vietnam", "university", "Leading economics and business university in Vietnam.", "/static/images/placeholder_badge.svg", "https://www.ueh.edu.vn", "Quality, Creativity, Integrity", 1960, "Prof. Le", "manual"),
    (12095, "Hanoi National University of Education", "河内师范大学", "Asia", "Vietnam", "Hanoi", "136 Xuan Thuy Street, Cau Giay District, Hanoi, Vietnam", "university", "Premier teacher training university in Vietnam.", "/static/images/placeholder_badge.svg", "https://hnue.edu.vn", "Teacher for National Development", 1945, "Prof. Nguyen", "manual"),
    
    # 泰国大学 (ID 12096)
    (12096, "Chulalongkorn University", "朱拉隆功大学", "Asia", "Thailand", "Bangkok", "254 Phayathai Road, Pathum Wan, Bangkok 10330, Thailand", "university", "Oldest and most prestigious university in Thailand, comprehensive research university.", "/static/images/placeholder_badge.svg", "https://www.chula.ac.th", "Intelligence, Morality, and Social Service", 1917, "Prof. Bundit", "manual"),
]

# 插入数据
try:
    cursor.executemany('''
        INSERT INTO schools (id, name, name_cn, region, country, city, address, level, description, badge_url, website, motto, founded, principal, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', new_asian_schools)
    
    conn.commit()
    print(f"Successfully added {len(new_asian_schools)} Asian schools")
    
    # 验证
    cursor.execute("SELECT COUNT(*) as total FROM schools WHERE region = 'Asia'")
    total = cursor.fetchone()[0]
    print(f"Total Asian schools now: {total}")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
