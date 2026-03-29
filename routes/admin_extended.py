"""
Admin Extended Routes - 管理后台扩展路由
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os
import sqlite3

admin_ext_bp = Blueprint('admin_ext', __name__, url_prefix='/admin')

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
    return jsonify({'success': True})

@admin_ext_bp.route('/school/<int:school_id>/campus-reject')
@admin_required
def campus_reject(school_id):
    """拒绝校园图片"""
    return jsonify({'success': True})

@admin_ext_bp.route('/school/<int:school_id>/campus-unapprove')
@admin_required
def campus_unapprove(school_id):
    """取消批准校园图片"""
    return jsonify({'success': True})

@admin_ext_bp.route('/campus-images/batch-approve', methods=['POST'])
@admin_required
def batch_approve_campus():
    """批量批准校园图片"""
    data = request.get_json()
    ids = data.get('ids', [])
    return jsonify({'success': True, 'approved': len(ids)})

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
    return jsonify({'success': True})

@admin_ext_bp.route('/school/<int:school_id>/badge-reject')
@admin_required
def badge_reject(school_id):
    """拒绝校徽图片"""
    return jsonify({'success': True})

@admin_ext_bp.route('/school/<int:school_id>/badge-unapprove')
@admin_required
def badge_unapprove(school_id):
    """取消批准校徽图片"""
    return jsonify({'success': True})

@admin_ext_bp.route('/badge-images/batch-approve', methods=['POST'])
@admin_required
def batch_approve_badge():
    """批量批准校徽图片"""
    data = request.get_json()
    ids = data.get('ids', [])
    return jsonify({'success': True, 'approved': len(ids)})

def register_routes(app):
    """注册扩展管理路由"""
    app.register_blueprint(admin_ext_bp)

from functools import wraps
