#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 108
Add 21 more Asian universities
Starting ID: 13844
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 108: East Asia & Central Asia Universities (21 schools)
# Countries: Taiwan, Hong Kong, Macau, China, Kazakhstan, Uzbekistan
SCHOOLS_BATCH_108 = [
    # Taiwan
    (13844, "National Taiwan University", "Taiwan", "Asia", "Taiwan", "Taipei", "University", "https://example.com/badge.png", "https://www.ntu.edu.tw", "Cultivate Talent, Serve the Nation", 1928, "Prof. Dr. Chung-Kai", None),
    (13845, "National Tsing Hua University", "Taiwan", "Asia", "Taiwan", "Hsinchu", "University", "https://example.com/badge.png", "https://www.nthu.edu.tw", "Sincerity with All Generations", 1911, "Prof. Dr. Hong", None),
    (13846, "National Cheng Kung University", "Taiwan", "Asia", "Taiwan", "Tainan", "University", "https://example.com/badge.png", "https://www.ncku.edu.tw", "Honesty, Diligence, Simplicity", 1931, "Prof. Dr. Huey-Jen", None),
    (13847, "National Chiao Tung University", "Taiwan", "Asia", "Taiwan", "Hsinchu", "University", "https://example.com/badge.png", "https://www.nctu.edu.tw", "Pureness, Perseverance, Perfection", 1958, "Prof. Dr. Ching-Ray", None),
    (13848, "National Yang Ming University", "Taiwan", "Asia", "Taiwan", "Taipei", "University", "https://example.com/badge.png", "https://www.ym.edu.tw", "Benevolent Healing", 1975, "Prof. Dr. Hsu", None),
    (13849, "National Central University", "Taiwan", "Asia", "Taiwan", "Taoyuan", "University", "https://example.com/badge.png", "https://www.ncu.edu.tw", "Sincerity, Simplicity, Diligence", 1915, "Prof. Dr. Wang", None),
    (13850, "National Sun Yat-sen University", "Taiwan", "Asia", "Taiwan", "Kaohsiung", "University", "https://example.com/badge.png", "https://www.nsysu.edu.tw", "Science for Humanity", 1980, "Prof. Dr. Shih", None),
    
    # Hong Kong
    (13851, "University of Hong Kong", "Hong Kong", "Asia", "Hong Kong", "Hong Kong", "University", "https://example.com/badge.png", "https://www.hku.hk", "Sapientia et Virtus", 1911, "Prof. Dr. Xiang", None),
    (13852, "Chinese University of Hong Kong", "Hong Kong", "Asia", "Hong Kong", "Hong Kong", "University", "https://example.com/badge.png", "https://www.cuhk.edu.hk", "The Whole Person", 1963, "Prof. Dr. Rocky", None),
    (13853, "Hong Kong University of Science and Technology", "Hong Kong", "Asia", "Hong Kong", "Hong Kong", "University", "https://example.com/badge.png", "https://www.hkust.edu.hk", "Advancing Knowledge, Serving Humanity", 1991, "Prof. Dr. Nancy", None),
    (13854, "Hong Kong Polytechnic University", "Hong Kong", "Asia", "Hong Kong", "Hong Kong", "University", "https://example.com/badge.png", "https://www.polyu.edu.hk", "To Learn and to Apply", 1937, "Prof. Dr. Timothy", None),
    (13855, "City University of Hong Kong", "Hong Kong", "Asia", "Hong Kong", "Hong Kong", "University", "https://example.com/badge.png", "https://www.cityu.edu.hk", "Professionalism and Creativity", 1984, "Prof. Dr. Waye", None),
    
    # Macau
    (13856, "University of Macau", "Macau", "Asia", "Macau", "Macau", "University", "https://example.com/badge.png", "https://www.um.edu.mo", "Truth, Friendship, Progress", 1981, "Prof. Dr. Yonghua", None),
    (13857, "Macau University of Science and Technology", "Macau", "Asia", "Macau", "Macau", "University", "https://example.com/badge.png", "https://www.must.edu.mo", "Excellence in Education, Innovation in Science", 2000, "Prof. Dr. Lei", None),
    
    # China (continued)
    (13858, "Peking University", "China", "Asia", "China", "Beijing", "University", "https://example.com/badge.png", "https://www.pku.edu.cn", "Freedoms and Responsibilities", 1898, "Prof. Dr. Hao", None),
    (13859, "Tsinghua University", "China", "Asia", "China", "Beijing", "University", "https://example.com/badge.png", "https://www.tsinghua.edu.cn", "Self-Discipline and Social Responsibility", 1911, "Prof. Dr. Qiu", None),
    (13860, "Fudan University", "China", "Asia", "China", "Shanghai", "University", "https://example.com/badge.png", "https://www.fudan.edu.cn", "Rich Knowledge, Ample Strength", 1905, "Prof. Dr.许宁", None),
    (13861, "Shanghai Jiao Tong University", "China", "Asia", "China", "Shanghai", "University", "https://example.com/badge.png", "https://www.sjtu.edu.cn", "Drive for Progress", 1896, "Prof. Dr. Lin", None),
    (13862, "Zhejiang University", "China", "Asia", "China", "Hangzhou", "University", "https://example.com/badge.png", "https://www.zju.edu.cn", "Seeking Truth, Pioneering Innovation", 1897, "Prof. Dr. Wu", None),
    (13863, "Nanjing University", "China", "Asia", "China", "Nanjing", "University", "https://example.com/badge.png", "https://www.nju.edu.cn", "Sincerity with Aspiration", 1902, "Prof. Dr. Tan", None),
    (13864, "Wuhan University", "China", "Asia", "China", "Wuhan", "University", "https://example.com/badge.png", "https://www.whu.edu.cn", "Self-Improvement, Determination", 1893, "Prof. Dr. Dou", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_108:
        id_, name, country, region, nation, city, level, badge_url, website, motto, founded, principal, school_code = school
        
        try:
            cursor.execute('''
                INSERT INTO schools (id, name, region, country, city, level, badge_url, website, motto, founded, principal, school_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_, name, region, nation, city, level, badge_url, website, motto, founded, principal, school_code))
            
            schools_added.append((id_, name, country))
            print(f"✓ Added ID {id_}: {name} ({country})")
            
        except sqlite3.IntegrityError as e:
            print(f"✗ Duplicate or error for ID {id_}: {name} - {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Batch 108 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
