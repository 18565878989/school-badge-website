"""
Message API Routes - 私信API
"""
from flask import Blueprint, request, jsonify, session
from services.message_service import message_service
import sqlite3
import os

message_api_bp = Blueprint('message_api', __name__, url_prefix='/api/messages')

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def require_login():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    return None

# ============ 私信 ============

@message_api_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """获取会话列表"""
    auth = require_login()
    if auth: return auth
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = message_service.get_conversations(session['user_id'], page, limit)
    return jsonify({'success': True, **result})

@message_api_bp.route('/with/<int:partner_id>', methods=['GET'])
def get_messages(partner_id):
    """获取与某用户的聊天记录"""
    auth = require_login()
    if auth: return auth
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    result = message_service.get_messages(session['user_id'], partner_id, page, limit)
    return jsonify({'success': True, **result})

@message_api_bp.route('/send', methods=['POST'])
def send_message():
    """发送私信"""
    auth = require_login()
    if auth: return auth
    
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()
    
    if not receiver_id or not content:
        return jsonify({'error': 'Missing parameters'}), 400
    
    if len(content) > 2000:
        return jsonify({'error': 'Content too long (max 2000)'}), 400
    
    message_id = message_service.send_message(session['user_id'], receiver_id, content)
    
    if message_id == -1:
        return jsonify({'error': 'Cannot send to yourself'}), 400
    
    return jsonify({'success': True, 'message_id': message_id})

@message_api_bp.route('/<int:message_id>/read', methods=['POST'])
def mark_read(message_id):
    """标记已读"""
    auth = require_login()
    if auth: return auth
    
    message_service.mark_as_read(session['user_id'], message_id)
    return jsonify({'success': True})

@message_api_bp.route('/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """删除消息"""
    auth = require_login()
    if auth: return auth
    
    success = message_service.delete_message(message_id, session['user_id'])
    return jsonify({'success': success})

@message_api_bp.route('/unread-count', methods=['GET'])
def unread_count():
    """获取未读数"""
    auth = require_login()
    if auth: return auth
    
    count = message_service.get_unread_count(session['user_id'])
    return jsonify({'success': True, 'unread': count})

@message_api_bp.route('/users/search', methods=['GET'])
def search_users():
    """搜索用户（用于发起私信）"""
    auth = require_login()
    if auth: return auth
    
    keyword = request.args.get('q', '')
    if len(keyword) < 2:
        return jsonify({'success': True, 'users': []})
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    
    users = conn.execute('''
        SELECT id, username, email FROM users
        WHERE username LIKE ? AND id != ?
        LIMIT 10
    ''', (f'%{keyword}%', session['user_id'])).fetchall()
    
    conn.close()
    
    return jsonify({'success': True, 'users': [dict(u) for u in users]})
