#!/usr/bin/env python3
"""
Batch 158: Add more underrepresented Asian schools
Countries: Russia, Kuwait, Yemen, Bahrain, Israel, Lebanon, Mongolia
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Schools to add from underrepresented Asian countries
SCHOOLS = [
    # Russia (European & Asian regions) - need more
    {"name": "Novosibirsk State University", "country": "Russia", "city": "Novosibirsk", "region": "Asia", "level": "University"},
    {"name": "Moscow Institute of Physics and Technology", "country": "Russia", "city": "Moscow", "region": "Asia", "level": "University"},
    {"name": "Saint Petersburg State University", "country": "Russia", "city": "Saint Petersburg", "region": "Asia", "level": "University"},
    {"name": "Kazan Federal University", "country": "Russia", "city": "Kazan", "region": "Asia", "level": "University"},
    {"name": "Siberian Federal University", "country": "Russia", "city": "Krasnoyarsk", "region": "Asia", "level": "University"},
    
    # Kuwait
    {"name": "Kuwait University", "country": "Kuwait", "city": "Kuwait City", "region": "Asia", "level": "University"},
    {"name": "American University of Kuwait", "country": "Kuwait", "city": "Kuwait City", "region": "Asia", "level": "University"},
    {"name": "Gulf University for Science and Technology", "country": "Kuwait", "city": "Hawally", "region": "Asia", "level": "University"},
    
    # Yemen
    {"name": "Sana'a University", "country": "Yemen", "city": "Sana'a", "region": "Asia", "level": "University"},
    {"name": "University of Aden", "country": "Yemen", "city": "Aden", "region": "Asia", "level": "University"},
    {"name": "Taiz University", "country": "Yemen", "city": "Taiz", "region": "Asia", "level": "University"},
    
    # Bahrain
    {"name": "University of Bahrain", "country": "Bahrain", "city": "Sakhir", "region": "Asia", "level": "University"},
    {"name": "Bahrain University", "country": "Bahrain", "city": "Manama", "region": "Asia", "level": "University"},
    {"name": "American University of Bahrain", "country": "Bahrain", "city": "Manama", "region": "Asia", "level": "University"},
    
    # Israel
    {"name": "Technion - Israel Institute of Technology", "country": "Israel", "city": "Haifa", "region": "Asia", "level": "University"},
    {"name": "Weizmann Institute of Science", "country": "Israel", "city": "Rehovot", "region": "Asia", "level": "University"},
    {"name": "Ben-Gurion University of the Negev", "country": "Israel", "city": "Beersheba", "region": "Asia", "level": "University"},
    
    # Lebanon
    {"name": "American University of Beirut", "country": "Lebanon", "city": "Beirut", "region": "Asia", "level": "University"},
    {"name": "Lebanese American University", "country": "Lebanon", "city": "Beirut", "region": "Asia", "level": "University"},
    {"name": "University of Balamand", "country": "Lebanon", "city": "Balamand", "region": "Asia", "level": "University"},
    
    # Mongolia
    {"name": "Mongolian University of Science and Technology", "country": "Mongolia", "city": "Ulaanbaatar", "region": "Asia", "level": "University"},
]

def add_schools():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    added = 0
    skipped = 0
    
    for school in SCHOOLS:
        # Check if school already exists
        cursor.execute(
            "SELECT id FROM schools WHERE name = ? AND country = ?",
            (school["name"], school["country"])
        )
        if cursor.fetchone():
            skipped += 1
            continue
        
        # Insert new school
        cursor.execute("""
            INSERT INTO schools (name, country, city, region, level, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (school["name"], school["country"], school["city"], school["region"], school["level"]))
        added += 1
    
    conn.commit()
    conn.close()
    
    print(f"Batch 158: Added {added} schools, skipped {skipped} duplicates")
    return added

if __name__ == "__main__":
    add_schools()
