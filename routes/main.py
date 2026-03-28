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
    """Home page."""
    conn = get_db_connection()
    
    # Get stats
    total_schools = conn.execute('SELECT COUNT(*) FROM schools').fetchone()[0]
    total_universities = conn.execute('SELECT COUNT(*) FROM schools WHERE level = "university"').fetchone()[0]
    total_with_badges = conn.execute('SELECT COUNT(*) FROM schools WHERE badge_url IS NOT NULL AND badge_url != ""').fetchone()[0]
    
    # Get recent schools
    recent_schools = conn.execute('''
        SELECT * FROM schools 
        ORDER BY created_at DESC 
        LIMIT 12
    ''').fetchall()
    
    # Get regions
    regions = get_regions()
    
    conn.close()
    
    return render_template('index.html',
                         total_schools=total_schools,
                         total_universities=total_universities,
                         total_with_badges=total_with_badges,
                         recent_schools=[dict(s) for s in recent_schools],
                         regions=regions,
                         page='home')

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
    """Social features page."""
    conn = get_db_connection()
    
    # Get active schools (with recent updates)
    schools = conn.execute('''
        SELECT s.*, COUNT(l.id) as likes
        FROM schools s
        LEFT JOIN likes l ON s.id = l.school_id
        GROUP BY s.id
        ORDER BY likes DESC, s.updated_at DESC
        LIMIT 50
    ''').fetchall()
    
    conn.close()
    
    return render_template('social.html', schools=[dict(s) for s in schools])

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
