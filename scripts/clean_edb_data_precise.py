#!/usr/bin/env python3
"""
清洗EDB数据 - 精确版
只移除真正的教育中心/培训机构
"""

import sqlite3
from datetime import datetime

def should_remove(name):
    """判断是否应该移除该记录"""
    name_upper = name.upper()
    
    # 定义培训机构关键词（完整匹配）
    training_patterns = [
        r'\bEDUCATION CENTRE\b',
        r'\bEDUCATION CENTER\b',
        r'\bTUTORIAL CENTRE\b',
        r'\bTUTORIAL SCHOOL\b',
        r'\bLEARNING CENTRE\b',
        r'\bLEARNING CENTER\b',
        r'\bENGLISH INSTITUTE\b',
        r'\bENGLISH ACADEMY\b',
        r'\bMATHEMATICS CENTRE\b',
        r'\bMATHS CENTRE\b',
        r'\bSCIENCE CENTRE\b',
    ]
    
    # 定义学校类型关键词（完整匹配）
    school_patterns = [
        r'\bSCHOOL\b',
        r'\bCOLLEGE\b',
        r'\bACADEMY\b',  # 保留
        r'\bUNIVERSITY\b',
        r'\bKINDERGARTEN\b',
        r'\bPRIMARY\b',
        r'\bSECONDARY\b',
    ]
    
    # 检查是否为培训机构
    is_training = any(re.search(p, name_upper) for p in training_patterns)
    
    # 检查是否为学校
    is_school = any(re.search(p, name_upper) for p in school_patterns)
    
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
    print("清洗EDB数据 - 精确版")
    print("=" * 70)
    
    # 统计清洗前
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source='edb'")
    before_total = cursor.fetchone()[0]
    print(f"\n清洗前 EDB学校: {before_total}")
    
    # 获取所有EDB学校
    cursor.execute("SELECT id, name, level FROM schools WHERE source='edb'")
    schools = cursor.fetchall()
    
    # 分类
    to_remove = []
    to_keep = []
    
    for school_id, name, level in schools:
        if should_remove(name):
            to_remove.append((school_id, name, level))
        else:
            to_keep.append((school_id, name, level))
    
    print(f"会移除: {len(to_remove)} 所")
    print(f"会保留: {len(to_keep)} 所")
    
    print("\n=== 会被移除的记录 (前20个) ===")
    for _, name, level in to_remove[:20]:
        print(f"  [{level:>10}] {name}")
    
    print("\n=== 会保留的记录 (前20个) ===")
    for _, name, level in to_keep[:20]:
        print(f"  [{level:>10}] {name}")
    
    # 检查是否有真正的学校被误删
    print("\n检查是否有真正的学校被误删...")
    false_positives = []
    for _, name, level in to_remove:
        # 如果包含SCHOOL或COLLEGE，可能是真正的学校
        if 'SCHOOL' in name.upper() or 'COLLEGE' in name.upper():
            false_positives.append((name, level))
    
    if false_positives:
        print(f"警告: 发现 {len(false_positives)} 个可能的误删:")
        for name, level in false_positives[:10]:
            print(f"  - {name} ({level})")
    else:
        print("✓ 没有发现误删")
    
    # 确认移除
    print(f"\n确认移除 {len(to_remove)} 条记录? (y/n)", end=" ")
    
    # 执行删除
    for school_id, _, _ in to_remove:
        cursor.execute("DELETE FROM schools WHERE id=?", (school_id,))
    
    conn.commit()
    
    # 统计清洗后
    cursor.execute("SELECT COUNT(*) FROM schools WHERE source='edb'")
    after_total = cursor.fetchone()[0]
    
    print(f"\n" + "=" * 70)
    print("结果:")
    print(f"  移除: {before_total - after_total} 所")
    print(f"  保留EDB: {after_total} 所")
    
    # 级别分布
    print("\n保留学校的级别分布:")
    cursor.execute("SELECT level, COUNT(*) FROM schools WHERE source='edb' GROUP BY level ORDER BY COUNT(*) DESC")
    for level, cnt in cursor.fetchall():
        print(f"  {level}: {cnt}")
    
    conn.close()

if __name__ == '__main__':
    import re
    clean_edb_data()
