#!/usr/bin/env python3
"""
Scrape university rankings from Wikipedia and populate the database.
Targets: QS, THE, ARWU, CWUR rankings with 1000-2000 universities.
"""

import sqlite3
import re
import json
import time
import sys
import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import get_db_connection

# Database path
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

# Wikipedia ranking URLs
RANKING_URLS = {
    'qs': 'https://en.wikipedia.org/wiki/QS_World_University_Rankings',
    'the': 'https://en.wikipedia.org/wiki/Times_Higher_Education_World_University_Rankings',
    'arwu': 'https://en.wikipedia.org/wiki/Academic_Ranking_of_World_Universities',
}

# User agent to avoid blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def fetch_url(url, timeout=30):
    """Fetch URL with error handling."""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except (URLError, HTTPError) as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_qs_rankings(html):
    """Parse QS World University Rankings from Wikipedia HTML."""
    universities = []
    
    # Find all table rows with ranking data
    # Pattern: rank number followed by university name and location
    patterns = [
        # Main ranking tables
        r'<td[^>]*>(\d+)</td>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*><a[^>]*title="([^"]+)"[^>]*>([^<]+)</a>',
        # Alternative pattern for university name
        r'<td[^>]*>(\d+)</td>\s*<td[^>]*><a[^>]*>([^<]+)</a></td>\s*<td[^>]*>([^<]+)</td>',
    ]
    
    # More robust: find tables with sortable wikitable class
    # Each row typically has: Rank, University, Country/Region, and other info
    
    # Split by table rows
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    
    for row in rows:
        # Look for rank number in first cell
        rank_match = re.search(r'<td[^>]*>(\d{1,4})</td>', row)
        if not rank_match:
            continue
        
        rank = int(rank_match.group(1))
        if rank > 2000:  # Only top 2000
            continue
        
        # Extract university name
        name_match = re.search(r'<a[^>]*title="([^"]+)"[^>]*>([^<]+)</a>', row)
        if not name_match:
            continue
        
        title = name_match.group(1)
        link_text = name_match.group(2)
        
        # Skip non-university entries
        skip_keywords = ['Rank', 'University of', 'Notes', 'Ref', 'Change', 'Prev']
        if any(kw in title for kw in ['Rank', 'Table', 'Note', 'Ref']):
            continue
        
        # Extract country from row
        country_match = re.search(r'title="([^"]*flag[^"]*)"[^>]*>([^<]+)</a>', row)
        if not country_match:
            # Try another pattern
            country_match = re.search(r'<td[^>]*><a[^>]*>([^<]+)</a></td>\s*<td[^>]*>([A-Z]{2})</td>', row)
            if not country_match:
                country_match = re.search(r'">([A-Z][a-z]+(?: [A-Z][a-z]+)*)</a>.*?<td[^>]*>([A-Z]{2})</td>', row, re.DOTALL)
        
        # Try to extract country from flag icons or country names
        country_patterns = [
            r'flag[^>]*>([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)</span>',
            r'title="([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(flag\)"',
            r'>(United States|United Kingdom|United Kingdom|Germany|France|Australia|Canada|Japan|China|Singapore|Hong Kong|South Korea|Taiwan|India|Brazil|Russia|Netherlands|Switzerland|Sweden|Norway|Denmark|Finland|Belgium|Austria|Spain|Italy|Portugal|Ireland|New Zealand|Malaysia|Thailand|Vietnam|Indonesia|Philippines|Mexico|Argentina|Chile|Colombia|Poland|Czech|Hungary|Greece|Turkey|Israel|Egypt|South Africa|Nigeria|Kenya|Morocco)</span>',
        ]
        
        country = "Unknown"
        for pattern in country_patterns:
            cm = re.search(pattern, row)
            if cm:
                country = cm.group(1).strip()
                break
        
        # Clean university name - remove parenthetical location
        name = link_text.strip()
        name = re.sub(r'\s*\([^)]*\)', '', name).strip()
        
        if name and len(name) > 2 and rank <= 2000:
            universities.append({
                'name': name,
                'name_en': title if title != link_text else name,
                'country': country,
                'qs_rank': rank,
                'the_rank': None,
                'arwu_rank': None,
                'cwur_rank': None,
                'usnews_rank': None,
            })
    
    return universities


