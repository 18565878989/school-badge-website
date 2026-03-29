"""
Social Routes - 社交功能路由
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

social_bp = Blueprint('social', __name__)

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@social_bp.route('/topic/<int:topic_id>')
def topic_detail(topic_id):
    """话题详情"""
    conn = get_db_connection()
    topic = conn.execute('''
        SELECT t.*, u.username as author_name
        FROM topics t
        LEFT JOIN users u ON t.author_id = u.id
        WHERE t.id = ?
    ''', (topic_id,)).fetchone()
    conn.close()
    
    if not topic:
        return render_template('404.html'), 404
    
    return render_template('topic_detail.html', topic=dict(topic))

@social_bp.route('/share')
def share():
    """分享页面"""
    return render_template('share.html')

@social_bp.route('/badges')
def badges():
    """校徽展示页"""
    conn = get_db_connection()
    schools = conn.execute('''
        SELECT * FROM schools 
        WHERE badge_url IS NOT NULL AND badge_url != ''
        ORDER BY RANDOM()
        LIMIT 100
    ''').fetchall()
    conn.close()
    return render_template('badge_hub.html', schools=[dict(s) for s in schools])

@social_bp.route('/social-v2')
def social_v3():
    """社交V2"""
    return render_template('social_v3.html')

@social_bp.route('/create_topic', methods=['POST'])
def create_topic():
    """创建话题"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    school_id = data.get('school_id')
    
    if not title or not content:
        return jsonify({'error': 'Title and content required'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO topics (title, content, author_id, school_id, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    ''', (title, content, session['user_id'], school_id))
    conn.commit()
    topic_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'topic_id': topic_id})

@social_bp.route('/topic/<int:topic_id>/reply', methods=['POST'])
def reply_topic(topic_id):
    """回复话题"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO topic_replies (topic_id, user_id, content, created_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (topic_id, session['user_id'], content))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@social_bp.route('/topic/<int:topic_id>/like', methods=['POST'])
def like_topic(topic_id):
    """点赞话题"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    
    # 检查是否已点赞
    existing = conn.execute('''
        SELECT id FROM topic_likes WHERE topic_id = ? AND user_id = ?
    ''', (topic_id, session['user_id'])).fetchone()
    
    if existing:
        conn.execute('DELETE FROM topic_likes WHERE id = ?', (existing['id'],))
        action = 'unliked'
    else:
        conn.execute('''
            INSERT INTO topic_likes (topic_id, user_id, created_at)
            VALUES (?, ?, datetime('now'))
        ''', (topic_id, session['user_id']))
        action = 'liked'
    
    # 更新话题点赞数
    count = conn.execute(
        'SELECT COUNT(*) FROM topic_likes WHERE topic_id = ?',
        (topic_id,)
    ).fetchone()[0]
    conn.execute(
        'UPDATE topics SET likes_count = ? WHERE id = ?',
        (count, topic_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'action': action, 'count': count})


def register_routes(app):
    """注册社交路由"""
    app.register_blueprint(social_bp)
