#!/usr/bin/env python3
"""Import Batch 130 - Asian Education and Teacher Training Universities"""

import sqlite3
import json
import os

DB_PATH = os.path.expanduser("~/.openclaw/workspace/school-badge-website/database.db")
BATCH_FILE = os.path.expanduser("~/.openclaw/workspace/school-badge-website/data/asian_schools_batch130.json")

def import_batch():
    with open(BATCH_FILE, 'r', encoding='utf-8') as f:
        batch_data = json.load(f)
    
    schools = batch_data['schools']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    
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
        except sqlite3.IntegrityError:
            skipped += 1
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE region='Asia' OR region LIKE '%Asia%'")
    asian_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(id) FROM schools")
    max_id = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Batch 130 Import Complete!")
    print(f"   Imported: {imported}")
    print(f"   Skipped (duplicates): {skipped}")
    print(f"   Asian schools total: {asian_count}")
    print(f"   Max ID: {max_id}")

if __name__ == '__main__':
    import_batch()
