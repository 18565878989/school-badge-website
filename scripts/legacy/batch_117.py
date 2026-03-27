#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 117
Add 21 more Asian universities - South Asia & Middle East
Starting ID: 16840
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 117: South Asia & Middle East Additional (21 schools)
SCHOOLS_BATCH_117 = [
    # Bangladesh - more entries
    (16840, "University of Dhaka", "Bangladesh", "Asia", "Dhaka", "University", "https://example.com/badge.png", "https://du.ac.bd", "Knowledge is Power", 1921, "Prof. Dr. Md.", None),
    (16841, "Bangladesh University of Engineering and Technology", "Bangladesh", "Asia", "Dhaka", "University", "https://example.com/badge.png", "https://buet.ac.bd", "Engineering Excellence", 1961, "Prof. Dr. Kazi", None),
    (16842, "Jahangirnagar University", "Bangladesh", "Asia", "Dhaka", "University", "https://example.com/badge.png", "https://juniv.edu", "Nature and Knowledge", 1970, "Prof. Dr. Farid", None),
    (16843, "Rajshahi University", "Bangladesh", "Asia", "Rajshahi", "University", "https://example.com/badge.png", "https://ru.ac.bd", "Light of Knowledge", 1951, "Prof. Dr. Sultana", None),
    (16844, "Bangladesh Agricultural University", "Bangladesh", "Asia", "Mymensingh", "University", "https://example.com/badge.png", "https://bau.edu.bd", "Agriculture for Nation", 1961, "Prof. Dr. Ali", None),
    
    # Nepal - more entries
    (16845, "Tribhuvan University", "Nepal", "Asia", "Kirtipur", "University", "https://example.com/badge.png", "https://tu.edu.np", "Science and Technology", 1959, "Prof. Dr. Bhadra", None),
    (16846, "Kathmandu University", "Nepal", "Asia", "Dhulikhel", "University", "https://example.com/badge.png", "https://ku.edu.np", "Excellence in Education", 1991, "Prof. Dr. Suresh", None),
    (16847, "Pokhara University", "Nepal", "Asia", "Pokhara", "University", "https://example.com/badge.png", "https://pu.edu.np", "Higher Education", 1996, "Prof. Dr. Gopal", None),
    
    # Sri Lanka - more entries
    (16848, "University of Colombo", "Sri Lanka", "Asia", "Colombo", "University", "https://example.com/badge.png", "https://cmb.ac.lk", "Scholarship and Service", 1942, "Prof. Dr. Chandrika", None),
    (16849, "University of Peradeniya", "Sri Lanka", "Asia", "Peradeniya", "University", "https://example.com/badge.png", "https://pdn.ac.lk", "Knowledge and Wisdom", 1952, "Prof. Dr. Upul", None),
    (16850, "University of Moratuwa", "Sri Lanka", "Asia", "Moratuwa", "University", "https://example.com/badge.png", "https://uom.lk", "Technology Excellence", 1972, "Prof. Dr. Nandika", None),
    (16851, "University of Kelaniya", "Sri Lanka", "Asia", "Kelaniya", "University", "https://example.com/badge.png", "https://kln.ac.ld", "Education and Culture", 1959, "Prof. Dr. Sunanda", None),
    
    # Iran - more entries
    (16852, "University of Tehran", "Iran", "Asia", "Tehran", "University", "https://example.com/badge.png", "https://ut.ac.ir", "Science and Wisdom", 1934, "Prof. Dr. Mohammad", None),
    (16853, "Sharif University of Technology", "Iran", "Asia", "Tehran", "University", "https://example.com/badge.png", "https://sharif.edu", "Technology and Science", 1966, "Prof. Dr. Ahmad", None),
    (16854, "Amirkabir University of Technology", "Iran", "Asia", "Tehran", "University", "https://example.com/badge.png", "https://aut.ac.ir", "Technical Excellence", 1958, "Prof. Dr. Reza", None),
    (16855, "Isfahan University of Technology", "Iran", "Asia", "Isfahan", "University", "https://example.com/badge.png", "https://iut.ac.ir", "Innovation in Technology", 1978, "Prof. Dr. Hossein", None),
    (16853, "Sharif University of Technology", "Iran", "Asia", "Tehran", "University", "https://example.com/badge.png", "https://sharif.edu", "Technology and Science", 1966, "Prof. Dr. Ahmad", None),
    (16854, "Amirkabir University of Technology", "Iran", "Asia", "Tehran", "University", "https://example.com/badge.png", "https://aut.ac.ir", "Technical Excellence", 1958, "Prof. Dr. Reza", None),
    (16855, "Isfahan University of Technology", "Iran", "Asia", "Isfahan", "University", "https://example.com/badge.png", "https://iut.ac.ir", "Innovation in Technology", 1978, "Prof. Dr. Hossein", None),
    
    # Iraq - more entries
    (16856, "University of Baghdad", "Iraq", "Asia", "Baghdad", "University", "https://example.com/badge.png", "https://uobaghdad.edu.iq", "Knowledge and Science", 1957, "Prof. Dr. Kadhim", None),
    (16857, "University of Technology, Baghdad", "Iraq", "Asia", "Baghdad", "University", "https://example.com/badge.png", "https://uotechnology.edu.iq", "Technical Excellence", 1975, "Prof. Dr. Ali", None),
    
    # Turkey - more entries
    (16858, "Istanbul University", "Turkey", "Asia", "Istanbul", "University", "https://example.com/badge.png", "https://istanbul.edu.tr", "Science and Art", 1933, "Prof. Dr. Mahmut", None),
    (16859, "Ankara University", "Turkey", "Asia", "Ankara", "University", "https://example.com/badge.png", "https://ankara.edu.tr", "Education and Research", 1946, "Prof. Dr. Necdet", None),
    (16860, "Bilkent University", "Turkey", "Asia", "Ankara", "University", "https://example.com/badge.png", "https://bilkent.edu.tr", "Excellence in Education", 1984, "Prof. Dr. Ihsan", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_117:
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
    print(f"Batch 117 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
