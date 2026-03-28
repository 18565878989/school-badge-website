"""
Main routes module - index, campus, social, etc.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory
from functools import wraps
import sqlite3
import os
from models import (
    get_all_schools, get_schools_by_region, get_schools_by_level,
    get_regions, get_school_by_id, get_db_connection
)
from i18n import _, LANGUAGE_NAMES, get_locale

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_globals():
    """Inject global variables into templates."""
    from app import is_admin, OAUTH_CONFIG
    return {
        '_': _,
        'LANGUAGE_NAMES': LANGUAGE_NAMES,
        'current_lang': get_locale(),
        'is_admin': lambda: 'user_id' in session and is_admin(session.get('user_id')),
        'oauth_configured': {k: bool(v.get('appid') or v.get('client_key')) for k, v in OAUTH_CONFIG.items()}
    }

@main_bp.route('/')
def index():
    """Homepage - list schools by region with pagination."""
    search_query = request.args.get('q', '')
    selected_region = request.args.get('region', '')
    selected_country = request.args.get('country', '')
    selected_city = request.args.get('city', '')
    selected_level = request.args.get('level', 'university')
    page = request.args.get('page', 1, type=int)
    per_page = 21
    
    conn = get_db_connection()
    
    # Get country list
    countries = []
    if selected_region:
        countries = conn.execute("SELECT DISTINCT country FROM schools WHERE region = ? ORDER BY country", 
                                  (selected_region,)).fetchall()
        countries = [c[0] for c in countries]
    
    # Get city list
    cities = []
    if selected_country:
        cities = conn.execute("SELECT DISTINCT city FROM schools WHERE country = ? AND city IS NOT NULL AND city != '' ORDER BY city", 
                              (selected_country,)).fetchall()
        cities = [c[0] for c in cities]
    
    # Get HK district list
    hk_districts = []
    if selected_country == 'Hong Kong':
        hk_districts = conn.execute("SELECT DISTINCT district FROM schools WHERE country = 'Hong Kong' AND district IS NOT NULL AND district != '' ORDER BY district").fetchall()
        hk_districts = [d[0] for d in hk_districts]
    
    selected_district = request.args.get('district', '')
    
    # Build query based on filters
    if search_query:
        schools = search_schools(search_query, selected_region, selected_level)
    elif selected_country and selected_level and selected_region and selected_district:
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND district = ? AND level = ? ORDER BY name", 
                               (selected_region, selected_country, selected_district, selected_level)).fetchall()
    elif selected_country and selected_level and selected_region and selected_city:
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND city = ? AND level = ? ORDER BY name", 
                               (selected_region, selected_country, selected_city, selected_level)).fetchall()
    elif selected_country and selected_level and selected_region:
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND level = ? ORDER BY name", 
                               (selected_region, selected_country, selected_level)).fetchall()
    elif selected_region and selected_country and selected_city:
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND city = ? ORDER BY name", 
                               (selected_region, selected_country, selected_city)).fetchall()
    elif selected_region and selected_country and selected_district:
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? AND district = ? ORDER BY name", 
                               (selected_region, selected_country, selected_district)).fetchall()
    elif selected_region and selected_country:
        schools = conn.execute("SELECT * FROM schools WHERE region = ? AND country = ? ORDER BY name", 
                               (selected_region, selected_country)).fetchall()
    elif selected_country and selected_level:
        schools = conn.execute("SELECT * FROM schools WHERE country = ? AND level = ? ORDER BY name", 
                               (selected_country, selected_level)).fetchall()
    elif selected_country:
        schools = conn.execute("SELECT * FROM schools WHERE country = ? ORDER BY name", 
                               (selected_country,)).fetchall()
    elif selected_region and selected_level:
        schools = get_schools_by_region_and_level(selected_region, selected_level)
    elif selected_region:
        schools = get_schools_by_region(selected_region)
    elif selected_level:
        schools = get_schools_by_level(selected_level)
    else:
        schools = get_all_schools()
    
    regions = ['Asia', 'North America', 'Europe', 'Oceania', 'Africa', 'South America']
    levels = ['university', 'middle', 'elementary', 'kindergarten']
    
    conn.close()
    
    # Pagination
    total = len(schools)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_schools = schools[start:end]
    
    return render_template('index_apple.html', 
                         schools=paginated_schools, 
                         regions=regions, 
                         levels=levels,
                         countries=countries,
                         cities=cities,
                         hk_districts=hk_districts,
                         search_query=search_query,
                         selected_region=selected_region,
                         selected_country=selected_country,
                         selected_city=selected_city,
                         selected_district=selected_district,
                         selected_level=selected_level,
                         page=page,
                         total_pages=total_pages,
                         total_schools=total)

@main_bp.route('/lang/<lang>')
def set_language(lang):
    """Set language."""
    from i18n import LANGUAGE_NAMES
    if lang in LANGUAGE_NAMES:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@main_bp.route('/campus')
def campus():
    """Campus gallery main page."""
    conn = get_db_connection()
    
    # Get schools with campus images
    schools = conn.execute('''
        SELECT * FROM schools 
        WHERE campus_image IS NOT NULL AND campus_image != ''
        ORDER BY RANDOM()
        LIMIT 50
    ''').fetchall()
    
    conn.close()
    
    return render_template('campus_gallery.html', schools=[dict(s) for s in schools])

@main_bp.route('/campus/<region>')
def campus_region(region):
    """Campus gallery by region."""
    region_map = {
        'north-america': 'North America',
        'europe': 'Europe',
        'asia': 'Asia',
        'oceania': 'Oceania',
        'south-america': 'South America',
        'africa': 'Africa'
    }
    
    region_name = region_map.get(region, region)
    
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT * FROM schools 
        WHERE region = ? AND campus_image IS NOT NULL AND campus_image != ''
        ORDER BY RANDOM()
        LIMIT 50
    ''', (region_name,)).fetchall()
    conn.close()
    
    return render_template(f'campus_{region}.html', 
                         schools=[dict(s) for s in schools],
                         region=region_name)

@main_bp.route('/social')
def social():
    """Social hub page - topics and discussions."""
    conn = get_db_connection()
    
    # Get topics
    tab = request.args.get('tab', 'hot')
    if tab == 'hot':
        cursor = conn.execute("""
            SELECT t.*, u.username as author_name, s.name as school_name, s.badge_url as school_badge
            FROM topics t
            LEFT JOIN users u ON t.author_id = u.id
            LEFT JOIN schools s ON t.school_id = s.id
            ORDER BY t.is_hot DESC, t.likes_count DESC, t.created_at DESC
            LIMIT 20
        """)
    else:
        cursor = conn.execute("""
            SELECT t.*, u.username as author_name, s.name as school_name, s.badge_url as school_badge
            FROM topics t
            LEFT JOIN users u ON t.author_id = u.id
            LEFT JOIN schools s ON t.school_id = s.id
            ORDER BY t.created_at DESC
            LIMIT 20
        """)
    
    topics = [dict(row) for row in cursor.fetchall()]
    
    # Get hot topics for sidebar
    cursor = conn.execute("""
        SELECT t.*, u.username as author_name
        FROM topics t
        LEFT JOIN users u ON t.author_id = u.id
        WHERE t.is_hot = 1
        ORDER BY t.likes_count DESC
        LIMIT 5
    """)
    hot_topics = [dict(row) for row in cursor.fetchall()]
    
    # Get replies count
    cursor = conn.execute('SELECT COUNT(*) FROM topic_replies')
    replies_count = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('social.html', 
                          topics=topics, 
                          hot_topics=hot_topics,
                          replies_count=replies_count,
                          tab=tab,
                          online_count=128,
                          breadcrumb='social')
@main_bp.route('/deep-search')
def deep_search():
    """Deep search page."""
    return render_template('deep_search.html')

@main_bp.route('/membership')
def membership():
    """Membership page."""
    return render_template('membership.html')

@main_bp.route('/shop')
def shop():
    """Shop page."""
    return render_template('shop.html')

@main_bp.route('/badge-hub')
def badge_hub():
    """Badge hub page."""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT * FROM schools 
        WHERE badge_url IS NOT NULL AND badge_url != ''
        ORDER BY RANDOM()
        LIMIT 100
    ''').fetchall()
    conn.close()
    return render_template('badge_hub.html', schools=[dict(s) for s in schools])

@main_bp.route('/share/<int:school_id>')
def share_school(school_id):
    """Share school page."""
    school = get_school_by_id(school_id)
    if not school:
        return render_template('404.html'), 404
    return render_template('share.html', school=school)

@main_bp.route('/topic/<int:topic_id>')
def topic_detail(topic_id):
    """Topic detail page."""
    return render_template('topic_detail.html')

@main_bp.route('/assistants')
def assistants():
    """AI Assistants page."""
    return render_template('assistants.html')


def register_routes(app):
    """Register main routes with the Flask app."""
    app.register_blueprint(main_bp)
