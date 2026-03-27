#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 113
Add 21 more Asian universities - Central Asia underrepresented
Starting ID: 16362
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 113: Central Asia Underrepresented (21 schools)
# Countries: Kazakhstan, Uzbekistan, Turkmenistan, Kyrgyzstan, Tajikistan
SCHOOLS_BATCH_113 = [
    # Kazakhstan - more entries
    (16362, "Kazakh Academy of Sciences", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://www.ksci.kz", "Science Academy", 1946, "Prof. Dr. Murat", None),
    (16363, "Kazakh State University of International Relations", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://www.ksuir.kz", "International Relations", 2019, "Prof. Dr. Yerbolat", None),
    (16364, "Almaty Management University", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://www.almau.edu.kz", "Management Excellence", 2000, "Prof. Dr. Aida", None),
    (16365, "Kazakhstan Institute of Management", "Kazakhstan", "Asia", "Almaty", "University", "https://example.com/badge.png", "https://www.kimep.kz", "Business Education", 1996, "Prof. Dr. David", None),
    (16366, "Astana International University", "Kazakhstan", "Asia", "Nur-Sultan", "University", "https://example.com/badge.png", "https://www.enu.kz", "International Education", 2018, "Prof. Dr. Zhandos", None),
    (16367, "Nazarbayev University", "Kazakhstan", "Asia", "Nur-Sultan", "University", "https://example.com/badge.png", "https://www.nu.edu.kz", "World-Class Education", 2010, "Prof. Dr. Zhenis", None),
    
    # Uzbekistan - more entries
    (16368, "Inha University in Tashkent", "Uzbekistan", "Asia", "Tashkent", "University", "https://example.com/badge.png", "https://www.inha.uz", "Technical Excellence", 2014, "Prof. Dr. Karim", None),
    (16369, "University of World Economy and Diplomacy", "Uzbekistan", "Asia", "Tashkent", "University", "https://example.com/badge.png", "https://www.uwed.uz", "Diplomacy and Trade", 2011, "Prof. Dr. Azamat", None),
    (16370, "Tashkent State University of Oriental Studies", "Uzbekistan", "Asia", "Tashkent", "University", "https://example.com/badge.png", "https://www.tsuos.uz", "Oriental Studies", 1918, "Prof. Dr. Rustam", None),
    (16371, "Westminster International University in Tashkent", "Uzbekistan", "Asia", "Tashkent", "University", "https://example.com/badge.png", "https://www.wiut.uz", "British Education Central Asia", 2002, "Prof. Dr. Shahlo", None),
    
    # Turkmenistan - more entries
    (16372, "Turkmen State Institute of Foreign Languages", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://www.tsifelm", "Languages for World", 1991, "Prof. Dr", None),
    (16373, "Turkmen State Institute of Transport", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://www.tsit.tm", "Transport Education", 1991, "Prof. Dr", None),
    
    # Kyrgyzstan - more entries
    (16374, "Kyrgyz-Russian Slavic University", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://www.krsu.edu.kg", "Unity of Peoples", 1993, "Prof. Dr. Roza", None),
    (16375, "Jalalabad State University", "Kyrgyzstan", "Asia", "Jalal-Abad", "University", "https://example.com/badge.png", "https://www.jdu.kg", "Education in South", 1993, "Prof. Dr. Bakyt", None),
    (16376, "Osh State University", "Kyrgyzstan", "Asia", "Osh", "University", "https://example.com/badge.png", "https://www.osu.kg", "Southern University", 1992, "Prof. Dr. Zhanyl", None),
    (16377, "Kyrgyz-Uzbek University", "Kyrgyzstan", "Asia", "Osh", "University", "https://example.com/badge.png", "https://www.kuu.kg", "Bilateral Education", 2000, "Prof. Dr. Uktam", None),
    
    # Tajikistan - more entries
    (16378, "Islamic Institute of Tajikistan", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://www.iit.tj", "Islamic Studies", 2009, "Mullah", None),
    (16379, "Tajik State Pedagogical University", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://www.tspu.tj", "Teacher Education", 1931, "Prof. Dr. Nargis", None),
    (16380, "Kulob State University", "Tajikistan", "Asia", "Kulob", "University", "https://example.com/badge.png", "https://www.ksu.tj", "Higher Education South", 2008, "Prof. Dr. Daler", None),
    (16381, "Bokhtar State University", "Tajikistan", "Asia", "Bokhtar", "University", "https://example.com/badge.png", "https://www.bokhtar.edu.tj", "Education in Khatlon", 2010, "Prof. Dr. Davlat", None),
    (16382, "Avicenna Tajik State Medical University", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://www.avicenna.tj", "Medical Excellence", 2019, "Prof. Dr. Gulzoda", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_113:
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
    print(f"Batch 113 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
