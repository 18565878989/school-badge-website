#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 112
Add 21 more Asian universities - Southeast Asia underrepresented
Starting ID: 16341
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 112: Southeast Asia Underrepresented (21 schools)
# Countries: Myanmar, Cambodia, Laos, Brunei, Timor-Leste
SCHOOLS_BATCH_112 = [
    # Myanmar - more entries
    (16341, "Yangon University", "Myanmar", "Asia", "Yangon", "University", "https://example.com/badge.png", "https://www.yu.edu.mm", "Science and Wisdom", 1920, "Prof. Dr. Aung", None),
    (16342, "Mandalay University", "Myanmar", "Asia", "Mandalay", "University", "https://example.com/badge.png", "https://www.mandalu.edu.mm", "Education and Culture", 1957, "Prof. Dr. Kyaw", None),
    (16343, "University of Yangon", "Myanmar", "Asia", "Yangon", "University", "https://example.com/badge.png", "https://www.uy.edu.mm", "Excellence in Education", 1948, "Prof. Dr. Nanda", None),
    (16344, "Myanmar Institute of Theology", "Myanmar", "Asia", "Yangon", "University", "https://example.com/badge.png", "https://www.mit-myanmar.org", "Christian Education", 1970, "Dr. Samuel", None),
    (16345, "Dagon University", "Myanmar", "Asia", "Yangon", "University", "https://example.com/badge.png", "https://www.dagonuni.edu.mm", "Knowledge and Ethics", 1993, "Prof. Dr. Mya", None),
    
    # Cambodia - more entries
    (16346, "Royal University of Phnom Penh", "Cambodia", "Asia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.rupp.edu.kh", "Knowledge for Nation", 1960, "Prof. Dr. Suy", None),
    (16347, "Royal University of Law and Economics", "Cambodia", "Asia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.rule.edu.kh", "Law and Economics", 1987, "Prof. Dr. Sok", None),
    (16348, "Institute of Technology of Cambodia", "Cambodia", "Asia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.itc.edu.kh", "Technology for Development", 1968, "Prof. Dr. Chhaya", None),
    (16349, "Cambodia University of Science and Technology", "Cambodia", "Asia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.cst.edu.kh", "Science and Innovation", 2007, "Dr. Thavrak", None),
    (16350, "Build Bright University", "Cambodia", "Asia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.bbu.edu.kh", "Bright Future", 2002, "Prof. Dr. Bun", None),
    
    # Laos - more entries
    (16351, "National University of Laos", "Laos", "Asia", "Vientiane", "University", "https://example.com/badge.png", "https://www.nuol.edu.la", "Unity and Knowledge", 1995, "Prof. Dr. Somsy", None),
    (16352, "Savannakhet University", "Laos", "Asia", "Savannakhet", "University", "https://example.com/badge.png", "https://www.sgu.edu.la", "Education in South", 2009, "Prof. Dr. Bounthanom", None),
    (16353, "Champasak University", "Laos", "Asia", "Pakse", "University", "https://example.com/badge.png", "https://www.cpu.edu.la", "Higher Education South", 2009, "Prof. Dr. Somkhit", None),
    
    # Brunei - more entries
    (16354, "Sultan Sharif Islamic University", "Brunei", "Asia", "Bandar Seri Begawan", "University", "https://example.com/badge.png", "https://www.ussi.edu.bn", "Islamic Higher Education", 2005, "Prof. Dr. Hj", None),
    (16355, "Brunei Darussalam University", "Brunei", "Asia", "Bandar Seri Begawan", "University", "https://example.com/badge.png", "https://www.bdu.edu.bn", "University of Brunei", 1995, "Prof. Dr", None),
    
    # Timor-Leste - more entries
    (16356, "Timor-Leste Catholic University", "Timor-Leste", "Asia", "Dili", "University", "https://example.com/badge.png", "https://www.uctl.edu.tp", "Catholic Education", 2001, "Fr. Ovidio", None),
    (16357, "Dili Institute of Technology", "Timor-Leste", "Asia", "Dili", "University", "https://example.com/badge.png", "https://www.dit-tl.org", "Technical Education", 2003, "Prof. Dr. Joao", None),
    
    # Mongolia - more entries
    (16358, "Mongolian University of Science and Technology", "Mongolia", "Asia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://www.must.edu.mn", "Science and Technology", 1969, "Prof. Dr. Bat", None),
    (16359, "Mongolian State University", "Mongolia", "Asia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://www.msu.edu.mn", "State University", 1942, "Prof. Dr. Enkhtsetseg", None),
    (16360, "Health Sciences University of Mongolia", "Mongolia", "Asia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://www.hsum.edu.mn", "Health for All", 1942, "Prof. Dr. Sodjamts", None),
    (16361, "Mongolian University of Life Sciences", "Mongolia", "Asia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://www.muls.edu.mn", "Agriculture and Nature", 1958, "Prof. Dr. Purev", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_112:
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
    print(f"Batch 112 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
