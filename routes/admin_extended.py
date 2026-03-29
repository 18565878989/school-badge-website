"""
Admin Extended Routes - 管理后台扩展路由
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os
import sqlite3
from functools import wraps

admin_ext_bp = Blueprint('admin_ext', __name__, url_prefix='/admin')

def log_admin_action(admin_id, action, target_type, target_id, details):
    """记录管理员操作日志"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO admin_logs (admin_id, action, target_type, target_id, details, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    ''', (admin_id, action, target_type, target_id, details))
    conn.commit()
    conn.close()

def admin_required(f):
    """管理员权限装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

@admin_ext_bp.route('/campus-images')
@admin_required
def campus_images():
    """校园图片管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取总数
    cursor.execute('SELECT COUNT(*) FROM schools WHERE badge_url IS NOT NULL AND badge_url != ""')
    total = cursor.fetchone()[0]
    
    conn.close()
    
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    return render_template('admin/campus_images.html', 
                         page=page, per_page=per_page, 
                         total=total, total_pages=total_pages)

@admin_ext_bp.route('/school/<int:school_id>/campus-edit', methods=['GET', 'POST'])
@admin_required
def campus_edit(school_id):
    """编辑校园图片"""
    if request.method == 'POST':
        # 处理上传
        return jsonify({'success': True})
    return render_template('admin/campus_edit.html', school_id=school_id)

@admin_ext_bp.route('/school/<int:school_id>/campus-approve')
@admin_required
def campus_approve(school_id):
    """批准校园图片"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE schools SET campus_reviewed=1, campus_reviewed_at=CURRENT_TIMESTAMP, campus_reviewed_by=? WHERE id=?',
                   (session['user_id'], school_id))
    conn.commit()
    
    log_admin_action(session['user_id'], 'APPROVE_CAMPUS', 'school', school_id, f'school_{school_id}')
    
    conn.close()
    return jsonify({'success': True, 'message': '校园图片已批准'})

@admin_ext_bp.route('/school/<int:school_id>/campus-reject')
@admin_required
def campus_reject(school_id):
    """拒绝校园图片"""
    reason = request.args.get('reason', '')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE schools SET campus_image="", campus_reviewed=0, campus_updated="Y" WHERE id=?', (school_id,))
    conn.commit()
    
    log_admin_action(session['user_id'], 'REJECT_CAMPUS', 'school', school_id, f'reason: {reason}')
    
    conn.close()
    return jsonify({'success': True, 'message': '校园图片已驳回'})

@admin_ext_bp.route('/school/<int:school_id>/campus-unapprove')
@admin_required
def campus_unapprove(school_id):
    """取消批准校园图片"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE schools SET campus_reviewed=0, campus_reviewed_by=NULL WHERE id=?', (school_id,))
    conn.commit()
    
    log_admin_action(session['user_id'], 'UNAPPROVE_CAMPUS', 'school', school_id, f'school_{school_id}')
    
    conn.close()
    return jsonify({'success': True, 'message': '已取消批准'})

@admin_ext_bp.route('/campus-images/batch-approve', methods=['POST'])
@admin_required
def batch_approve_campus():
    """批量批准校园图片"""
    data = request.get_json()
    ids = data.get('ids', [])
    
    if not ids:
        return jsonify({'success': False, 'message': '请选择要批准的图片'})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    approved = 0
    for sid in ids:
        cursor.execute('UPDATE schools SET campus_reviewed=1, campus_reviewed_at=CURRENT_TIMESTAMP, campus_reviewed_by=? WHERE id=? AND campus_image IS NOT NULL AND campus_image != ""',
                       (session['user_id'], sid))
        if cursor.rowcount > 0:
            approved += 1
            log_admin_action(session['user_id'], 'BATCH_APPROVE_CAMPUS', 'school', sid, f'school_{sid}')
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'approved': approved, 'message': f'已批准 {approved} 所学校的校园图片'})

@admin_ext_bp.route('/campus-images/batch-reject', methods=['POST'])
@admin_required
def batch_reject_campus():
    """批量驳回校园图片"""
    data = request.get_json()
    ids = data.get('ids', [])
    
    if not ids:
        return jsonify({'success': False, 'message': '请选择要驳回的图片'})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    rejected = 0
    for sid in ids:
        cursor.execute('UPDATE schools SET campus_image="", campus_reviewed=0, campus_updated="Y" WHERE id=?', (sid,))
        if cursor.rowcount > 0:
            rejected += 1
            log_admin_action(session['user_id'], 'BATCH_REJECT_CAMPUS', 'school', sid, f'school_{sid}')
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'rejected': rejected, 'message': f'已驳回 {rejected} 所学校的校园图片'})

