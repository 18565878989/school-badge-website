#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 114
Add 21 more Asian universities - Caucasus & Final batch
Starting ID: 16383
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 114: Caucasus & Additional Underrepresented (21 schools)
# Countries: Georgia, Armenia, Azerbaijan, Cyprus, Bahrain
SCHOOLS_BATCH_114 = [
    # Georgia - more entries
    (16383, "Tbilisi State University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://www.tsu.edu.ge", "Science and Truth", 1918, "Prof. Dr. George", None),
    (16384, "Ivane Javakhishvili Tbilisi State University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://www.tsu.ge", "Academic Excellence", 2018, "Prof. Dr. Lasha", None),
    (16385, "Ilia State University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://www.iliauni.edu.ge", "Innovation and Science", 2006, "Prof. Dr. Ketevan", None),
    (16386, "Georgian Technical University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://www.gtu.edu.ge", "Technical Progress", 1932, "Prof. Dr. David", None),
    (16387, "Caucasus University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://www.cu.edu.ge", "Excellence in Caucasus", 2000, "Prof. Dr. Nikoloz", None),
    
    # Armenia - more entries
    (16388, "Yerevan State University", "Armenia", "Asia", "Yerevan", "University", "https://example.com/badge.png", "https://www.ysu.am", "Science, Education, Culture", 1919, "Prof. Dr. Hovhannes", None),
    (16389, "National Polytechnic University of Armenia", "Armenia", "Asia", "Yerevan", "University", "https://example.com/badge.png", "https://www.polytechnic.am", "Technical Excellence", 1933, "Prof. Dr. Gagik", None),
    (16390, "American University of Armenia", "Armenia", "Asia", "Yerevan", "University", "https://example.com/badge.png", "https://www.aua.am", "American Education Armenia", 1991, "Dr. Karin", None),
    (16391, "Armenian State University of Economics", "Armenia", "Asia", "Yerevan", "University", "https://example.com/badge.png", "https://www.asue.am", "Economics for Nation", 1922, "Prof. Dr. Ashot", None),
    
    # Azerbaijan - more entries
    (16392, "Baku State University", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://www.bsu.edu.az", "Science and Progress", 1919, "Prof. Dr. Elchin", None),
    (16393, "Azerbaijan State Oil and Industry University", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://www.asoiu.edu.az", "Oil and Industry", 1920, "Prof. Dr. Valeh", None),
    (16394, "Azerbaijan Technical University", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://www.aztu.edu.az", "Technical Excellence", 1936, "Prof. Dr. Vafa", None),
    (16395, "UNEC Azerbaijan State University of Economics", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://www.unec.edu.az", "Economic Science", 1930, "Prof. Dr. Zaur", None),
    
    # Cyprus - more entries
    (16396, "University of Cyprus", "Cyprus", "Asia", "Nicosia", "University", "https://example.com/badge.png", "https://www.ucy.ac.cy", "Science and Innovation", 1989, "Prof. Dr. Tasos", None),
    (16397, "Cyprus International University", "Cyprus", "Asia", "Nicosia", "University", "https://example.com/badge.png", "https://www.ciu.edu.tr", "International Education", 1997, "Prof. Dr. Kagan", None),
    (16398, "Eastern Mediterranean University", "Cyprus", "Asia", "Famagusta", "University", "https://example.com/badge.png", "https://www.emu.edu.tr", "Mediterranean Excellence", 1979, "Prof. Dr. Ahmad", None),
    (16399, "Near East University", "Cyprus", "Asia", "Nicosia", "University", "https://example.com/badge.png", "https://www.neu.edu.tr", "Near East Excellence", 1988, "Prof. Dr. Kadir", None),
    
    # Bahrain - more entries
    (16400, "University of Bahrain", "Bahrain", "Asia", "Sakhir", "University", "https://example.com/badge.png", "https://www.uob.edu.bh", "Excellence and Heritage", 1986, "Prof. Dr. Khalifa", None),
    (16401, "Bahrain University", "Bahrain", "Asia", "Manama", "University", "https://example.com/badge.png", "https://www.bahrain-u.edu.bh", "Higher Education Bahrain", 2002, "Prof. Dr. Jamil", None),
    (16402, "Arabian Gulf University", "Bahrain", "Asia", "Manama", "University", "https://example.com/badge.png", "https://www.agu.edu.bh", "Gulf Cooperation", 1980, "Prof. Dr. Abdullah", None),
    (16403, "College of Health Sciences", "Bahrain", "Asia", "Manama", "University", "https://example.com/badge.png", "https://www.chs.edu.bh", "Health for Gulf", 1976, "Prof. Dr. Samira", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_114:
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
    print(f"Batch 114 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
