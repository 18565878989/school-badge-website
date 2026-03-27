"""
校徽网 - Flask Application (模块化重构版)
主入口文件 - 精简后

功能:
- 路由注册 (通过 blueprints)
- 配置管理
- 数据库初始化
- 会话管理
"""

import os
from flask import Flask, session, redirect, url_for, flash, render_template

# 加载 .env 配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 初始化 Flask App
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 确保上传目录存在
os.makedirs('static/images', exist_ok=True)

# ==========================================
# 导入现有模块 (保持向后兼容)
# ==========================================
from models import init_db, get_db_connection
from i18n import _, LANGUAGE_NAMES, get_locale

# 支持的语言列表
SUPPORTED_LANGUAGES = ['zh', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'pt', 'it', 'ru', 'ar']

# 初始化数据库
init_db()

# ==========================================
# 注入全局变量到模板
# ==========================================
@app.context_processor
def inject_globals():
    """注入全局变量到模板."""
    return {
        '_': _,
        'LANGUAGE_NAMES': LANGUAGE_NAMES,
        'current_lang': get_locale(),
        'is_admin': is_admin,
        'app_name': '校徽网'
    }

# ==========================================
# 语言切换
# ==========================================
@app.route('/lang/<lang>')
def set_language(lang):
    """设置语言."""
    if lang in SUPPORTED_LANGUAGES:
        session['lang'] = lang
    from flask import request
    return redirect(request.referrer or url_for('index'))

# ==========================================
# 登录/登出 (简单内联实现)
# ==========================================
@app.route('/login')
def login():
    from flask import request, render_template
    from models import get_db_connection
    from werkzeug.security import check_password_hash
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                           (username, username)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(_('Login successful'), 'success')
            return redirect(url_for('index'))
        else:
            flash(_('Invalid username or password'), 'error')
    
    return render_template('login.html')

# ==========================================
# 首页
# ==========================================
@app.route('/')
def index():
    from models import get_all_schools
    
    conn = get_db_connection()
    total_schools = conn.execute('SELECT COUNT(*) FROM schools').fetchone()[0]
    total_universities = conn.execute('SELECT COUNT(*) FROM schools WHERE level = "university"').fetchone()[0]
    total_with_badges = conn.execute('SELECT COUNT(*) FROM schools WHERE badge_url IS NOT NULL AND badge_url != ""').fetchone()[0]
    
    recent_schools = conn.execute('SELECT * FROM schools ORDER BY created_at DESC LIMIT 12').fetchall()
    
    from models import get_regions
    regions = get_regions()
    conn.close()
    
    return render_template('index.html',
                         total_schools=total_schools,
                         total_universities=total_universities,
                         total_with_badges=total_with_badges,
                         recent_schools=[dict(s) for s in recent_schools],
                         regions=regions,
                         page='home')

