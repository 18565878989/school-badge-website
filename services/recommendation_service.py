"""
Recommendation Service - 推荐算法服务
基于用户行为和内容特征的智能推荐
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

class RecommendationService:
    """推荐服务"""
    
    # 权重配置
    WEIGHTS = {
        'quality': 0.3,      # 内容质量
        'recency': 0.2,      # 时效性
        'popularity': 0.25,  # 热门程度
        'personal': 0.25     # 个性化匹配
    }
    
    @staticmethod
    def record_interaction(user_id: int, target_type: str, target_id: int, action_type: str, score: float = 1.0):
        """记录用户交互"""
        conn = sqlite3.connect(get_db_path())
        conn.execute('''
            INSERT INTO user_interactions (user_id, target_type, target_id, action_type, score, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        ''', (user_id, target_type, target_id, action_type, score))
        conn.commit()
        conn.close()
        
        # 更新内容热度
        RecommendationService.update_content_hot_score(target_type, target_id, action_type)
    
    @staticmethod
    def update_content_hot_score(target_type: str, target_id: int, action_type: str):
        """更新内容热度分"""
        if target_type != 'post':
            return
        
        conn = sqlite3.connect(get_db_path())
        
        # 计算热度：点赞*3 + 评论*5 + 浏览*1
        hot_score = 0
        if action_type == 'like':
            hot_score = 3
        elif action_type == 'comment':
            hot_score = 5
        elif action_type == 'view':
            hot_score = 1
        
        if hot_score > 0:
            conn.execute('''
                INSERT INTO content_features (post_id, hot_score, created_at)
                VALUES (?, COALESCE((SELECT hot_score FROM content_features WHERE post_id = ?), 0) + ?, datetime('now'))
                ON CONFLICT(post_id) DO UPDATE SET
                    hot_score = hot_score + ?
            ''', (target_id, target_id, hot_score, hot_score))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_preferences(user_id: int) -> Dict:
        """获取用户偏好"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        prefs = conn.execute('''
            SELECT * FROM user_preferences WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        if not prefs:
            # 初始化
            conn.execute('''
                INSERT INTO user_preferences (user_id, last_updated)
                VALUES (?, datetime('now'))
            ''', (user_id,))
            conn.commit()
            conn.close()
            return {'categories': [], 'keywords': []}
        
        # 解析历史交互
        interested = json.loads(prefs['interested_categories']) if prefs['interested_categories'] else []
        
        conn.close()
        return {'categories': interested}
    
    @staticmethod
    def update_user_preferences(user_id: int):
        """更新用户偏好"""
        conn = sqlite3.connect(get_db_path())
        
        # 获取用户最近交互的类别
        categories = conn.execute('''
            SELECT cf.category, COUNT(*) as cnt
            FROM user_interactions ui
            JOIN content_features cf ON ui.target_id = cf.post_id AND ui.target_type = 'post'
            WHERE ui.user_id = ? AND ui.created_at > datetime('now', '-7 days')
            GROUP BY cf.category
            ORDER BY cnt DESC
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        interested = [c['category'] for c in categories if c['category']]
        
        conn.execute('''
            UPDATE user_preferences
            SET interested_categories = ?, last_updated = datetime('now')
            WHERE user_id = ?
        ''', (json.dumps(interested), user_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def recommend_for_user(user_id: int, limit: int = 10, exclude_ids: List[int] = None) -> List[Dict]:
        """为用户推荐内容"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        # 排除已看过的
        exclude_clause = ""
        params = []
        if exclude_ids:
            placeholders = ','.join(['?'] * len(exclude_ids))
            exclude_clause = f"AND p.id NOT IN ({placeholders})"
            params.extend(exclude_ids)
        
        # 推荐算法：综合热度 + 质量 + 时效性
        query = f'''
            SELECT p.*,
                   COALESCE(cf.quality_score, 0.5) as quality_score,
                   COALESCE(cf.hot_score, 0) as hot_score,
                   u.username as author_name,
                   s.name as school_name,
                   (
                       COALESCE(cf.quality_score, 0.5) * ? +
                       (1 - MIN((julianday('now') - julianday(p.created_at)) / 7, 1)) * ? +
                       MIN(COALESCE(cf.hot_score, 0) / 100, 1) * ?
                   ) as recommendation_score
            FROM posts p
            LEFT JOIN content_features cf ON p.id = cf.post_id
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN schools s ON p.school_id = s.id
            WHERE p.status = 'published'
            AND p.created_at > datetime('now', '-30 days')
            {exclude_clause}
            ORDER BY recommendation_score DESC, p.created_at DESC
            LIMIT ?
        '''
        params.extend([
            RecommendationService.WEIGHTS['quality'],
            RecommendationService.WEIGHTS['recency'],
            RecommendationService.WEIGHTS['popularity'],
            limit
        ])
        
        recommendations = conn.execute(query, params).fetchall()
        
        conn.close()
        return [dict(r) for r in recommendations]
    
    @staticmethod
    def get_hot_posts(limit: int = 10, timeframe: str = 'day') -> List[Dict]:
        """获取热门帖子"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        # 时间范围
        time_map = {'day': '-1 day', 'week': '-7 days', 'month': '-30 days'}
        time_clause = time_map.get(timeframe, '-1 day')
        
        posts = conn.execute(f'''
            SELECT p.*,
                   COALESCE(cf.hot_score, 0) as hot_score,
                   u.username as author_name,
                   s.name as school_name,
                   (p.likes_count * 3 + p.comments_count * 5) as engagement
            FROM posts p
            LEFT JOIN content_features cf ON p.id = cf.post_id
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN schools s ON p.school_id = s.id
            WHERE p.status = 'published'
            AND p.created_at > datetime('now', ?)
            ORDER BY engagement DESC, hot_score DESC
            LIMIT ?
        ''', (time_clause, limit)).fetchall()
        
        conn.close()
        return [dict(p) for p in posts]
    
    @staticmethod
    def get_trending_topics(limit: int = 5) -> List[Dict]:
        """获取热门话题"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        topics = conn.execute('''
            SELECT t.*, COUNT(p.id) as post_count
            FROM post_topics t
            LEFT JOIN posts p ON t.id = p.topic_id AND p.created_at > datetime('now', '-7 days')
            GROUP BY t.id
            ORDER BY post_count DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        return [dict(t) for t in topics]


# 全局实例
recommendation_service = RecommendationService()
