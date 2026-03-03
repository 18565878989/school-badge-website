"""
stats-analyze Skill - 统计分析
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent / "database.db"

def get_comprehensive_stats():
    """获取全面统计数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stats = {}
    
    # 总数
    cursor.execute("SELECT COUNT(*) FROM schools")
    stats['total'] = cursor.fetchone()[0]
    
    # 按地区
    cursor.execute("SELECT region, COUNT(*) FROM schools GROUP BY region ORDER BY COUNT(*) DESC")
    stats['by_region'] = cursor.fetchall()
    
    # 按国家 TOP 20
    cursor.execute("SELECT country, COUNT(*) FROM schools GROUP BY country ORDER BY COUNT(*) DESC LIMIT 20")
    stats['by_country'] = cursor.fetchall()
    
    # 按类型
    cursor.execute("SELECT level, COUNT(*) FROM schools GROUP BY level ORDER BY COUNT(*) DESC")
    stats['by_level'] = cursor.fetchall()
    
    # 有校徽的
    cursor.execute("SELECT COUNT(*) FROM schools WHERE badge_url IS NOT NULL AND badge_url != ''")
    stats['with_badge'] = cursor.fetchone()[0]
    
    # 有网站的
    cursor.execute("SELECT COUNT(*) FROM schools WHERE website IS NOT NULL AND website != ''")
    stats['with_website'] = cursor.fetchone()[0]
    
    # 最近的添加
    cursor.execute("SELECT created_at, COUNT(*) FROM schools GROUP BY DATE(created_at) ORDER BY created_at DESC LIMIT 10")
    stats['recent'] = cursor.fetchall()
    
    conn.close()
    return stats

def generate_report():
    """生成报告"""
    stats = get_comprehensive_stats()
    
    report = f"""
╔════════════════════════════════════════════════════════════╗
║                  校徽网 - 数据统计报告                        ║
║                     {datetime.now().strftime('%Y-%m-%d')}                              ║
╠════════════════════════════════════════════════════════════╣
║  📊 总数据: {stats['total']:,} 所学校                                 
╠════════════════════════════════════════════════════════════╣
║  🌍 按地区:                                                 
"""
    
    for region, cnt in stats['by_region']:
        pct = cnt / stats['total'] * 100
        report += f"║    {region:15} {cnt:5,} ({pct:5.1f}%)\n"
    
    report += f"""╠════════════════════════════════════════════════════════════╣
║  🏫 按类型:                                                 
"""
    
    for level, cnt in stats['by_level']:
        report += f"║    {level:15} {cnt:5,}\n"
    
    report += f"""╠════════════════════════════════════════════════════════════╣
║  🏆 TOP 10 国家:                                          
"""
    
    for i, (country, cnt) in enumerate(stats['by_country'][:10], 1):
        report += f"║    {i:2}. {country:20} {cnt:5,}\n"
    
    report += f"""╠════════════════════════════════════════════════════════════╣
║  ✓ 有校徽: {stats['with_badge']:,} ({stats['with_badge']/stats['total']*100:.1f}%)                              
║  🌐 有网站: {stats['with_website']:,} ({stats['with_website']/stats['total']*100:.1f}%)                              
╚════════════════════════════════════════════════════════════╝
"""
    
    return report, stats

def run():
    """运行统计"""
    report, stats = generate_report()
    print(report)
    return stats

if __name__ == "__main__":
    run()