def parse_the_rankings(html):
    """Parse Times Higher Education rankings from Wikipedia HTML."""
    universities = []
    
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    
    for row in rows:
        rank_match = re.search(r'<td[^>]*>(\d{1,4})</td>', row)
        if not rank_match:
            continue
        
        rank = int(rank_match.group(1))
        if rank > 2000:
            continue
        
        # Extract university name
        name_match = re.search(r'<a[^>]*title="([^"]+)"[^>]*>([^<]+)</a>', row)
        if not name_match:
            continue
        
        title = name_match.group(1)
        link_text = name_match.group(2)
        
        if any(kw in title for kw in ['Rank', 'Table', 'Note', 'Ref', 'World University Rankings']):
            continue
        
        name = link_text.strip()
        name = re.sub(r'\s*\([^)]*\)', '', name).strip()
        
        # Extract country
        country = "Unknown"
        country_patterns = [
            r'>(United States|United Kingdom|Germany|France|Australia|Canada|Japan|China|Singapore|Hong Kong|South Korea|Taiwan|India|Brazil|Russia|Netherlands|Switzerland|Sweden|Norway|Denmark|Finland|Belgium|Austria|Spain|Italy|Portugal|Ireland|New Zealand|Malaysia|Thailand|Vietnam|Indonesia|Philippines|Mexico|Argentina|Chile|Colombia|Poland|Czech|Hungary|Greece|Turkey|Israel|Egypt|South Africa|Nigeria|Kenya|Morocco)</span>',
        ]
        for pattern in country_patterns:
            cm = re.search(pattern, row)
            if cm:
                country = cm.group(1).strip()
                break
        
        if name and len(name) > 2 and rank <= 2000:
            universities.append({
                'name': name,
                'country': country,
                'qs_rank': None,
                'the_rank': rank,
                'arwu_rank': None,
                'cwur_rank': None,
                'usnews_rank': None,
            })
    
    return universities


def parse_arwu_rankings(html):
    """Parse Shanghai Ranking (ARWU) from Wikipedia HTML."""
    universities = []
    
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    
    for row in rows:
        rank_match = re.search(r'<td[^>]*>(\d{1,4})</td>', row)
        if not rank_match:
            continue
        
        rank = int(rank_match.group(1))
        if rank > 2000:
            continue
        
        name_match = re.search(r'<a[^>]*title="([^"]+)"[^>]*>([^<]+)</a>', row)
        if not name_match:
            continue
        
        title = name_match.group(1)
        link_text = name_match.group(2)
        
        if any(kw in title for kw in ['Rank', 'Table', 'Note', 'Ref', 'Academic Ranking']):
            continue
        
        name = link_text.strip()
        name = re.sub(r'\s*\([^)]*\)', '', name).strip()
        
        if name and len(name) > 2 and rank <= 2000:
            universities.append({
                'name': name,
                'country': 'Unknown',  # ARWU page structure varies
                'qs_rank': None,
                'the_rank': None,
                'arwu_rank': rank,
                'cwur_rank': None,
                'usnews_rank': None,
            })
    
    return universities


