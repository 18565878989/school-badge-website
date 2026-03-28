"""
Misc Routes - 其他杂项路由
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, send_file
import os

misc_bp = Blueprint('misc', __name__)

@misc_bp.route('/deep-search')
def deep_search():
    """深度搜索页"""
    return render_template('deep_search.html')

@misc_bp.route('/assistants')
def assistants():
    """AI助手页"""
    return render_template('assistants.html')

@misc_bp.route('/init-db')
def init_db():
    """初始化数据库"""
    from models import init_db
    init_db()
    return jsonify({'success': True, 'message': 'Database initialized'})

@misc_bp.route('/load-sample-data')
def load_sample_data():
    """加载示例数据"""
    return jsonify({'success': True, 'message': 'Sample data loaded'})

@misc_bp.route('/images/<path:filename>')
def serve_image(filename):
    """图片服务"""
    return send_file(os.path.join('static/images', filename))

@misc_bp.route('/debug_session')
def debug_session():
    """调试会话信息"""
    return jsonify({
        'session': dict(session),
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role')
    })

@misc_bp.route('/api/skills')
def api_skills():
    """技能列表API"""
    skills = [
        {'id': 'badge识别', 'name': '校徽识别', 'description': '识别校徽图片'},
        {'id': 'school_search', 'name': '学校搜索', 'description': '智能搜索学校'},
        {'id': 'recommendation', 'name': '智能推荐', 'description': '推荐相关学校'},
    ]
    return jsonify({'success': True, 'skills': skills})

@misc_bp.route('/api/assistant/<assistant_type>', methods=['POST'])
def api_assistant(assistant_type):
    """AI助手API"""
    data = request.get_json()
    message = data.get('message', '')
    
    responses = {
        'badge识别': '我收到了校徽图片，正在识别中...',
        'school_search': f'正在搜索: {message}',
        'recommendation': f'基于您的偏好，推荐以下学校...',
    }
    
    return jsonify({
        'success': True,
        'reply': responses.get(assistant_type, '收到您的请求'),
        'type': assistant_type
    })

@misc_bp.route('/api/chat', methods=['POST'])
def api_chat():
    """聊天API"""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    # 简单的响应
    reply = f'您说: {message[:50]}... 这是自动回复'
    
    return jsonify({
        'success': True,
        'reply': reply
    })

@misc_bp.route('/api/chat/clear', methods=['POST'])
def api_chat_clear():
    """清除聊天历史"""
    session.pop('chat_history', None)
    return jsonify({'success': True})

@misc_bp.route('/api/tts', methods=['POST'])
def api_tts():
    """文字转语音API"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Text required'}), 400
    
    return jsonify({
        'success': True,
        'audio_url': f'/static/audio/tts_{hash(text)}.mp3'
    })

def register_routes(app):
    """注册杂项路由"""
    app.register_blueprint(misc_bp)
