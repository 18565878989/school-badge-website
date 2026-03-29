"""
Social Service - 社交服务模块
统一的社交功能服务层
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

class SocialService:
    """社交服务类"""
    
    # ============ Posts ============
    
    @staticmethod
    def get_posts(page: int = 1, limit: int = 20, 
                  sort: str = 'new', author_id: int = None,
                  school_id: int = None, visibility: str = 'public') -> Dict:
        """
        获取帖子列表
        sort: new | hot | following
        """
        offset = (page - 1) * limit
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        where_clauses = ["p.status = 'published'"]
        params = []
        
        if author_id:
            where_clauses.append("p.author_id = ?")
            params.append(author_id)
        
        if school_id:
            where_clauses.append("p.school_id = ?")
            params.append(school_id)
        
        if visibility:
            where_clauses.append("p.visibility = ?")
            params.append(visibility)
        
        where_sql = " AND ".join(where_clauses)
        
        # 排序
        if sort == 'hot':
            order_by = "p.likes_count DESC, p.comments_count DESC, p.created_at DESC"
        elif sort == 'following' and author_id:
            order_by = "p.created_at DESC"
        else:
            order_by = "p.created_at DESC"
        
        # 获取总数
        total = conn.execute(
            f"SELECT COUNT(*) FROM posts p WHERE {where_sql}", params
        ).fetchone()[0]
        
        # 获取列表
        sql = f'''
            SELECT p.*, u.username as author_name, u.avatar_url as author_avatar,
                   s.name as school_name,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM post_comments WHERE post_id = p.id) as comment_count
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN schools s ON p.school_id = s.id
            WHERE {where_sql}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])
        
        posts = conn.execute(sql, params).fetchall()
        conn.close()
        
        return {
            'posts': [dict(p) for p in posts],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_post(post_id: int) -> Optional[Dict]:
        """获取单个帖子"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        post = conn.execute('''
            SELECT p.*, u.username as author_name, u.avatar_url as author_avatar,
                   s.name as school_name,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM post_comments WHERE post_id = p.id) as comment_count
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN schools s ON p.school_id = s.id
            WHERE p.id = ?
        ''', (post_id,)).fetchone()
        
        conn.close()
        return dict(post) if post else None
    
    @staticmethod
    def create_post(author_id: int, content: str, 
                    content_type: str = 'text', media_urls: str = None,
                    school_id: int = None, visibility: str = 'public',
                    tags: str = None) -> int:
        """创建帖子"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO posts (author_id, school_id, content_type, content, media_urls,
                             visibility, tags, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'published', datetime('now'))
        ''', (author_id, school_id, content_type, content, media_urls, visibility, tags))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return post_id
    
    @staticmethod
    def update_post(post_id: int, author_id: int, content: str) -> bool:
        """更新帖子"""
        conn = sqlite3.connect(get_db_path())
        conn.execute('''
            UPDATE posts SET content = ?, updated_at = datetime('now')
            WHERE id = ? AND author_id = ?
        ''', (content, post_id, author_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete_post(post_id: int, author_id: int = None) -> bool:
        """删除帖子"""
        conn = sqlite3.connect(get_db_path())
        if author_id:
            conn.execute('DELETE FROM posts WHERE id = ? AND author_id = ?', (post_id, author_id))
        else:
            conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return True
    
    # ============ Likes ============
    
    @staticmethod
    def like_post(post_id: int, user_id: int) -> bool:
        """点赞帖子"""
        conn = sqlite3.connect(get_db_path())
        try:
            conn.execute('''
                INSERT INTO post_likes (post_id, user_id, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (post_id, user_id))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False  # 已点赞
        conn.close()
        return success
    
    @staticmethod
    def unlike_post(post_id: int, user_id: int) -> bool:
        """取消点赞"""
        conn = sqlite3.connect(get_db_path())
        conn.execute(
            'DELETE FROM post_likes WHERE post_id = ? AND user_id = ?',
            (post_id, user_id)
        )
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def is_liked(post_id: int, user_id: int) -> bool:
        """检查是否已点赞"""
        conn = sqlite3.connect(get_db_path())
        result = conn.execute(
            'SELECT 1 FROM post_likes WHERE post_id = ? AND user_id = ?',
            (post_id, user_id)
        ).fetchone()
        conn.close()
        return result is not None
    
    @staticmethod
    def get_like_count(post_id: int) -> int:
        """获取点赞数"""
        conn = sqlite3.connect(get_db_path())
        count = conn.execute(
            'SELECT COUNT(*) FROM post_likes WHERE post_id = ?', (post_id,)
        ).fetchone()[0]
        conn.close()
        return count
    
    # ============ Collections ============
    
    @staticmethod
    def collect_post(post_id: int, user_id: int) -> bool:
        """收藏帖子"""
        conn = sqlite3.connect(get_db_path())
        try:
            conn.execute('''
                INSERT INTO post_collections (post_id, user_id, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (post_id, user_id))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        conn.close()
        return success
    
    @staticmethod
    def uncollect_post(post_id: int, user_id: int) -> bool:
        """取消收藏"""
        conn = sqlite3.connect(get_db_path())
        conn.execute(
            'DELETE FROM post_collections WHERE post_id = ? AND user_id = ?',
            (post_id, user_id)
        )
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_user_collections(user_id: int, page: int = 1, limit: int = 20) -> Dict:
        """获取用户收藏"""
        offset = (page - 1) * limit
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        total = conn.execute(
            'SELECT COUNT(*) FROM post_collections WHERE user_id = ?', (user_id,)
        ).fetchone()[0]
        
        posts = conn.execute('''
            SELECT p.*, u.username as author_name, pc.created_at as collected_at
            FROM post_collections pc
            JOIN posts p ON pc.post_id = p.id
            LEFT JOIN users u ON p.author_id = u.id
            WHERE pc.user_id = ?
            ORDER BY pc.created_at DESC
            LIMIT ? OFFSET ?
        ''', (user_id, limit, offset)).fetchall()
        
        conn.close()
        
        return {
            'posts': [dict(p) for p in posts],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    # ============ Comments ============
    
    @staticmethod
    def get_comments(post_id: int, page: int = 1, limit: int = 20) -> Dict:
        """获取评论列表"""
        offset = (page - 1) * limit
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        total = conn.execute(
            'SELECT COUNT(*) FROM post_comments WHERE post_id = ? AND is_approved = 1',
            (post_id,)
        ).fetchone()[0]
        
        comments = conn.execute('''
            SELECT c.*, u.username as author_name, u.avatar_url as author_avatar
            FROM post_comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.post_id = ? AND c.is_approved = 1
            ORDER BY c.created_at ASC
            LIMIT ? OFFSET ?
        ''', (post_id, limit, offset)).fetchall()
        
        conn.close()
        
        return {
            'comments': [dict(c) for c in comments],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def add_comment(post_id: int, user_id: int, content: str, 
                   parent_id: int = None) -> int:
        """添加评论"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO post_comments (post_id, user_id, content, parent_id, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (post_id, user_id, content, parent_id))
        
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return comment_id
    
    @staticmethod
    def delete_comment(comment_id: int, user_id: int = None) -> bool:
        """删除评论"""
        conn = sqlite3.connect(get_db_path())
        if user_id:
            conn.execute('DELETE FROM post_comments WHERE id = ? AND user_id = ?', 
                        (comment_id, user_id))
        else:
            conn.execute('DELETE FROM post_comments WHERE id = ?', (comment_id,))
        conn.commit()
        conn.close()
        return True
    
    # ============ Follows ============
    
    @staticmethod
    def follow_user(follower_id: int, following_id: int) -> bool:
        """关注用户"""
        if follower_id == following_id:
            return False
        
        conn = sqlite3.connect(get_db_path())
        try:
            conn.execute('''
                INSERT INTO follows (follower_id, following_id, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (follower_id, following_id))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        conn.close()
        return success
    
    @staticmethod
    def unfollow_user(follower_id: int, following_id: int) -> bool:
        """取消关注"""
        conn = sqlite3.connect(get_db_path())
        conn.execute(
            'DELETE FROM follows WHERE follower_id = ? AND following_id = ?',
            (follower_id, following_id)
        )
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def is_following(follower_id: int, following_id: int) -> bool:
        """检查是否关注"""
        conn = sqlite3.connect(get_db_path())
        result = conn.execute(
            'SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?',
            (follower_id, following_id)
        ).fetchone()
        conn.close()
        return result is not None
    
    @staticmethod
    def get_followers(user_id: int, page: int = 1, limit: int = 20) -> Dict:
        """获取粉丝列表"""
        offset = (page - 1) * limit
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        total = conn.execute(
            'SELECT COUNT(*) FROM follows WHERE following_id = ?', (user_id,)
        ).fetchone()[0]
        
        users = conn.execute('''
            SELECT u.id, u.username, u.avatar_url, u.membership_tier,
                   f.created_at as followed_at
            FROM follows f
            JOIN users u ON f.follower_id = u.id
            WHERE f.following_id = ?
            ORDER BY f.created_at DESC
            LIMIT ? OFFSET ?
        ''', (user_id, limit, offset)).fetchall()
        
        conn.close()
        
        return {
            'users': [dict(u) for u in users],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def get_followings(user_id: int, page: int = 1, limit: int = 20) -> Dict:
        """获取关注列表"""
        offset = (page - 1) * limit
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        total = conn.execute(
            'SELECT COUNT(*) FROM follows WHERE follower_id = ?', (user_id,)
        ).fetchone()[0]
        
        users = conn.execute('''
            SELECT u.id, u.username, u.avatar_url, u.membership_tier,
                   f.created_at as followed_at
            FROM follows f
            JOIN users u ON f.following_id = u.id
            WHERE f.follower_id = ?
            ORDER BY f.created_at DESC
            LIMIT ? OFFSET ?
        ''', (user_id, limit, offset)).fetchall()
        
        conn.close()
        
        return {
            'users': [dict(u) for u in users],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    # ============ Notifications ============
    
    @staticmethod
    def create_notification(user_id: int, notif_type: str,
                           source_type: str = None, source_id: int = None,
                           title: str = None, content: str = None) -> int:
        """创建通知"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (user_id, type, source_type, source_id, title, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (user_id, notif_type, source_type, source_id, title, content))
        
        notif_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return notif_id
    
    @staticmethod
    def get_notifications(user_id: int, notif_type: str = None,
                          page: int = 1, limit: int = 20) -> Dict:
        """获取通知列表"""
        offset = (page - 1) * limit
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        where_sql = "user_id = ?"
        params = [user_id]
        
        if notif_type:
            where_sql += " AND type = ?"
            params.append(notif_type)
        
        total = conn.execute(
            f"SELECT COUNT(*) FROM notifications WHERE {where_sql}", params
        ).fetchone()[0]
        
        notifications = conn.execute(f'''
            SELECT * FROM notifications
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (*params, limit, offset)).fetchall()
        
        conn.close()
        
        return {
            'notifications': [dict(n) for n in notifications],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def mark_notification_read(notif_id: int, user_id: int) -> bool:
        """标记通知已读"""
        conn = sqlite3.connect(get_db_path())
        conn.execute(
            'UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?',
            (notif_id, user_id)
        )
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def mark_all_read(user_id: int) -> int:
        """标记所有通知已读"""
        conn = sqlite3.connect(get_db_path())
        conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user_id,))
        count = conn.total_changes
        conn.commit()
        conn.close()
        return count
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """获取未读通知数"""
        conn = sqlite3.connect(get_db_path())
        count = conn.execute(
            'SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0',
            (user_id,)
        ).fetchone()[0]
        conn.close()
        return count
    
    # ============ Reports ============
    
    @staticmethod
    def report_content(reporter_id: int, target_type: str, target_id: int,
                      reason: str) -> int:
        """举报内容"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (reporter_id, target_type, target_id, reason, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', datetime('now'))
        ''', (reporter_id, target_type, target_id, reason))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return report_id
    
    @staticmethod
    def get_reports(status: str = 'pending', page: int = 1, limit: int = 20) -> Dict:
        """获取举报列表"""
        offset = (page - 1) * limit
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        total = conn.execute(
            'SELECT COUNT(*) FROM reports WHERE status = ?', (status,)
        ).fetchone()[0]
        
        reports = conn.execute('''
            SELECT r.*, u.username as reporter_name
            FROM reports r
            LEFT JOIN users u ON r.reporter_id = u.id
            WHERE r.status = ?
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        ''', (status, limit, offset)).fetchall()
        
        conn.close()
        
        return {
            'reports': [dict(r) for r in reports],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def handle_report(report_id: int, handler_id: int, action: str) -> bool:
        """处理举报"""
        conn = sqlite3.connect(get_db_path())
        
        if action == 'dismiss':
            conn.execute('UPDATE reports SET status = ?, handled_by = ?, handled_at = datetime("now") WHERE id = ?',
                        ('dismissed', handler_id, report_id))
        elif action == 'delete':
            conn.execute('UPDATE reports SET status = ?, handled_by = ?, handled_at = datetime("now") WHERE id = ?',
                        ('deleted', handler_id, report_id))
            # 获取举报信息
            report = conn.execute('SELECT * FROM reports WHERE id = ?', (report_id,)).fetchone()
            if report:
                if report['target_type'] == 'post':
                    conn.execute('DELETE FROM posts WHERE id = ?', (report['target_id'],))
                elif report['target_type'] == 'comment':
                    conn.execute('DELETE FROM post_comments WHERE id = ?', (report['target_id'],))
        
        conn.commit()
        conn.close()
        return True


# 全局实例
social_service = SocialService()
