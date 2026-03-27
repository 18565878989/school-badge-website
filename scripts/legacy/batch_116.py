#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 116
Add 21 more Asian universities - Central & West Asia
Starting ID: 16819
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 116: Central & West Asia Additional (21 schools)
SCHOOLS_BATCH_116 = [
    # Kazakhstan - more entries
    (16819, "Al-Farabi Kazakh National University", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://kaznu.edu.kz", "Science and Education", 1934, "Prof. Dr. Zhanseit", None),
    (16820, "Kazakh National Technical University", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://kazntu.edu.kz", "Technical Excellence", 1931, "Prof. Dr. Alim", None),
    (16821, "Kazakhstan Institute of Management", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://kimep.kz", "Business Excellence", 1996, "Prof. Dr. Baur", None),
    
    # Uzbekistan - more entries
    (16822, "Tashkent State University of Economics", "Uzbekistan", "Asia", "Tashkent", "University", "https://example.com/badge.png", "https://tsue.uz", "Economics for Nation", 1930, "Prof. Dr. Botir", None),
    (16823, "Tashkent State Technical University", "Uzbekistan", "Asia", "Tashkent", "University", "https://example.com/badge.png", "https://tstu.uz", "Technical Progress", 1954, "Prof. Dr. Said", None),
    (16824, "National University of Uzbekistan", "Uzbekistan", "Asia", "Tashkent", "University", "https://example.com/badge.png", "https://nuu.uz", "Science and Knowledge", 1918, "Prof. Dr. Abdul", None),
    
    # Turkmenistan - more entries
    (16825, "Turkmen State University", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://tsu.edu.tm", "Science and Innovation", 1991, "Prof. Dr. Saparmurat", None),
    (16826, "Turkmen Agricultural University", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://tau.edu.tm", "Agriculture Excellence", 1990, "Prof. Dr. Annamurad", None),
    
    # Kyrgyzstan - more entries
    (16827, "Kyrgyz National University", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://university.kg", "Science and Nation", 1925, "Prof. Dr. Sydykov", None),
    (16828, "American University of Central Asia", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://auca.kg", "American Education Central Asia", 1997, "Prof. Dr. Daniel", None),
    (16829, "Kyrgyz State Technical University", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://kstu.kg", "Technical Excellence", 1950, "Prof. Dr. Tilek", None),
    
    # Tajikistan - more entries
    (16830, "Tajik National University", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://tnu.tj", "Science and Progress", 1948, "Prof. Dr. Khushvakht", None),
    (16831, "Tajik Technical University", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://ttu.tj", "Technical Education", 1956, "Prof. Dr. Davlat", None),
    (16832, "University of Central Asia", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://ucentralasia.org", "Central Asian Excellence", 2000, "Prof. Dr. Shamsh", None),
    
    # Mongolia - more entries
    (16833, "Mongolian University of Science and Technology", "Mongolia", "Asia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://must.edu.mn", "Science and Technology", 1979, "Prof. Dr. Batbaatar", None),
    (16834, "Mongolian State University", "Mongolia", "Asia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://msu.edu.mn", "Excellence in Education", 1942, "Prof. Dr. Galsan", None),
    (16835, "National University of Mongolia", "Mongolia", "Asia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://num.edu.mn", "Science and Nation", 1942, "Prof. Dr. Sonom", None),
    
    # Pakistan - more entries
    (16836, "University of Punjab", "Pakistan", "Asia", "Lahore", "University", "https://example.com/badge.png", "https://pu.edu.pk", "Knowledge and Wisdom", 1882, "Prof. Dr. Niaz", None),
    (16837, "University of Karachi", "Pakistan", "Asia", "Karachi", "University", "https://example.com/badge.png", "https://uok.edu.pk", "Education and Research", 1951, "Prof. Dr. Pirzada", None),
    (16838, "Lahore University of Management Sciences", "Pakistan", "Asia", "Lahore", "University", "https://example.com/badge.png", "https://lums.edu.pk", "Management Excellence", 1987, "Prof. Dr. Ahmad", None),
    (16839, "National University of Sciences and Technology", "Pakistan", "Asia", "Islamabad", "University", "https://example.com/badge.png", "https://nstu.edu.pk", "Science and Technology", 1991, "Prof. Dr. Javed", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_116:
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
    print(f"Batch 116 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
