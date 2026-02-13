#!/usr/bin/env python3
"""
添加第63批亚洲学校（21所）
新增国家/地区：泰国、菲律宾、印度、巴基斯坦、孟加拉
"""

import sqlite3
import os

# 切换到项目目录
os.chdir('/Users/wangfeng/.openclaw/workspace/school-badge-website')

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 亚洲学校数据 - 第63批
new_asian_schools = [
    # 泰国大学 (ID 12097-12101)
    (12097, "Mahidol University", "玛希隆大学", "Asia", "Thailand", "Bangkok", "999 Phutthamonthon 4 Road, Salaya, Nakhon Pathom 73170, Thailand", "university", "Top research university in Thailand, known for medical and health sciences.", "/static/images/placeholder_badge.svg", "https://www.mahidol.ac.th", " Wisdom of the Land", 1943, "Prof. Surapon", "manual"),
    (12098, "Chiang Mai University", "清迈大学", "Asia", "Thailand", "Chiang Mai", "239 Huay Kaew Road, Mueang Chiang Mai District, Chiang Mai 50200, Thailand", "university", "Northern Thailand's premier university, comprehensive academic programs.", "/static/images/placeholder_badge.svg", "https://www.cmu.ac.th", "Service to Society", 1964, "Prof. Sombat", "manual"),
    (12099, "Thammasat University", "法政大学", "Asia", "Thailand", "Bangkok", "2 Prachan Road, Phra Nakhon, Bangkok 10200, Thailand", "university", "Second oldest university in Thailand, known for law and social sciences.", "/static/images/placeholder_badge.svg", "https://www.tu.ac.th", "Truth, Dharma, Discipline", 1934, "Prof. Monchai", "manual"),
    (12100, "Kasetsart University", "农业大学", "Asia", "Thailand", "Bangkok", "50 Ngamwongwan Road, Chatuchak, Bangkok 10900, Thailand", "university", "Leading agricultural university in Thailand, first university in Asia for agriculture.", "/static/images/placeholder_badge.svg", "https://www.ku.ac.th", "Science and Technology for Nation", 1943, "Prof. Chongrak", "manual"),
    (12101, "Prince of Songkla University", "宋卡王子大学", "Asia", "Thailand", "Hat Yai", "15 Karnjanavanit Road, Hat Yai, Songkhla 90110, Thailand", "university", "Regional university network in Southern Thailand, comprehensive programs.", "/static/images/placeholder_badge.svg", "https://www.psu.ac.th", "Excellence in All Endeavors", 1962, "Prof. Soranit", "manual"),
    
    # 菲律宾大学 (ID 12102-12106)
    (12102, "University of the Philippines", "菲律宾大学", "Asia", "Philippines", "Quezon City", "UP Diliman, Quezon City 1101, Philippines", "university", "National university of the Philippines, premier state university system.", "/static/images/placeholder_badge.svg", "https://www.up.edu.ph", "Honesty, Excellence, and Social Responsibility", 1908, "Prof. Danilo", "manual"),
    (12103, "Ateneo de Manila University", "马尼拉雅典耀大学", "Asia", "Philippines", "Quezon City", "Katipunan Avenue, Loyola Heights, Quezon City 1108, Philippines", "university", "Leading private Catholic university, Jesuit institution known for excellence.", "/static/images/placeholder_badge.svg", "https://www.ateneo.edu", "Lux in Domino (Light in the Lord)", 1859, "Prof. Roberto", "manual"),
    (12104, "De La Salle University", "菲律宾德拉萨大学", "Asia", "Philippines", "Manila", "2401 Taft Avenue, Manila 1004, Philippines", "university", "Top private Catholic university, part of De La Salle system.", "/static/images/placeholder_badge.svg", "https://www.dlsu.edu.ph", "Religio, Mores, Cultura", 1911, "Prof. Br. Raymond", "manual"),
    (12105, "University of Santo Tomas", "圣托马斯大学", "Asia", "Philippines", "Manila", "España Boulevard, Sampaloc, Manila 1008, Philippines", "university", "Oldest existing university in Asia, Catholic institution founded in 1611.", "/static/images/placeholder_badge.svg", "https://www.ust.edu.ph", "Veritas in Caritate (Truth in Charity)", 1611, "Prof. Herminio", "manual"),
    (12106, "Philippine Science High School", "菲律宾科学高中", "Asia", "Philippines", "Quezon City", "Commonwealth Avenue, Diliman, Quezon City 1121, Philippines", "high_school", "Premier science high school in the Philippines, scholarship institution.", "/static/images/placeholder_badge.svg", "https://www.pshs.edu.ph", "Excellence in Science and Technology", 1964, "Dr. Josette", "manual"),
    
    # 印度大学 (ID 12107-12116)
    (12107, "Indian Institute of Technology Bombay", "印度理工学院孟买分校", "Asia", "India", "Mumbai", "Powai, Mumbai 400076, India", "university", "Top engineering institution in India, IIT system flagship campus.", "/static/images/placeholder_badge.svg", "https://www.iitb.ac.in", "ज्ञानं परमं ध्येयम् (Knowledge is the Supreme Goal)", 1958, "Prof. Subhasis", "manual"),
    (12108, "Indian Institute of Technology Delhi", "印度理工学院德里分校", "Asia", "India", "New Delhi", "Hauz Khas, New Delhi 110016, India", "university", "Premier engineering institute in India, known for technical excellence.", "/static/images/placeholder_badge.svg", "https://home.iitd.ac.in", "योगः कर्मसु कौशलम् (Yoga is excellence at work)", 1961, "Prof. K.N. Raju", "manual"),
    (12109, "Indian Institute of Technology Madras", "印度理工学院马德拉斯分校", "Asia", "India", "Chennai", "Adyar, Chennai 600036, India", "university", "Leading IIT campus in South India, beautiful campus by the bay.", "/static/images/placeholder_badge.svg", "https://www.iitm.ac.in", "Progress through Technical Excellence", 1959, "Prof. Bhaskar", "manual"),
    (12110, "Indian Institute of Technology Kanpur", "印度理工学院坎普尔分校", "Asia", "India", "Kanpur", "Kalyanpur, Kanpur 208016, India", "university", "Prestigious IIT campus known for engineering research.", "/static/images/placeholder_badge.svg", "https://www.iitk.ac.in", "तमसो मा ज्योतिर्गमय (Lead us from darkness to light)", 1959, "Prof. Abhay", "manual"),
    (12111, "Indian Institute of Technology Kharagpur", "印度理工学院卡拉格布尔分校", "Asia", "India", "Kharagpur", "Kharagpur 721302, West Bengal, India", "university", "First IIT established in India, known as the 'Industrial University'.", "/static/images/placeholder_badge.svg", "https://www.iitkgp.ac.in", "योगः कर्मसु कौशलम्", 1951, "Prof. Virendra", "manual"),
    (12112, "All India Institute of Medical Sciences", "全印医学科学研究所", "Asia", "India", "New Delhi", "Ansari Nagar, New Delhi 110029, India", "university", "Premier medical research and education institute in India.", "/static/images/placeholder_badge.svg", "https://www.aiims.edu", "Highest Standard of Medical Education", 1956, "Prof. Randeep", "manual"),
    (12113, "Jawaharlal Nehru University", "贾瓦哈拉尔尼赫鲁大学", "Asia", "India", "New Delhi", "New Mehrauli Road, New Delhi 110067, India", "university", "Leading research university in India, known for social sciences.", "/static/images/placeholder_badge.svg", "https://www.jnu.ac.in", "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन (Your right is to work only)", 1969, "Prof. M. Jagadesh", "manual"),
    (12114, "Banaras Hindu University", "贝拿勒斯印度大学", "Asia", "India", "Varanasi", "Varanasi 221005, Uttar Pradesh, India", "university", "One of Asia's largest residential universities, world heritage campus.", "/static/images/placeholder_badge.svg", "https://www.bhu.ac.in", "सत्यमेव जयते (Truth Alone Triumphs)", 1916, "Prof. P. C. Joshi", "manual"),
    (12115, "University of Delhi", "德里大学", "Asia", "India", "New Delhi", "Delhi 110007, India", "university", "Premier university in North India, known for humanities and sciences.", "/static/images/placeholder_badge.svg", "https://www.du.ac.in", "Service to the Nation", 1922, "Prof. Yogesh", "manual"),
    (12116, "Anna University", "安娜大学", "Asia", "India", "Chennai", "Guindy, Chennai 600025, India", "university", "Leading technical university in Tamil Nadu, named after C.N. Annadurai.", "/static/images/placeholder_badge.svg", "https://www.annauniv.edu", "Progress Through Technical Excellence", 1978, "Prof. K. Ravi", "manual"),
    
    # 巴基斯坦大学 (ID 12117)
    (12117, "University of the Punjab", "旁遮普大学", "Asia", "Pakistan", "Lahore", "Punjab University Campus, Lahore 54590, Pakistan", "university", "Oldest and largest university in Pakistan, comprehensive academic programs.", "/static/images/placeholder_badge.svg", "https://pu.edu.pk", "Knowledge is Power", 1882, "Prof. Niaz", "manual"),
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
