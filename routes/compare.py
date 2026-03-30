"""
学校对比功能路由
"""
from flask import Blueprint, render_template, request, jsonify, session
import sqlite3

compare_bp = Blueprint('compare', __name__)

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_school_basic(school_id):
    """获取学校基本信息"""
    conn = get_db_connection()
    school = conn.execute("""
        SELECT s.*, 
               (SELECT COUNT(*) FROM likes WHERE school_id = s.id) as likes_count
        FROM schools s
        WHERE s.id = ?
    """, (school_id,)).fetchone()
    conn.close()
    return dict(school) if school else None

def get_school_yearly_stats(school_id):
    """获取学校历年数据"""
    conn = get_db_connection()
    stats = conn.execute("""
        SELECT year, student_count, teacher_count, class_s1
        FROM school_yearly_stats
        WHERE school_id = ?
        ORDER BY year DESC
        LIMIT 3
    """, (school_id,)).fetchall()
    conn.close()
    return [dict(s) for s in stats]

@compare_bp.route('/compare')
def compare():
    """学校对比页面"""
    school1_id = request.args.get('s1', type=int)
    school2_id = request.args.get('s2', type=int)
    
    school1 = get_school_basic(school1_id) if school1_id else None
    school2 = get_school_basic(school2_id) if school2_id else None
    
    # 获取香港学校列表（用于选择）
    conn = get_db_connection()
    hk_schools = conn.execute("""
        SELECT id, name, name_cn, district, gender, finance_type
        FROM schools
        WHERE country = 'Hong Kong'
        ORDER BY district, name
        LIMIT 100
    """).fetchall()
    conn.close()
    
    return render_template('compare.html',
                         school1=school1,
                         school2=school2,
                         hk_schools=[dict(s) for s in hk_schools])

@compare_bp.route('/api/compare/<int:id1>/<int:id2>')
def api_compare(id1, id2):
    """对比两所学校"""
    school1 = get_school_basic(id1)
    school2 = get_school_basic(id2)
    
    if not school1 or not school2:
        return jsonify({'error': '学校不存在'}), 404
    
    # 获取历年数据
    stats1 = get_school_yearly_stats(id1)
    stats2 = get_school_yearly_stats(id2)
    
    return jsonify({
        'school1': school1,
        'school2': school2,
        'stats1': stats1,
        'stats2': stats2
    })

@compare_bp.route('/api/search-schools')
def search_schools():
    """搜索学校"""
    q = request.args.get('q', '')
    country = request.args.get('country', '')
    
    conn = get_db_connection()
    
    query = """
        SELECT id, name, name_cn, district, country, level, gender, finance_type
        FROM schools
        WHERE (name LIKE ? OR name_cn LIKE ?)
    """
    params = [f'%{q}%', f'%{q}%']
    
    if country:
        query += " AND country = ?"
        params.append(country)
    
    query += " ORDER BY name LIMIT 20"
    
    schools = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(s) for s in schools])
