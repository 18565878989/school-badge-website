"""
Ranking service - business logic for university rankings
"""

from models import get_db_connection

# Ranking year configuration
RANKING_YEARS = {
    'qs': 2026,
    'usnews': 2026,
    'the': 2026,
    'arwu': 2025,
    'cwur': 2025
}

def get_latest_rankings(ranking_type=None, limit=100):
    """Get latest rankings for a specific ranking type."""
    conn = get_db_connection()
    
    rank_column = f'{ranking_type}_rank' if ranking_type else 'qs_rank'
    year_column = f'{ranking_type}_year' if ranking_type else 'qs_year'
    
    schools = conn.execute(f'''
        SELECT * FROM schools 
        WHERE {rank_column} IS NOT NULL AND level = 'university'
        ORDER BY {rank_column}
        LIMIT ?
    ''', (limit,)).fetchall()
    
    conn.close()
    
    return [dict(s) for s in schools]

def get_school_rankings_all(school_id):
    """Get all rankings for a specific school."""
    conn = get_db_connection()
    school = conn.execute('SELECT * FROM schools WHERE id = ?', (school_id,)).fetchone()
    conn.close()
    
    if not school:
        return None
    
    school = dict(school)
    rankings = []
    
    ranking_info = [
        ('qs', 'QS World University Rankings', school.get('qs_rank'), school.get('qs_year')),
        ('usnews', 'U.S. News Best Global Universities', school.get('usnews_rank'), school.get('usnews_year')),
        ('the', 'Times Higher Education', school.get('the_rank'), school.get('the_year')),
        ('arwu', 'ARWU (Shanghai Ranking)', school.get('arwu_rank'), school.get('arwu_year')),
        ('cwur', 'CWUR World University Rankings', school.get('cwur_rank'), school.get('cwur_year')),
    ]
    
    for r_id, r_name, rank, year in ranking_info:
        if rank:
            rankings.append({
                'id': r_id,
                'name': r_name,
                'rank': rank,
                'year': year
            })
    
    return rankings

def get_ranking_summary():
    """Get summary of all rankings."""
    conn = get_db_connection()
    
    summary = {}
    for r_type in ['qs', 'usnews', 'the', 'arwu', 'cwur']:
        rank_col = f'{r_type}_rank'
        year_col = f'{r_type}_year'
        
        count = conn.execute(f'SELECT COUNT(*) FROM schools WHERE {rank_col} IS NOT NULL AND level = "university"').fetchone()[0]
        latest_year = conn.execute(f'SELECT MAX({year_col}) FROM schools WHERE {rank_col} IS NOT NULL').fetchone()[0]
        
        summary[r_type] = {
            'count': count,
            'latest_year': latest_year
        }
    
    conn.close()
    return summary

def compare_schools(school_ids):
    """Compare rankings across multiple schools."""
    if not school_ids:
        return []
    
    conn = get_db_connection()
    placeholders = ','.join(['?'] * len(school_ids))
    
    schools = conn.execute(f'''
        SELECT id, name, name_cn, 
               qs_rank, usnews_rank, the_rank, arwu_rank, cwur_rank
        FROM schools 
        WHERE id IN ({placeholders})
    ''', school_ids).fetchall()
    
    conn.close()
    
    return [dict(s) for s in schools]

def get_top_by_ranking(ranking_type, region=None, limit=50):
    """Get top schools by ranking type, optionally filtered by region."""
    conn = get_db_connection()
    
    rank_col = f'{ranking_type}_rank'
    
    query = f'''
        SELECT * FROM schools 
        WHERE {rank_col} IS NOT NULL AND level = 'university'
    '''
    params = []
    
    if region:
        query += ' AND region = ?'
        params.append(region)
    
    query += f' ORDER BY {rank_col} LIMIT {limit}'
    
    schools = conn.execute(query, params).fetchall()
    conn.close()
    
    return [dict(s) for s in schools]
