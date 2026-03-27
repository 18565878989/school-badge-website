"""
School service - business logic for schools
"""

from models import get_db_connection
import sqlite3

def get_school_with_details(school_id):
    """Get school with all details including rankings."""
    conn = get_db_connection()
    school = conn.execute('SELECT * FROM schools WHERE id = ?', (school_id,)).fetchone()
    conn.close()
    
    if not school:
        return None
    
    return dict(school)

def get_schools_by_criteria(region=None, level=None, country=None, has_badge=None, limit=100):
    """Get schools by various criteria."""
    conn = get_db_connection()
    
    query = 'SELECT * FROM schools WHERE 1=1'
    params = []
    
    if region:
        query += ' AND region = ?'
        params.append(region)
    
    if level:
        query += ' AND level = ?'
        params.append(level)
    
    if country:
        query += ' AND country = ?'
        params.append(country)
    
    if has_badge:
        query += ' AND badge_url IS NOT NULL AND badge_url != ""'
    
    query += f' ORDER BY name LIMIT {limit}'
    
    schools = conn.execute(query, params).fetchall()
    conn.close()
    
    return [dict(s) for s in schools]

def search_schools_advanced(query, filters=None):
    """Advanced school search with filters."""
    if filters is None:
        filters = {}
    
    conn = get_db_connection()
    
    sql = '''
        SELECT * FROM schools 
        WHERE (name LIKE ? OR name_cn LIKE ? OR motto LIKE ?)
    '''
    params = [f'%{query}%', f'%{query}%', f'%{query}%']
    
    if filters.get('region'):
        sql += ' AND region = ?'
        params.append(filters['region'])
    
    if filters.get('level'):
        sql += ' AND level = ?'
        params.append(filters['level'])
    
    if filters.get('country'):
        sql += ' AND country = ?'
        params.append(filters['country'])
    
    sql += ' ORDER BY name LIMIT 50'
    
    schools = conn.execute(sql, params).fetchall()
    conn.close()
    
    return [dict(s) for s in schools]

def get_school_statistics():
    """Get overall school statistics."""
    conn = get_db_connection()
    
    stats = {
        'total': conn.execute('SELECT COUNT(*) FROM schools').fetchone()[0],
        'universities': conn.execute('SELECT COUNT(*) FROM schools WHERE level = "university"').fetchone()[0],
        'with_badges': conn.execute('SELECT COUNT(*) FROM schools WHERE badge_url IS NOT NULL AND badge_url != ""').fetchone()[0],
        'with_rankings': conn.execute('SELECT COUNT(*) FROM schools WHERE qs_rank IS NOT NULL OR usnews_rank IS NOT NULL').fetchone()[0],
        'by_region': {},
        'by_level': {}
    }
    
    # Region stats
    regions = conn.execute('SELECT region, COUNT(*) as count FROM schools GROUP BY region').fetchall()
    for r in regions:
        stats['by_region'][r['region'] or 'Unknown'] = r['count']
    
    # Level stats
    levels = conn.execute('SELECT level, COUNT(*) as count FROM schools GROUP BY level').fetchall()
    for l in levels:
        stats['by_level'][l['level'] or 'Unknown'] = l['count']
    
    conn.close()
    return stats

def update_school_badges_batch(school_ids, badge_urls):
    """Batch update school badges."""
    if len(school_ids) != len(badge_urls):
        raise ValueError("IDs and URLs count must match")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updated = 0
    for school_id, badge_url in zip(school_ids, badge_urls):
        cursor.execute('UPDATE schools SET badge_url = ?, updated_at = datetime("now") WHERE id = ?', 
                      (badge_url, school_id))
        updated += cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return updated
