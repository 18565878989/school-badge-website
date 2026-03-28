"""
Extended API Routes - 额外的API路由
"""
from flask import Blueprint, request, jsonify, session
import sqlite3
import os

api_ext_bp = Blueprint('api_ext', __name__)

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@api_ext_bp.route('/api/chat', methods=['POST'])
def chat():
    """AI Chat API"""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # 简单的响应（实际项目中应调用AI服务）
    response = {
        'reply': f'您发送了: {message[:50]}... 这是一个模拟响应',
        'timestamp': '2026-03-29'
    }
    
    return jsonify(response)

@api_ext_bp.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    session.pop('chat_history', None)
    return jsonify({'success': True})

@api_ext_bp.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Text to Speech API"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    # 返回模拟音频URL
    return jsonify({
        'success': True,
        'audio_url': f'/static/audio/tts_{hash(text)}.mp3'
    })

@api_ext_bp.route('/api/recommend/favorites', methods=['GET'])
def recommend_favorites():
    """Get favorite recommendations"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    
    # 获取用户点赞的学校
    liked = conn.execute('''
        SELECT school_id FROM likes WHERE user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    liked_ids = [l['school_id'] for l in liked]
    
    # 简单推荐：同地区同类型的其他学校
    if liked_ids:
        first_school = conn.execute(
            'SELECT region, level FROM schools WHERE id = ?',
            (liked_ids[0],)
        ).fetchone()
        
        if first_school:
            recommended = conn.execute('''
                SELECT * FROM schools 
                WHERE region = ? AND level = ? AND id NOT IN ({})
                ORDER BY RANDOM()
                LIMIT 10
            '''.format(','.join('?' * len(liked_ids))),
                (first_school['region'], first_school['level'], *liked_ids)
            ).fetchall()
        else:
            recommended = []
    else:
        recommended = conn.execute('''
            SELECT * FROM schools ORDER BY RANDOM() LIMIT 10
        ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'recommendations': [dict(r) for r in recommended]
    })

@api_ext_bp.route('/api/similar/<int:school_id>', methods=['GET'])
def similar_schools(school_id):
    """Get similar schools"""
    conn = get_db_connection()
    
    school = conn.execute(
        'SELECT * FROM schools WHERE id = ?', (school_id,)
    ).fetchone()
    
    if not school:
        conn.close()
        return jsonify({'error': 'School not found'}), 404
    
    # 找同地区同类型的学校
    similar = conn.execute('''
        SELECT * FROM schools 
        WHERE region = ? AND level = ? AND id != ?
        ORDER BY RANDOM()
        LIMIT 10
    ''', (school['region'], school['level'], school_id)).fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'similar': [dict(s) for s in similar]
    })

@api_ext_bp.route('/api/deep-search', methods=['POST'])
def deep_search():
    """Deep search API - AI powered search"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # 模拟深度搜索响应
    return jsonify({
        'success': True,
        'results': [],
        'message': 'Deep search requires AI service integration'
    })


def register_routes(app):
    """Register extended API routes"""
    app.register_blueprint(api_ext_bp, url_prefix='')
