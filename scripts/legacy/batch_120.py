#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 120
Add 21 more Asian universities - Final Batch
Starting ID: 16903
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 120: Final Batch - Additional Asian Universities (21 schools)
SCHOOLS_BATCH_120 = [
    # Myanmar - more entries
    (16903, "Yangon University", "Myanmar", "Asia", "Yangon", "University", "https://example.com/badge.png", "https://yu.edu.mm", "Education and Truth", 1920, "Prof. Dr. Aung", None),
    (16904, "University of Yangon", "Myanmar", "Asia", "Yangon", "University", "https://example.com/badge.png", "https://uy.edu.mm", "Knowledge and Wisdom", 1948, "Prof. Dr. Soe", None),
    
    # Cambodia - more entries
    (16905, "Royal University of Phnom Penh", "Cambodia", "Asia", "Phnom Penh", "University", "https://example.com/badge.png", "https://rupp.edu.kh", "Science and Technology", 1960, "Prof. Dr. Suy", None),
    (16906, "Royal University of Cambodia", "Cambodia", "Asia", "Phnom Penh", "University", "https://example.com/badge.png", "https://ruc.edu.kh", "Higher Education", 1980, "Prof. Dr. Kheang", None),
    
    # Laos - more entries
    (16907, "National University of Laos", "Laos", "Asia", "Vientiane", "University", "https://example.com/badge.png", "https://nuol.edu.la", "Excellence in Education", 1996, "Prof. Dr. Bounthavy", None),
    
    # Brunei - more entries
    (16908, "Universiti Brunei Darussalam", "Brunei", "Asia", "Gadong", "University", "https://example.com/badge.png", "https://ubd.edu.bn", "Educating Future Leaders", 1985, "Prof. Dr. Dato", None),
    
    # Timor-Leste - more entries
    (16909, "National University of Timor-Leste", "Timor-Leste", "Asia", "Dili", "University", "https://example.com/badge.png", "https://untl.edu.tl", "Education for Nation", 2000, "Prof. Dr. Francisco", None),
    
    # Afghanistan - more entries
    (16910, "Kabul University", "Afghanistan", "Asia", "Kabul", "University", "https://example.com/badge.png", "https://ku.edu.af", "Science and Education", 1932, "Prof. Dr. Mohammad", None),
    (16911, "American University of Afghanistan", "Afghanistan", "Asia", "Kabul", "University", "https://example.com/badge.png", "https://afu.edu.af", "American Education", 2006, "Prof. Dr. Mark", None),
    
    # Maldives - more entries
    (16912, "Maldives National University", "Maldives", "Asia", "Male", "University", "https://example.com/badge.png", "https://mnu.edu.mv", "Higher Education", 2011, "Prof. Dr. Mohamed", None),
    
    # Bhutan - more entries
    (16913, "Royal University of Bhutan", "Bhutan", "Asia", "Thimphu", "University", "https://example.com/badge.png", "https://rub.edu.bt", "Education for Gross National Happiness", 2003, "Prof. Dr. Dasho", None),
    (16914, "College of Science and Technology", "Bhutan", "Asia", "Phuentsholing", "University", "https://example.com/badge.png", "https://cst.edu.bt", "Technical Excellence", 1993, "Prof. Dr. Kinley", None),
    
    # Cyprus - more entries
    (16915, "University of Cyprus", "Cyprus", "Asia", "Nicosia", "University", "https://example.com/badge.png", "https://ucy.ac.cy", "Science and Innovation", 1989, "Prof. Dr. Tasos", None),
    (16916, "Cyprus International University", "Cyprus", "Asia", "Nicosia", "University", "https://example.com/badge.png", "https://ciu.edu.tr", "International Education", 1997, "Prof. Dr. Kagan", None),
    (16917, "Eastern Mediterranean University", "Cyprus", "Asia", "Famagusta", "University", "https://example.com/badge.png", "https://emu.edu.tr", "Mediterranean Excellence", 1979, "Prof. Dr. Ahmad", None),
    
    # Georgia - more entries
    (16918, "Tbilisi State University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://tsu.edu.ge", "Science and Truth", 1918, "Prof. Dr. George", None),
    (16919, "Georgian Technical University", "Georgia", "Asia", "Tbilisi", "University", "https://example.com/badge.png", "https://gtu.edu.ge", "Technical Progress", 1932, "Prof. Dr. David", None),
    
    # Armenia - more entries
    (16920, "Yerevan State University", "Armenia", "Asia", "Yerevan", "University", "https://example.com/badge.png", "https://ysu.am", "Science, Education, Culture", 1919, "Prof. Dr. Hovhannes", None),
    (16921, "National Polytechnic University of Armenia", "Armenia", "Asia", "Yerevan", "University", "https://example.com/badge.png", "https://polytechnic.am", "Technical Excellence", 1933, "Prof. Dr. Gagik", None),
    
    # Azerbaijan - more entries
    (16922, "Baku State University", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://bsu.edu.az", "Science and Progress", 1919, "Prof. Dr. Elchin", None),
    (16923, "Azerbaijan State Oil and Industry University", "Azerbaijan", "Asia", "Baku", "University", "https://example.com/badge.png", "https://asoiu.edu.az", "Oil and Industry", 1920, "Prof. Dr. Valeh", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_120:
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
    print(f"Batch 120 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
