"""
升学资讯聚合路由
聚合香港升学相关的新闻、文章、视频等内容
"""
from flask import Blueprint, render_template, request, jsonify
import sqlite3
import re
from datetime import datetime, timedelta
import hashlib

news_bp = Blueprint('news', __name__)

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_news_table():
    """初始化资讯表"""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS school_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            title_cn TEXT,
            content TEXT,
            summary TEXT,
            source TEXT,
            source_url TEXT,
            category TEXT,
            tags TEXT,
            school_id INTEGER,
            region TEXT,
            image_url TEXT,
            published_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            view_count INTEGER DEFAULT 0,
            FOREIGN KEY (school_id) REFERENCES schools(id)
        )
    """)
    
    # 创建索引
    conn.execute("CREATE INDEX IF NOT EXISTS idx_news_category ON school_news(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_news_region ON school_news(region)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON school_news(published_at DESC)")
    
    conn.commit()
    conn.close()

@news_bp.route('/news')
def news_page():
    """升学资讯首页"""
    category = request.args.get('category', 'all')
    region = request.args.get('region', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    conn = get_db_connection()
    
    # 构建查询
    query = "SELECT * FROM school_news WHERE 1=1"
    count_query = "SELECT COUNT(*) FROM school_news WHERE 1=1"
    params = []
    
    if category != 'all':
        query += " AND category = ?"
        count_query += " AND category = ?"
        params.append(category)
    
    if region != 'all':
        query += " AND region = ?"
        count_query += " AND region = ?"
        params.append(region)
    
    # 获取总数
    total = conn.execute(count_query, params).fetchone()[0]
    
    # 分页
    offset = (page - 1) * per_page
    query += " ORDER BY published_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    
    news_list = conn.execute(query, params).fetchall()
    conn.close()
    
    # 获取分类统计
    conn = get_db_connection()
    categories = conn.execute("""
        SELECT category, COUNT(*) as count 
        FROM school_news 
        GROUP BY category
    """).fetchall()
    conn.close()
    
    return render_template('news.html',
                         news_list=[dict(n) for n in news_list],
                         categories=[dict(c) for c in categories],
                         total=total,
                         page=page,
                         per_page=per_page,
                         category=category,
                         region=region)

@news_bp.route('/news/<int:news_id>')
def news_detail(news_id):
    """资讯详情页"""
    conn = get_db_connection()
    
    # 获取资讯
    news = conn.execute("SELECT * FROM school_news WHERE id = ?", (news_id,)).fetchone()
    
    if not news:
        conn.close()
        return "资讯不存在", 404
    
    # 增加浏览数
    conn.execute("UPDATE school_news SET view_count = view_count + 1 WHERE id = ?", (news_id,))
    conn.commit()
    
    # 获取相关资讯
    related = conn.execute("""
        SELECT * FROM school_news 
        WHERE id != ? AND category = ?
        ORDER BY RANDOM()
        LIMIT 5
    """, (news_id, news['category'])).fetchall()
    
    conn.close()
    
    return render_template('news_detail.html',
                         news=dict(news),
                         related=[dict(r) for r in related])

@news_bp.route('/api/news')
def api_news():
    """获取资讯列表 API"""
    category = request.args.get('category', 'all')
    region = request.args.get('region', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    
    conn = get_db_connection()
    
    query = "SELECT * FROM school_news WHERE 1=1"
    params = []
    
    if category != 'all':
        query += " AND category = ?"
        params.append(category)
    if region != 'all':
        query += " AND region = ?"
        params.append(region)
    
    total = conn.execute("SELECT COUNT(*) FROM school_news WHERE 1=1" + 
                        (" AND category = ?" if category != 'all' else "") +
                        (" AND region = ?" if region != 'all' else ""), 
                        [c for c in [category if category != 'all' else None, region if region != 'all' else None] if c]).fetchone()[0]
    
    offset = (page - 1) * per_page
    query += " ORDER BY published_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    
    news_list = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify({
        'news': [dict(n) for n in news_list],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@news_bp.route('/api/news/latest')
def api_news_latest():
    """获取最新资讯"""
    conn = get_db_connection()
    latest = conn.execute("""
        SELECT * FROM school_news 
        ORDER BY published_at DESC 
        LIMIT 6
    """).fetchall()
    conn.close()
    
    return jsonify([dict(n) for n in latest])

@news_bp.route('/api/news/stats')
def api_news_stats():
    """获取资讯统计"""
    conn = get_db_connection()
    
    stats = {
        'total': conn.execute("SELECT COUNT(*) FROM school_news").fetchone()[0],
        'by_category': {},
        'by_source': {},
        'recent_count': conn.execute("""
            SELECT COUNT(*) FROM school_news 
            WHERE published_at > datetime('now', '-7 days')
        """).fetchone()[0]
    }
    
    for row in conn.execute("SELECT category, COUNT(*) as count FROM school_news GROUP BY category").fetchall():
        stats['by_category'][row['category']] = row['count']
    
    for row in conn.execute("SELECT source, COUNT(*) as count FROM school_news GROUP BY source").fetchall():
        stats['by_source'][row['source']] = row['count']
    
    conn.close()
    
    return jsonify(stats)

# 初始化数据库
init_news_table()

# 种子数据
def seed_sample_news():
    """添加示例资讯"""
    conn = get_db_connection()
    
    # 检查是否已有数据
    existing = conn.execute("SELECT COUNT(*) FROM school_news").fetchone()[0]
    if existing > 0:
        conn.close()
        return
    
    sample_news = [
        {
            'title': '2025年香港中学学位分配办法',
            'title_cn': '2025 Central Allocation Method for Hong Kong Secondary Schools',
            'content': '2025年度香港中学学位分配办法已经发布...',
            'summary': '教育局公布2025年中学学位分配办法详情',
            'source': '教育局',
            'category': 'policy',
            'region': 'Hong Kong',
            'tags': '升学,派位,中学',
            'published_at': datetime.now().isoformat()
        },
        {
            'title': '香港国际学校开放日一览',
            'title_cn': 'Hong Kong International Schools Open Days',
            'content': '各国际学校陆续公布2025年开放日安排...',
            'summary': '盘点香港主要国际学校开放日期',
            'source': '升学天地',
            'category': 'event',
            'region': 'Hong Kong',
            'tags': '国际学校,开放日',
            'published_at': (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            'title': 'Band 1中学排名及升学率分析',
            'title_cn': 'Band 1 Secondary Schools Ranking Analysis',
            'content': '根据最新数据，分析Band 1中学的升学率...',
            'summary': '深入分析Band 1中学升学情况',
            'source': 'SchoolAnd',
            'category': 'analysis',
            'region': 'Hong Kong',
            'tags': 'Band 1,排名,升学率',
            'published_at': (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            'title': '如何选择适合的中学',
            'title_cn': 'How to Choose the Right Secondary School',
            'content': '专家分享选校的关键考虑因素...',
            'summary': '资深教育专家分享选校建议',
            'source': '教育专家',
            'category': 'guide',
            'region': 'Hong Kong',
            'tags': '选校,建议',
            'published_at': (datetime.now() - timedelta(days=3)).isoformat()
        },
        {
            'title': '直资学校 vs 官津学校：如何选择',
            'title_cn': 'Direct Subsidy Scheme vs Government/Aided Schools',
            'content': '比较直资学校和官津学校的优劣...',
            'summary': '分析不同办学类型学校的特点',
            'source': '家长指南',
            'category': 'guide',
            'region': 'Hong Kong',
            'tags': '直资,官津,比较',
            'published_at': (datetime.now() - timedelta(days=4)).isoformat()
        },
        {
            'title': '2025年DSE考试时间表公布',
            'title_cn': '2025 DSE Exam Schedule Released',
            'content': '考评局公布2025年中学文凭试详情...',
            'summary': '2025年DSE考试日程安排',
            'source': '考评局',
            'category': 'exam',
            'region': 'Hong Kong',
            'tags': 'DSE,考试',
            'published_at': (datetime.now() - timedelta(days=5)).isoformat()
        }
    ]
    
    for news in sample_news:
        conn.execute("""
            INSERT INTO school_news (title, title_cn, content, summary, source, category, region, tags, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (news['title'], news['title_cn'], news['content'], news['summary'], 
              news['source'], news['category'], news['region'], news['tags'], news['published_at']))
    
    conn.commit()
    conn.close()
    print("✅ 资讯种子数据已添加")

# 运行种子数据
seed_sample_news()
