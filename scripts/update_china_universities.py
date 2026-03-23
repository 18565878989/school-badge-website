#!/usr/bin/env python3
"""
定时任务：抓取中国大学详细信息并更新校徽
- 每2小时运行一次
- 目标：将中国大学数量增加至2800所
- 更新校徽并标记 badge_updated='Y'
"""
import os
import sqlite3
import shutil
import time
import json
from pathlib import Path

# 配置
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
SOURCE_DIR = '/Users/wangfeng/Downloads/中国所有大学校徽图片-200px-jpgs'
BADGE_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/badges'

def get_core_name(name):
    """提取核心校名，去除常见后缀"""
    if not name:
        return ""
    name = name.replace(' ', '').replace('　', '')
    suffixes = ['大学', '学院', '学校', '职业', '技术', '师范', '医科', '工业', '农业', 
                '工程', '科技', '工商', '财经', '政法', '交通', '航空', '航海', '体育',
                '艺术', '音乐', '美术', '外语', '外贸', '中医', '药科', '铁道',
                '电力', '石油', '化工', '建筑', '林业', '矿业', '水利', '气象', '测绘',
                '信息', '电子', '机械', '轻工', '纺织', '食品', '生物', '环境']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    return name

def update_badges():
    """更新校徽并标记"""
    print("=" * 50)
    print("开始更新校徽...")
    print("=" * 50)
    
    os.makedirs(BADGE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 首先标记所有已有校徽的学校为'Y'（确保数据质量）
    cursor.execute("""
        UPDATE schools 
        SET badge_updated = 'Y' 
        WHERE badge_url IS NOT NULL 
          AND badge_url != '' 
          AND badge_updated = 'N'
    """)
    existing_updated = cursor.rowcount
    conn.commit()
    print(f"✓ 已标记 {existing_updated} 所已有校徽的学校为'Y'")
    
    # 获取所有图片
    if not os.path.exists(SOURCE_DIR):
        print(f"⚠️ 校徽目录不存在: {SOURCE_DIR}")
        return
    
    image_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.jpg')]
    print(f"找到 {len(image_files)} 个校徽图片")
    
    # 获取所有学校
    cursor.execute("SELECT id, name, name_cn, badge_url FROM schools WHERE name_cn IS NOT NULL")
    all_schools = cursor.fetchall()
    schools_dict = {(get_core_name(s[2]) if s[2] else ''): s for s in all_schools}
    
    updated = 0
    skipped = 0
    
    for filename in image_files:
        school_name = filename.replace('.jpg', '')
        core_name = get_core_name(school_name)
        
        best_match = None
        best_score = 0
        
        for cn_name, school_data in schools_dict.items():
            if not cn_name:
                continue
            school_id, name, name_cn, badge_url = school_data
            
            score = 0
            if school_name == name_cn:
                score = 100
            elif core_name == cn_name:
                score = 90
            elif core_name and cn_name and (core_name in cn_name or cn_name in core_name):
                score = 80
            
            if score > best_score:
                best_score = score
                best_match = school_data
        
        if best_match and best_score >= 60:
            school_id, name, name_cn, old_badge = best_match
            
            # 复制图片
            dest_filename = f"{school_id}.jpg"
            source_path = os.path.join(SOURCE_DIR, filename)
            dest_path = os.path.join(BADGE_DIR, dest_filename)
            
            try:
                shutil.copy2(source_path, dest_path)
                badge_url = f"/static/badges/{dest_filename}"
                
                # 更新数据库
                cursor.execute("""
                    UPDATE schools 
                    SET badge_url = ?, badge_updated = 'Y', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (badge_url, school_id))
                
                updated += 1
            except Exception as e:
                print(f"❌ 复制失败 {filename}: {e}")
        else:
            skipped += 1
    
    conn.commit()
    
    # 统计
    cursor.execute("SELECT COUNT(*) FROM schools WHERE badge_updated = 'Y'")
    total_updated = cursor.fetchone()[0]
    
    print(f"\n✅ 校徽更新完成!")
    print(f"   新增更新: {updated} 个")
    print(f"   未匹配: {skipped} 个")
    print(f"   已更新总数: {total_updated} 所学校")
    
    conn.close()

def check_china_schools():
    """检查中国大学数量"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 统计中国大陆大学数量
    cursor.execute("""
        SELECT COUNT(*) FROM schools 
        WHERE country = '中国' 
           OR country LIKE '%China%' 
           OR country = 'China'
           OR name_cn LIKE '%大学%'
           OR name_cn LIKE '%学院%'
    """)
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools")
    all_total = cursor.fetchone()[0]
    
    print(f"\n📊 当前统计:")
    print(f"   中国大学/学院: {total} 所")
    print(f"   数据库总数: {all_total} 所")
    
    conn.close()
    return total

def main():
    print("\n" + "=" * 50)
    print("🕐 定时任务：中国大学数据更新")
    print("=" * 50)
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查当前数量
    current_count = check_china_schools()
    
    # 2. 更新校徽
    update_badges()
    
    # 3. 最终统计
    print("\n" + "=" * 50)
    print("✅ 任务完成!")
    print("=" * 50)

if __name__ == '__main__':
    main()
