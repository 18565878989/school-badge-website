"""
User Service - 用户服务
用户积分、等级、成就、敏感词过滤
"""
import sqlite3
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

class UserService:
    """用户服务类"""
    
    # 积分配置
    POINTS_CONFIG = {
        'post': 10,           # 发帖
        'post_delete': -10,    # 删除帖
        'like_received': 2,    # 被点赞
        'like_given': 1,      # 点赞他人
        'comment': 5,          # 评论
        'comment_delete': -5,  # 删除评论
        'comment_received': 3, # 被评论
        'share': 3,           # 分享
        'daily_login': 5,      # 每日登录
        'first_post': 50,      # 首次发帖
        'report_handled': 20,  # 举报被处理
    }
    
    # 等级配置
    LEVEL_CONFIG = [
        (0, 1, '新手'),
        (100, 2, '入门'),
        (500, 3, '活跃'),
        (1000, 4, '达人'),
        (3000, 5, '专家'),
        (5000, 6, '大师'),
        (10000, 7, '传奇'),
    ]
    
    # 徽章配置
    BADGES_CONFIG = {
        'first_post': {'name': '初次发言', 'desc': '发布第一篇帖子'},
        'like_10': {'name': '赞不绝口', 'desc': '累计获得10个赞'},
        'like_100': {'name': '人气博主', 'desc': '累计获得100个赞'},
        'like_1000': {'name': '万众瞩目', 'desc': '累计获得1000个赞'},
        'post_10': {'name': '笔耕不辍', 'desc': '发布10篇帖子'},
        'post_100': {'name': '著作等身', 'desc': '发布100篇帖子'},
        'daily_7': {'name': '连续签到', 'desc': '连续签到7天'},
        'daily_30': {'name': '月签达人', 'desc': '连续签到30天'},
        'reporter': {'name': '纠错达人', 'desc': '成功举报10条违规内容'},
        'vip': {'name': 'VIP会员', 'desc': '升级为VIP会员'},
    }
    
    # ============ 敏感词过滤 ============
    
    @staticmethod
    def check_sensitive_words(content: str) -> Tuple[bool, List[str]]:
        """
        检查内容是否包含敏感词
        返回: (是否通过, 敏感词列表)
        """
        if not content:
            return True, []
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # 获取所有敏感词
        cursor.execute('SELECT word, level FROM sensitive_words')
        sensitive_words = cursor.fetchall()
        conn.close()
        
        found_words = []
        for word, level in sensitive_words:
            if word in content:
                found_words.append(word)
        
        return len(found_words) == 0, found_words
    
    @staticmethod
    def filter_sensitive_words(content: str, replacement: '***') -> str:
        """过滤敏感词"""
        if not content:
            return content
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('SELECT word FROM sensitive_words')
        sensitive_words = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        filtered = content
        for word in sensitive_words:
            filtered = re.sub(word, replacement, filtered)
        
        return filtered
    
    @staticmethod
    def add_sensitive_word(word: str, category: str = 'blocked', level: int = 1) -> bool:
        """添加敏感词"""
        try:
            conn = sqlite3.connect(get_db_path())
            conn.execute(
                'INSERT OR IGNORE INTO sensitive_words (word, category, level) VALUES (?, ?, ?)',
                (word, category, level)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    @staticmethod
    def get_sensitive_words(page: int = 1, limit: int = 50) -> Dict:
        """获取敏感词列表"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        offset = (page - 1) * limit
        total = conn.execute('SELECT COUNT(*) FROM sensitive_words').fetchone()[0]
        words = conn.execute(
            'SELECT * FROM sensitive_words ORDER BY id DESC LIMIT ? OFFSET ?',
            (limit, offset)
        ).fetchall()
        conn.close()
        
        return {
            'words': [dict(w) for w in words],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    # ============ 用户积分 ============
    
    @staticmethod
    def get_or_create_user_points(user_id: int) -> Dict:
        """获取或创建用户积分记录"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        user = conn.execute(
            'SELECT * FROM user_points WHERE user_id = ?', (user_id,)
        ).fetchone()
        
        if not user:
            conn.execute(
                'INSERT INTO user_points (user_id, points, level) VALUES (?, 0, 1)',
                (user_id,)
            )
            conn.commit()
            user = conn.execute(
                'SELECT * FROM user_points WHERE user_id = ?', (user_id,)
            ).fetchone()
        
        result = dict(user)
        conn.close()
        
        # 添加等级名称
        result['level_name'] = UserService.get_level_name(result['level'])
        
        return result
    
    @staticmethod
    def get_level_name(level: int) -> str:
        """获取等级名称"""
        for threshold, lvl, name in UserService.LEVEL_CONFIG:
            if level == lvl:
                return name
        return '新手'
    
    @staticmethod
    def add_points(user_id: int, action_type: str, description: str = None) -> Dict:
        """添加积分"""
        points_delta = UserService.POINTS_CONFIG.get(action_type, 0)
        if points_delta == 0:
            return UserService.get_or_create_user_points(user_id)
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # 获取当前积分
        cursor.execute('SELECT points, level FROM user_points WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            cursor.execute(
                'INSERT INTO user_points (user_id, points, level) VALUES (?, 0, 1)',
                (user_id,)
            )
            current_points = 0
            current_level = 1
        else:
            current_points = row[0]
            current_level = row[1]
        
        new_points = max(0, current_points + points_delta)
        
        # 检查是否升级
        new_level = current_level
        for threshold, lvl, name in reversed(UserService.LEVEL_CONFIG):
            if new_points >= threshold:
                new_level = lvl
                break
        
        # 更新积分
        cursor.execute('''
            UPDATE user_points 
            SET points = ?, level = ?,
                total_posts = total_posts + CASE WHEN ? = 'post' THEN 1 ELSE 0 END,
                total_likes = total_likes + CASE WHEN ? = 'like_received' THEN 1 ELSE 0 END,
                total_comments = total_comments + CASE WHEN ? = 'comment' THEN 1 ELSE 0 END,
                updated_at = datetime('now')
            WHERE user_id = ?
        ''', (new_points, new_level, action_type, action_type, action_type, user_id))
        
        # 记录积分日志
        cursor.execute('''
            INSERT INTO point_logs (user_id, action_type, points, description, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (user_id, action_type, points_delta, description))
        
        conn.commit()
        conn.close()
        
        # 检查获得新徽章
        UserService.check_and_award_badges(user_id)
        
        return UserService.get_or_create_user_points(user_id)
    
    @staticmethod
    def get_point_logs(user_id: int, page: int = 1, limit: int = 20) -> Dict:
        """获取积分日志"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        offset = (page - 1) * limit
        total = conn.execute(
            'SELECT COUNT(*) FROM point_logs WHERE user_id = ?', (user_id,)
        ).fetchone()[0]
        
        logs = conn.execute('''
            SELECT * FROM point_logs
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (user_id, limit, offset)).fetchall()
        
        conn.close()
        
        return {
            'logs': [dict(log) for log in logs],
            'total': total,
            'page': page
        }
    
    # ============ 用户徽章 ============
    
    @staticmethod
    def check_and_award_badges(user_id: int):
        """检查并授予徽章"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # 获取用户统计
        cursor.execute('SELECT points, total_posts, total_likes FROM user_points WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return
        
        points, total_posts, total_likes = row
        
        # 检查各徽章条件
        badges_to_award = []
        
        if total_posts >= 1:
            badges_to_award.append('first_post')
        if total_posts >= 10:
            badges_to_award.append('post_10')
        if total_posts >= 100:
            badges_to_award.append('post_100')
        if total_likes >= 10:
            badges_to_award.append('like_10')
        if total_likes >= 100:
            badges_to_award.append('like_100')
        if total_likes >= 1000:
            badges_to_award.append('like_1000')
        if points >= 1000:
            badges_to_award.append('reporter')
        
        # 授予徽章
        for badge_type in badges_to_award:
            try:
                cursor.execute('''
                    INSERT INTO user_badges (user_id, badge_type, badge_name, earned_at)
                    VALUES (?, ?, ?, datetime('now'))
                ''', (user_id, badge_type, UserService.BADGES_CONFIG[badge_type]['name']))
            except:
                pass  # 已拥有
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_badges(user_id: int) -> List[Dict]:
        """获取用户徽章"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        badges = conn.execute('''
            SELECT * FROM user_badges
            WHERE user_id = ?
            ORDER BY earned_at DESC
        ''', (user_id,)).fetchall()
        
        conn.close()
        
        return [dict(b) for b in badges]
    
    # ============ 用户禁言 ============
    
    @staticmethod
    def is_user_muted(user_id: int) -> Tuple[bool, Optional[str]]:
        """检查用户是否被禁言"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        cursor.execute(
            'SELECT mute_until FROM users WHERE id = ?', (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row and row['mute_until']:
            mute_until = datetime.strptime(row['mute_until'], '%Y-%m-%d %H:%M:%S')
            if mute_until > datetime.now():
                return True, row['mute_until']
        
        return False, None
    
    @staticmethod
    def mute_user(user_id: int, days: int = 7, reason: str = None) -> bool:
        """禁言用户"""
        from datetime import timedelta
        
        mute_until = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect(get_db_path())
        conn.execute(
            'UPDATE users SET mute_until = ?, mute_reason = ? WHERE id = ?',
            (mute_until, reason, user_id)
        )
        conn.commit()
        conn.close()
        
        return True
    
    @staticmethod
    def unmute_user(user_id: int) -> bool:
        """解除禁言"""
        conn = sqlite3.connect(get_db_path())
        conn.execute(
            'UPDATE users SET mute_until = NULL, mute_reason = NULL WHERE id = ?',
            (user_id,)
        )
        conn.commit()
        conn.close()
        
        return True
    
    # ============ 举报管理 ============
    
    @staticmethod
    def report_content(reporter_id: int, target_type: str, target_id: int, reason: str) -> int:
        """举报内容"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO content_reports (reporter_id, target_type, target_id, reason, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', datetime('now'))
        ''', (reporter_id, target_type, target_id, reason))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return report_id
    
    @staticmethod
    def get_pending_reports(page: int = 1, limit: int = 20) -> Dict:
        """获取待处理举报"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        offset = (page - 1) * limit
        total = conn.execute(
            "SELECT COUNT(*) FROM content_reports WHERE status = 'pending'"
        ).fetchone()[0]
        
        reports = conn.execute('''
            SELECT r.*, u.username as reporter_name
            FROM content_reports r
            LEFT JOIN users u ON r.reporter_id = u.id
            WHERE r.status = 'pending'
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()
        
        conn.close()
        
        return {
            'reports': [dict(r) for r in reports],
            'total': total,
            'page': page
        }
    
    @staticmethod
    def handle_report(report_id: int, handler_id: int, action: str) -> bool:
        """
        处理举报
        action: dismiss(驳回) / delete(删除内容) / mute(禁言用户)
        """
        conn = sqlite3.connect(get_db_path())
        
        if action == 'dismiss':
            conn.execute(
                "UPDATE content_reports SET status = 'dismissed', handle_by = ?, handle_result = 'dismissed' WHERE id = ?",
                (handler_id, report_id)
            )
        elif action == 'delete':
            conn.execute(
                "UPDATE content_reports SET status = 'deleted', handle_by = ?, handle_result = 'content_deleted' WHERE id = ?",
                (handler_id, report_id)
            )
            # 获取举报信息并删除内容
            report = conn.execute('SELECT * FROM content_reports WHERE id = ?', (report_id,)).fetchone()
            if report:
                if report['target_type'] == 'post':
                    conn.execute('DELETE FROM posts WHERE id = ?', (report['target_id'],))
                elif report['target_type'] == 'comment':
                    conn.execute('DELETE FROM post_comments WHERE id = ?', (report['target_id'],))
        elif action == 'mute':
            conn.execute(
                "UPDATE content_reports SET status = 'muted', handle_by = ?, handle_result = 'user_muted' WHERE id = ?",
                (handler_id, report_id)
            )
            # 获取举报信息并禁言用户
            # 需要根据 target_type 获取 user_id
        
        conn.commit()
        conn.close()
        
        return True


# 全局实例
user_service = UserService()
