#!/usr/bin/env python3
"""
Import Batch 123 of Asian Schools into the database
Specialized and technical institutions from Bangladesh, Japan, South Korea, Thailand
"""

import sqlite3
import json
from datetime import datetime

def get_db_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def import_batch123_schools():
    """Import Asian Schools Batch 123 (21 schools)"""
    
    # Load the batch data
    with open('data/asian_schools_batch123.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    schools = data['schools']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    added_count = 0
    
    for school in schools:
        # Insert new school (ignore if exists)
        cursor.execute('''
            INSERT OR IGNORE INTO schools (
                id, name, name_cn, region, country, city, level, 
                website, founded, source, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            school['id'],
            school['name'],
            school.get('name_cn'),
            school['region'],
            school['country'],
            school['city'],
            school['level'],
            school.get('website'),
            school.get('founded'),
            'batch123',
            now,
            now
        ))
        if cursor.rowcount > 0:
            added_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"Batch 123 import complete!")
    print(f"Schools added: {added_count}")
    print(f"Total schools in batch: {len(schools)}")

if __name__ == "__main__":
    import_batch123_schools()
