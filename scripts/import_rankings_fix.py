#!/usr/bin/env python3
"""Import top university rankings - standalone script"""
import sqlite3
import os

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Reset all rankings
c.execute('UPDATE schools SET usnews_rank = NULL, the_rank = NULL, arwu_rank = NULL, cwur_rank = NULL, qs_rank = NULL')
conn.commit()
print('Reset all rankings')

# Add top universities with all 5 rankings
top_universities = [
    # (name, qs, usnews, the, arwu, cwur)
    ('Massachusetts Institute of Technology', 1, 2, 3, 3, 2),
    ('MIT', 1, 2, 3, 3, 2),
    ('Harvard University', 4, 1, 2, 1, 1),
    ('Stanford University', 6, 3, 4, 2, 3),
    ('University of Oxford', 3, 6, 1, 10, 5),
    ('University of Cambridge', 5, 9, 5, 14, 6),
    ('Columbia University', 13, 2, 7, 8, 7),
    ('Yale University', 18, 5, 9, 11, 8),
    ('University of Chicago', 16, 6, 10, 13, 9),
    ('Princeton University', 21, 1, 6, 17, 4),
    ('University of Pennsylvania', 9, 7, 12, 15, 10),
    ('Cornell University', 17, 12, 14, 12, 11),
    ('Johns Hopkins University', 15, 7, 13, 16, 12),
    ('UC Berkeley', 12, 15, 8, 5, 13),
    ('UCLA', 25, 13, 20, 13, 17),
    ('Duke University', 22, 4, 15, 30, 15),
    ('Northwestern University', 23, 9, 16, 28, 18),
    ('Tsinghua University', 10, 16, 11, 22, 12),
    ('Peking University', 11, 18, 17, 29, 14),
    ('Nanyang Technological University', 19, 3, 19, 36, 25),
    ('National University of Singapore', 8, 26, 18, 35, 22),
    ("King's College London", 26, 35, 36, 48, 30),
    ('University of Edinburgh', 24, 37, 30, 38, 28),
    ('ETH Zurich', 7, 5, 11, 20, 25),
    ('Imperial College London', 2, 12, 8, 16, 15),
]

for name, qs, usnews, the, arwu, cwur in top_universities:
    c.execute('''
        UPDATE schools SET 
            qs_rank = ?, usnews_rank = ?, the_rank = ?, arwu_rank = ?, cwur_rank = ?,
            qs_year = 2026, usnews_year = 2026, the_year = 2026, arwu_year = 2025, cwur_year = 2025
        WHERE name = ?
    ''', (qs, usnews, the, arwu, cwur, name))
    status = '✓' if c.rowcount > 0 else '✗'
    print(f'{status} {name}: QS#{qs}')

conn.commit()

# Stats
c.execute('SELECT COUNT(*) FROM schools WHERE qs_rank IS NOT NULL')
qs_count = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM schools WHERE usnews_rank IS NOT NULL')
usnews_count = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM schools WHERE the_rank IS NOT NULL')
the_count = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM schools WHERE arwu_rank IS NOT NULL')
arwu_count = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM schools WHERE cwur_rank IS NOT NULL')
cwur_count = c.fetchone()[0]

print(f'\n📊 Rankings Stats:')
print(f'  QS: {qs_count}, US News: {usnews_count}, THE: {the_count}, ARWU: {arwu_count}, CWUR: {cwur_count}')

# Show top 10
print('\n🏆 Top 10 by QS:')
c.execute('''
    SELECT name, qs_rank, usnews_rank, the_rank, arwu_rank, cwur_rank
    FROM schools WHERE qs_rank IS NOT NULL
    ORDER BY qs_rank LIMIT 10
''')
for row in c.fetchall():
    print(f'  QS#{row[1]} {row[0]} - US#{row[2]} THE#{row[3]} ARWU#{row[4]} CWUR#{row[5]}')

conn.close()
print('\nDone!')
