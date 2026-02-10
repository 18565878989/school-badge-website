#!/usr/bin/env python3
"""
综合导入脚本 - 导入所有香港学校数据批次
"""

import json
import sqlite3
import os
import glob

DATA_DIR = 'data'
DB_FILE = 'database.db'

def create_badge_template(name, color_scheme="blue"):
    """生成学校SVG校徽模板"""
    
    colors = {
        'blue': {'primary': '#1a5fb4', 'secondary': '#3584e4'},
        'green': {'primary': '#26a269', 'secondary': '#4ac26b'},
        'red': {'primary': '#c01c28', 'secondary': '#e01b24'},
        'purple': {'primary': '#613583', 'secondary': '#813d9c'},
        'gold': {'primary': '#c64600', 'secondary': '#e66100'},
    }
    
    c = colors.get(color_scheme, colors['blue'])
    initial = name[0].upper() if name else 'S'
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c['primary']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{c['secondary']};stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="95" fill="url(#bg)" />
  <circle cx="100" cy="100" r="85" fill="none" stroke="white" stroke-width="3" opacity="0.3"/>
  <text x="100" y="115" font-family="Georgia, serif" font-size="80" font-weight="bold" fill="white" text-anchor="middle" opacity="0.95">{initial}</text>
  <circle cx="100" cy="100" r="90" fill="none" stroke="white" stroke-width="2" opacity="0.5"/>
</svg>'''
    
    return svg

def import_all_batches():
    """导入所有数据批次"""
    print("=" * 60)
    print("香港学校数据综合导入工具")
    print("=" * 60)
    
    # 查找所有JSON数据文件
    json_files = glob.glob(f'{DATA_DIR}/hk_schools*.json')
    print(f"\n找到 {len(json_files)} 个数据文件:")
    for f in json_files:
        print(f"  - {f}")
    
    all_schools = []
    
    # 读取所有数据文件
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                schools = data.get('schools', [])
                print(f"\n从 {os.path.basename(json_file)} 读取 {len(schools)} 所学校")
                all_schools.extend(schools)
        except Exception as e:
            print(f"  错误读取 {json_file}: {e}")
    
    print(f"\n总共准备导入 {len(all_schools)} 所学校")
    
    # 连接数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 获取当前最大ID
    cursor.execute('SELECT MAX(id) FROM schools')
    max_id = cursor.fetchone()[0] or 0
    print(f"当前数据库最大ID: {max_id}")
    
    # 统计
    imported = 0
    skipped = 0
    errors = []
    badge_count = 0
    
    for i, school in enumerate(all_schools):
        try:
            # 检查是否已存在
            cursor.execute(
                'SELECT id FROM schools WHERE name = ? AND level = ?',
                (school.get('name', ''), school.get('level', ''))
            )
            if cursor.fetchone():
                skipped += 1
                continue
            
            # 插入新学校
            cursor.execute('''
                INSERT INTO schools (
                    name, name_cn, region, country, city, address, level,
                    description, website, badge_url, motto, founded, principal
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school.get('name', ''),
                school.get('name_cn', ''),
                school.get('region', 'Hong Kong'),
                school.get('country', 'Hong Kong'),
                school.get('city', 'Hong Kong'),
                school.get('address', ''),
                school.get('level', 'middle'),
                school.get('description', ''),
                school.get('website', ''),
                school.get('badge_url', ''),
                school.get('motto', ''),
                school.get('founded', 0),
                school.get('principal', '')
            ))
            
            # 生成校徽（如果需要）
            if not school.get('badge_url'):
                badge_svg = create_badge_template(
                    school.get('name', ''),
                    'blue'
                )
                # 保存校徽文件
                safe_name = school.get('name', '').lower().replace(' ', '_').replace("'", "").replace("&", "and")
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')[:30]
                badge_path = f"static/images/{safe_name}.svg"
                
                with open(badge_path, 'w', encoding='utf-8') as bf:
                    bf.write(badge_svg)
                
                # 更新记录的badge_url
                cursor.execute(
                    'UPDATE schools SET badge_url = ? WHERE name = ? AND level = ?',
                    (badge_path, school.get('name', ''), school.get('level', ''))
                )
                badge_count += 1
            
            imported += 1
            print(f"  ✓ {school.get('name_cn')} ({school.get('name')})")
            
        except Exception as e:
            errors.append((school.get('name_cn', 'Unknown'), str(e)))
            print(f"  ✗ {school.get('name_cn')}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("导入完成!")
    print("=" * 60)
    print(f"成功导入: {imported} 所")
    print(f"已存在跳过: {skipped} 所")
    print(f"生成校徽: {badge_count} 个")
    print(f"错误: {len(errors)} 个")
    
    if errors:
        print("\n错误详情:")
        for name, error in errors[:5]:
            print(f"  - {name}: {error}")
    
    return imported

def verify_database():
    """验证数据库中的学校"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("数据库统计")
    print("=" * 60)
    
    # 按地区统计
    print("\n按地区统计:")
    cursor.execute("SELECT region, level, COUNT(*) FROM schools GROUP BY region, level ORDER BY region, level")
    for region, level, count in cursor.fetchall():
        print(f"  {region} - {level}: {count}所")
    
    # 香港学校统计
    print("\n香港学校统计:")
    cursor.execute("SELECT level, COUNT(*) FROM schools WHERE region = 'Hong Kong' GROUP BY level")
    for level, count in cursor.fetchall():
        print(f"  {level}: {count}所")
    
    cursor.execute('SELECT COUNT(*) FROM schools')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools WHERE region = "Hong Kong"')
    hk_total = cursor.fetchone()[0]
    
    print(f"\n学校总数: {total}所")
    print(f"香港学校: {hk_total}所")
    print(f"距离2000所还差: {2000 - hk_total}所")
    
    conn.close()
    return hk_total

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        verify_database()
    else:
        import_all_batches()
        print()
        verify_database()
