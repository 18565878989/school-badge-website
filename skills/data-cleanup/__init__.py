"""
data-cleanup Skill - 数据清理与去重
"""
import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent.parent / "database.db"

def find_duplicates():
    """查找重复学校"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查找相同名称和国家的学校
    cursor.execute("""
        SELECT name, country, COUNT(*) as cnt
        FROM schools
        GROUP BY name, country
        HAVING cnt > 1
    """)
    
    duplicates = cursor.fetchall()
    conn.close()
    
    return duplicates

def remove_duplicates(keep_newer=True):
    """删除重复学校"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 找出重复的 ID
    cursor.execute("""
        SELECT name, country, GROUP_CONCAT(id) as ids
        FROM schools
        GROUP BY name, country
        HAVING COUNT(*) > 1
    """)
    
    deleted = 0
    for name, country, ids in cursor.fetchall():
        id_list = ids.split(",")
        # 保留第一个，删除其余
        to_keep = id_list[0]
        to_delete = id_list[1:]
        
        cursor.execute(f"DELETE FROM schools WHERE id IN ({','.join(to_delete)})")
        deleted += len(to_delete)
        print(f"✓ 删除重复: {name} ({country}) - 保留 ID {to_keep}")
    
    conn.commit()
    conn.close()
    
    return deleted

def fix_regions():
    """修复地区分类"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 亚洲国家列表
    asia_countries = [
        "China", "Japan", "South Korea", "North Korea", "India", "Pakistan",
        "Bangladesh", "Sri Lanka", "Nepal", "Bhutan", "Myanmar", "Thailand",
        "Vietnam", "Indonesia", "Philippines", "Malaysia", "Singapore", "Brunei",
        "Laos", "Cambodia", "Mongolia", "Kazakhstan", "Uzbekistan", "Kyrgyzstan",
        "Tajikistan", "Turkmenistan", "Afghanistan", "Iran", "Iraq", "Turkey",
        "Saudi Arabia", "UAE", "Qatar", "Kuwait", "Bahrain", "Oman", "Yemen",
        "Jordan", "Lebanon", "Syria", "Israel", "Palestine", "Georgia",
        "Armenia", "Azerbaijan", "Cyprus", "Taiwan", "Hong Kong", "Macau"
    ]
    
    fixed = 0
    for country in asia_countries:
        cursor.execute("""
            UPDATE schools 
            SET region = 'Asia' 
            WHERE country = ? AND region != 'Asia'
        """, (country,))
        fixed += cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return fixed

def analyze_data():
    """数据分析"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总数
    cursor.execute("SELECT COUNT(*) FROM schools")
    total = cursor.fetchone()[0]
    
    # 按地区
    cursor.execute("SELECT region, COUNT(*) FROM schools GROUP BY region")
    by_region = cursor.fetchall()
    
    # 按国家
    cursor.execute("SELECT country, COUNT(*) FROM schools GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10")
    by_country = cursor.fetchall()
    
    conn.close()
    
    return {
        "total": total,
        "by_region": by_region,
        "by_country": by_country
    }

def run(mode="analyze"):
    """运行清理"""
    if mode == "dedup":
        duplicates = find_duplicates()
        print(f"⚠ 发现 {len(duplicates)} 组重复学校")
        
        if duplicates:
            confirm = input("删除重复? (y/n): ")
            if confirm.lower() == "y":
                deleted = remove_duplicates()
                print(f"✓ 已删除 {deleted} 条重复记录")
        return {"duplicates": len(duplicates)}
    
    elif mode == "fix-region":
        fixed = fix_regions()
        print(f"✓ 已修复 {fixed} 条地区记录")
        return {"fixed": fixed}
    
    elif mode == "analyze":
        stats = analyze_data()
        print(f"\n📊 数据统计")
        print(f"  总数: {stats['total']} 所学校")
        print(f"\n  按地区:")
        for region, cnt in stats['by_region']:
            print(f"    {region}: {cnt}")
        print(f"\n  TOP 10 国家:")
        for country, cnt in stats['by_country']:
            print(f"    {country}: {cnt}")
        return stats
    
    else:
        return {"error": f"未知模式: {mode}"}

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    run(mode)
