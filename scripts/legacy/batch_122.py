#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools - Batch 122 (Next Batch)
Add 21 more Asian universities continuing the sequence
Starting ID: 20090
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 122: Additional Asian Universities (21 schools)
# Focusing on underrepresented countries and regions
SCHOOLS_BATCH_122 = [
    # Taiwan - underrepresented (adding more)
    (20090, "National Chengchi University", "Taiwan", "Asia", "Taipei", "University", "https://example.com/badge.png", "https://nccu.edu.tw", "Integrity and Innovation", 1927, "Prof. Dr. Shen", None),
    (20091, "National Chung Hsing University", "Taiwan", "Asia", "Taichung", "University", "https://example.com/badge.png", "https://nchu.edu.tw", "Sincerity and Effort", 1919, "Prof. Dr. Chang", None),
    (20092, "National Yang Ming Chiao Tung University", "Taiwan", "Asia", "Taipei", "University", "https://example.com/badge.png", "https://ym.edu.tw", "Benefit Humanity", 1975, "Prof. Dr. Lin", None),
    (20093, "National Dong Hwa University", "Taiwan", "Asia", "Hualien", "University", "https://example.com/badge.png", "https://ndhu.edu.tw", "Sincerity and Simplicity", 1994, "Prof. Dr. Wu", None),
    (20094, "National Cheng Kung University", "Taiwan", "Asia", "Tainan", "University", "https://example.com/badge.png", "https://ncku.edu.tw", "Diligence and Frugality", 1931, "Prof. Dr. Huei", None),
    
    # Hong Kong - underrepresented
    (20095, "The University of Hong Kong", "Hong Kong", "Asia", "Hong Kong", "University", "https://example.com/badge.png", "https://hku.hk", "Sapientia et Virtus", 1911, "Prof. Dr. Xiang", None),
    (20096, "The Chinese University of Hong Kong", "Hong Kong", "Asia", "Hong Kong", "University", "https://example.com/badge.png", "https://cuhk.edu.hk", "Combining Knowledge with Moral Vision", 1963, "Prof. Dr. Rocky", None),
    (20097, "Hong Kong University of Science and Technology", "Hong Kong", "Asia", "Hong Kong", "University", "https://example.com/badge.png", "https://hkust.edu.hk", "Advancing Knowledge, Creating Impact", 1991, "Prof. Dr. Wei", None),
    (20098, "City University of Hong Kong", "Hong Kong", "Asia", "Hong Kong", "University", "https://example.com/badge.png", "https://cityu.edu.hk", "Officium et Civitas", 1984, "Prof. Dr. Tang", None),
    (20099, "Hong Kong Polytechnic University", "Hong Kong", "Asia", "Hong Kong", "University", "https://example.com/badge.png", "https://polyu.edu.hk", "To Learn and to Apply, for the Benefit of Mankind", 1937, "Prof. Dr. Chew", None),
    
    # Macau - underrepresented
    (20100, "Macao Polytechnic University", "Macau", "Asia", "Macau", "University", "https://example.com/badge.png", "https://mpu.edu.mo", "Wisdom and Perseverance", 1981, "Prof. Dr. Lei", None),
    (20101, "Macao University of Science and Technology", "Macau", "Asia", "Macau", "University", "https://example.com/badge.png", "https://must.edu.mo", "Science and Innovation", 2000, "Prof. Dr. Liu", None),
    (20102, "Institute for Tourism Studies", "Macau", "Asia", "Macau", "Institute", "https://example.com/badge.png", "https://ift.edu.mo", "Excellence in Tourism Education", 1995, "Prof. Dr. Fanny", None),
    
    # Central Asia - underrepresented
    (20103, "Kazakhstan Institute of Management", "Kazakhstan", "Asia", "Almaty", "Institute", "https://example.com/badge.png", "https://kimep.kz", "Excellence in Business Education", 1991, "Prof. Dr. Baltabay", None),
    (20104, "Al-Farabi Kazakh National University", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://kaznu.edu.kz", "Knowledge, Innovation, Globalization", 1934, "Prof. Dr. Zhanseit", None),
    (20105, "KIMEP University", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://kimep.kz", "Education for Global Competitiveness", 1992, "Prof. Dr. Botakoz", None),
    (20106, "American University of Central Asia", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://auca.kg", "Liberal Arts Education", 1997, "Prof. Dr. Andrew", None),
    (20107, "Kyrgyz National University", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://university.kg", "Science and Knowledge", 1951, "Prof. Dr. Rysbek", None),
    (20108, "Osh State University", "Kyrgyzstan", "Asia", "Osh", "University", "https://example.com/badge.png", "https://oshsu.kg", "Higher Education Excellence", 1992, "Prof. Dr. Askar", None),
    (20109, "Tajik National University", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://tnu.tj", "Science and Progress", 1947, "Prof. Dr. Davlat", None),
    (20110, "National University of Uzbekistan", "Uzbekistan", "Asia", "Tashkent", "University", "https://example.com/badge.png", "https://nuu.uz", "Knowledge and Innovation", 1918, "Prof. Dr. Botir", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_122:
        id_, name, country, region, city, level, badge_url, website, motto, founded, principal, school_code = school
        
        try:
            cursor.execute('''
                INSERT INTO schools (id, name, region, country, city, level, badge_url, website, motto, founded, principal, school_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_, name, region, country, city, level, badge_url, website, motto, founded, principal, school_code))
            
            schools_added.append((id_, name, country))
            print(f"✓ Added ID {id_}: {name} ({country})")
            
        except sqlite3.IntegrityError as e:
            print(f"✗ Duplicate or error for ID {id_}: {name} - {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Batch 122 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
