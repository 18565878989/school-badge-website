#!/usr/bin/env python3
"""
Batch 160: Add more underrepresented Asian schools - Part 3
Focus: Adding more variety from underrepresented countries
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Schools to add from Asian countries
SCHOOLS = [
    # More Russia
    {"name": "Russian Presidential Academy of National Economy and Public Administration", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "Moscow State University of Civil Engineering", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "Moscow State Technical University of St. Petersburg", "country": "Russia", "city": "St. Petersburg", "region": "Asia", "level": "University"},
    {"name": "Financial University under the Government of Russia", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "Peoples' Friendship University of Russia", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "Irkutsk State University", "country": "Russia", "city": "Irkutsk", "region": "Asia", "level": "University"},
    {"name": "Vladivostok State University", "country": "Russia", "city": "Vladivostok", "region": "Asia", "level": "University"},
    
    # More UAE
    {"name": "Emirates Aviation University", "country": "UAE", "city": "Dubai", "region": "Asia", "level": "University"},
    {"name": "Dubai Medical College", "country": "UAE", "city": "Dubai", "region": "Asia", "level": "University"},
    {"name": "University of Wollongong Dubai", "country": "UAE", "city": "Dubai", "region": "Asia", "level": "University"},
    {"name": "Abu Dhabi University", "country": "UAE", "city": "Abu Dhabi", "region": "Asia", "level": "University"},
    
    # More Kuwait
    {"name": "Arab Open University Kuwait", "country": "Kuwait", "city": "Kuwait City", "region": "Asia", "level": "University"},
    {"name": "Private University of Kuwait", "country": "Kuwait", "city": "Kuwait City", "region": "Asia", "level": "University"},
    
    # More Yemen
    {"name": "Sabeil University", "country": "Yemen", "city": "Sana'a", "region": "Asia", "level": "University"},
    {"name": "Modern University of Science and Technology Yemen", "country": "Yemen", "city": "Sana'a", "region": "Asia", "level": "University"},
    {"name": "Al-Majmaah University", "country": "Yemen", "city": "Al-Majmaah", "region": "Asia", "level": "University"},
    
    # More Bahrain
    {"name": "Arab Institute for Training and Research", "country": "Bahrain", "city": "Manama", "region": "Asia", "level": "University"},
    {"name": "University College of Bahrain", "country": "Bahrain", "city": "Manama", "region": "Asia", "level": "University"},
    
    # More Israel
    {"name": "Israel Institute of Technology", "country": "Israel", "city": "Haifa", "region": "Asia", "level": "University"},
    {"name": "Ariel University", "country": "Israel", "city": "Ariel", "region": "Asia", "level": "University"},
    {"name": "Ono Academic College", "country": "Israel", "city": "Kiryat Ono", "region": "Asia", "level": "University"},
    {"name": "Reichman University", "country": "Israel", "city": "Herzliya", "region": "Asia", "level": "University"},
]

def add_schools():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    added = 0
    skipped = 0
    
    for school in SCHOOLS:
        # Check if school already exists (case insensitive)
        cursor.execute(
            "SELECT id FROM schools WHERE LOWER(name) = LOWER(?) AND country = ?",
            (school["name"], school["country"])
        )
        if cursor.fetchone():
            skipped += 1
            print(f"Skipped (exists): {school['name']}")
            continue
        
        # Insert new school
        cursor.execute("""
            INSERT INTO schools (name, country, city, region, level, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (school["name"], school["country"], school["city"], school["region"], school["level"]))
        added += 1
        print(f"Added: {school['name']}")
    
    conn.commit()
    conn.close()
    
    print(f"\nBatch 160: Added {added} schools, skipped {skipped} duplicates")
    return added

if __name__ == "__main__":
    add_schools()
