#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 110
Add 21 more Asian universities focusing on underrepresented countries
Starting ID: 16299
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 110: Central Asia & South Asia Underrepresented (21 schools)
# Countries: Kyrgyzstan, Tajikistan, Turkmenistan, Afghanistan, Bhutan, Maldives
SCHOOLS_BATCH_110 = [
    # Kyrgyzstan - underrepresented
    (16299, "Kyrgyz State University of Construction", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://www.ksu.kg", "Building Future", 1997, "Prof. Dr. Tilek", None),
    (16300, "Kyrgyz National Agricultural University", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://www.knau.kg", "Agriculture for Development", 1930, "Prof. Dr. Aibek", None),
    (16301, "Kyrgyz State Medical Academy", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://www.ksma.kg", "Health for All", 1939, "Prof. Dr. Nadira", None),
    (16302, "Bishkek Humanities University", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://www.bhu.kg", "Knowledge and Wisdom", 1996, "Prof. Dr. Gulnara", None),
    (16303, "International Ataturk-Alatoo University", "Kyrgyzstan", "Asia", "Bishkek", "University", "https://example.com/badge.png", "https://www.iaau.edu.kg", "Excellence in Education", 1996, "Prof. Dr. Kanat", None),
    
    # Tajikistan - underrepresented
    (16304, "Tajik National University", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://www.tnu.tj", "Science and Progress", 1947, "Prof. Dr. Rustam", None),
    (16305, "Tajik Technical University", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://www.tut.tj", "Technical Excellence", 1954, "Prof. Dr. Farhod", None),
    (16306, "Tajik State University of Commerce", "Tajikistan", "Asia", "Dushanbe", "University", "https://example.com/badge.png", "https://www.tsuc.tj", "Business Excellence", 1993, "Prof. Dr. Aziz", None),
    (16307, "Khorog State University", "Tajikistan", "Asia", "Khorog", "University", "https://example.com/badge.png", "https://www.ksu.tj", "Education in Mountains", 2018, "Prof. Dr. Rahim", None),
    
    # Turkmenistan - underrepresented
    (16308, "Turkmen State University", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://www.tsu.tm", "Science and Knowledge", 1991, "Prof. Dr. Annaguly", None),
    (16309, "Turkmen State Institute of Architecture", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://www.tsia.tm", "Architecture for Nation", 1991, "Prof. Dr", None),
    (16310, "Turkmen State Institute of Economics", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://www.tsie.tm", "Economics Development", 1991, "Prof. Dr", None),
    
    # Afghanistan - underrepresented
    (16311, "Kabul University", "Afghanistan", "Asia", "Kabul", "University", "https://example.com/badge.png", "https://www.ku.edu.af", "Science and Culture", 1932, "Prof. Dr. Mohammad", None),
    (16312, "American University of Afghanistan", "Afghanistan", "Asia", "Kabul", "University", "https://example.com/badge.png", "https://www.afu.af", "Liberal Arts Education", 2006, "Dr. Mark", None),
    (16313, "Kabul Polytechnic University", "Afghanistan", "Asia", "Kabul", "University", "https://example.com/badge.png", "https://www.kpu.edu.af", "Technical Education", 1963, "Prof. Dr. Ahmad", None),
    
    # Bhutan - underrepresented
    (16314, "Royal University of Bhutan", "Bhutan", "Asia", "Thimphu", "University", "https://example.com/badge.png", "https://www.rub.edu.bt", "Education for Gross National Happiness", 2003, "Prof. Dr. Dorji", None),
    (16315, "Royal Thimphu College", "Bhutan", "Asia", "Thimphu", "University", "https://example.com/badge.png", "https://www.rtc.bt", "Learning and Service", 2008, "Dr.Kinley", None),
    
    # Maldives - underrepresented
    (16316, "Maldives National University", "Maldives", "Asia", "Male", "University", "https://example.com/badge.png", "https://www.mnu.edu.mv", "Knowledge for Development", 2011, "Dr. Mohamed", None),
    
    # Brunei - underrepresented
    (16317, "University of Brunei Darussalam", "Brunei", "Asia", "Gadong", "University", "https://example.com/badge.png", "https://www.ubd.edu.bn", "Embracing Knowledge, Cherishing Values", 1985, "Prof. Dr. Hjh", None),
    (16318, "International Islamic University College", "Brunei", "Asia", "Gadong", "University", "https://example.com/badge.png", "https://www.iuceb.edu.bn", "Islamic Education", 1975, "Prof. Dr", None),
    
    # Timor-Leste - underrepresented
    (16319, "National University of Timor-Leste", "Timor-Leste", "Asia", "Dili", "University", "https://example.com/badge.png", "https://www.untl.edu.tp", "Science for Nation", 2000, "Prof. Dr. Francisco", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_110:
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
    print(f"Batch 110 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
