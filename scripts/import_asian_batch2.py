#!/usr/bin/env python3
"""
Import batch of Asian schools into the database
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database.db')
SCHOOLS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'asian_schools_batch2.json')

def import_schools():
    # Read schools data
    with open(SCHOOLS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    schools = data['schools']
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    for school in schools:
        try:
            cursor.execute('''
                INSERT INTO schools (
                    id, name, name_cn, region, country, city, address, level,
                    description, website, badge_url, motto, founded, principal
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school['id'],
                school['name'],
                school.get('name_cn', ''),
                school['region'],
                school['country'],
                school['city'],
                school.get('address', ''),
                school['level'],
                school['description'],
                school['website'],
                school.get('badge_url', ''),
                school.get('motto', ''),
                school.get('founded'),
                school.get('principal', '')
            ))
            imported += 1
            print(f"✓ Added: {school['name']} ({school['country']})")
        except sqlite3.IntegrityError as e:
            print(f"✗ Already exists: {school['name']} - {e}")
        except Exception as e:
            print(f"✗ Error: {school['name']} - {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"Batch import complete: {imported}/{len(schools)} schools added")
    return imported

if __name__ == '__main__':
    import_schools()
