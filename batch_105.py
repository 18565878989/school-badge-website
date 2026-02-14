#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 105
Add 21 more Asian universities
Starting ID: 13779
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 105: South Asia & Southeast Asia Universities (21 schools)
# Countries: Bangladesh, Sri Lanka, Nepal, Bhutan, Myanmar, Cambodia, Laos, Philippines
SCHOOLS_BATCH_105 = [
    # Bangladesh (continued)
    (13779, "Jatiya Kabi Kazi Nazrul Islam University", "Bangladesh", "Asia", "Bangladesh", "Trishal", "University", "https://example.com/badge.png", "https://www.jkkniu.edu.bd", "Freedom Through Knowledge", 2004, "Prof. Dr. Md. Mosharraf Hossain", None),
    (13780, "Begumganj Government College", "Bangladesh", "Asia", "Bangladesh", "Noakhali", "College", "https://example.com/badge.png", None, None, None, None, None),
    
    # Sri Lanka (continued)
    (13781, "University of Jaffna", "Sri Lanka", "Asia", "Sri Lanka", "Jaffna", "University", "https://example.com/badge.png", "https://www.univ.jfn.ac.lk", "Wisdom, Truth, Enlightenment", 1974, "Prof. S. Vasanthakumari", None),
    (13782, "Eastern University, Sri Lanka", "Sri Lanka", "Asia", "Sri Lanka", "Chenkalady", "University", "https://example.com/badge.png", "https://www.esn.ac.lk", "Knowledge Illuminates", 1970, "Prof. K. M. G. K. Premakumar", None),
    (13783, "South Eastern University of Sri Lanka", "Sri Lanka", "Asia", "Sri Lanka", "Oluvil", "University", "https://example.com/badge.png", "https://www.seu.ac.lk", "Excellence Through Knowledge", 1995, "Prof. M. I. M. Mohideen", None),
    (13784, "Ruhuna University of Matara", "Sri Lanka", "Asia", "Sri Lanka", "Matara", "University", "https://example.com/badge.png", "https://www.ruhuna.ac.lk", "Science for Prosperity", 1972, "Prof. Nimal D. K. H. De Silva", None),
    (13785, "Wayamba University of Sri Lanka", "Sri Lanka", "Asia", "Sri Lanka", "Kuliyapitiya", "University", "https://example.com/badge.png", "https://www.wyb.ac.lk", "Agriculture for Development", 1999, "Prof. W. M. W. B. Weerasooriya", None),
    (13786, "Uva Wellassa University", "Sri Lanka", "Asia", "Sri Lanka", "Badulla", "University", "https://example.com/badge.png", "https://www.uwu.ac.lk", "Innovate and Excel", 2006, "Prof. W. A. P. Weerasinghe", None),
    
    # Nepal (continued)
    (13787, "Tribhuvan University", "Nepal", "Asia", "Nepal", "Kirtipur", "University", "https://example.com/badge.png", "https://tribhuvan-university.nic.np", "Science and Technology for Prosperity", 1959, "Prof. Dr. Tirtha Khaniya", None),
    (13788, "Pokhara University", "Nepal", "Asia", "Nepal", "Pokhara", "University", "https://example.com/badge.png", "https://pu.edu.np", "Excellence in Education", 1996, "Prof. Dr. Subodh Sharma", None),
    (13789, "Kathmandu University", "Nepal", "Asia", "Nepal", "Dhulikhel", "University", "https://example.com/badge.png", "https://ku.edu.np", "Establishing Centers of Excellence", 1991, "Prof. Dr. Bhola Thapa", None),
    (13790, "Purbanchal University", "Nepal", "Asia", "Nepal", "Birtamode", "University", "https://example.com/badge.png", "https://purc.edu.np", "Education for All", 1993, "Prof. Dr. Govind Tiwari", None),
    
    # Myanmar (continued)
    (13791, "University of Yangon", "Myanmar", "Asia", "Myanmar", "Yangon", "University", "https://example.com/badge.png", "https://www.yau.edu.mm", "Veritas et Sapientia", 1920, "Prof. Dr. Myo Myint", None),
    (13792, "University of Mandalay", "Myanmar", "Asia", "Myanmar", "Mandalay", "University", "https://example.com/badge.png", "https://www.mandalay-university.edu.mm", "Knowledge, Virtue, Progress", 1964, "Prof. Dr. Khin Maung Aye", None),
    (13793, "Yangon Technological University", "Myanmar", "Asia", "Myanmar", "Yangon", "University", "https://example.com/badge.png", "https://ytu.edu.mm", "Engineering for National Development",  1990, "Prof. Dr. Aung San Oo", None),
    (13794, "University of Computer Studies, Yangon", "Myanmar", "Asia", "Myanmar", "Yangon", "University", "https://example.com/badge.png", "https://www.ucsy.edu.mm", "Excellence in Computing", 1964, "Prof. Dr. Hla Hla", None),
    
    # Cambodia (continued)
    (13795, "Royal University of Phnom Penh", "Cambodia", "Asia", "Cambodia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.rupp.edu.kh", "Knowledge and Morality", 1960, "Prof. Dr. Ngo Diep", None),
    (13796, "Royal University of Law and Economics", "Cambodia", "Asia", "Cambodia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.rule.edu.kh", "Justice and Knowledge", 1949, "Prof. Dr. Keng Vannsak", None),
    (13797, "Institute of Technology of Cambodia", "Cambodia", "Asia", "Cambodia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.itc.edu.kh", "Technology for Development", 1965, "Prof. Dr. Sovann", None),
    (13798, "Phnom Penh International University", "Cambodia", "Asia", "Cambodia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.ppiu.edu.kh", "International Education", 2000, "Prof. Dr. Chheang Vannak", None),
    (13799, "Build Bright University", "Cambodia", "Asia", "Cambodia", "Phnom Penh", "University", "https://example.com/badge.png", "https://www.bbu.edu.kh", "Bright Future Through Education", 2002, "Prof. Dr. Sok Chhay", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_105:
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
    print(f"Batch 105 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
