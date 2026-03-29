"""
Content API Routes - 内容管理API
置顶功能
"""
from flask import Blueprint, request, jsonify, session
from services.content_service import content_service
import sqlite3
import os

content_api_bp = Blueprint('content_api', __name__, url_prefix='/api/content')

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def require_login():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    return None

def require_admin():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin required'}), 403
    return None

# ============ 置顶管理 ============

@content_api_bp.route('/pinned', methods=['GET'])
def get_pinned_posts():
    """获取置顶帖子列表"""
    posts = content_service.get_pinned_posts()
    return jsonify({'success': True, 'posts': posts, 'count': len(posts)})

@content_api_bp.route('/pinned/<int:post_id>', methods=['POST'])
def pin_post(post_id):
    """置顶帖子"""
    auth = require_admin()
    if auth: return auth
    
    data = request.get_json() or {}
    position = data.get('position', 0)
    expire_days = data.get('expire_days')  # None 表示永久
    
    success = content_service.pin_post(post_id, session['user_id'], position, expire_days)
    
    return jsonify({'success': success})

@content_api_bp.route('/pinned/<int:post_id>', methods=['DELETE'])
def unpin_post(post_id):
    """取消置顶"""
    auth = require_admin()
    if auth: return auth
    
    success = content_service.unpin_post(post_id)
    
    return jsonify({'success': success})

@content_api_bp.route('/pinned/reorder', methods=['POST'])
def reorder_pins():
    """重新排序置顶"""
    auth = require_admin()
    if auth: return auth
    
    data = request.get_json()
    post_ids = data.get('post_ids', [])
    
    success = content_service.reorder_pins(post_ids)
    
    return jsonify({'success': success})

@content_api_bp.route('/pinned/cleanup', methods=['POST'])
def cleanup_expired():
    """清理过期置顶"""
    auth = require_admin()
    if auth: return auth
    
    count = content_service.cleanup_expired_pins()
    
    return jsonify({'success': True, 'cleaned': count})

@content_api_bp.route('/pinned/check/<int:post_id>', methods=['GET'])
def check_pinned(post_id):
    """检查帖子是否置顶"""
    is_pinned = content_service.is_pinned(post_id)
    return jsonify({'success': True, 'is_pinned': is_pinned})
