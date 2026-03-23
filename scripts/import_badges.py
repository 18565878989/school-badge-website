#!/usr/bin/env python3
"""
导入校徽图片到数据库 - 增强版模糊匹配
"""
import os
import sqlite3
import shutil

# 配置
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
SOURCE_DIR = '/Users/wangfeng/Downloads/中国所有大学校徽图片-200px-jpgs'
BADGE_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/badges'

def get_core_name(name):
    """提取核心校名，去除常见后缀"""
    if not name:
        return ""
    name = name.replace(' ', '').replace('　', '')
    # 去除常见后缀
    suffixes = ['大学', '学院', '学校', '职业', '技术', '师范', '医科', '工业', '农业', 
                '工程', '科技', '工商', '财经', '政法', '交通', '航空', '航海', '体育',
                '艺术', '音乐', '美术', '师范', '外语', '外贸', '中医', '药科', '铁道',
                '电力', '石油', '化工', '建筑', '林业', '矿业', '水利', '气象', '测绘',
                '信息', '电子', '机械', '轻工', '纺织', '服装', '食品', '生物', '环境',
                '成人', '继续教育', '广播电视', '网络教育', '高职', '高专', '职工', '培训']
    
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    return name

def main():
    os.makedirs(BADGE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    image_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.jpg')]
    print(f"找到 {len(image_files)} 个校徽图片")
    
    # 获取所有学校
    cursor.execute("SELECT id, name, name_cn, badge_url FROM schools")
    all_schools = cursor.fetchall()
    
    # 构建索引
    schools_list = [(s[0], s[1], s[2], s[3]) for s in all_schools if s[2]]
    
    matched = 0
    skipped = 0
    
    for i, filename in enumerate(image_files):
        school_name = filename.replace('.jpg', '')
        core_name = get_core_name(school_name)
        
        best_match = None
        best_score = 0
        
        for school_id, name, name_cn, badge_url in schools_list:
            if badge_url and badge_url.strip():
                continue  # 跳过已有校徽的
            
            score = 0
            cn_core = get_core_name(name_cn) if name_cn else ""
            
            # 完全匹配
            if school_name == name_cn:
                score = 100
            # 核心名匹配
            elif core_name and cn_core and core_name == cn_core:
                score = 90
            # 包含匹配
            elif core_name and cn_core and (core_name in cn_core or cn_core in core_name):
                score = 80
            # 模糊：至少4个字相同
            elif len(core_name) >= 4 and len(cn_core) >= 4:
                common = set(core_name) & set(cn_core)
                if len(common) >= min(len(core_name), len(cn_core)) * 0.7:
                    score = 60
            
            if score > best_score:
                best_score = score
                best_match = (school_id, name_cn, badge_url)
        
        if best_match and best_score >= 60:
            school_id, name_cn, _ = best_match
            
            dest_filename = f"{school_id}.jpg"
            source_path = os.path.join(SOURCE_DIR, filename)
            dest_path = os.path.join(BADGE_DIR, dest_filename)
            
            try:
                shutil.copy2(source_path, dest_path)
                badge_url = f"/static/badges/{dest_filename}"
                
                cursor.execute("UPDATE schools SET badge_url = ? WHERE id = ?", (badge_url, school_id))
                matched += 1
                
                if matched % 50 == 0:
                    print(f"已匹配 {matched} 个...")
                    
            except Exception as e:
                print(f"失败 {filename}: {e}")
        else:
            skipped += 1
    
    conn.commit()
    
    # 统计
    cursor.execute("SELECT COUNT(*) FROM schools WHERE badge_url IS NOT NULL AND badge_url != ''")
    total_with_badge = cursor.fetchone()[0]
    
    print(f"\n导入完成!")
    print(f"新增匹配: {matched} 个")
    print(f"未匹配: {skipped} 个")
    print(f"数据库现有校徽总数: {total_with_badge}")
    
    conn.close()

if __name__ == '__main__':
    main()
