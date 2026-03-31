"""
API routes module
"""

from flask import Blueprint, request, jsonify
from models import get_schools_paginated, search_schools, get_regions, get_region_stats, get_db_connection

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/schools')
def schools():
    """Get schools list with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    region = request.args.get('region')
    level = request.args.get('level')
    
    schools, total = get_schools_paginated(page=page, per_page=per_page, region=region, level=level)
    
    return jsonify({
        'schools': [dict(s) for s in schools],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })

@api_bp.route('/schools/search')
def search():
    """Search schools."""
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify({'schools': []})
    
    results = search_schools(q, limit=20)
    return jsonify({'schools': [dict(r) for r in results]})

@api_bp.route('/regions')
def regions():
    """Get all regions."""
    region_list = get_regions()
    return jsonify({'regions': region_list})

@api_bp.route('/regions/stats')
def region_stats():
    """Get region statistics."""
    stats = get_region_stats()
    return jsonify({'stats': stats})

@api_bp.route('/countries')
def countries():
    """Get countries by region."""
    region = request.args.get('region', '')
    conn = get_db_connection()
    if region:
        rows = conn.execute(
            "SELECT DISTINCT country, COUNT(*) as cnt FROM schools WHERE region = ? GROUP BY country ORDER BY cnt DESC",
            (region,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT DISTINCT country, COUNT(*) as cnt FROM schools GROUP BY country ORDER BY cnt DESC"
        ).fetchall()
    conn.close()
    return jsonify({'countries': [{'name': r['country'], 'count': r['cnt']} for r in rows]})

@api_bp.route('/cities')
def cities():
    """Get cities by country."""
    country = request.args.get('country', '')
    if not country:
        return jsonify({'cities': []})
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT DISTINCT city FROM schools WHERE country = ? AND city IS NOT NULL AND city != '' ORDER BY city",
        (country,)
    ).fetchall()
    conn.close()
    return jsonify({'cities': [r['city'] for r in rows if r['city']]})

@api_bp.route('/districts')
def districts():
    """Get HK districts by country."""
    country = request.args.get('country', '')
    if not country:
        return jsonify({'districts': []})
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT DISTINCT district FROM schools WHERE country = ? AND district IS NOT NULL AND district != '' ORDER BY district",
        (country,)
    ).fetchall()
    conn.close()
    return jsonify({'districts': [r['district'] for r in rows if r['district']]})


def register_routes(app):
    """Register API routes with the Flask app."""
    app.register_blueprint(api_bp)
