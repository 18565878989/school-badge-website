"""
User API Routes - 用户相关API
积分、等级、敏感词、举报
"""
from flask import Blueprint, request, jsonify, session
from services.user_service import user_service
import sqlite3
import os

user_api_bp = Blueprint('user_api', __name__, url_prefix='/api/user')

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def require_login():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    return None

# ============ 内容审核 ============

@user_api_bp.route('/content/check', methods=['POST'])
def check_content():
    """检查内容是否包含敏感词"""
    data = request.get_json()
    content = data.get('content', '')
    
    is_clean, words = user_service.check_sensitive_words(content)
    
    if not is_clean:
        return jsonify({
            'success': True,
            'passed': False,
            'words': words,
            'message': f'内容包含敏感词: {", ".join(words)}'
        })
    
    return jsonify({
        'success': True,
        'passed': True,
        'words': []
    })

@user_api_bp.route('/content/filter', methods=['POST'])
def filter_content():
    """过滤内容中的敏感词"""
    data = request.get_json()
    content = data.get('content', '')
    
    filtered = user_service.filter_sensitive_words(content)
    
    return jsonify({
        'success': True,
        'original': content,
        'filtered': filtered
    })

# ============ 敏感词管理 ============

@user_api_bp.route('/sensitive-words', methods=['GET'])
def get_sensitive_words():
    """获取敏感词列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    result = user_service.get_sensitive_words(page, limit)
    return jsonify({'success': True, **result})

@user_api_bp.route('/sensitive-words', methods=['POST'])
def add_sensitive_word():
    """添加敏感词"""
    auth = require_login()
    if auth: return auth
    
    # 检查是否是管理员
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin required'}), 403
    
    data = request.get_json()
    word = data.get('word', '').strip()
    category = data.get('category', 'blocked')
    level = data.get('level', 1)
    
    if not word:
        return jsonify({'error': 'Word required'}), 400
    
    success = user_service.add_sensitive_word(word, category, level)
    
    return jsonify({'success': success})

# ============ 用户积分 ============

@user_api_bp.route('/points', methods=['GET'])
def get_my_points():
    """获取我的积分信息"""
    auth = require_login()
    if auth: return auth
    
    points_info = user_service.get_or_create_user_points(session['user_id'])
    return jsonify({'success': True, **points_info})

@user_api_bp.route('/points/logs', methods=['GET'])
def get_point_logs():
    """获取积分日志"""
    auth = require_login()
    if auth: return auth
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = user_service.get_point_logs(session['user_id'], page, limit)
    return jsonify({'success': True, **result})

@user_api_bp.route('/points/levels')
def get_levels():
    """获取等级配置"""
    levels = [
        {'level': l, 'name': n, 'threshold': t}
        for t, l, n in user_service.LEVEL_CONFIG
    ]
    return jsonify({'success': True, 'levels': levels})

# ============ 用户徽章 ============

@user_api_bp.route('/badges', methods=['GET'])
def get_my_badges():
    """获取我的徽章"""
    auth = require_login()
    if auth: return auth
    
    badges = user_service.get_user_badges(session['user_id'])
    return jsonify({'success': True, 'badges': badges})

@user_api_bp.route('/users/<int:user_id>/badges', methods=['GET'])
def get_user_badges(user_id):
    """获取用户徽章"""
    badges = user_service.get_user_badges(user_id)
    return jsonify({'success': True, 'badges': badges})

# ============ 用户禁言 ============

@user_api_bp.route('/users/<int:user_id>/mute-status', methods=['GET'])
def get_mute_status(user_id):
    """获取用户禁言状态"""
    is_muted, mute_until = user_service.is_user_muted(user_id)
    
    return jsonify({
        'success': True,
        'is_muted': is_muted,
        'mute_until': mute_until
    })

@user_api_bp.route('/users/<int:user_id>/mute', methods=['POST'])
def mute_user(user_id):
    """禁言用户"""
    auth = require_login()
    if auth: return auth
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin required'}), 403
    
    data = request.get_json()
    days = data.get('days', 7)
    reason = data.get('reason', '')
    
    user_service.mute_user(user_id, days, reason)
    
    return jsonify({'success': True, 'message': f'用户已被禁言{days}天'})

@user_api_bp.route('/users/<int:user_id>/unmute', methods=['POST'])
def unmute_user(user_id):
    """解除禁言"""
    auth = require_login()
    if auth: return auth
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin required'}), 403
    
    user_service.unmute_user(user_id)
    
    return jsonify({'success': True, 'message': '用户已解除禁言'})

# ============ 举报管理 ============

@user_api_bp.route('/reports', methods=['POST'])
def report_content():
    """举报内容"""
    auth = require_login()
    if auth: return auth
    
    data = request.get_json()
    target_type = data.get('target_type')  # post | comment
    target_id = data.get('target_id')
    reason = data.get('reason', '')
    
    if not target_type or not target_id:
        return jsonify({'error': 'Missing parameters'}), 400
    
    report_id = user_service.report_content(
        session['user_id'], target_type, target_id, reason
    )
    
    return jsonify({'success': True, 'report_id': report_id})

@user_api_bp.route('/reports/pending', methods=['GET'])
def get_pending_reports():
    """获取待处理举报"""
    auth = require_login()
    if auth: return auth
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin required'}), 403
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = user_service.get_pending_reports(page, limit)
    return jsonify({'success': True, **result})

@user_api_bp.route('/reports/<int:report_id>/handle', methods=['POST'])
def handle_report(report_id):
    """处理举报"""
    auth = require_login()
    if auth: return auth
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin required'}), 403
    
    data = request.get_json()
    action = data.get('action')  # dismiss | delete | mute
    
    if not action:
        return jsonify({'error': 'Action required'}), 400
    
    user_service.handle_report(report_id, session['user_id'], action)
    
    return jsonify({'success': True, 'message': f'举报已处理: {action}'})

# ============ 用户社交统计 ============

@user_api_bp.route('/users/<int:user_id>/social-stats', methods=['GET'])
def get_user_social_stats(user_id):
    """获取用户社交统计"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    
    # 获取积分信息
    points_info = user_service.get_or_create_user_points(user_id)
    
    # 获取徽章
    badges = user_service.get_user_badges(user_id)
    
    # 获取发帖数
    post_count = conn.execute(
        "SELECT COUNT(*) FROM posts WHERE author_id = ? AND status = 'published'",
        (user_id,)
    ).fetchone()[0]
    
    # 获取粉丝数
    follower_count = conn.execute(
        'SELECT COUNT(*) FROM follows WHERE following_id = ?',
        (user_id,)
    ).fetchone()[0]
    
    # 获取关注数
    following_count = conn.execute(
        'SELECT COUNT(*) FROM follows WHERE follower_id = ?',
        (user_id,)
    ).fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'points': points_info['points'],
            'level': points_info['level'],
            'level_name': points_info['level_name'],
            'posts': post_count,
            'followers': follower_count,
            'following': following_count,
            'badges': len(badges)
        }
    })
