#!/usr/bin/env python3
"""
清洗EDB数据，过滤掉非学校机构
改进版：更精确的过滤逻辑
"""

import sqlite3
from datetime import datetime

def should_remove(name):
    """判断是否应该移除该记录"""
    name_upper = name.upper()
    
    # 定义培训机构关键词
    training_keywords = [
        'EDUCATION CENTRE', 'EDUCATION CENTER',
        'TUTORIAL CENTRE', 'TUTORIAL SCHOOL',
        'LEARNING CENTRE', 'LEARNING CENTER',
        'ENGLISH INSTITUTE', 'ENGLISH ACADEMY',
        'MATHEMATICS CENTRE', 'MATHS CENTRE',
        'SCIENCE CENTRE',
    ]
    
    # 定义学校类型关键词（保留）
    school_keywords = [
        'SCHOOL',
        'COLLEGE',
        'ACADEMY',  # 保留，但如果是纯ACADEMY则需谨慎
        'UNIVERSITY',
        'KINDERGARTEN',
        'PRIMARY',
        'SECONDARY',
    ]
    
    # 检查是否为培训机构
    is_training = False
    for kw in training_keywords:
        if kw in name_upper:
            is_training = True
            break
    
    # 检查是否为学校
    is_school = False
    for kw in school_keywords:
        if kw in name_upper:
            is_school = True
            break
    
    # 特殊处理：某些包含ACADEMY的可能是学校
    if 'ACADEMY' in name_upper and not is_training:
        is_school = True
    
    # 如果是培训机构且不是学校，移除
    if is_training and not is_school:
        return True
    
    # 如果不是学校，移除
    if not is_school:
        return True
    
    return False

def clean_edb_data():
    """清洗EDB数据"""
    db_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("清洗EDB数据 - 改进版")
    print("=" * 70)
    
    # 统计清洗前
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source='edb'")
    before_total = cursor.fetchone()[0]
    print(f"\n清洗前 EDB学校: {before_total}")
    
    # 获取所有EDB学校
    cursor.execute("SELECT id, name FROM schools WHERE source='edb'")
    schools = cursor.fetchall()
    
    # 统计会被移除的
    to_remove = []
    for school_id, name in schools:
        if should_remove(name):
            to_remove.append((school_id, name))
    
    print(f"会被移除: {len(to_remove)} 所")
    
    print("\n会被移除的样本 (前15个):")
    for _, name in to_remove[:15]:
        print(f"  - {name}")
    
    print("\n保留的样本 (前15个):")
    kept = [s for s in schools if not should_remove(s[1])]
    for _, name in kept[:15]:
        print(f"  - {name}")
    
    # 确认移除
    print(f"\n确认移除 {len(to_remove)} 条记录? (y/n)", end=" ")
    # 自动执行
    for school_id, _ in to_remove:
        cursor.execute("DELETE FROM schools WHERE id=?", (school_id,))
    
    conn.commit()
    
    # 统计清洗后
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source='edb'")
    after_total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools")
    total_all = cursor.fetchone()[0]
    
    print(f"\n结果:")
    print(f"  移除: {before_total - after_total} 所")
    print(f"  保留EDB: {after_total} 所")
    print(f"  总学校数: {total_all} 所")
    
    # 级别分布
    print("\n保留学校的级别分布:")
    cursor.execute("SELECT level, COUNT(*) FROM schools WHERE source='edb' GROUP BY level ORDER BY COUNT(*) DESC")
    for level, cnt in cursor.fetchall():
        print(f"  {level}: {cnt}")
    
    conn.close()
    
    return before_total - after_total

if __name__ == '__main__':
    clean_edb_data()
