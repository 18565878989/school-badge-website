#!/usr/bin/env python3
"""
Import script for Asian Schools Batch 6
"""

import json
import sqlite3
import os
from datetime import datetime

DB_PATH = 'database.db'
BATCH_FILE = 'data/asian_schools_batch6.json'

def import_batch():
    """Import Asian schools from batch 6 JSON file."""
    
    # Load batch data
    with open(BATCH_FILE, 'r', encoding='utf-8') as f:
        batch_data = json.load(f)
    
    schools = batch_data['schools']
    print(f"Importing {len(schools)} Asian schools from {BATCH_FILE}")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    
    for school in schools:
        # Check if school already exists
        cursor.execute("SELECT id FROM schools WHERE name = ?", (school['name'],))
        existing = cursor.fetchone()
        
        if existing:
            print(f"  Skipped: {school['name']} (already exists)")
            skipped += 1
            continue
        
        # Insert school
        try:
            cursor.execute('''
                INSERT INTO schools (
                    id, name, name_cn, region, country, city, address,
                    level, description, website, badge_url, motto,
                    founded, principal, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school['id'],
                school['name'],
                school.get('name_cn'),
                school['region'],
                school['country'],
                school['city'],
                school.get('address'),
                school['level'],
                school.get('description'),
                school['website'],
                school.get('badge_url'),
                school.get('motto'),
                school.get('founded'),
                school.get('principal'),
                datetime.now(),
                datetime.now()
            ))
            imported += 1
            print(f"  Added: {school['name']} ({school['country']})")
        except Exception as e:
            print(f"  Error adding {school['name']}: {e}")
            skipped += 1
    
    conn.commit()
    conn.close()
    
    print(f"\nImport complete: {imported} added, {skipped} skipped")

if __name__ == '__main__':
    import_batch()
