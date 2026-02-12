#!/usr/bin/env python3
"""
Import script for Asian Schools Batches 14-18
"""

import json
import sqlite3
import os
from datetime import datetime

DB_PATH = 'database.db'
BATCHES = [
    'data/asian_schools_batch14.json',
    'data/asian_schools_batch15.json',
    'data/asian_schools_batch16.json',
    'data/asian_schools_batch17.json',
    'data/asian_schools_batch18.json',
]

def import_batches():
    """Import Asian schools from multiple batch files."""
    
    total_imported = 0
    total_skipped = 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for batch_file in BATCHES:
        if not os.path.exists(batch_file):
            print(f"  File not found: {batch_file}")
            continue
            
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)
        
        schools = batch_data['schools']
        batch_num = batch_data.get('batch', 'unknown')
        print(f"\nProcessing Batch {batch_num}: {len(schools)} schools")
        
        imported = 0
        skipped = 0
        
        for school in schools:
            cursor.execute("SELECT id FROM schools WHERE id = ?", (school['id'],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"  Skipped: ID {school['id']} - {school['name']} (already exists)")
                skipped += 1
                continue
            
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
                    school.get('city'),
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
                print(f"  Added: {school['id']} - {school['name']} ({school['country']})")
            except Exception as e:
                print(f"  Error adding {school['name']}: {e}")
                skipped += 1
        
        total_imported += imported
        total_skipped += skipped
        print(f"  Batch {batch_num} complete: +{imported}, skipped {skipped}")
    
    conn.commit()
    
    # Show final counts
    cursor.execute("SELECT COUNT(*) FROM schools")
    total_schools = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE region = 'Asia'")
    total_asian = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(id) FROM schools")
    max_id = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✓ Import Complete!")
    print(f"  - Total added: {total_imported}")
    print(f"  - Total skipped: {total_skipped}")
    print(f"  - Total schools in database: {total_schools}")
    print(f"  - Asian schools: {total_asian}")
    print(f"  - Max ID: {max_id}")
    print(f"{'='*60}")

if __name__ == '__main__':
    import_batches()
