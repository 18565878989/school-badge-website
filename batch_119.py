#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 119
Add 21 more Asian universities - Middle East & Central Asia
Starting ID: 16882
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 119: Middle East & Central Asia Additional (21 schools)
SCHOOLS_BATCH_119 = [
    # Israel - more entries
    (16882, "Hebrew University of Jerusalem", "Israel", "Asia", "Jerusalem", "University", "https://example.com/badge.png", "https://huji.ac.il", "The Light of Learning", 1918, "Prof. Dr. Asher", None),
    (16883, "Tel Aviv University", "Israel", "Asia", "Tel Aviv", "University", "https://example.com/badge.png", "https://tau.ac.il", "Knowledge and Innovation", 1956, "Prof. Dr. Yosef", None),
    (16884, "Technion Israel Institute of Technology", "Israel", "Asia", "Haifa", "University", "https://example.com/badge.png", "https://technion.ac.il", "Science for Progress", 1912, "Prof. Dr. Uri", None),
    (16885, "Weizmann Institute of Science", "Israel", "Asia", "Rehovot", "University", "https://example.com/badge.png", "https://weizmann.ac.il", "Science for Humanity", 1934, "Prof. Dr. Daniel", None),
    
    # Jordan - more entries
    (16886, "University of Jordan", "Jordan", "Asia", "Amman", "University", "https://example.com/badge.png", "https://ju.edu.jo", "Science and Innovation", 1962, "Prof. Dr. Adel", None),
    (16887, "Jordan University of Science and Technology", "Jordan", "Asia", "Irbid", "University", "https://example.com/badge.png", "https://just.edu.jo", "Excellence in Science", 1986, "Prof. Dr. Sa'ad", None),
    
    # Lebanon - more entries
    (16888, "American University of Beirut", "Lebanon", "Asia", "Beirut", "University", "https://example.com/badge.png", "https://aub.edu.lb", "That They May Have Life", 1866, "Prof. Dr. Fadlo", None),
    (16889, "Lebanese American University", "Lebanon", "Asia", "Beirut", "University", "https://example.com/badge.png", "https://lau.edu.lb", "Liberty and Excellence", 1924, "Prof. Dr. Michel", None),
    (16890, "Saint Joseph University", "Lebanon", "Asia", "Beirut", "University", "https://example.com/badge.png", "https://usj.edu.lb", "Science and Truth", 1875, "Prof. Dr. Father", None),
    
    # Saudi Arabia - more entries
    (16891, "King Saud University", "Saudi Arabia", "Asia", "Riyadh", "University", "https://example.com/badge.png", "https://ksu.edu.sa", "Science and Knowledge", 1957, "Prof. Dr. Badran", None),
    (16892, "King Abdulaziz University", "Saudi Arabia", "Asia", "Jeddah", "University", "https://example.com/badge.png", "https://kau.edu.sa", "Excellence in Education", 1967, "Prof. Dr. Abdulrahman", None),
    (16893, "King Abdullah University of Science and Technology", "Saudi Arabia", "Asia", "Thuwal", "University", "https://example.com/badge.png", "https://kaust.edu.sa", "Innovation and Discovery", 2009, "Prof. Dr. Tony", None),
    
    # UAE - more entries
    (16894, "United Arab Emirates University", "UAE", "Asia", "Al Ain", "University", "https://example.com/badge.png", "https://uaeu.ac.ae", "Education and Research", 1976, "Prof. Dr. Mohammed", None),
    (16895, "Khalifa University", "UAE", "Asia", "Abu Dhabi", "University", "https://example.com/badge.png", "https://ku.ac.ae", "Knowledge for Humanity", 1989, "Prof. Dr. Arif", None),
    (16896, "American University of Sharjah", "UAE", "Asia", "Sharjah", "University", "https://example.com/badge.png", "https://aus.edu", "Knowledge, Integrity, Progress", 1997, "Prof. Dr. Susan", None),
    
    # Qatar - more entries
    (16897, "Qatar University", "Qatar", "Asia", "Doha", "University", "https://example.com/badge.png", "https://qu.edu.qa", "Education for Progress", 1973, "Prof. Dr. Hassan", None),
    (16898, "Hamad Bin Khalifa University", "Qatar", "Asia", "Doha", "University", "https://example.com/badge.png", "https://hbku.edu.qa", "Innovation in Education", 2010, "Prof. Dr. Ahmad", None),
    
    # Oman - more entries
    (16899, "Sultan Qaboos University", "Oman", "Asia", "Muscat", "University", "https://example.com/badge.png", "https://squ.edu.om", "Education for Nation", 1986, "Prof. Dr. Ali", None),
    
    # Kuwait - more entries
    (16900, "Kuwait University", "Kuwait", "Asia", "Kuwait City", "University", "https://example.com/badge.png", "https://ku.edu.kw", "Science and Knowledge", 1966, "Prof. Dr. Fahad", None),
    
    # Bahrain - more entries
    (16901, "Bahrain University", "Bahrain", "Asia", "Manama", "University", "https://example.com/badge.png", "https://ub.edu.bh", "Higher Education Excellence", 1978, "Prof. Dr. Walid", None),
    (16902, "Ahlia University", "Bahrain", "Asia", "Manama", "University", "https://example.com/badge.png", "https://ahlia.edu.bh", "Education and Development", 2001, "Prof. Dr. Jassim", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_119:
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
    print(f"Batch 119 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
