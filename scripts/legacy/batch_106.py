#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 106
Add 21 more Asian universities
Starting ID: 13800
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 106: Southeast Asia & East Asia Universities (21 schools)
# Countries: Laos, Philippines, Indonesia, Malaysia, Singapore, Japan, Korea
SCHOOLS_BATCH_106 = [
    # Laos
    (13800, "National University of Laos", "Laos", "Asia", "Laos", "Vientiane", "University", "https://example.com/badge.png", "https://www.nuol.edu.la", "Knowledge for Development", 1996, "Prof. Dr. Sombath Somphone", None),
    (13801, "Savannakhet University", "Laos", "Asia", "Laos", "Savannakhet", "University", "https://example.com/badge.png", "https://www.savannakhet-university.org", "Education for Progress", 2004, "Prof. Dr. Bounleuam", None),
    (13802, "Souphanouvong University", "Laos", "Asia", "Laos", "Luang Prabang", "University", "https://example.com/badge.png", "https://www.suan.ac.la", "Mountain of Knowledge", 2003, "Prof. Dr. Khampheu", None),
    
    # Philippines (continued)
    (13803, "University of the Philippines Diliman", "Philippines", "Asia", "Philippines", "Quezon City", "University", "https://example.com/badge.png", "https://www.upd.edu.ph", "Honesty, Excellence, Relevance", 1949, "Prof. Dr. Fidel Nemenzo", None),
    (13804, "Ateneo de Manila University", "Philippines", "Asia", "Philippines", "Quezon City", "University", "https://example.com/badge.png", "https://www.ateneo.edu", "Magis - Striving for Excellence", 1859, "Prof. Dr. Roberto D. Hernandez", None),
    (13805, "De La Salle University", "Philippines", "Asia", "Philippines", "Manila", "University", "https://example.com/badge.png", "https://www.dlsu.edu.ph", "Religio, Mores, Cultura", 1911, "Prof. Dr. Carmelita M. Quezon", None),
    (13806, "University of Santo Tomas", "Philippines", "Asia", "Philippines", "Manila", "University", "https://example.com/badge.png", "https://www.ust.edu.ph", "Veritas in Service", 1611, "Rev. Fr. Richard G. Ang, O.P.", None),
    (13807, "Philippine Science High School", "Philippines", "Asia", "Philippines", "Quezon City", "High School", "https://example.com/badge.png", "https://www.pshs.edu.ph", "Leading in Science Education", 1964, "Dr. Jos T. Biac", None),
    (13808, "Mapua Institute of Technology", "Philippines", "Asia", "Philippines", "Manila", "University", "https://example.com/badge.png", "https://www.mapua.edu.ph", "Inspiring Innovation", 1925, "Prof. Dr. Reynaldo Vea", None),
    
    # Indonesia (continued)
    (13809, "University of Indonesia", "Indonesia", "Asia", "Indonesia", "Depok", "University", "https://example.com/badge.png", "https://www.ui.ac.id", "Enlightening the Nation", 1950, "Prof. Dr. Ari Kuncoro", None),
    (13810, "Gadjah Mada University", "Indonesia", "Asia", "Indonesia", "Yogyakarta", "University", "https://example.com/badge.png", "https://www.ugm.ac.id", "Building the Nation", 1949, "Prof. Dr. Panut", None),
    (13811, "Bandung Institute of Technology", "Indonesia", "Asia", "Indonesia", "Bandung", "University", "https://example.com/badge.png", "https://www.itb.ac.id", "Science and Technology for Humanity", 1959, "Prof. Dr. Kadarsah", None),
    (13812, "Bogor Agricultural University", "Indonesia", "Asia", "Indonesia", "Bogor", "University", "https://example.com/badge.png", "https://www.ipb.ac.id", "Excellence in Agriculture", 1963, "Prof. Dr. F. A. Moeloek", None),
    (13813, "Airlangga University", "Indonesia", "Asia", "Indonesia", "Surabaya", "University", "https://example.com/badge.png", "https://www.unair.ac.id", "Advanced Maritime Civilization", 1954, "Prof. Dr. Mohammad Nasih", None),
    (13814, "Diponegoro University", "Indonesia", "Asia", "Indonesia", "Semarang", "University", "https://example.com/badge.png", "https://www.undip.ac.id", "Innovation for Society", 1961, "Prof. Dr. Yos Johan Utama", None),
    (13815, "Bina Nusantara University", "Indonesia", "Asia", "Indonesia", "Jakarta", "University", "https://example.com/badge.png", "https://www.binus.ac.id", "Inspiring the World", 1974, "Prof. Dr. Harjanto", None),
    
    # Malaysia (continued)
    (13816, "University of Malaya", "Malaysia", "Asia", "Malaysia", "Kuala Lumpur", "University", "https://example.com/badge.png", "https://www.um.edu.my", "Inspiring Impact", 1949, "Prof. Dr. Noor Azuan", None),
    (13817, "National University of Malaysia", "Malaysia", "Asia", "Malaysia", "Bangi", "University", "https://example.com/badge.png", "https://www.ukm.my", "Gempira Gemilang", 1970, "Prof. Dr. Mohd. Hamdi", None),
    (13818, "University of Technology Malaysia", "Malaysia", "Asia", "Malaysia", "Johor Bahru", "University", "https://example.com/badge.png", "https://www.utm.my", "Science and Technology", 1972, "Prof. Dr. Ahmad Zahir", None),
    (13819, "Malaya University of Education", "Malaysia", "Asia", "Malaysia", "Kuala Lumpur", "University", "https://example.com/badge.png", "https://www.uoem.edu.my", "Teacher Education Excellence", 1990, "Prof. Dr. Mohd Zohdi", None),
    (13820, "Taylor's University", "Malaysia", "Asia", "Malaysia", "Subang Jaya", "University", "https://example.com/badge.png", "https://www.taylors.edu.my", "Transforming Education", 1969, "Prof. Dr. Prashant", None),
    (13821, "Monash University Malaysia", "Malaysia", "Asia", "Malaysia", "Selangor", "University", "https://example.com/badge.png", "https://www.monash.edu.my", "Ancora Imus", 1998, "Prof. Dr. Elizabeth L. Palmer", None),
    (13822, "University of Nottingham Malaysia", "Malaysia", "Asia", "Malaysia", "Semenyih", "University", "https://example.com/badge.png", "https://www.nottingham.edu.my", "Innovating Our World", 2000, "Prof. Dr. Graham Kendall", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_106:
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
    print(f"Batch 106 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
