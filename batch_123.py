#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools - Batch 123 (Next Batch)
Add 21 more Asian universities continuing the sequence
Starting ID: 20111
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 123: Additional Asian Universities (21 schools)
# Focusing on underrepresented countries and regions
SCHOOLS_BATCH_123 = [
    # Turkmenistan - underrepresented
    (20111, "Turkmen State University", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://tsu.edu.tm", "Science and Knowledge", 1991, "Prof. Dr. Gurbanguly", None),
    (20112, "International Turkmen University of Technology", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://intut.edu.tm", "Technology Innovation", 2013, "Prof. Dr. Annageldi", None),
    (20113, "Turkmen Agricultural University", "Turkmenistan", "Asia", "Ashgabat", "University", "https://example.com/badge.png", "https://tau.edu.tm", "Agricultural Excellence", 1990, "Prof. Dr. Saparmurat", None),
    
    # Armenia - underrepresented
    (20114, "Yerevan State University", "Armenia", "Asia", "Yerevan", "University", "https://example.com/badge.png", "https://ysu.am", "Truth and Freedom", 1919, "Prof. Dr. Hovhannes", None),
    (20115, "Armenian National Academy of Sciences", "Armenia", "Asia", "Yerevan", "Academy", "https://example.com/badge.png", "https://anas.am", "Science for Progress", 1943, "Prof. Dr. Radik", None),
    (20116, "Yerevan State Medical University", "Armenia", "Asia", "Yerevan", "University", "https://example.com/badge.png", "https://ysmu.am", "Medicine and Humanity", 1920, "Prof. Dr. Aram", None),
    
    # Azerbaijan - underrepresented
    (20117, "Baku State University", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://bsu.edu.az", "Science and Progress", 1919, "20118", None),
    (20118, "Azerbaijan State Oil and Industry University", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://asoiu.edu.az", "Oil and Industry Excellence", 1920, "Prof. Dr. Vagif", None),
    (20119, "Azerbaijan Technical University", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://aztu.edu.az", "Technical Innovation", 1950, "Prof. Dr. Elshad", None),
    
    # Georgia - underrepresented
    (20120, "Tbilisi State University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://tsu.edu.ge", "Truth and Wisdom", 1918, "Prof. Dr. George", None),
    (20121, "Ilia State University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://iliauni.edu.ge", "Innovation and Excellence", 2006, "Prof. Dr. Ketevan", None),
    (20122, "Georgian Technical University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://gtu.edu.ge", "Technical Leadership", 1922, "Prof. Dr. David", None),
    
    # Cyprus - underrepresented
    (20123, "University of Cyprus", "Cyprus", "Asia", "Nicosia", "University", "https://example.com/badge.png", "https://ucy.ac.cy", "Education and Research", 1989, "Prof. Dr. Christos", None),
    (20124, "Cyprus University of Technology", "Cyprus", "Asia", "Limassol", "University", "https://example.com/badge.png", "https://cut.ac.cy", "Technology and Innovation", 2004, "Prof. Dr. Panayiotis", None),
    (20125, "European University Cyprus", "Cyprus", "Asia", "Nicosia", "University", "https://example.com/badge.png", "https://euc.ac.cy", "European Excellence", 1961, "Prof. Dr. Andreas", None),
    
    # Afghanistan - underrepresented
    (20126, "Kabul University", "Afghanistan", "Asia", "Kabul", "University", "https://example.com/badge.png", "https://kabul.edu.af", "Education for All", 1932, "Prof. Dr. Mohammad", None),
    (20127, "American University of Afghanistan", "Afghanistan", "Asia", "Kabul", "University", "https://example.com/badge.png", "https://auaf.edu.af", "American Education", 2006, "Prof. Dr. Mark", None),
    (20128, "Herat University", "Afghanistan", "Asia", "Herat", "University", "https://example.com/badge.png", "https://herat.edu.af", "Higher Learning", 1987, "Prof. Dr. Ahmad", None),
    
    # Palestine - underrepresented
    (20129, "Birzeit University", "Palestine", "Asia", "Ramallah", "University", "https://example.com/badge.png", "https://birzeit.edu.ps", "Knowledge and Freedom", 1924, "Prof. Dr. Johnny", None),
    (20130, "An-Najah National University", "Palestine", "Asia", "Nablus", "University", "https://example.com/badge.png", "https://najah.edu", "Excellence and Leadership", 1918, "20131", None),
    (20131, "Hebron University", "Palestine", "Asia", "Hebron", "University", "https://example.com/badge.png", "https://hebron.edu.ps", "Faith and Science", 1980, "Prof. Dr. Taysir", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    schools_skipped = []
    
    for school in SCHOOLS_BATCH_123:
        id_, name, country, region, city, level, badge_url, website, motto, founded, principal, school_code = school
        
        try:
            cursor.execute('''
                INSERT INTO schools (id, name, region, country, city, level, badge_url, website, motto, founded, principal, school_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_, name, region, country, city, level, badge_url, website, motto, founded, principal, school_code))
            
            schools_added.append((id_, name, country))
            print(f"✓ Added ID {id_}: {name} ({country})")
            
        except sqlite3.IntegrityError as e:
            schools_skipped.append((id_, name, country, str(e)))
            print(f"✗ Duplicate or error for ID {id_}: {name} - {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Batch 123 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  Total skipped: {len(schools_skipped)}")
    if schools_added:
        print(f"  ID range: {schools_added[0][0]} - {schools_added[-1][0]}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
