"""
school-import Skill - 批量导入学校数据
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database.db"

def validate_schools(schools):
    """验证学校数据格式"""
    required_fields = ["name", "country"]
    valid_levels = ["university", "middle", "elementary", "kindergarten"]
    
    valid = []
    errors = []
    
    for i, school in enumerate(schools):
        missing = [f for f in required_fields if f not in school]
        if missing:
            errors.append(f"Row {i}: missing {missing}")
            continue
        
        if school.get("level") and school["level"] not in valid_levels:
            errors.append(f"Row {i}: invalid level '{school['level']}'")
            continue
            
        valid.append(school)
    
    return valid, errors

def check_duplicates(schools):
    """检查重复数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    duplicates = []
    for school in schools:
        cursor.execute(
            "SELECT id FROM schools WHERE name = ? AND country = ?",
            (school["name"], school["country"])
        )
        if cursor.fetchone():
            duplicates.append(school["name"])
    
    conn.close()
    return duplicates

def import_schools(schools, imported_by="AI"):
    """导入学校数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    imported_count = 0
    
    for school in schools:
        cursor.execute("""
            INSERT INTO schools (
                name, name_cn, country, region, city, address,
                level, badge_url, website, motto, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            school.get("name"),
            school.get("name_cn"),
            school.get("country"),
            school.get("region", "Asia"),
            school.get("city"),
            school.get("address"),
            school.get("level", "university"),
            school.get("badge_url"),
            school.get("website"),
            school.get("motto"),
            now
        ))
        imported_count += 1
    
    conn.commit()
    conn.close()
    
    return imported_count

def run(file_path=None, dry_run=False):
    """运行导入"""
    if not file_path:
        return {"error": "请提供文件路径 --file"}
    
    # 读取数据
    with open(file_path, "r", encoding="utf-8") as f:
        schools = json.load(f)
    
    # 1. 验证
    valid, errors = validate_schools(schools)
    print(f"✓ 验证: {len(valid)}/{len(schools)} 有效")
    if errors:
        for e in errors[:5]:
            print(f"  ⚠ {e}")
    
    # 2. 去重检查
    duplicates = check_duplicates(valid)
    if duplicates:
        print(f"⚠ 发现 {len(duplicates)} 个重复: {duplicates[:3]}...")
        valid = [s for s in valid if s["name"] not in duplicates]
    
    # 3. 导入
    if dry_run:
        print(f"🔍 模拟模式: 将导入 {len(valid)} 所学校")
        return {"count": len(valid), "dry_run": True}
    
    count = import_schools(valid)
    print(f"✓ 成功导入 {count} 所学校")
    
    return {"count": count, "imported": True}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--file":
        run(sys.argv[2])
    else:
        print("Usage: python -m skills.school-import --file data.json")
