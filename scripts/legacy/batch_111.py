#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 111
Add 21 more Asian universities focusing on West Asia underrepresented
Starting ID: 16320
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 111: West Asia Underrepresented (21 schools)
# Countries: Palestine, Yemen, Syria, Lebanon, Jordan
SCHOOLS_BATCH_111 = [
    # Palestine - underrepresented
    (16320, "Birzeit University", "Palestine", "Asia", "Birzeit", "University", "https://example.com/badge.png", "https://www.birzeit.edu", "Knowledge for Liberation", 1924, "Prof. Dr. Abdullatif", None),
    (16321, "Al-Quds University", "Palestine", "Asia", "Jerusalem", "University", "https://example.com/badge.png", "https://www.alquds.edu", "Jerusalem's University", 1995, "Prof. Dr. Sari", None),
    (16322, "Hebron University", "Palestine", "Asia", "Hebron", "University", "https://example.com/badge.png", "https://www.hebron.edu", "Faith and Science", 1980, "Prof. Dr. Taha", None),
    (16323, "An-Najah National University", "Palestine", "Asia", "Nablus", "University", "https://example.com/badge.png", "https://www.najah.edu", "We Will Not Be Conquered", 1918, "Prof. Dr. Rami", None),
    (16324, "Bethlehem University", "Palestine", "Asia", "Bethlehem", "University", "https://example.com/badge.png", "https://www.bethlehem.edu", "Christian Higher Education", 1973, "Fr. George", None),
    (16325, "Islamic University of Gaza", "Palestine", "Asia", "Gaza", "University", "https://example.com/badge.png", "https://www.iugaza.edu", "Science and Faith", 1978, "Prof. Dr. Ahmed", None),
    
    # Yemen - underrepresented
    (16326, "Sana'a University", "Yemen", "Asia", "Sana'a", "University", "https://example.com/badge.png", "https://www.su.edu.ye", "Science and Unity", 1872, "Prof. Dr. Abdulwahab", None),
    (16327, "University of Aden", "Yemen", "Asia", "Aden", "University", "https://example.com/badge.png", "https://www.univ-aden.edu", "Knowledge and Development", 1975, "Prof. Dr. Salem", None),
    (16328, "Yemenia University", "Yemen", "Asia", "Sana'a", "University", "https://example.com/badge.png", "https://www.yemenia.edu.ye", "Excellence in Education", 1990, "Prof. Dr. Ali", None),
    (16329, "Ibb University", "Yemen", "Asia", "Ibb", "University", "https://example.com/badge.png", "https://www.ibbun.edu.ye", "Education for Yemen", 1999, "Prof. Dr. Nasser", None),
    
    # Syria - underrepresented
    (16330, "University of Damascus", "Syria", "Asia", "Damascus", "University", "https://example.com/badge.png", "https://www.damascusuniversity.edu.sy", "Science and Future", 1923, "Prof. Dr. Bassam", None),
    (16331, "Aleppo University", "Syria", "Asia", "Aleppo", "University", "https://example.com/badge.png", "https://www.alepuniv.edu.sy", "Knowledge and Peace", 1946, "Prof. Dr. Mohammad", None),
    (16332, "Tishreen University", "Syria", "Asia", "Latakia", "University", "https://example.com/badge.png", "https://www.tishreen.edu.sy", "Excellence in Science", 1975, "Prof. Dr. Waddah", None),
    (16333, "Al-Baath University", "Syria", "Asia", "Homs", "University", "https://example.com/badge.png", "https://www.albaath-university.edu.sy", "Baath and Science", 1979, "Prof. Dr. Fahd", None),
    
    # Lebanon - more entries
    (16334, "American University of Beirut", "Lebanon", "Asia", "Beirut", "University", "https://example.com/badge.png", "https://www.aub.edu.lb", "That They May Have Life", 1866, "Dr. Fadlo", None),
    (16335, "Lebanese American University", "Lebanon", "Asia", "Byblos", "University", "https://example.com/badge.png", "https://www.lau.edu.lb", " Excellence and Innovation", 1924, "Dr. Michel", None),
    (16336, "Saint Joseph University", "Lebanon", "Asia", "Beirut", "University", "https://example.com/badge.png", "https://www.usj.edu.lb", "Science and Faith", 1875, "Prof. Dr. Samir", None),
    
    # Jordan - more entries
    (16337, "University of Jordan", "Jordan", "Asia", "Amman", "University", "https://example.com/badge.png", "https://www.ju.edu.jo", "The Pioneer University", 1962, "Prof. Dr. Radwan", None),
    (16338, "Jordan University of Science and Technology", "Jordan", "Asia", "Irbid", "University", "https://example.com/badge.png", "https://www.just.edu.jo", "Science for Prosperity", 1986, "Prof. Dr. Kamal", None),
    (16339, "Hashemite University", "Jordan", "Asia", "Zarqa", "University", "https://example.com/badge.png", "https://www.hu.edu.jo", "Education for Future", 1995, "Prof. Dr. Fayez", None),
    (16340, "Al-Balqa' Applied University", "Jordan", "Asia", "Al-Salt", "University", "https://example.com/badge.png", "https://www.bau.edu.jo", "Applied Knowledge", 1997, "Prof. Dr. Mohammad", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_111:
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
    print(f"Batch 111 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
