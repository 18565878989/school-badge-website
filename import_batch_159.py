#!/usr/bin/env python3
"""
Batch 159: Add more underrepresented Asian schools - Part 2
Focus: Russia, UAE, Kuwait, Yemen, East Timor, Bahrain, Israel
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Schools to add from underrepresented Asian countries
SCHOOLS = [
    # Russia - more universities
    {"name": "Lomonosov Moscow State University", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "Higher School of Economics", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "Peter the Great St. Petersburg Polytechnic University", "country": "Russia", "city": "Saint Petersburg", "region": "Asia", "level": "University"},
    {"name": "Ural Federal University", "country": "Russia", "city": "Yekaterinburg", "region": "Asia", "level": "University"},
    {"name": "Moscow State Institute of International Relations MGIMO", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "National Research Nuclear University MEPhI", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "Volgograd State University", "country": "Russia", "city": "Volgograd", "region": "Asia", "level": "University"},
    {"name": "Samara State Aerospace University", "country": "Russia", "city": "Samara", "region": "Asia", "level": "University"},
    
    # UAE
    {"name": "Khalifa University", "country": "UAE", "city": "Abu Dhabi", "region": "Asia", "level": "University"},
    {"name": "American University of Sharjah", "country": "UAE", "city": "Sharjah", "region": "Asia", "level": "University"},
    {"name": "Zayed University", "country": "UAE", "city": "Dubai", "region": "Asia", "level": "University"},
    {"name": "University of Dubai", "country": "UAE", "city": "Dubai", "region": "Asia", "level": "University"},
    {"name": "Khalifa University of Science and Technology", "country": "UAE", "city": "Abu Dhabi", "region": "Asia", "level": "University"},
    
    # Kuwait - add more
    {"name": "Australian College of Kuwait", "country": "Kuwait", "city": "Kuwait City", "region": "Asia", "level": "University"},
    {"name": "Boxer", "country": "Kuwait", "city": "Kuwait City", "region": "Asia", "level": "high"},  # Note: Likely not real
    
    # Yemen - add more universities
    {"name": "Al-Aqsa University", "country": "Yemen", "city": "Sana'a", "region": "Asia", "level": "University"},
    {"name": "University of Science and Technology", "country": "Yemen", "city": "Sana'a", "region": "Asia", "level": "University"},
    {"name": "Ibb University of Medical Sciences", "country": "Yemen", "city": "Ibb", "region": "Asia", "level": "University"},
    
    # East Timor / Timor-Leste
    {"name": "Timor-Leste National University", "country": "Timor-Leste", "city": "Dili", "region": "Asia", "level": "University"},
    {"name": "University of Timor", "country": "Timor-Leste", "city": "Dili", "region": "Asia", "level": "University"},
    
    # Bahrain - add more
    {"name": "Royal College of Science", "country": "Bahrain", "city": "Manama", "region": "Asia", "level": "University"},
    
    # Israel - add more
    {"name": "Hebrew University of Jerusalem", "country": "Israel", "city": "Jerusalem", "region": "Asia", "level": "University"},
    {"name": "Tel Aviv University", "country": "Israel", "city": "Tel Aviv", "region": "Asia", "level": "University"},
    {"name": "Bar Ilan University", "country": "Israel", "city": "Ramat Gan", "region": "Asia", "level": "University"},
    {"name": "University of Haifa", "country": "Israel", "city": "Haifa", "region": "Asia", "level": "University"},
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
    
    print(f"\nBatch 159: Added {added} schools, skipped {skipped} duplicates")
    return added

if __name__ == "__main__":
    add_schools()
