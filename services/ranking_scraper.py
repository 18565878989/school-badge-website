"""
Ranking scraper service - fetch top 500 for each ranking system
Only fetches top 500 to ensure data accuracy
"""

import requests
import sqlite3
import re
import os
from datetime import datetime
from models import get_db_connection

# Ranking systems configuration
RANKING_SYSTEMS = {
    'qs': {
        'name': 'QS World University Rankings',
        'url': 'https://www.topuniversities.com/rankings/2024',
        'limit': 500,
        'source': 'topuniversities.com'
    },
    'the': {
        'name': 'Times Higher Education World University Rankings',
        'url': 'https://www.timeshighereducation.com/world-university-rankings',
        'limit': 500,
        'source': 'timeshighereducation.com'
    },
    'usnews': {
        'name': 'U.S. News Best Global Universities',
        'url': 'https://www.usnews.com/education/best-global-universities',
        'limit': 500,
        'source': 'usnews.com'
    },
    'arwu': {
        'name': 'ARWU (Shanghai Ranking)',
        'url': 'http://www.shanghairanking.com',
        'limit': 500,
        'source': 'shanghairanking.com'
    },
    'cwur': {
        'name': 'CWUR World University Rankings',
        'url': 'https://cwur.org',
        'limit': 500,
        'source': 'cwur.org'
    }
}


def get_schools_needing_ranks():
    """Get list of schools that need ranking data."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT id, name, name_cn FROM schools 
        WHERE level = 'university'
        AND (qs_rank IS NULL OR the_rank IS NULL OR usnews_rank IS NULL 
             OR arwu_rank IS NULL OR cwur_rank IS NULL)
    ''').fetchall()
    conn.close()
    return [dict(s) for s in schools]


def update_school_rank(school_id, ranking_type, rank_value, year):
    """Update a single school's ranking."""
    if rank_value is None or rank_value <= 0:
        return False
    
    conn = get_db_connection()
    try:
        # Verify school exists
        school = conn.execute('SELECT id FROM schools WHERE id = ?', (school_id,)).fetchone()
        if not school:
            conn.close()
            return False
        
        rank_col = f'{ranking_type}_rank'
        year_col = f'{ranking_type}_year'
        
        conn.execute(f'''
            UPDATE schools 
            SET {rank_col} = ?, {year_col} = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (rank_value, year, school_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f'Error updating rank: {e}')
        conn.close()
        return False


def batch_update_ranks(ranking_type, rankings_list):
    """
    Batch update rankings for a specific ranking system.
    
    Args:
        ranking_type: 'qs', 'the', 'usnews', 'arwu', 'cwur'
        rankings_list: List of dicts with 'school_name', 'rank', 'year'
    
    Returns:
        Number of schools updated
    """
    if not rankings_list:
        return 0
    
    conn = get_db_connection()
    updated = 0
    rank_col = f'{ranking_type}_rank'
    year_col = f'{ranking_type}_year'
    
    for item in rankings_list:
        school_name = item.get('school_name', '').strip()
        rank = item.get('rank')
        year = item.get('year', 2024)
        
        if not school_name or not rank:
            continue
        
        try:
            # Try to find school by name
            result = conn.execute('''
                SELECT id FROM schools 
                WHERE name LIKE ? OR name_cn LIKE ?
                LIMIT 1
            ''', (f'%{school_name}%', f'%{school_name}%')).fetchone()
            
            if result:
                school_id = result[0]
                conn.execute(f'''
                    UPDATE schools 
                    SET {rank_col} = ?, {year_col} = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (rank, year, school_id))
                updated += 1
        except Exception as e:
            print(f'Error updating {school_name}: {e}')
            continue
    
    conn.commit()
    conn.close()
    return updated


def get_ranking_stats():
    """Get current ranking coverage statistics."""
    conn = get_db_connection()
    
    stats = {}
    for r_type in ['qs', 'the', 'usnews', 'arwu', 'cwur']:
        rank_col = f'{r_type}_rank'
        count = conn.execute(f'''
            SELECT COUNT(*) FROM schools 
            WHERE level = 'university' AND {rank_col} IS NOT NULL
        ''').fetchone()[0]
        stats[r_type] = count
    
    conn.close()
    return stats


def export_top_n(ranking_type, n=500):
    """Export top N schools for a ranking system."""
    conn = get_db_connection()
    rank_col = f'{ranking_type}_rank'
    year_col = f'{ranking_type}_year'
    
    schools = conn.execute(f'''
        SELECT name, name_cn, country, {rank_col}, {year_col}
        FROM schools
        WHERE level = 'university' AND {rank_col} IS NOT NULL
        ORDER BY {rank_col} ASC
        LIMIT ?
    ''', (n,)).fetchall()
    
    conn.close()
    return [dict(s) for s in schools]


def validate_ranking_data():
    """Validate ranking data quality."""
    conn = get_db_connection()
    
    issues = []
    
    # Check for invalid ranks (0 or negative)
    for r_type in ['qs', 'the', 'usnews', 'arwu', 'cwur']:
        rank_col = f'{r_type}_rank'
        invalid = conn.execute(f'''
            SELECT COUNT(*) FROM schools 
            WHERE level = 'university' AND {rank_col} IS NOT NULL AND {rank_col} <= 0
        ''').fetchone()[0]
        if invalid > 0:
            issues.append(f'{r_type}: {invalid} schools with invalid rank (0 or negative)')
        
        # Check for ranks > 500 (if limit is 500)
        over_limit = conn.execute(f'''
            SELECT COUNT(*) FROM schools 
            WHERE level = 'university' AND {rank_col} > 500
        ''').fetchone()[0]
        if over_limit > 0:
            issues.append(f'{r_type}: {over_limit} schools with rank > 500')
    
    conn.close()
    return issues


def clean_invalid_ranks():
    """Remove ranks that are invalid (>500 or <=0)."""
    conn = get_db_connection()
    cleaned = 0
    
    for r_type in ['qs', 'the', 'usnews', 'arwu', 'cwur']:
        rank_col = f'{r_type}_rank'
        year_col = f'{r_type}_year'
        
        # Set invalid ranks to NULL
        cursor = conn.execute(f'''
            UPDATE schools 
            SET {rank_col} = NULL, {year_col} = NULL
            WHERE level = 'university' 
            AND {rank_col} IS NOT NULL 
            AND ({rank_col} <= 0 OR {rank_col} > 500)
        ''')
        cleaned += cursor.rowcount
    
    conn.commit()
    conn.close()
    return cleaned


# Current ranking stats
def get_summary():
    """Get ranking coverage summary."""
    stats = get_ranking_stats()
    total = stats.get('qs', 0) + stats.get('the', 0) + stats.get('usnews', 0)
    
    return {
        'total_schools_with_any_rank': total,
        'by_system': stats,
        'validated': len(validate_ranking_data()) == 0
    }
