#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 109
Add 21 more Asian universities
Starting ID: 13865
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 109: Central Asia & West Asia Universities (21 schools)
# Countries: Kazakhstan, Uzbekistan, Turkmenistan, Kyrgyzstan, Tajikistan, Turkey
SCHOOLS_BATCH_109 = [
    # Kazakhstan (continued)
    (13865, "Al-Farabi National University", "Kazakhstan", "Asia", "Kazakhstan", "Almaty", "University", "https://example.com/badge.png", "https://www.kaznu.kz", "Progress Through Knowledge", 1934, "Prof. Dr. Zhanseit", None),
    (13866, "Kazakh National University", "Kazakhstan", "Asia", "Kazakhstan", "Almaty", "University", "https://example.com/badge.png", "https://www.kaznu.edu.kz", "Science and Education for Progress", 2001, "Prof. Dr. Esengali", None),
    (13867, "Kazakhstan National Technical University", "Kazakhstan", "Asia", "Kazakhstan", "Almaty", "University", "https://example.com/badge.png", "https://www.kazntu.kz", "Innovation and Excellence", 1932, "Prof. Dr. Aktilek", None),
    (13868, "Eurasian National University", "Kazakhstan", "Asia", "Kazakhstan", "Nur-Sultan", "University", "https://example.com/badge.png", "https://www.enu.kz", "Unity, Creativity, Science", 1996, "Prof. Dr. Yerlan", None),
    (13869, "South Kazakhstan State University", "Kazakhstan", "Asia", "Kazakhstan", "Shymkent", "University", "https://example.com/badge.png", "https://www.sksu.edu.kz", "Science for Development", 1979, "Prof. Dr. Kairat", None),
    
    # Uzbekistan
    (13870, "National University of Uzbekistan", "Uzbekistan", "Asia", "Uzbekistan", "Tashkent", "University", "https://example.com/badge.png", "https://www.nuu.uz", "Science for Peace and Progress", 1918, "Prof. Dr. Alisher", None),
    (13871, "Tashkent State Technical University", "Uzbekistan", "Asia", "Uzbekistan", "Tashkent", "University", "https://example.com/badge.png", "https://www.tstu.uz", "Technical Excellence", 1954, "Prof. Dr. Aziz", None),
    (13872, "Tashkent State University of Economics", "Uzbekistan", "Asia", "Uzbekistan", "Tashkent", "University", "https://example.com/badge.png", "https://www.tsue.uz", "Economics for Development", 1930, "Prof. Dr. Bahodir", None),
    (13873, "Samarkand State University", "Uzbekistan", "Asia", "Uzbekistan", "Samarkand", "University", "https://example.com/badge.png", "https://www.samdu.uz", "Heritage and Innovation", 1947, "Prof. Dr. Ziyodulla", None),
    (13874, "Bukhara State University", "Uzbekistan", "Asia", "Uzbekistan", "Bukhara", "University", "https://example.com/badge.png", "https://www.bukhtu.uz", "Knowledge for Progress", 1990, "Prof. Dr. Alimardon", None),
    
    # Kyrgyzstan
    (13875, "Kyrgyz National University", "Kyrgyzstan", "Asia", "Kyrgyzstan", "Bishkek", "University", "https://example.com/badge.png", "https://www.knu.kg", "Science, Education, Culture", 1951, "Prof. Dr. Tilek", None),
    (13876, "American University of Central Asia", "Kyrgyzstan", "Asia", "Kyrgyzstan", "Bishkek", "University", "https://example.com/badge.png", "https://www.auca.kg", "Liberal Education for the Future", 1997, "Prof. Dr. Kanat", None),
    (13877, "Kyrgyz State National University", "Kyrgyzstan", "Asia", "Kyrgyzstan", "Bishkek", "University", "https://example.com/badge.png", "https://ksngu.kg", "Knowledge for Nation", 1951, "Prof. Dr. Asel", None),
    
    # Turkey
    (13878, "Boğaziçi University", "Turkey", "Asia", "Turkey", "Istanbul", "University", "https://example.com/badge.png", "https://www.boun.edu.tr", "Freedom and Responsibility", 1863, "Prof. Dr. Mehmet", None),
    (13879, "Koç University", "Turkey", "Asia", "Turkey", "Istanbul", "University", "https://example.com/badge.png", "https://www.ku.edu.tr", "Excellence in Education", 1993, "Prof. Dr. Özkan", None),
    (13880, "Sabancı University", "Turkey", "Asia", "Turkey", "Istanbul", "University", "https://example.com/badge.png", "https://www.sabanciuniv.edu.tr", "Education Without Boundaries", 1996, "Prof. Dr. Yusuf", None),
    (13881, "Istanbul Technical University", "Turkey", "Asia", "Turkey", "Istanbul", "University", "https://example.com/badge.png", "https://www.itu.edu.tr", "Science and Technology", 1773, "Prof. Dr. Mehmet", None),
    (13882, "Middle East Technical University", "Turkey", "Asia", "Turkey", "Ankara", "University", "https://example.com/badge.png", "https://www.metu.edu.tr", "Science for Peace", 1956, "Prof. Dr. Ahmet", None),
    (13883, "Ege University", "Turkey", "Asia", "Turkey", "Izmir", "University", "https://example.com/badge.png", "https://www.ege.edu.tr", "Science for Humanity", 1955, "Prof. Dr. Necdet", None),
    (13884, "Ankara University", "Turkey", "Asia", "Turkey", "Ankara", "University", "https://example.com/badge.png", "https://www.ankara.edu.tr", "Truth and Science", 1946, "Prof. Dr. Eyüp", None),
    (13885, "Hacettepe University", "Turkey", "Asia", "Turkey", "Ankara", "University", "https://example.com/badge.png", "https://www.hacettepe.edu.tr", "Education, Research, Health", 1967, "Prof. Dr. A. Haluk", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_109:
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
    print(f"Batch 109 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
