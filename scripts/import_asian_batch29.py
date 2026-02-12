#!/usr/bin/env python3
"""
Import script for Asian Schools Batch 29
"""

import json
import sqlite3
import os
from datetime import datetime

DB_PATH = 'database.db'
BATCH_FILE = 'data/asian_schools_batch29.json'
BATCH_NUM = 29

def import_batch():
    """Import Asian schools from batch 29."""

    if not os.path.exists(BATCH_FILE):
        print(f"  File not found: {BATCH_FILE}")
        return 0, 0

    with open(BATCH_FILE, 'r', encoding='utf-8') as f:
        batch_data = json.load(f)

    schools = batch_data['schools']
    description = batch_data.get('description', '')
    print(f"\n{'='*60}")
    print(f"Processing Batch {BATCH_NUM}: {len(schools)} schools")
    print(f"Description: {description}")
    print(f"{'='*60}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
    print(f"✓ Batch {BATCH_NUM} Import Complete!")
    print(f"{'='*60}")
    print(f"  - Added this batch: {imported}")
    print(f"  - Skipped (duplicates): {skipped}")
    print(f"  - Total schools in database: {total_schools}")
    print(f"  - Asian schools: {total_asian}")
    print(f"  - Max ID: {max_id}")
    print(f"{'='*60}")

    return imported, skipped

if __name__ == '__main__':
    import_batch()