@admin_ext_bp.route('/badge-images')
@admin_required
def badge_images():
    """校徽图片管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取总数
    cursor.execute('SELECT COUNT(*) FROM schools WHERE badge_url IS NOT NULL AND badge_url != ""')
    total = cursor.fetchone()[0]
    
    conn.close()
    
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    return render_template('admin/badge_images.html',
                         page=page, per_page=per_page,
                         total=total, total_pages=total_pages)

@admin_ext_bp.route('/school/<int:school_id>/badge-edit', methods=['GET', 'POST'])
@admin_required
def badge_edit(school_id):
    """编辑校徽图片"""
    if request.method == 'POST':
        return jsonify({'success': True})
    return render_template('admin/badge_edit.html', school_id=school_id)

@admin_ext_bp.route('/school/<int:school_id>/badge-approve')
@admin_required
def badge_approve(school_id):
    """批准校徽图片"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE schools SET badge_reviewed=1, badge_reviewed_at=CURRENT_TIMESTAMP, badge_reviewed_by=? WHERE id=?',
                   (session['user_id'], school_id))
    conn.commit()
    
    log_admin_action(session['user_id'], 'APPROVE_BADGE', 'school', school_id, f'school_{school_id}')
    
    conn.close()
    return jsonify({'success': True, 'message': '校徽已批准'})

@admin_ext_bp.route('/school/<int:school_id>/badge-reject')
@admin_required
def badge_reject(school_id):
    """拒绝校徽图片"""
    reason = request.args.get('reason', '')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE schools SET badge_url="", badge_reviewed=0, badge_updated="Y" WHERE id=?', (school_id,))
    conn.commit()
    
    log_admin_action(session['user_id'], 'REJECT_BADGE', 'school', school_id, f'reason: {reason}')
    
    conn.close()
    return jsonify({'success': True, 'message': '校徽已驳回'})

@admin_ext_bp.route('/school/<int:school_id>/badge-unapprove')
@admin_required
def badge_unapprove(school_id):
    """取消批准校徽图片"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE schools SET badge_reviewed=0, badge_reviewed_by=NULL WHERE id=?', (school_id,))
    conn.commit()
    
    log_admin_action(session['user_id'], 'UNAPPROVE_BADGE', 'school', school_id, f'school_{school_id}')
    
    conn.close()
    return jsonify({'success': True, 'message': '已取消批准'})

@admin_ext_bp.route('/badge-images/batch-approve', methods=['POST'])
@admin_required
def batch_approve_badge():
    """批量批准校徽图片"""
    data = request.get_json()
    ids = data.get('ids', [])
    
    if not ids:
        return jsonify({'success': False, 'message': '请选择要批准的图片'})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    approved = 0
    for sid in ids:
        cursor.execute('UPDATE schools SET badge_reviewed=1, badge_reviewed_at=CURRENT_TIMESTAMP, badge_reviewed_by=? WHERE id=? AND badge_url IS NOT NULL AND badge_url != ""',
                       (session['user_id'], sid))
        if cursor.rowcount > 0:
            approved += 1
            log_admin_action(session['user_id'], 'BATCH_APPROVE_BADGE', 'school', sid, f'school_{sid}')
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'approved': approved, 'message': f'已批准 {approved} 所学校的校徽'})

@admin_ext_bp.route('/badge-images/batch-reject', methods=['POST'])
@admin_required
def batch_reject_badge():
    """批量驳回校徽图片"""
    data = request.get_json()
    ids = data.get('ids', [])
    
    if not ids:
        return jsonify({'success': False, 'message': '请选择要驳回的图片'})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    rejected = 0
    for sid in ids:
        cursor.execute('UPDATE schools SET badge_url="", badge_reviewed=0, badge_updated="Y" WHERE id=?', (sid,))
        if cursor.rowcount > 0:
            rejected += 1
            log_admin_action(session['user_id'], 'BATCH_REJECT_BADGE', 'school', sid, f'school_{sid}')
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'rejected': rejected, 'message': f'已驳回 {rejected} 所学校的校徽'})

@admin_ext_bp.route('/badge-images/auto-review')
@admin_required
def auto_review_badges():
    """自动审核校徽 - 基于规则"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取所有待审核的校徽
    cursor.execute('''
        SELECT id, name, badge_url FROM schools 
        WHERE badge_url IS NOT NULL AND badge_url != "" AND badge_reviewed = 0
        LIMIT 100
    ''')
    pending = cursor.fetchall()
    
    auto_approved = 0
    auto_rejected = 0
    
    for school in pending:
        school_id, name, badge_url = school
        
        # 自动审核规则
        should_approve = True
        reason = ''
        
        # 规则1: 检查URL是否有效
        if not badge_url.startswith('http'):
            should_approve = False
            reason = '无效的URL格式'
        
        # 规则2: 检查是否是已知的图片托管服务
        valid_hosts = ['bing.com', 'google.com', 'schooland.hk', 'edb.gov.hk', 'cdn', 'images']
        if should_approve and not any(host in badge_url.lower() for host in valid_hosts):
            # 如果不是已知来源，标记为待人工审核
            continue
        
        # 规则3: 检查学校名称是否有效（非测试数据）
        test_patterns = ['test', 'Test', 'TEST', 'xxx', 'sample']
        if any(p in name for p in test_patterns):
            should_approve = False
            reason = '测试数据'
        
        if should_approve:
            cursor.execute('''
                UPDATE schools SET badge_reviewed=1, badge_reviewed_at=CURRENT_TIMESTAMP, badge_reviewed_by=?
                WHERE id=? AND badge_reviewed=0
            ''', (session['user_id'], school_id))
            if cursor.rowcount > 0:
                auto_approved += 1
                log_admin_action(session['user_id'], 'AUTO_APPROVE_BADGE', 'school', school_id, 'auto_review')
        else:
            cursor.execute('''
                UPDATE schools SET badge_url="", badge_reviewed=0, badge_updated="Y"
                WHERE id=?
            ''', (school_id,))
            auto_rejected += 1
            log_admin_action(session['user_id'], 'AUTO_REJECT_BADGE', 'school', school_id, reason)
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'auto_approved': auto_approved,
        'auto_rejected': auto_rejected,
        'pending': len(pending) - auto_approved - auto_rejected,
        'message': f'自动审核完成: 批准 {auto_approved}, 驳回 {auto_rejected}, 待审核 {len(pending) - auto_approved - auto_rejected}'
    })