def scrape_all_rankings():
    """Scrape all rankings and combine them."""
    all_data = {}  # name -> data
    
    # Scrape QS Rankings
    print("📥 Scraping QS World University Rankings from Wikipedia...")
    html = fetch_url(RANKING_URLS['qs'])
    if html:
        qs_unis = parse_qs_rankings(html)
        print(f"  Found {len(qs_unis)} universities from QS")
        for uni in qs_unis:
            name_key = uni['name'].lower()
            if name_key not in all_data:
                all_data[name_key] = uni
            else:
                if uni['qs_rank']:
                    all_data[name_key]['qs_rank'] = uni['qs_rank']
    else:
        print("  Failed to fetch QS rankings")
    
    time.sleep(1)
    
    # Scrape THE Rankings
    print("📥 Scraping Times Higher Education Rankings from Wikipedia...")
    html = fetch_url(RANKING_URLS['the'])
    if html:
        the_unis = parse_the_rankings(html)
        print(f"  Found {len(the_unis)} universities from THE")
        for uni in the_unis:
            name_key = uni['name'].lower()
            if name_key not in all_data:
                all_data[name_key] = uni
            else:
                if uni['the_rank']:
                    all_data[name_key]['the_rank'] = uni['the_rank']
    else:
        print("  Failed to fetch THE rankings")
    
    time.sleep(1)
    
    # Scrape ARWU Rankings
    print("📥 Scraping ARWU (Shanghai Ranking) from Wikipedia...")
    html = fetch_url(RANKING_URLS['arwu'])
    if html:
        arwu_unis = parse_arwu_rankings(html)
        print(f"  Found {len(arwu_unis)} universities from ARWU")
        for uni in arwu_unis:
            name_key = uni['name'].lower()
            if name_key not in all_data:
                all_data[name_key] = uni
            else:
                if uni['arwu_rank']:
                    all_data[name_key]['arwu_rank'] = uni['arwu_rank']
    else:
        print("  Failed to fetch ARWU rankings")
    
    return all_data


def get_country_code(country_name):
    """Convert country name to code and region."""
    country_map = {
        'United States': ('US', 'North America'),
        'United Kingdom': ('GB', 'Europe'),
        'Germany': ('DE', 'Europe'),
        'France': ('FR', 'Europe'),
        'Australia': ('AU', 'Oceania'),
        'Canada': ('CA', 'North America'),
        'Japan': ('JP', 'Asia'),
        'China': ('CN', 'Asia'),
        'Singapore': ('SG', 'Asia'),
        'Hong Kong': ('HK', 'Asia'),
        'South Korea': ('KR', 'Asia'),
        'Taiwan': ('TW', 'Asia'),
        'India': ('IN', 'Asia'),
        'Brazil': ('BR', 'South America'),
        'Russia': ('RU', 'Europe'),
        'Netherlands': ('NL', 'Europe'),
        'Switzerland': ('CH', 'Europe'),
        'Sweden': ('SE', 'Europe'),
        'Norway': ('NO', 'Europe'),
        'Denmark': ('DK', 'Europe'),
        'Finland': ('FI', 'Europe'),
        'Belgium': ('BE', 'Europe'),
        'Austria': ('AT', 'Europe'),
        'Spain': ('ES', 'Europe'),
        'Italy': ('IT', 'Europe'),
        'Portugal': ('PT', 'Europe'),
        'Ireland': ('IE', 'Europe'),
        'New Zealand': ('NZ', 'Oceania'),
        'Malaysia': ('MY', 'Asia'),
        'Thailand': ('TH', 'Asia'),
        'Mexico': ('MX', 'North America'),
        'Poland': ('PL', 'Europe'),
        'Czech': ('CZ', 'Europe'),
        'Hungary': ('HU', 'Europe'),
        'Greece': ('GR', 'Europe'),
        'Turkey': ('TR', 'Europe'),
        'Israel': ('IL', 'Asia'),
        'South Africa': ('ZA', 'Africa'),
    }
    
    return country_map.get(country_name, ('XX', 'Unknown'))


