#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 115
Add 21 more Asian universities - Southeast & South Asia
Starting ID: 16404
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 115: Southeast & South Asia Additional (21 schools)
SCHOOLS_BATCH_115 = [
    # Indonesia - more entries
    (16404, "Gadjah Mada University", "Indonesia", "Asia", "Yogyakarta", "University", "https://example.com/badge.png", "https://www.ugm.ac.id", "Veritas, Probitas, Iustitia", 1949, "Prof. Dr. Ova", None),
    (16405, "Bandung Institute of Technology", "Indonesia", "Asia", "Bandung", "University", "https://example.com/badge.png", "https://www.itb.ac.id", "Science and Technology", 1959, "Prof. Dr. Kadim", None),
    (16406, "University of Indonesia", "Indonesia", "Asia", "Depok", "University", "https://example.com/badge.png", "https://www.ui.ac.id", "Integrity, Independence, Enlightenment", 1849, "Prof. Dr. Ari", None),
    (16407, "Airlangga University", "Indonesia", "Asia", "Surabaya", "University", "https://example.com/badge.png", "https://unair.ac.id", "Excellence in Science", 1954, "Prof. Dr. Moh.", None),
    (16408, "Bogor Agricultural University", "Indonesia", "Asia", "Bogor", "University", "https://example.com/badge.png", "https://ipb.ac.id", "Agriculture for Nation", 1963, "Prof. Dr. Arif", None),
    
    # Vietnam - more entries
    (16409, "Vietnam National University, Hanoi", "Vietnam", "Asia", "Hanoi", "University", "https://example.com/badge.png", "https://vnu.edu.vn", "Science and Technology", 1945, "Prof. Dr. Le", None),
    (16410, "Vietnam National University, Ho Chi Minh City", "Vietnam", "Asia", "Ho Chi Minh City", "University", "https://example.com/badge.png", "https://vnuhcm.edu.vn", "Education and Research", 2000, "Prof. Dr. Tran", None),
    (16411, "Hanoi University of Science and Technology", "Vietnam", "Asia", "Hanoi", "University", "https://example.com/badge.png", "https://hust.edu.vn", "Technology for Development", 1956, "Prof. Dr. Pham", None),
    (16412, "University of Natural Science", "Vietnam", "Asia", "Ho Chi Minh City", "University", "https://example.com/badge.png", "https://hcmuns.edu.vn", "Science Excellence", 1976, "Prof. Dr. Nguyen", None),
    
    # Thailand - more entries
    (16413, "Chulalongkorn University", "Thailand", "Asia", "Bangkok", "University", "https://example.com/badge.png", "https://chula.ac.th", "Science of Mind", 1917, "Prof. Dr. Bundit", None),
    (16414, "Mahidol University", "Thailand", "Asia", "Nakhon Pathom", "University", "https://example.com/badge.png", "https://mahidol.ac.th", "Wisdom of the Land", 1888, "Prof. Dr. Pim", None),
    (16415, "Kasetsart University", "Thailand", "Asia", "Bangkok", "University", "https://example.com/badge.png", "https://ku.ac.th", "Agriculture and Science", 1943, "Prof. Dr. Chon", None),
    (16416, "Thammasat University", "Thailand", "Asia", "Bangkok", "University", "https://example.com/badge.png", "https://tu.ac.th", "Democracy and Education", 1934, "Prof. Dr. Sombat", None),
    (16417, "Chiang Mai University", "Thailand", "Asia", "Chiang Mai", "University", "https://example.com/badge.png", "https://cmu.ac.th", "Northern Excellence", 1964, "Prof. Dr. Niwes", None),
    
    # Philippines - more entries
    (16418, "University of the Philippines", "Philippines", "Asia", "Quezon City", "University", "https://example.com/badge.png", "https://up.edu.ph", "Honor and Excellence", 1908, "Prof. Dr. Angelo", None),
    (16419, "Ateneo de Manila University", "Philippines", "Asia", "Quezon City", "University", "https://example.com/badge.png", "https://ateneo.edu", "Magis, Men and Magnanimity", 1859, "Prof. Dr. Roberto", None),
    (16420, "De La Salle University", "Philippines", "Asia", "Manila", "University", "https://example.com/badge.png", "https://dlsu.edu.ph", "Science and Virtue", 1911, "Prof. Dr. Mars", None),
    (16421, "University of Santo Tomas", "Philippines", "Asia", "Manila", "University", "https://example.com/badge.png", "https://ust.edu.ph", "Truth and Virtue", 1611, "Prof. Dr. Richard", None),
    (16422, "Philippine Normal University", "Philippines", "Asia", "Manila", "University", "https://example.com/badge.png", "https://pnu.edu.ph", "Education for All", 1901, "Prof. Dr. Aurora", None),
    
    # Malaysia - more entries
    (16423, "University of Malaya", "Malaysia", "Asia", "Kuala Lumpur", "University", "https://example.com/badge.png", "https://um.edu.my", "Knowledge is Light", 1949, "Prof. Dr. Dato", None),
    (16424, "National University of Malaysia", "Malaysia", "Asia", "Bangi", "University", "https://example.com/badge.png", "https://ukm.my", "Science and Technology", 1970, "Prof. Dr. Mohd", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_115:
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
    print(f"Batch 115 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
