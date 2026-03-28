"""
Full API Routes - 完整API路由
"""
from flask import Blueprint, request, jsonify, session
import sqlite3
import os

api_full_bp = Blueprint('api_full', __name__, url_prefix='/api')

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ============ Posts API ============

@api_full_bp.route('/posts', methods=['GET', 'POST'])
def posts():
    """获取或创建帖子"""
    if request.method == 'GET':
        conn = get_db_connection()
        posts = conn.execute('''
            SELECT p.*, u.username as author_name
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT 50
        ''').fetchall()
        conn.close()
        return jsonify({'success': True, 'posts': [dict(p) for p in posts]})
    else:
        # POST - 创建帖子
        if 'user_id' not in session:
            return jsonify({'error': 'Please login'}), 401
        
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content required'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO posts (user_id, content, created_at)
            VALUES (?, ?, datetime('now'))
        ''', (session['user_id'], content))
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'post_id': post_id})

@api_full_bp.route('/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
def post_detail(post_id):
    """帖子详情"""
    conn = get_db_connection()
    
    if request.method == 'GET':
        post = conn.execute('''
            SELECT p.*, u.username as author_name
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        ''', (post_id,)).fetchone()
        conn.close()
        if not post:
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'success': True, 'post': dict(post)})
    
    elif request.method == 'PUT':
        if 'user_id' not in session:
            return jsonify({'error': 'Please login'}), 401
        
        data = request.get_json()
        content = data.get('content', '')
        
        conn.execute('UPDATE posts SET content = ? WHERE id = ?', (content, post_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    else:  # DELETE
        if 'user_id' not in session:
            return jsonify({'error': 'Please login'}), 401
        
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@api_full_bp.route('/posts/<int:post_id>/like', methods=['POST', 'DELETE'])
def post_like(post_id):
    """帖子点赞"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        try:
            conn.execute('''
                INSERT INTO post_likes (post_id, user_id, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (post_id, session['user_id']))
            conn.commit()
        except:
            pass  # 已点赞
        action = 'liked'
    else:
        conn.execute(
            'DELETE FROM post_likes WHERE post_id = ? AND user_id = ?',
            (post_id, session['user_id'])
        )
        conn.commit()
        action = 'unliked'
    
    count = conn.execute(
        'SELECT COUNT(*) FROM post_likes WHERE post_id = ?',
        (post_id,)
    ).fetchone()[0]
    conn.close()
    
    return jsonify({'success': True, 'action': action, 'count': count})

@api_full_bp.route('/posts/<int:post_id>/comments')
def post_comments(post_id):
    """获取帖子评论"""
    conn = get_db_connection()
    comments = conn.execute('''
        SELECT c.*, u.username as author_name
        FROM post_comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC
    ''', (post_id,)).fetchall()
    conn.close()
    return jsonify({'success': True, 'comments': [dict(c) for c in comments]})

@api_full_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    """添加评论"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    data = request.get_json()
    content = data.get('content', '')
    
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO post_comments (post_id, user_id, content, created_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (post_id, session['user_id'], content))
    conn.commit()
    comment_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'comment_id': comment_id})

# ============ User API ============

@api_full_bp.route('/users/<int:user_id>/follow', methods=['POST', 'DELETE'])
def follow_user(user_id):
    """关注用户"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        try:
            conn.execute('''
                INSERT INTO follows (follower_id, following_id, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (session['user_id'], user_id))
            conn.commit()
        except:
            pass
        action = 'followed'
    else:
        conn.execute(
            'DELETE FROM follows WHERE follower_id = ? AND following_id = ?',
            (session['user_id'], user_id)
        )
        conn.commit()
        action = 'unfollowed'
    
    conn.close()
    return jsonify({'success': True, 'action': action})

# ============ Notifications API ============

@api_full_bp.route('/notifications')
def notifications():
    """获取通知"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    notifications = conn.execute('''
        SELECT * FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 50
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return jsonify({'success': True, 'notifications': [dict(n) for n in notifications]})

@api_full_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_read(notification_id):
    """标记已读"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE notifications SET is_read = 1 WHERE id = ?',
        (notification_id,)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@api_full_bp.route('/notifications/read-all', methods=['POST'])
def mark_all_read():
    """全部标记已读"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE notifications SET is_read = 1 WHERE user_id = ?',
        (session['user_id'],)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ============ Collections API ============

@api_full_bp.route('/collections')
def collections():
    """获取收藏夹"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    collections = conn.execute('''
        SELECT * FROM collections
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return jsonify({'success': True, 'collections': [dict(c) for c in collections]})

@api_full_bp.route('/collections', methods=['POST'])
def create_collection():
    """创建收藏夹"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    data = request.get_json()
    name = data.get('name', '')
    
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO collections (user_id, name, created_at)
        VALUES (?, ?, datetime('now'))
    ''', (session['user_id'], name))
    conn.commit()
    collection_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'collection_id': collection_id})

@api_full_bp.route('/collections/<int:collection_id>/items', methods=['POST'])
def add_to_collection(collection_id):
    """添加项目到收藏夹"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    data = request.get_json()
    item_type = data.get('type', 'school')
    item_id = data.get('item_id')
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO collection_items (collection_id, item_type, item_id, created_at)
            VALUES (?, ?, ?, datetime('now'))
        ''', (collection_id, item_type, item_id))
        conn.commit()
    except:
        pass
    conn.close()
    
    return jsonify({'success': True})

# ============ Stats API ============

@api_full_bp.route('/stats/overview')
def stats_overview():
    """统计概览"""
    conn = get_db_connection()
    
    stats = {
        'total_schools': conn.execute('SELECT COUNT(*) FROM schools').fetchone()[0],
        'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'total_likes': conn.execute('SELECT COUNT(*) FROM likes').fetchone()[0],
        'total_posts': conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0],
    }
    
    conn.close()
    return jsonify({'success': True, 'stats': stats})

# ============ Ads API ============

@api_full_bp.route('/ads/positions')
def ad_positions():
    """广告位置"""
    positions = [
        {'code': 'home_top', 'name': '首页顶部'},
        {'code': 'home_side', 'name': '首页侧边'},
        {'code': 'school_detail', 'name': '学校详情页'},
    ]
    return jsonify({'success': True, 'positions': positions})

@api_full_bp.route('/ads/<position_code>')
def ads_by_position(position_code):
    """按位置获取广告"""
    return jsonify({'success': True, 'ads': []})

@api_full_bp.route('/ads/<int:ad_id>/click', methods=['POST'])
def ad_click(ad_id):
    """广告点击"""
    return jsonify({'success': True})

def register_routes(app):
    """注册完整API路由"""
    app.register_blueprint(api_full_bp)