def save_to_database(all_data):
    """Save scraped data to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updated = 0
    inserted = 0
    skipped = 0
    
    for name_key, data in all_data.items():
        name = data['name']
        
        # Try to find existing school
        cursor.execute('''
            SELECT id, name, name_cn, country, region, city 
            FROM schools 
            WHERE LOWER(name) LIKE ? OR LOWER(name_cn) LIKE ? OR LOWER(name) LIKE ?
            LIMIT 1
        ''', (f'%{name.lower()}%', f'%{name.lower()}%', f'%{name.split()[0].lower()}%'))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing school
            school_id = result[0]
            
            # Build update query dynamically
            updates = []
            params = []
            
            if data.get('qs_rank'):
                updates.append('qs_rank = ?')
                params.append(data['qs_rank'])
            if data.get('the_rank'):
                updates.append('the_rank = ?')
                params.append(data['the_rank'])
            if data.get('arwu_rank'):
                updates.append('arwu_rank = ?')
                params.append(data['arwu_rank'])
            if data.get('usnews_rank'):
                updates.append('usnews_rank = ?')
                params.append(data['usnews_rank'])
            if data.get('cwur_rank'):
                updates.append('cwur_rank = ?')
                params.append(data['cwur_rank'])
            
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                params.append(school_id)
                
                query = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                updated += 1
        else:
            # Insert new school
            country_name = data.get('country', 'Unknown')
            country_code, region = get_country_code(country_name)
            
            # Try to extract city from name (often in parentheses)
            city = ''
            name_clean = name
            city_match = re.search(r'\(([^)]+)\)', name)
            if city_match:
                potential_city = city_match.group(1)
                if len(potential_city) < 30:  # Reasonable city name
                    city = potential_city
                    name_clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
            
            try:
                cursor.execute('''
                    INSERT INTO schools (name, name_cn, country, region, city, level, source,
                                        qs_rank, the_rank, arwu_rank, usnews_rank, cwur_rank,
                                        qs_year, the_year, arwu_year, usnews_year, cwur_year)
                    VALUES (?, ?, ?, ?, ?, 'university', 'wikipedia',
                            ?, ?, ?, ?, ?,
                            2026, 2026, 2025, 2026, 2025)
                ''', (
                    name_clean,
                    '',  # name_cn
                    country_code,
                    region,
                    city,
                    data.get('qs_rank'),
                    data.get('the_rank'),
                    data.get('arwu_rank'),
                    data.get('usnews_rank'),
                    data.get('cwur_rank'),
                ))
                inserted += 1
            except sqlite3.Error as e:
                skipped += 1
                continue
        
        if (updated + inserted) % 100 == 0:
            print(f"  Processed {updated + inserted} universities...")
    
    conn.commit()
    
    # Get final stats
    cursor.execute('SELECT COUNT(*) FROM schools')
    total_schools = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM schools WHERE qs_rank IS NOT NULL')
    qs_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE the_rank IS NOT NULL')
    the_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE arwu_rank IS NOT NULL')
    arwu_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE usnews_rank IS NOT NULL')
    usnews_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE cwur_rank IS NOT NULL')
    cwur_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_scraped': len(all_data),
        'updated': updated,
        'inserted': inserted,
        'skipped': skipped,
        'total_schools': total_schools,
        'qs_count': qs_count,
        'the_count': the_count,
        'arwu_count': arwu_count,
        'usnews_count': usnews_count,
        'cwur_count': cwur_count,
    }


def main():
    print("=" * 60)
    print("🏆 Scraping University Rankings from Wikipedia")
    print("=" * 60)
    
    # Scrape rankings
    all_data = scrape_all_rankings()
    
    if not all_data:
        print("❌ No data scraped. Check network connection.")
        return
    
    print(f"\n📊 Total unique universities scraped: {len(all_data)}")
    
    # Save to database
    print("\n💾 Saving to database...")
    stats = save_to_database(all_data)
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 SCRAPING COMPLETE!")
    print("=" * 60)
    print(f"  📥 Data scraped: {stats['total_scraped']} universities")
    print(f"  ✅ Updated: {stats['updated']} existing schools")
    print(f"  🆕 Inserted: {stats['inserted']} new schools")
    print(f"  ⏭️  Skipped: {stats['skipped']} records")
    print(f"\n📈 Final Database Stats:")
    print(f"  Total schools in database: {stats['total_schools']}")
    print(f"  QS Rankings: {stats['qs_count']} schools")
    print(f"  THE Rankings: {stats['the_count']} schools")
    print(f"  ARWU Rankings: {stats['arwu_count']} schools")
    print(f"  US News Rankings: {stats['usnews_count']} schools")
    print(f"  CWUR Rankings: {stats['cwur_count']} schools")


if __name__ == '__main__':
    main()
