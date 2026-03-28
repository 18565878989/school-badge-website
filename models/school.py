"""
School Model - 学校相关数据访问
"""
import sqlite3
import os

def get_db_connection():
    """获取数据库连接"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ============ 学校查询 ============

def get_all_schools():
    """获取所有学校"""
    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM schools ORDER BY name').fetchall()
    conn.close()
    return [dict(s) for s in schools]

def get_school_by_id(school_id):
    """根据ID获取学校"""
    conn = get_db_connection()
    school = conn.execute('SELECT * FROM schools WHERE id = ?', (school_id,)).fetchone()
    conn.close()
    return dict(school) if school else None

def get_schools_by_region(region):
    """根据地区获取学校"""
    conn = get_db_connection()
    schools = conn.execute(
        'SELECT * FROM schools WHERE region = ? ORDER BY name',
        (region,)
    ).fetchall()
    conn.close()
    return [dict(s) for s in schools]

def get_schools_by_level(level):
    """根据类型获取学校"""
    conn = get_db_connection()
    schools = conn.execute(
        'SELECT * FROM schools WHERE level = ? ORDER BY name',
        (level,)
    ).fetchall()
    conn.close()
    return [dict(s) for s in schools]

def get_schools_by_region_and_level(region, level):
    """根据地区和类型获取学校"""
    conn = get_db_connection()
    schools = conn.execute(
        'SELECT * FROM schools WHERE region = ? AND level = ? ORDER BY name',
        (region, level)
    ).fetchall()
    conn.close()
    return [dict(s) for s in schools]

def get_schools_paginated(page=1, per_page=48, region=None, level=None, search=None):
    """分页获取学校"""
    conn = get_db_connection()
    offset = (page - 1) * per_page
    
    query = 'SELECT * FROM schools WHERE 1=1'
    params = []
    
    if region:
        query += ' AND region = ?'
        params.append(region)
    if level:
        query += ' AND level = ?'
        params.append(level)
    if search:
        query += ' AND (name LIKE ? OR name_cn LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY name LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    schools = conn.execute(query, params).fetchall()
    
    # 获取总数
    count_query = 'SELECT COUNT(*) FROM schools WHERE 1=1'
    count_params = []
    if region:
        count_query += ' AND region = ?'
        count_params.append(region)
    if level:
        count_query += ' AND level = ?'
        count_params.append(level)
    if search:
        count_query += ' AND (name LIKE ? OR name_cn LIKE ?)'
        count_params.extend([f'%{search}%', f'%{search}%'])
    
    total = conn.execute(count_query, count_params).fetchone()[0]
    conn.close()
    
    return [dict(s) for s in schools], total

def search_schools(query, region=None, level=None):
    """搜索学校"""
    conn = get_db_connection()
    
    sql = 'SELECT * FROM schools WHERE (name LIKE ? OR name_cn LIKE ?)'
    params = [f'%{query}%', f'%{query}%']
    
    if region:
        sql += ' AND region = ?'
        params.append(region)
    if level:
        sql += ' AND level = ?'
        params.append(level)
    
    sql += ' ORDER BY name LIMIT 100'
    
    schools = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(s) for s in schools]

def get_regions():
    """获取所有地区"""
    conn = get_db_connection()
    regions = conn.execute('SELECT DISTINCT region FROM schools ORDER BY region').fetchall()
    conn.close()
    return [r['region'] for r in regions]

def get_region_stats():
    """获取各地区统计"""
    conn = get_db_connection()
    stats = conn.execute('''
        SELECT region, COUNT(*) as count 
        FROM schools 
        GROUP BY region 
        ORDER BY count DESC
    ''').fetchall()
    conn.close()
    return [dict(s) for s in stats]

def get_school_rankings(school_id):
    """获取学校排名信息"""
    school = get_school_by_id(school_id)
    if not school:
        return {}
    
    rankings = {}
    ranking_systems = ['qs', 'usnews', 'the', 'arwu', 'cwur']
    
    for system in ranking_systems:
        rank_key = f'{system}_rank'
        if school.get(rank_key):
            rankings[system] = {
                'rank': school[rank_key],
                'year': 2026 if system != 'cwur' else 2025
            }
    
    return rankings

# ============ 学校创建/更新/删除 ============

def create_school(name, region, country, city, level, **kwargs):
    """创建学校"""
    conn = get_db_connection()
    cursor = conn.execute('''
        INSERT INTO schools (name, region, country, city, level, 
                           name_cn, address, description, badge_url, website,
                           motto, founded, principal, source, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    ''', (
        name, region, country, city, level,
        kwargs.get('name_cn'),
        kwargs.get('address'),
        kwargs.get('description'),
        kwargs.get('badge_url'),
        kwargs.get('website'),
        kwargs.get('motto'),
        kwargs.get('founded'),
        kwargs.get('principal'),
        kwargs.get('source', 'manual')
    ))
    conn.commit()
    school_id = cursor.lastrowid
    conn.close()
    return school_id

def update_school(school_id, **kwargs):
    """更新学校"""
    conn = get_db_connection()
    
    fields = []
    values = []
    for key in ['name', 'name_cn', 'region', 'country', 'city', 'address', 
                'level', 'description', 'badge_url', 'website', 'motto', 
                'founded', 'principal', 'district', 'finance_type', 'gender',
                'session_type', 'supervisor', 'phone', 'fax', 'school_type',
                'source_school_id', 'source']:
        if key in kwargs:
            fields.append(f'{key} = ?')
            values.append(kwargs[key])
    
    if fields:
        fields.append('updated_at = datetime("now")')
        values.append(school_id)
        conn.execute(
            f'UPDATE schools SET {", ".join(fields)} WHERE id = ?',
            values
        )
        conn.commit()
    
    conn.close()

def delete_school(school_id):
    """删除学校"""
    conn = get_db_connection()
    conn.execute('DELETE FROM schools WHERE id = ?', (school_id,))
    conn.commit()
    conn.close()

# ============ 来源统计 ============

def get_schools_by_source(source):
    """根据来源获取学校"""
    conn = get_db_connection()
    schools = conn.execute(
        'SELECT * FROM schools WHERE source = ? ORDER BY name',
        (source,)
    ).fetchall()
    conn.close()
    return [dict(s) for s in schools]

def get_source_stats():
    """获取来源统计"""
    conn = get_db_connection()
    stats = conn.execute('''
        SELECT source, COUNT(*) as count 
        FROM schools 
        GROUP BY source 
        ORDER BY count DESC
    ''').fetchall()
    conn.close()
    return [dict(s) for s in stats]

def update_school_source(school_id, source):
    """更新学校来源"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE schools SET source = ?, updated_at = datetime("now") WHERE id = ?',
        (source, school_id)
    )
    conn.commit()
    conn.close()
