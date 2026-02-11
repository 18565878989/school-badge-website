#!/usr/bin/env python3
"""
清洗EDB数据，过滤掉非学校机构
"""

import sqlite3
from datetime import datetime

def is_education_center(name):
    """检查是否为教育中心/培训机构"""
    keywords = [
        'EDUCATION CENTRE', 'EDUCATION CENTER',
        'TUTORIAL', 'TUTORING',
        'LEARNING CENTRE', 'LEARNING CENTER',
        'ENGLISH INSTITUTE',
        'MONTESSORI',  # 保留，但如果是INTERNATIONAL SCHOOL则保留
    ]
    
    name_upper = name.upper()
    
    # 检查关键词
    for kw in keywords:
        if kw in name_upper:
            # 特殊情况：如果是国际学校，保留
            if 'INTERNATIONAL SCHOOL' in name_upper:
                return False
            return True
    
    return False

def is_valid_school(name):
    """检查是否为有效的学校"""
    # 检查是否包含学校类型关键词
    school_types = [
        'SCHOOL',
        'COLLEGE',
        'ACADEMY',
        'INSTITUTE',
        'UNIVERSITY',
        'KINDERGARTEN',
        'PRIMARY',
        'SECONDARY',
    ]
    
    name_upper = name.upper()
    
    for st in school_types:
        if st in name_upper:
            return True
    
    return False

def clean_edb_data():
    """清洗EDB数据"""
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # 获取所有EDB学校
    cursor.execute("SELECT id, name, name_cn, level FROM schools WHERE source='edb'")
    schools = cursor.fetchall()
    
    print("=" * 70)
    print("清洗EDB数据")
    print("=" * 70)
    
    removed = 0
    kept = 0
    level_changed = 0
    
    # 统计移除前的级别分布
    before_levels = {}
    for _, _, _, level in schools:
        before_levels[level] = before_levels.get(level, 0) + 1
    
    print("\n清洗前级别分布:")
    for lvl, cnt in sorted(before_levels.items()):
        print(f"  {lvl}: {cnt}")
    
    # 处理每条记录
    for school_id, name, name_cn, level in schools:
        name_upper = name.upper()
        
        # 检查是否应该移除
        if is_education_center(name):
            # 标记为非学校（删除或标记）
            cursor.execute("DELETE FROM schools WHERE id=?", (school_id,))
            removed += 1
            continue
        
        # 检查是否为有效学校
        if not is_valid_school(name):
            cursor.execute("DELETE FROM schools WHERE id=?", (school_id,))
            removed += 1
            continue
        
        kept += 1
    
    conn.commit()
    
    # 统计清洗后的级别分布
    cursor.execute("SELECT level, COUNT(*) FROM schools WHERE source='edb' GROUP BY level")
    after_levels = dict(cursor.fetchall())
    
    print(f"\n清洗后级别分布:")
    for lvl, cnt in sorted(after_levels.items()):
        print(f"  {lvl}: {cnt}")
    
    # 总数
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source='edb'")
    total_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools")
    total_all = cursor.fetchone()[0]
    
    print(f"\n结果:")
    print(f"  移除: {removed} 所")
    print(f"  保留EDB: {total_after} 所")
    print(f"  总学校数: {total_all} 所")
    
    conn.close()
    
    return removed

if __name__ == '__main__':
    clean_edb_data()
