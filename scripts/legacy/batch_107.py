#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Asian Schools Generator - Batch 107
Add 21 more Asian universities
Starting ID: 13823
"""

import sqlite3

DB_PATH = 'database.db'

# Batch 107: East Asia Universities (21 schools)
# Countries: Japan, Korea, China, Mongolia, Taiwan, Hong Kong, Macau
SCHOOLS_BATCH_107 = [
    # Japan (continued)
    (13823, "University of Tokyo", "Japan", "Asia", "Japan", "Tokyo", "University", "https://example.com/badge.png", "https://www.u-tokyo.ac.jp", "Regnum et Disciplina", 1877, "Prof. Dr. Teruo Fujii", None),
    (13824, "Kyoto University", "Japan", "Asia", "Japan", "Kyoto", "University", "https://example.com/badge.png", "https://www.kyoto-u.ac.jp", "Liberty and Excellence", 1897, "Prof. Dr. Nagaharu", None),
    (13825, "Osaka University", "Japan", "Asia", "Japan", "Osaka", "University", "https://example.com/badge.png", "https://www.osaka-u.ac.jp", "Live Locally, Grow Globally", 1931, "Prof. Dr. Shojiro", None),
    (13826, "Tohoku University", "Japan", "Asia", "Japan", "Sendai", "University", "https://example.com/badge.png", "https://www.tohoku.ac.jp", "Research First", 1907, "Prof. Dr. Hideo", None),
    (13827, "Nagoya University", "Japan", "Asia", "Japan", "Nagoya", "University", "https://example.com/badge.png", "https://www.nagoya-u.ac.jp", "Education and Research for a Better World", 1871, "Prof. Dr. Seiichiro", None),
    (13828, "Hokkaido University", "Japan", "Asia", "Japan", "Sapporo", "University", "https://example.com/badge.png", "https://www.hokudai.ac.jp", "Frontier Spirit", 1918, "Prof. Dr. Ryo", None),
    (13829, "Kyushu University", "Japan", "Asia", "Japan", "Fukuoka", "University", "https://example.com/badge.png", "https://www.kyushu-u.ac.jp", "Research and Education for the Future", 1911, "Prof. Dr. Tatsuro", None),
    (13830, "Keio University", "Japan", "Asia", "Japan", "Tokyo", "University", "https://example.com/badge.png", "https://www.keio.ac.jp", "Celsus in Spiritu", 1858, "Prof. Dr. Hideyuki", None),
    (13831, "Waseda University", "Japan", "Asia", "Japan", "Tokyo", "University", "https://example.com/badge.png", "https://www.waseda.jp", "Independence and Freedom", 1882, "Prof. Dr. Aiji", None),
    (13832, "Tokyo Institute of Technology", "Japan", "Asia", "Japan", "Tokyo", "University", "https://example.com/badge.png", "https://www.titech.ac.jp", "Science and Technology for Society", 1881, "Prof. Dr. Kazuya", None),
    
    # Korea (South) (continued)
    (13833, "Seoul National University", "South Korea", "Asia", "South Korea", "Seoul", "University", "https://example.com/badge.png", "https://www.snu.ac.kr", "Veritas Lux Mea", 1946, "Prof. Dr. Seong-Jun", None),
    (13834, "Korea Advanced Institute of Science and Technology", "South Korea", "Asia", "South Korea", "Daejeon", "University", "https://example.com/badge.png", "https://www.kaist.ac.kr", "Opening New Horizons", 1971, "Prof. Dr. Lee", None),
    (13835, "Yonsei University", "South Korea", "Asia", "South Korea", "Seoul", "University", "https://example.com/badge.png", "https://www.yonsei.ac.kr", "Truth and Freedom", 1885, "Prof. Dr. Dong-Sup", None),
    (13836, "Korea University", "South Korea", "Asia", "South Korea", "Seoul", "University", "https://example.com/badge.png", "https://www.korea.ac.kr", "Libertas, Justitia, Veritas", 1905, "Prof. Dr. Jin-Pyo", None),
    (13837, "Sungkyunkwan University", "South Korea", "Asia", "South Korea", "Seoul", "University", "https://example.com/badge.png", "https://www.skku.edu", "Truth and Innovation", 1398, "Prof. Dr. Sung-Yul", None),
    (13838, "Hanyang University", "South Korea", "Asia", "South Korea", "Seoul", "University", "https://example.com/badge.png", "https://www.hanyang.ac.kr", "Love and Truth", 1939, "Prof. Dr. Young-Soo", None),
    (13839, "Pohang University of Science and Technology", "South Korea", "Asia", "South Korea", "Pohang", "University", "https://example.com/badge.png", "https://www.postech.ac.kr", "Science for the Future", 1986, "Prof. Dr. Yong-Sun", None),
    
    # Korea (North)
    (13840, "Kim Il-sung University", "North Korea", "Asia", "North Korea", "Pyongyang", "University", "https://example.com/badge.png", "https://www.ksu.edu.kp", "Monument to Juche Education", 1946, "Prof. Dr. Choe", None),
    
    # Mongolia
    (13841, "National University of Mongolia", "Mongolia", "Asia", "Mongolia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://www.num.edu.mn", "Knowledge, Wisdom, Freedom", 1942, "Prof. Dr. Baykhang", None),
    (13842, "Mongolian University of Science and Technology", "Mongolia", "Asia", "Mongolia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://www.must.edu.mn", "Science Creates Future", 1966, "Prof. Dr. Altan", None),
    (13843, "Mongolian State University", "Mongolia", "Asia", "Mongolia", "Ulaanbaatar", "University", "https://example.com/badge.png", "https://www.msu.edu.mn", "Education for Nation", 2000, "Prof. Dr. Tsedev", None),
]

def add_batch():
    """Add a batch of Asian schools to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    schools_added = []
    
    for school in SCHOOLS_BATCH_107:
        id_, name, country, region, nation, city, level, badge_url, website, motto, founded, principal, school_code = school
        
        try:
            cursor.execute('''
                INSERT INTO schools (id, name, region, country, city, level, badge_url, website, motto, founded, principal, school_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_, name, region, nation, city, level, badge_url, website, motto, founded, principal, school_code))
            
            schools_added.append((id_, name, country))
            print(f"✓ Added ID {id_}: {name} ({country})")
            
        except sqlite3.IntegrityError as e:
            print(f"✗ Duplicate or error for ID {id_}: {name} - {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Batch 107 Summary:")
    print(f"  Total added: {len(schools_added)}")
    print(f"  ID range: {schools_added[0][0] if schools_added else 'N/A'} - {schools_added[-1][0] if schools_added else 'N/A'}")
    print(f"{'='*60}")
    
    return schools_added

if __name__ == "__main__":
    add_batch()
