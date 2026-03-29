"""
Content Service - 内容置顶服务
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

class ContentService:
    """内容管理服务"""
    
    @staticmethod
    def pin_post(post_id: int, admin_id: int, position: int = 0, expire_days: int = None) -> bool:
        """置顶帖子"""
        conn = sqlite3.connect(get_db_path())
        
        expire_at = None
        if expire_days:
            from datetime import timedelta
            expire_at = (datetime.now() + timedelta(days=expire_days)).strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            conn.execute('''
                INSERT OR REPLACE INTO pinned_posts (post_id, pinned_by, pinned_at, expire_at, position)
                VALUES (?, ?, datetime('now'), ?, ?)
            ''', (post_id, admin_id, expire_at, position))
            conn.commit()
            success = True
        except:
            success = False
        
        conn.close()
        return success
    
    @staticmethod
    def unpin_post(post_id: int) -> bool:
        """取消置顶"""
        conn = sqlite3.connect(get_db_path())
        conn.execute('DELETE FROM pinned_posts WHERE post_id = ?', (post_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_pinned_posts() -> List[Dict]:
        """获取置顶帖子列表"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        posts = conn.execute('''
            SELECT p.*, pp.pinned_at, pp.position, pp.expire_at,
                   u.username as pinned_by_name
            FROM pinned_posts pp
            JOIN posts p ON pp.post_id = p.id
            JOIN users u ON pp.pinned_by = u.id
            WHERE pp.expire_at IS NULL OR pp.expire_at > datetime('now')
            ORDER BY pp.position ASC, pp.pinned_at DESC
        ''').fetchall()
        
        conn.close()
        return [dict(p) for p in posts]
    
    @staticmethod
    def is_pinned(post_id: int) -> bool:
        """检查帖子是否置顶"""
        conn = sqlite3.connect(get_db_path())
        result = conn.execute('''
            SELECT COUNT(*) FROM pinned_posts
            WHERE post_id = ? AND (expire_at IS NULL OR expire_at > datetime('now'))
        ''', (post_id,)).fetchone()[0]
        conn.close()
        return result > 0
    
    @staticmethod
    def get_pinned_count() -> int:
        """获取置顶数量"""
        conn = sqlite3.connect(get_db_path())
        count = conn.execute('''
            SELECT COUNT(*) FROM pinned_posts
            WHERE expire_at IS NULL OR expire_at > datetime('now')
        ''').fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def reorder_pins(post_ids: List[int]) -> bool:
        """重新排序置顶"""
        conn = sqlite3.connect(get_db_path())
        for i, post_id in enumerate(post_ids):
            conn.execute('UPDATE pinned_posts SET position = ? WHERE post_id = ?', (i, post_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def cleanup_expired_pins() -> int:
        """清理过期置顶"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.execute('''
            DELETE FROM pinned_posts WHERE expire_at < datetime('now')
        ''')
        conn.commit()
        conn.close()
        return cursor.rowcount


# 全局实例
content_service = ContentService()
