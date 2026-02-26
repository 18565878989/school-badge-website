#!/usr/bin/env python3
"""Import Batch 141 - More Asian Universities"""

import sqlite3
import json
import os

DB_PATH = os.path.expanduser("~/.openclaw/workspace/school-badge-website/database.db")
BATCH_FILE = os.path.expanduser("~/.openclaw/workspace/school-badge-website/data/asian_schools_batch141.json")

def import_batch():
    with open(BATCH_FILE, 'r', encoding='utf-8') as f:
        batch_data = json.load(f)
    
    schools = batch_data['schools']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    added_schools = []
    
    for school in schools:
        try:
            cursor.execute('''
                INSERT INTO schools (id, name, name_cn, region, country, city, level, website, founded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school['id'],
                school['name'],
                school.get('name_cn', ''),
                school['region'],
                school['country'],
                school['city'],
                school['level'],
                school.get('website', ''),
                school.get('founded', None)
            ))
            imported += 1
            added_schools.append((school['id'], school['name'], school['country']))
            print(f"✓ Added ID {school['id']}: {school['name']} ({school['country']})")
        except sqlite3.IntegrityError as e:
            skipped += 1
            print(f"✗ Duplicate ID {school['id']}: {school['name']} - {e}")
            continue
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE region='Asia' OR region LIKE '%Asia%'")
    asian_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(id) FROM schools WHERE region='Asia' OR region LIKE '%Asia%'")
    max_id = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*70}")
    print(f"✅ Batch 141 Import Complete!")
    print(f"{'='*70}")
    print(f"   Schools added: {imported}")
    print(f"   Skipped (duplicates/errors): {skipped}")
    print(f"   ID range: {added_schools[0][0]} - {added_schools[-1][0]}" if added_schools else "   ID range: N/A")
    print(f"   Asian schools total: {asian_count}")
    print(f"   New max ID (Asia): {max_id}")
    print(f"\n   Countries covered:")
    countries = {}
    for _, name, country in added_schools:
        countries[country] = countries.get(country, 0) + 1
    for country, count in sorted(countries.items()):
        print(f"     - {country}: {count} schools")
    print(f"{'='*70}")
    
    return imported, added_schools

if __name__ == '__main__':
    import_batch()
