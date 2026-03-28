"""
Schools routes module
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
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
        return render_template('404.html'), 404
    
    rankings = get_school_rankings(school_id)
    
    # Get like status
    liked = False
    likes_count = get_likes_count(school_id)
    
    if 'user_id' in session:
        like = get_like(session['user_id'], school_id)
        liked = like is not None
    
    # Get badge URL
    badge_url = school.get('badge_url', '')
    if badge_url and not badge_url.startswith(('http://', 'https://')):
        badge_url = url_for('static', filename=f'images/{badge_url}')
    
    return render_template('school.html',
                         school=school,
                         rankings=rankings,
                         liked=liked,
                         likes_count=likes_count,
                         badge_url=badge_url)

@schools_bp.route('/badge-history/<int:school_id>')
def badge_history(school_id):
    """Badge history page."""
    school = get_school_by_id(school_id)
    if not school:
        return render_template('404.html'), 404
    
    return render_template('badge_history.html', school=school)

@schools_bp.route('/like/<int:school_id>', methods=['POST'])
def toggle_like(school_id):
    """Toggle like for a school."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
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
    """Register schools routes with the Flask app."""
    app.register_blueprint(schools_bp)
