"""
Rankings routes module
"""

from flask import Blueprint, render_template, request
from models import get_schools_paginated, get_db_connection

rankings_bp = Blueprint('rankings', __name__)

# Ranking systems configuration
RANKING_SYSTEMS = [
    {'id': 'qs', 'name': 'QS', 'year': 2026, 'color': '#10b981'},
    {'id': 'usnews', 'name': 'U.S. News', 'year': 2026, 'color': '#3b82f6'},
    {'id': 'the', 'name': 'THE', 'year': 2026, 'color': '#8b5cf6'},
    {'id': 'arwu', 'name': 'ARWU', 'year': 2025, 'color': '#ec4899'},
    {'id': 'cwur', 'name': 'CWUR', 'year': 2025, 'color': '#f59e0b'},
]

RANK_COLUMNS = {
    'qs': 'qs_rank',
    'usnews': 'usnews_rank',
    'the': 'the_rank',
    'arwu': 'arwu_rank',
    'cwur': 'cwur_rank'
}

@rankings_bp.route('/rankings')
def rankings():
    """World University Rankings page."""
    active_ranking = request.args.get('tab', 'qs')
    if active_ranking not in ['qs', 'usnews', 'the', 'arwu', 'cwur']:
        active_ranking = 'qs'
    
    conn = get_db_connection()
    
    # Get ranking counts
    ranking_counts = {}
    for col, name in RANK_COLUMNS.items():
        count = conn.execute(f'SELECT COUNT(*) FROM schools WHERE {col} IS NOT NULL').fetchone()[0]
        ranking_counts[name] = count
    
    # Get rank column
    rank_col = RANK_COLUMNS.get(active_ranking, 'qs_rank')
    
    # Get schools sorted by ranking
    schools = conn.execute(f'''
        SELECT * FROM schools 
        WHERE {rank_col} IS NOT NULL AND level = 'university'
        ORDER BY {rank_col}
        LIMIT 100
    ''').fetchall()
    
    # Convert to list of dicts
    schools_list = []
    for school in schools:
        schools_list.append(dict(school))
    
    # Process schools to add ranking display info
    for school in schools_list:
        rankings_list = []
        if school.get('qs_rank'):
            rankings_list.append({'id': 'qs', 'name': 'QS', 'rank': school['qs_rank']})
        if school.get('usnews_rank'):
            rankings_list.append({'id': 'usnews', 'name': 'U.S. News', 'rank': school['usnews_rank']})
        if school.get('the_rank'):
            rankings_list.append({'id': 'the', 'name': 'THE', 'rank': school['the_rank']})
        if school.get('arwu_rank'):
            rankings_list.append({'id': 'arwu', 'name': 'ARWU', 'rank': school['arwu_rank']})
        if school.get('cwur_rank'):
            rankings_list.append({'id': 'cwur', 'name': 'CWUR', 'rank': school['cwur_rank']})
        
        if rankings_list:
            school['rankings'] = rankings_list
        else:
            school['rankings'] = []
    
    conn.close()
    
    return render_template('rankings.html',
                         rankings_config=RANKING_SYSTEMS,
                         ranking_counts=ranking_counts,
                         active_ranking=active_ranking,
                         top_schools=schools_list,
                         page='rankings')


def register_routes(app):
    """Register rankings routes with the Flask app."""
    app.register_blueprint(rankings_bp)
