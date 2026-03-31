"""
Schools routes module
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
from models import (
    get_school_by_id, get_schools_paginated, get_school_rankings,
    search_schools, get_regions, get_like, get_likes_count,
    like_school, unlike_school, get_user_liked_schools
)

schools_bp = Blueprint('schools', __name__)

@schools_bp.route('/school/<int:school_id>')
def school_detail(school_id):
    """School detail page."""
    school = get_school_by_id(school_id)
    if not school:
        abort(404)
    
    rankings = get_school_rankings(school_id)
    
    liked = False
    likes_count = get_likes_count(school_id)
    
    if 'user_id' in session:
        like = get_like(session['user_id'], school_id)
        liked = like is not None
    
    badge_url = school.get('badge_url', '')
    if badge_url and not badge_url.startswith(('http://', 'https://')):
        badge_url = url_for('static', filename=f'images/{badge_url}')
    
    # Build map query string
    school_dict = dict(school)
    addr = school_dict.get('address', '')
    name = school_dict.get('name', '')
    city = school_dict.get('city', '')
    country = school_dict.get('country', '')
    district = school_dict.get('district', '')
    
    if addr:
        map_query = addr
        if country and country.lower() not in addr.lower():
            map_query += ',' + country
    elif name:
        map_query = name
        if district:
            map_query += ',' + district
        elif city:
            map_query += ',' + city
        if country:
            map_query += ',' + country
    else:
        map_query = ""
    
    # Get related schools for Hong Kong schools (same district or feeder/linked schools)
    related_schools = []
    yearly_stats = []
    conn = None
    if school_dict.get('country') == 'Hong Kong' and school_dict.get('district'):
        from models.school import get_db_connection
        conn = get_db_connection()
        # Find schools in same district
        related = conn.execute("""
            SELECT id, name, name_cn, badge_url, district, school_type, level 
            FROM schools 
            WHERE country = 'Hong Kong' 
            AND district = ? 
            AND id != ?
            LIMIT 6
        """, (school_dict.get('district'), school_id)).fetchall()
        related_schools = [dict(row) for row in related]
        
        # Get yearly stats for Hong Kong schools
        stats = conn.execute("""
            SELECT year, student_count, teacher_count, class_s1, class_s2, class_s3
            FROM school_yearly_stats
            WHERE school_id = ?
            ORDER BY year DESC
            LIMIT 7
        """, (school_id,)).fetchall()
        yearly_stats = [dict(row) for row in stats]
    
    if conn:
        conn.close()
    
    return render_template('school.html',
                         school=school,
                         rankings=rankings,
                         liked=liked,
                         likes_count=likes_count,
                         badge_url=badge_url,
                         map_query=map_query,
                         related_schools=related_schools,
                         yearly_stats=yearly_stats)

@schools_bp.route('/badge-history/<int:school_id>')
def badge_history(school_id):
    """Badge history page."""
    school = get_school_by_id(school_id)
    if not school:
        abort(404)
    
    return render_template('badge_history.html', school=school)

@schools_bp.route('/like/<int:school_id>', methods=['POST'])
def toggle_like(school_id):
    """Toggle like for a school."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    existing_like = get_like(user_id, school_id)
    
    if existing_like:
        unlike_school(user_id, school_id)
        action = 'unliked'
    else:
        like_school(user_id, school_id)
        action = 'liked'
    
    likes_count = get_likes_count(school_id)
    
    return jsonify({
        'success': True,
        'action': action,
        'likes_count': likes_count
    })

@schools_bp.route('/my-likes')
def my_likes():
    """My liked schools."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    liked_schools = get_user_liked_schools(user_id)
    
    return render_template('my_likes.html', schools=liked_schools)


def register_routes(app):
    """Register schools routes with the app."""
    app.register_blueprint(schools_bp)