# ==========================================
# 排行榜页面
# ==========================================
@app.route('/rankings')
def rankings():
    from models import get_schools_paginated
    
    active_ranking = request.args.get('tab', 'qs')
    if active_ranking not in ['qs', 'usnews', 'the', 'arwu', 'cwur']:
        active_ranking = 'qs'
    
    ranking_systems = [
        {'id': 'qs', 'name': 'QS', 'year': 2026, 'color': '#10b981'},
        {'id': 'usnews', 'name': 'U.S. News', 'year': 2026, 'color': '#3b82f6'},
        {'id': 'the', 'name': 'THE', 'year': 2026, 'color': '#8b5cf6'},
        {'id': 'arwu', 'name': 'ARWU', 'year': 2025, 'color': '#ec4899'},
        {'id': 'cwur', 'name': 'CWUR', 'year': 2025, 'color': '#f59e0b'},
    ]
    
    rank_columns = {
        'qs': 'qs_rank', 'usnews': 'usnews_rank', 
        'the': 'the_rank', 'arwu': 'arwu_rank', 'cwur': 'cwur_rank'
    }
    
    conn = get_db_connection()
    ranking_counts = {}
    for col, name in [('qs_rank','qs'), ('usnews_rank','usnews'), ('the_rank','the'), 
                      ('arwu_rank','arwu'), ('cwur_rank','cwur')]:
        ranking_counts[name] = conn.execute(f'SELECT COUNT(*) FROM schools WHERE {col} IS NOT NULL').fetchone()[0]
    
    rank_col = rank_columns.get(active_ranking, 'qs_rank')
    schools = conn.execute(f'''
        SELECT * FROM schools 
        WHERE {rank_col} IS NOT NULL AND level = 'university'
        ORDER BY {rank_col}
        LIMIT 100
    ''').fetchall()
    
    # 处理排名数据
    schools_list = []
    for school in schools:
        school_dict = dict(school)
        rankings_list = []
        if school_dict.get('qs_rank'):
            rankings_list.append({'id': 'qs', 'name': 'QS', 'rank': school_dict['qs_rank']})
        if school_dict.get('usnews_rank'):
            rankings_list.append({'id': 'usnews', 'name': 'U.S. News', 'rank': school_dict['usnews_rank']})
        if school_dict.get('the_rank'):
            rankings_list.append({'id': 'the', 'name': 'THE', 'rank': school_dict['the_rank']})
        if school_dict.get('arwu_rank'):
            rankings_list.append({'id': 'arwu', 'name': 'ARWU', 'rank': school_dict['arwu_rank']})
        if school_dict.get('cwur_rank'):
            rankings_list.append({'id': 'cwur', 'name': 'CWUR', 'rank': school_dict['cwur_rank']})
        school_dict['rankings'] = rankings_list
        schools_list.append(school_dict)
    
    conn.close()
    
    return render_template('rankings.html',
                         rankings_config=ranking_systems,
                         ranking_counts=ranking_counts,
                         active_ranking=active_ranking,
                         top_schools=schools_list,
                         page='rankings')

# ==========================================
# 学校详情页
# ==========================================
@app.route('/school/<int:school_id>')
def school_detail(school_id):
    from models import get_school_by_id, get_school_rankings, get_like, get_likes_count
    
    school = get_school_by_id(school_id)
    if not school:
        return render_template('404.html'), 404
    
    rankings = get_school_rankings(school_id)
    liked = False
    likes_count = get_likes_count(school_id)
    
    if 'user_id' in session:
        like = get_like(session['user_id'], school_id)
        liked = like is not None
    
    badge_url = school.get('badge_url', '')
    if badge_url and not badge_url.startswith(('http://', 'https://')):
        badge_url = url_for('static', filename=f'images/{badge_url}')
    
    return render_template('school.html',
                         school=school,
                         rankings=rankings,
                         liked=liked,
                         likes_count=likes_count,
                         badge_url=badge_url)

# ==========================================
# 收藏功能
# ==========================================
@app.route('/like/<int:school_id>', methods=['POST'])
def toggle_like(school_id):
    from flask import jsonify
    from models import get_like, like_school, unlike_school, get_likes_count
    
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

# ==========================================
# 静态文件
# ==========================================
@app.route('/static/badges/<path:filename>')
def serve_badge(filename):
    from flask import send_from_directory
    return send_from_directory('static/badges', filename)

# ==========================================
# 健康检查
# ==========================================
@app.route('/health')
def health():
    return {'status': 'ok', 'app': 'school-badge-website'}

# ==========================================
# 错误处理
# ==========================================
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ==========================================
# 辅助函数
# ==========================================
def is_admin(user_id=None):
    """检查用户是否为管理员."""
    if user_id is None:
        user_id = session.get('user_id')
    if not user_id:
        return False
    from models import get_user_by_id
    user = get_user_by_id(user_id)
    return user and user.get('role') == 'admin'

# ==========================================
# 启动应用
# ==========================================
if __name__ == '__main__':
    print("=" * 50)
    print("校徽网启动中...")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)
