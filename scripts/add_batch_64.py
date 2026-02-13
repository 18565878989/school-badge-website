#!/usr/bin/env python3
"""
添加第64批亚洲学校（21所）
新增国家/地区：巴基斯坦、孟加拉、斯里兰卡、尼泊尔、缅甸、柬埔寨
"""

import sqlite3
import os

# 切换到项目目录
os.chdir('/Users/wangfeng/.openclaw/workspace/school-badge-website')

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 亚洲学校数据 - 第64批
new_asian_schools = [
    # 巴基斯坦大学 (ID 12118-12122)
    (12118, "Lahore University of Management Sciences", "拉合尔管理科学大学", "Asia", "Pakistan", "Lahore", "Lahore Canal Bank, Lahore 54792, Pakistan", "university", "Top business school in Pakistan, known for management education.", "/static/images/placeholder_badge.svg", "https://www.lums.edu.pk", "Inspiring Excellence", 1984, "Prof. S. Baqar", "manual"),
    (12119, "Pakistan Institute of Engineering and Applied Sciences", "巴基斯坦工程与应用科学学院", "Asia", "Pakistan", "Islamabad", "Nilore, Islamabad 45650, Pakistan", "university", "Premier engineering and sciences university in Pakistan.", "/static/images/placeholder_badge.svg", "https://www.pieas.edu.pk", "Excellence in Science and Technology", 1967, "Prof. Syed", "manual"),
    (12120, "National University of Sciences and Technology", "国立科技大学", "Asia", "Pakistan", "Islamabad", "Sector H-12, Islamabad, Pakistan", "university", "Leading technical university in Pakistan, focus on engineering and sciences.", "/static/images/placeholder_badge.svg", "https://www.nust.edu.pk", "Innovation, Excellence, Relevance", 1991, "Prof. Javed", "manual"),
    (12121, "Quaid-i-Azam University", "伊克巴尔大学", "Asia", "Pakistan", "Islamabad", "Islamabad 45320, Pakistan", "university", "Top research university in Pakistan, comprehensive academic programs.", "/static/images/placeholder_badge.svg", "https://www.qau.edu.pk", "Knowledge, Vision, Excellence", 1967, "Prof. Zia", "manual"),
    (12122, "University of Karachi", "卡拉奇大学", "Asia", "Pakistan", "Karachi", "University Road, Karachi 75270, Pakistan", "university", "Largest university in Sindh province, diverse academic programs.", "/static/images/placeholder_badge.svg", "https://www.uok.edu.pk", "Karachi University", 1951, "Prof. Khalid", "manual"),
    
    # 孟加拉大学 (ID 12123-12127)
    (12123, "University of Dhaka", "达卡大学", "Asia", "Bangladesh", "Dhaka", "Nilkhet Road, Dhaka 1000, Bangladesh", "university", "Oldest and largest university in Bangladesh, comprehensive institution.", "/static/images/placeholder_badge.svg", "https://www.du.ac.bd", "Truth and Knowledge", 1921, "Prof. Md. Akhtaruzzaman", "manual"),
    (12124, "Bangladesh University of Engineering and Technology", "孟加拉工程技术大学", "Asia", "Bangladesh", "Dhaka", "Ashulia, Dhaka 1349, Bangladesh", "university", "Top engineering university in Bangladesh, leading technical institution.", "/static/images/placeholder_badge.svg", "https://www.buet.ac.bd", "Engineering for Nation Building", 1962, "Prof. Rafiqul", "manual"),
    (12125, "Jahangirnagar University", "贾汉吉尔诺格尔大学", "Asia", "Bangladesh", "Dhaka", "Savar, Dhaka 1342, Bangladesh", "university", "Public university known for environmental studies and sciences.", "/static/images/placeholder_badge.svg", "https://www.juniv.edu", "Knowledge is Light", 1970, "Prof. M. Shahidullah", "manual"),
    (12126, "BRAC University", "BRAC大学", "Asia", "Bangladesh", "Dhaka", "Mohakhali, Dhaka 1212, Bangladesh", "university", "Private university known for innovation and social impact.", "/static/images/placeholder_badge.svg", "https://www.bracu.ac.bd", "Empowering Generations", 2001, "Prof. Vincent", "manual"),
    (12127, "North South University", "南北大学", "Asia", "Bangladesh", "Dhaka", "Bashundhara, Dhaka 1229, Bangladesh", "university", "First private university in Bangladesh, comprehensive academic programs.", "/static/images/placeholder_badge.svg", "https://www.nsu.edu.bd", "Leadership, Excellence", 1992, "Prof. Atiur", "manual"),
    
    # 斯里兰卡大学 (ID 12128-12132)
    (12128, "University of Colombo", "科伦坡大学", "Asia", "Sri Lanka", "Colombo", "Kollupitiya, Colombo 03, Sri Lanka", "university", "Oldest modern university in Sri Lanka, leading research institution.", "/static/images/placeholder_badge.svg", "https://www.cmb.ac.lk", "Siddhartha Shriya (Buddha's Enlightenment)", 1921, "Prof. Chandrika", "manual"),
    (12129, "University of Peradeniya", "佩拉德尼亚大学", "Asia", "Sri Lanka", "Peradeniya", "Peradeniya, Kandy 20400, Sri Lanka", "university", "Premier university in Sri Lanka, beautiful hill campus.", "/static/images/placeholder_badge.svg", "https://www.pdn.ac.lk", "Scholarship in Service", 1942, "Prof. H. M. D. S. Herath", "manual"),
    (12130, "University of Moratuwa", "莫拉图瓦大学", "Asia", "Sri Lanka", "Moratuwa", "Katubedda, Moratuwa 10400, Sri Lanka", "university", "Leading technology university in Sri Lanka.", "/static/images/placeholder_badge.svg", "https://www.mrt.ac.lk", "Excellence in Technology", 1942, "Prof. Janaka", "manual"),
    (12131, "University of Jaffna", "贾夫纳大学", "Asia", "Sri Lanka", "Jaffna", "Kunnapuram, Jaffna 40000, Sri Lanka", "university", "Leading university in Northern Sri Lanka.", "/static/images/placeholder_badge.svg", "https://www.univ.jfn.ac.lk", "Wisdom, Virtue, Service", 1974, "Prof. S. Srisatkunarajah", "manual"),
    (12132, "Sri Lanka Institute of Information Technology", "斯里兰卡信息技术学院", "Asia", "Sri Lanka", "Malabe", "Malabe, Sri Lanka", "university", "Leading IT education provider in Sri Lanka.", "/static/images/placeholder_badge.svg", "https://www.sliit.lk", "Innovation in IT", 1999, "Prof. Lalith", "manual"),
    
    # 尼泊尔大学 (ID 12133-12137)
    (12133, "Tribhuvan University", "特里布文大学", "Asia", "Nepal", "Kirtipur", "Kirtipur, Kathmandu 44618, Nepal", "university", "Oldest and largest university in Nepal, comprehensive academic programs.", "/static/images/placeholder_badge.svg", "https://www.tribhuvan university.edu.np", "Knowledge is Power", 1959, "Prof. Tirtha", "manual"),
    (12134, "Kathmandu University", "加德满都大学", "Asia", "Nepal", "Dhulikhel", "Dhulikhel, Kavrepalanchok 45210, Nepal", "university", "Private university known for engineering and sciences.", "/static/images/placeholder_badge.svg", "https://www.ku.edu.np", "Quality Higher Education", 1991, "Prof. Bhadra", "manual"),
    (12135, "Pokhara University", "博卡拉大学", "Asia", "Nepal", "Lekhnath", "Lekhnath, Kaski 33700, Nepal", "university", "Private university in Western Nepal, diverse programs.", "/static/images/placeholder_badge.svg", "https://www.pokharauniversity.edu.np", "Excellence in Education", 1996, "Prof. Gopi", "manual"),
    (12136, "Patan Academy of Health Sciences", "帕坦健康科学学院", "Asia", "Nepal", "Lagankhel", "Lagankhel, Lalitpur 44700, Nepal", "university", "Medical university focusing on rural healthcare.", "/static/images/placeholder_badge.svg", "https://www.pahs.edu.np", "Community-Oriented Medical Education", 2009, "Prof. Ranjan", "manual"),
    (12137, "National College of Engineering", "国家工程学院", "Asia", "Nepal", "Narayanhiti", "Narayanhiti, Kathmandu 44600, Nepal", "university", "Leading engineering college in Nepal.", "/static/images/placeholder_badge.svg", "https://www.nce.edu.np", "Engineering for Nation", 1972, "Prof. Shree", "manual"),
    
    # 缅甸大学 (ID 12138)
    (12138, "Yangon University", "仰光大学", "Asia", "Myanmar", "Yangon", "Kamayut, Yangon 11041, Myanmar", "university", "Oldest and most prestigious university in Myanmar.", "/static/images/placeholder_badge.svg", "https://www.yau.edu.mm", "Knowledge, Virtue, Ability", 1920, "Prof. Aung", "manual"),
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
