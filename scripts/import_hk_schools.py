#!/usr/bin/env python3
"""
香港学校数据导入工具
功能：
1. 从JSON文件导入学校数据
2. 生成SVG校徽模板
3. 更新数据库
"""

import json
import sqlite3
import os

# 配置文件
DATA_FILE = 'data/hk_schools_2024.json'
DB_FILE = 'database.db'

def create_badge_template(name, motto="", color_scheme="blue"):
    """生成学校SVG校徽模板"""
    
    # 根据学校类型选择颜色
    colors = {
        'blue': {'primary': '#1a5fb4', 'secondary': '#3584e4', 'bg': '#f8f9fa'},
        'green': {'primary': '#26a269', 'secondary': '#4ac26b', 'bg': '#f8f9fa'},
        'red': {'primary': '#c01c28', 'secondary': '#e01b24', 'bg': '#f8f9fa'},
        'purple': {'primary': '#613583', 'secondary': '#813d9c', 'bg': '#f8f9fa'},
    }
    
    c = colors.get(color_scheme, colors['blue'])
    
    # 获取学校名称的首字母
    initial = name[0].upper() if name else 'S'
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c['primary']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{c['secondary']};stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- 背景圆 -->
  <circle cx="100" cy="100" r="95" fill="url(#bg)" />
  <circle cx="100" cy="100" r="85" fill="none" stroke="white" stroke-width="3" opacity="0.3"/>
  
  <!-- 学校首字母 -->
  <text x="100" y="115" 
        font-family="Georgia, serif" 
        font-size="80" 
        font-weight="bold"
        fill="white" 
        text-anchor="middle"
        opacity="0.95">{initial}</text>
  
  <!-- 装饰边框 -->
  <circle cx="100" cy="100" r="90" fill="none" stroke="white" stroke-width="2" opacity="0.5"/>
  
  <!-- 顶部装饰 -->
  <path d="M60,30 Q100,10 140,30" fill="none" stroke="white" stroke-width="2" opacity="0.6"/>
</svg>'''
    
    return svg

def import_schools():
    """从JSON文件导入学校数据"""
    print("=" * 60)
    print("香港学校数据导入工具")
    print("=" * 60)
    
    # 检查数据文件
    if not os.path.exists(DATA_FILE):
        print(f"错误: 找不到数据文件 {DATA_FILE}")
        return
    
    # 读取数据
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    schools = data.get('schools', [])
    print(f"准备导入 {len(schools)} 所学校...")
    
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
    
    for i, school in enumerate(schools):
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
                    school.get('motto', ''),
                    'blue'
                )
                # 保存校徽文件
                safe_name = school.get('name', '').lower().replace(' ', '_').replace("'", "")
                badge_path = f"static/images/{safe_name[:30]}.svg"
                with open(badge_path, 'w', encoding='utf-8') as bf:
                    bf.write(badge_svg)
                
                # 更新记录的badge_url
                cursor.execute(
                    'UPDATE schools SET badge_url = ? WHERE name = ? AND level = ?',
                    (badge_path, school.get('name', ''), school.get('level', ''))
                )
            
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
    print(f"错误: {len(errors)} 个")
    
    if errors:
        print("\n错误详情:")
        for name, error in errors[:5]:
            print(f"  - {name}: {error}")
    
    return imported

def verify_database():
    """验证数据库中的香港学校"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 统计香港学校
    cursor.execute("SELECT level, COUNT(*) FROM schools WHERE region = 'Hong Kong' GROUP BY level")
    stats = cursor.fetchall()
    
    print("\n当前香港学校统计:")
    for level, count in stats:
        print(f"  {level}: {count}所")
    
    cursor.execute('SELECT COUNT(*) FROM schools WHERE region = "Hong Kong"')
    total = cursor.fetchone()[0]
    print(f"  总计: {total}所")
    
    conn.close()
    return total

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        verify_database()
    else:
        import_schools()
        print()
        verify_database()
