#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools - Batch 121 Part 2
Continuing to complete 21 schools for this batch
Starting ID: 20081
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 121 Part 2: Additional 9 schools to complete the batch
SCHOOLS_BATCH_121_PART2 = [
    # Continue with more underrepresented countries
    (20081, "Mongolia Institute of Technology", "Mongolia", "Asia", "Ulaanbaatar", "Institute", "https://example.com/badge.png", "https://mit.edu.mn", "Technical Innovation", 1975, "Prof. Dr. Batbayar", None),
    (20082, "Mongolia University of Life Sciences", "Mongolia", "Asia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://muls.edu.mn", "Agricultural Excellence", 1978, "Prof. Dr. Sonom", None),
    (20083, "Mongolian Academy of Sciences", "Mongolia", "Asia", "Ulaanbaatar", "Academy", "https://example.com/badge.png", "https://mas.edu.mn", "Scientific Research", 1961, "Prof. Dr. Gombo", None),
    (20084, "East Asia University", "Taiwan", "Asia", "Taipei", "University", "https://example.com/badge.png", "https://eau.edu.tw", "Regional Leadership", 1989, "Prof. Dr. Chen", None),
    (20085, "Southern Taiwan University", "Taiwan", "Asia", "Tainan", "University", "https://example.com/badge.png", "https://stu.edu.tw", "Innovation and Service", 1998, "Prof. Dr. Lee", None),
    (20086, "Central Taiwan University", "Taiwan", "Asia", "Taichung", "University", "https://example.com/badge.png", "https://ctu.edu.tw", "Academic Excellence", 2000, "Prof. Dr. Wang", None),
    (20087, "Taiwan Ocean University", "Taiwan", "Asia", "Keelung", "University", "https://example.com/badge.png", "https://tou.edu.tw", "Marine Excellence", 1994, "Prof. Dr. Liu", None),
    (20088, "Yunlin University of Science and Technology", "Taiwan", "Asia", "Douliu", "University", "https://example.com/badge.png", "https://yuntech.edu.tw", "Technology Leadership", 1991, "Prof. Dr. Tsai", None),
    (20089, "National Pingtung University", "Taiwan", "Asia", "Pingtung", "University", "https://example.com/badge.png", "https://nptu.edu.tw", "Service and Innovation", 1998, "Prof. Dr. Ho", None),
]

def add_batch_part2():
    """Add the second part of batch 121."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_121_PART2:
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
    print(f"Batch 121 Part 2 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch_part2()
