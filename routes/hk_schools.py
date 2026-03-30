"""
Hong Kong Schools Routes - 香港学校专区
"""
from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

hk_bp = Blueprint('hk', __name__)

def get_db_connection():
    conn = sqlite3.connect('/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@hk_bp.route('/hk')
def index():
    """香港学校专区首页"""
    conn = get_db_connection()
    
    # 获取查询参数
    selected_level = request.args.get('level', '')
    selected_district = request.args.get('district', '')
    selected_gender = request.args.get('gender', '')
    selected_finance = request.args.get('finance', '')
    
    # 构建查询
    query = "SELECT * FROM schools WHERE country = 'Hong Kong'"
    params = []
    
    if selected_level:
        if selected_level == 'university':
            query += " AND (level = 'university' OR school_type LIKE '%大学%' OR school_type LIKE '%学院%')"
        else:
            query += " AND level = ?"
            params.append(selected_level)
    
    if selected_district:
        query += " AND district = ?"
        params.append(selected_district)
    
    if selected_gender:
        query += " AND gender = ?"
        params.append(selected_gender)
    
    if selected_finance:
        query += " AND (finance_type LIKE ? OR school_type LIKE ?)"
        params.extend([f'%{selected_finance}%', f'%{selected_finance}%'])
    
    query += " ORDER BY name LIMIT 100"
    
    schools = conn.execute(query, params).fetchall()
    schools = [dict(row) for row in schools]
    
    # 获取所有区域
    districts = conn.execute(
        "SELECT DISTINCT district FROM schools WHERE country = 'Hong Kong' AND district IS NOT NULL AND district != '' ORDER BY district"
    ).fetchall()
    districts = [d['district'] for d in districts if d['district']]
    
    # 统计数据
    hk_stats = {
        'total': conn.execute("SELECT COUNT(*) FROM schools WHERE country = 'Hong Kong'").fetchone()[0],
        'with_badge': conn.execute("SELECT COUNT(*) FROM schools WHERE country = 'Hong Kong' AND badge_url IS NOT NULL AND badge_url != ''").fetchone()[0],
        'districts': len(districts)
    }
    
    conn.close()
    
    return render_template('hk_schools.html',
                         schools=schools,
                         districts=districts,
                         hk_stats=hk_stats,
                         selected_level=selected_level,
                         selected_district=selected_district,
                         selected_gender=selected_gender,
                         selected_finance=selected_finance)
