"""
Analytics Service - 数据分析服务
提供页面访问统计、用户行为分析等功能
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AnalyticsService:
    """分析服务类"""
    
    @staticmethod
    def record_page_view(page_path: str, page_name: str = '', user_id: int = None, 
                         session_id: str = '', ip_address: str = '', 
                         user_agent: str = '', referer: str = ''):
        """记录页面访问"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # 检查是否已有当天的访问记录
        cursor.execute('''
            SELECT COUNT(*) FROM page_views 
            WHERE page_path = ? AND view_date = date('now') AND session_id = ?
        ''', (page_path, session_id))
        
        is_unique = 1 if cursor.fetchone()[0] == 0 else 0
        
        cursor.execute('''
            INSERT INTO page_views (page_path, page_name, user_id, session_id, 
                                   ip_address, user_agent, referer, view_date, is_unique)
            VALUES (?, ?, ?, ?, ?, ?, ?, date('now'), ?)
        ''', (page_path, page_name, user_id, session_id, ip_address, user_agent, referer, is_unique))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_daily_stats(days: int = 7) -> Dict:
        """获取每日统计数据"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # 获取最近N天的汇总
        cursor.execute('''
            SELECT stat_date, total_pv, total_uv, new_users, active_users
            FROM daily_stats
            WHERE stat_date >= date('now', '-' || ? || ' days')
            ORDER BY stat_date DESC
        ''', (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'date': r[0],
            'pv': r[1],
            'uv': r[2],
            'new_users': r[3],
            'active_users': r[4]
        } for r in rows]
    
    @staticmethod
    def get_page_views_stats(days: int = 7) -> List[Dict]:
        """获取页面访问统计"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT page_path, page_name, COUNT(*) as pv, 
                   COUNT(DISTINCT session_id) as uv
            FROM page_views
            WHERE view_date >= date('now', '-' || ? || ' days')
            GROUP BY page_path
            ORDER BY pv DESC
            LIMIT 10
        ''', (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'path': r[0],
            'name': r[1] or r[0],
            'pv': r[2],
            'uv': r[3]
        } for r in rows]
    
    @staticmethod
    def get_today_stats() -> Dict:
        """获取今日统计数据"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # 首先检查daily_stats表
        cursor.execute('''
            SELECT total_pv, total_uv, new_users, active_users, page_views_detail
            FROM daily_stats WHERE stat_date = date('now')
        ''')
        row = cursor.fetchone()
        
        if row:
            result = {
                'pv': row[0],
                'uv': row[1],
                'new_users': row[2],
                'active_users': row[3],
                'page_detail': row[4]
            }
            conn.close()
            return result
        
        # 如果没有数据，从page_views计算
        cursor.execute('''
            SELECT COUNT(*), COUNT(DISTINCT session_id)
            FROM page_views WHERE view_date = date('now')
        ''', )
        pv, uv = cursor.fetchone()
        
        # 获取新增用户
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE date(created_at) = date('now')
        ''')
        new_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'pv': pv or 0,
            'uv': uv or 0,
            'new_users': new_users,
            'active_users': uv or 0,
            'page_detail': None
        }
    
    @staticmethod
    def get_user_stats() -> Dict:
        """获取用户统计数据"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # 总用户数
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # 今日新增
        cursor.execute("SELECT COUNT(*) FROM users WHERE date(created_at) = date('now')")
        today_new = cursor.fetchone()[0]
        
        # 活跃用户（7天内有访问）
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM page_views 
            WHERE view_date >= date('now', '-7 days') AND user_id IS NOT NULL
        ''')
        active_7d = cursor.fetchone()[0]
        
        # 会员统计
        cursor.execute("SELECT COUNT(*) FROM users WHERE membership_tier = 'pro'")
        pro_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE membership_tier = 'basic'")
        basic_users = cursor.fetchone()[0]
        
        # 社交绑定用户
        cursor.execute("SELECT COUNT(*) FROM users WHERE oauth_provider IS NOT NULL AND oauth_provider != ''")
        oauth_users = cursor.fetchone()[0]
        
        # 封禁用户
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'banned'")
        banned_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total_users,
            'today_new': today_new,
            'active_7d': active_7d,
            'pro': pro_users,
            'basic': basic_users,
            'oauth': oauth_users,
            'banned': banned_users
        }
    
    @staticmethod
    def update_daily_stats():
        """更新每日统计数据（定时任务调用）"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        # 计算昨日PV/UV
        cursor.execute('''
            SELECT COUNT(*), COUNT(DISTINCT session_id)
            FROM page_views WHERE view_date = ?
        ''', (yesterday_str,))
        pv, uv = cursor.fetchone()
        
        # 计算新增用户
        cursor.execute('''
            SELECT COUNT(*) FROM users WHERE date(created_at) = ?
        ''', (yesterday_str,))
        new_users = cursor.fetchone()[0]
        
        # 活跃用户
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM page_views 
            WHERE view_date >= ? AND user_id IS NOT NULL
        ''', (yesterday_str,))
        active_users = cursor.fetchone()[0]
        
        # 页面详情
        cursor.execute('''
            SELECT page_name, COUNT(*) FROM page_views
            WHERE view_date = ?
            GROUP BY page_name
            ORDER BY COUNT(*) DESC
            LIMIT 5
        ''', (yesterday_str,))
        pages = dict(cursor.fetchall())
        
        # 更新或插入
        cursor.execute('''
            INSERT OR REPLACE INTO daily_stats 
            (stat_date, total_pv, total_uv, new_users, active_users, page_views_detail)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (yesterday_str, pv, uv, new_users, active_users, str(pages)))
        
        conn.commit()
        conn.close()


# 全局实例
analytics_service = AnalyticsService()
