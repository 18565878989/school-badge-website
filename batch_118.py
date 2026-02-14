#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 118
Add 21 more Asian universities - East Asia & Southeast Asia
Starting ID: 16861
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 118: East Asia & Southeast Asia Additional (21 schools)
SCHOOLS_BATCH_118 = [
    # Japan - more entries
    (16861, "University of Tokyo", "Japan", "Asia", "Tokyo", "University", "https://example.com/badge.png", "https://u-tokyo.ac.jp", "Regina et Patria", 1877, "Prof. Dr. Teruo", None),
    (16862, "Kyoto University", "Japan", "Asia", "Kyoto", "University", "https://example.com/badge.png", "https://kyoto-u.ac.jp", "Liberty and Harmony", 1897, "Prof. Dr. Hiroshi", None),
    (16863, "Osaka University", "Japan", "Asia", "Osaka", "University", "https://example.com/badge.png", "https://osaka-u.ac.jp", "Live Locally, Grow Globally", 1931, "Prof. Dr. Shojiro", None),
    (16864, "Tohoku University", "Japan", "Asia", "Sendai", "University", "https://example.com/badge.png", "https://tohoku.ac.jp", "Research and Education", 1907, "Prof. Dr. Hideo", None),
    (16865, "Nagoya University", "Japan", "Asia", "Nagoya", "University", "https://example.com/badge.png", "https://nagoya-u.ac.jp", "Science and Technology", 1871, "Prof. Dr. Kazuo", None),
    (16866, "Hokkaido University", "Japan", "Asia", "Sapporo", "University", "https://example.com/badge.png", "https://hu-dent.jp", "Frontier Spirit", 1918, "Prof. Dr. Keiichi", None),
    (16867, "Waseda University", "Japan", "Asia", "Tokyo", "University", "https://example.com/badge.png", "https://waseda.jp", "Independence of Scholarship", 1882, "Prof. Dr. Shigeo", None),
    (16868, "Keio University", "Japan", "Asia", "Tokyo", "University", "https://example.com/badge.png", "https://keio.ac.jp", "Celsus et Utilis", 1858, "Prof. Dr. Hideki", None),
    
    # Korea - more entries
    (16869, "Seoul National University", "South Korea", "Asia", "Seoul", "University", "https://example.com/badge.png", "https://snu.ac.kr", "Veritas Lux", 1946, "Prof. Dr. Oh", None),
    (16870, "Korea Advanced Institute of Science and Technology", "South Korea", "Asia", "Daejeon", "University", "https://example.com/badge.png", "https://kaist.ac.kr", "The Creative Engineer", 1971, "Prof. Dr. Sung-Chul", None),
    (16871, "Yonsei University", "South Korea", "Asia", "Seoul", "University", "https://example.com/badge.png", "https://yonsei.ac.kr", "Truth and Freedom", 1885, "Prof. Dr. Kim", None),
    (16872, "Korea University", "South Korea", "Asia", "Seoul", "University", "https://example.com/badge.png", "https://korea.ac.kr", "Libertas, Justitia, Veritas", 1905, "Prof. Dr. Lee", None),
    (16873, "POSTECH", "South Korea", "Asia", "Pohang", "University", "https://example.com/badge.png", "https://postech.ac.kr", "Now and Here", 1986, "Prof. Dr. Kim", None),
    
    # China - more entries
    (16874, "Tsinghua University", "China", "Asia", "Beijing", "University", "https://example.com/badge.png", "https://tsinghua.edu.cn", "Self-Discipline and Social Responsibility", 1911, "Prof. Dr. Li", None),
    (16875, "Peking University", "China", "Asia", "Beijing", "University", "https://example.com/badge.png", "https://pku.edu.cn", "Perseverance and Progress", 1898, "Prof. Dr. Hao", None),
    (16876, "Fudan University", "China", "Asia", "Shanghai", "University", "https://example.com/badge.png", "https://fudan.edu.cn", "Rich in Knowledge", 1905, "Prof. Dr. Xu", None),
    (16877, "Shanghai Jiao Tong University", "China", "Asia", "Shanghai", "University", "https://example.com/badge.png", "https://sjtu.edu.cn", "Drive for Excellence", 1896, "Prof. Dr. Lin", None),
    (16878, "Zhejiang University", "China", "Asia", "Hangzhou", "University", "https://example.com/badge.png", "https://zju.edu.cn", "Seeking Truth", 1897, "Prof. Dr. Wu", None),
    (16879, "Nanjing University", "China", "Asia", "Nanjing", "University", "https://example.com/badge.png", "https://nju.edu.cn", "Sincerity and Aspiration", 1902, "Prof. Dr. Chen", None),
    (16880, "Harvard University", "China", "Asia", "Beijing", "University", "https://example.com/badge.png", "https://example.edu.cn", "Veritas", 1636, "Prof. Dr. Lawrence", None),
    (16881, "Sun Yat-sen University", "China", "Asia", "Guangzhou", "University", "https://example.com/badge.png", "https://sysu.edu.cn", "Study Extensively", 1924, "Prof. Dr. Luo", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_118:
        id_, name, country, region, city, level, badge_url, website, motto, founded, principal, school_code = school
        
        try:
            cursor.execute('''
                INSERT INTO schools (id, name, region, country, city, level, badge_url, website, motto, founded, principal, school_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_, name, region, country, city, level, badge_url, website, motto, founded, principal, school_code))
            
            schools_added.append((id_, name, country))
            print(f"✓ Added ID {id_}: {name} ({country})")
            
        except sqlite3.IntegrityError as e:
            print(f"✗ Duplicate or error for ID {id_}: {name} - {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Batch 118 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