@admin_ext_bp.route('/campus-images/auto-review')
@admin_required
def auto_review_campus():
    """自动审核校园图片 - 基于规则"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取所有待审核的校园图片
    cursor.execute('''
        SELECT id, name, campus_image FROM schools 
        WHERE campus_image IS NOT NULL AND campus_image != "" AND campus_reviewed = 0
        LIMIT 100
    ''')
    pending = cursor.fetchall()
    
    auto_approved = 0
    auto_rejected = 0
    
    for school in pending:
        school_id, name, campus_image = school
        
        # 自动审核规则
        should_approve = True
        reason = ''
        
        # 规则1: 检查URL是否有效
        if not campus_image.startswith('http'):
            should_approve = False
            reason = '无效的URL格式'
        
        # 规则2: 检查是否是已知的图片托管服务
        valid_hosts = ['bing.com', 'google.com', 'schooland.hk', 'edb.gov.hk', 'cdn', 'images', 'flickr', 'imgur']
        if should_approve and not any(host in campus_image.lower() for host in valid_hosts):
            continue
        
        if should_approve:
            cursor.execute('''
                UPDATE schools SET campus_reviewed=1, campus_reviewed_at=CURRENT_TIMESTAMP, campus_reviewed_by=?
                WHERE id=? AND campus_reviewed=0
            ''', (session['user_id'], school_id))
            if cursor.rowcount > 0:
                auto_approved += 1
                log_admin_action(session['user_id'], 'AUTO_APPROVE_CAMPUS', 'school', school_id, 'auto_review')
        else:
            cursor.execute('''
                UPDATE schools SET campus_image="", campus_reviewed=0, campus_updated="Y"
                WHERE id=?
            ''', (school_id,))
            auto_rejected += 1
            log_admin_action(session['user_id'], 'AUTO_REJECT_CAMPUS', 'school', school_id, reason)
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'auto_approved': auto_approved,
        'auto_rejected': auto_rejected,
        'pending': len(pending) - auto_approved - auto_rejected,
        'message': f'自动审核完成: 批准 {auto_approved}, 驳回 {auto_rejected}, 待审核 {len(pending) - auto_approved - auto_rejected}'
    })

def register_routes(app):
    """注册扩展管理路由"""
    app.register_blueprint(admin_ext_bp)

from functools import wraps
