"""
Recommendation API Routes - 推荐算法API
"""
from flask import Blueprint, request, jsonify, session
from services.recommendation_service import recommendation_service
from services.social_service import social_service
import sqlite3
import os

recommendation_api_bp = Blueprint('recommendation_api', __name__, url_prefix='/api/recommend')

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def require_login():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    return None

# ============ 推荐 ============

@recommendation_api_bp.route('/for-you', methods=['GET'])
def recommend_for_you():
    """为你推荐"""
    auth = require_login()
    if auth: return auth
    
    limit = request.args.get('limit', 10, type=int)
    
    # 获取用户最近看过的帖子（排除用）
    conn = sqlite3.connect(get_db_path())
    viewed = conn.execute('''
        SELECT target_id FROM user_interactions
        WHERE user_id = ? AND target_type = 'post' AND action_type = 'view'
        ORDER BY created_at DESC LIMIT 50
    ''', (session['user_id'],)).fetchall()
    exclude_ids = [v[0] for v in viewed]
    conn.close()
    
    posts = recommendation_service.recommend_for_user(
        session['user_id'], limit, exclude_ids
    )
    
    # 记录推荐曝光
    for post in posts:
        recommendation_service.record_interaction(
            session['user_id'], 'post', post['id'], 'view', 0.1
        )
    
    return jsonify({'success': True, 'posts': posts})

@recommendation_api_bp.route('/hot', methods=['GET'])
def get_hot_posts():
    """热门帖子"""
    timeframe = request.args.get('timeframe', 'day')  # day/week/month
    limit = request.args.get('limit', 10, type=int)
    
    posts = recommendation_service.get_hot_posts(limit, timeframe)
    
    return jsonify({'success': True, 'posts': posts, 'timeframe': timeframe})

@recommendation_api_bp.route('/trending', methods=['GET'])
def get_trending():
    """热门话题"""
    limit = request.args.get('limit', 5, type=int)
    
    topics = recommendation_service.get_trending_topics(limit)
    
    return jsonify({'success': True, 'topics': topics})

@recommendation_api_bp.route('/interact', methods=['POST'])
def record_interaction():
    """记录用户交互（用于改进推荐）"""
    auth = require_login()
    if auth: return auth
    
    data = request.get_json()
    target_type = data.get('target_type', 'post')  # post/comment/user
    target_id = data.get('target_id')
    action_type = data.get('action_type')  # view/like/comment/share/follow
    score = data.get('score', 1.0)
    
    if not target_id or not action_type:
        return jsonify({'error': 'Missing parameters'}), 400
    
    recommendation_service.record_interaction(
        session['user_id'], target_type, target_id, action_type, score
    )
    
    return jsonify({'success': True})

@recommendation_api_bp.route('/update-preferences', methods=['POST'])
def update_preferences():
    """更新用户偏好"""
    auth = require_login()
    if auth: return auth
    
    recommendation_service.update_user_preferences(session['user_id'])
    
    return jsonify({'success': True})

@recommendation_api_bp.route('/following', methods=['GET'])
def recommend_from_following():
    """关注的人的最新动态"""
    auth = require_login()
    if auth: return auth
    
    limit = request.args.get('limit', 10, type=int)
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    
    # 获取关注用户的ID
    following = conn.execute('''
        SELECT following_id FROM follows WHERE follower_id = ?
    ''', (session['user_id'],)).fetchall()
    following_ids = [f[0] for f in following]
    
    if not following_ids:
        return jsonify({'success': True, 'posts': []})
    
    placeholders = ','.join(['?'] * len(following_ids))
    
    posts = conn.execute(f'''
        SELECT p.*, u.username as author_name, s.name as school_name
        FROM posts p
        JOIN users u ON p.author_id = u.id
        LEFT JOIN schools s ON p.school_id = s.id
        WHERE p.author_id IN ({placeholders})
        AND p.status = 'published'
        ORDER BY p.created_at DESC
        LIMIT ?
    ''', (*following_ids, limit)).fetchall()
    
    conn.close()
    
    return jsonify({'success': True, 'posts': [dict(p) for p in posts]})
