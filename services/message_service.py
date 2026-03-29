"""
Message Service - 私信服务
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

class MessageService:
    """私信服务"""
    
    @staticmethod
    def send_message(sender_id: int, receiver_id: int, content: str) -> int:
        """发送私信"""
        if sender_id == receiver_id:
            return -1
        
        # 检查对方是否接收私信
        # TODO: 可以添加黑名单功能
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO private_messages (sender_id, receiver_id, content, created_at)
            VALUES (?, ?, ?, datetime('now'))
        ''', (sender_id, receiver_id, content))
        
        message_id = cursor.lastrowid
        
        # 创建通知
        conn.execute('''
            INSERT INTO notifications (user_id, type, source_type, source_id, title, created_at)
            VALUES (?, 'message', 'private', ?, '收到新私信', datetime('now'))
        ''', (receiver_id, message_id))
        
        conn.commit()
        conn.close()
        
        return message_id
    
    @staticmethod
    def get_conversations(user_id: int, page: int = 1, limit: int = 20) -> Dict:
        """获取会话列表"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        offset = (page - 1) * limit
        
        # 获取与每个用户的最新一条消息
        conversations = conn.execute('''
            SELECT 
                CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END as partner_id,
                content,
                created_at,
                is_read,
                (SELECT COUNT(*) FROM private_messages 
                 WHERE sender_id = CASE WHEN p.sender_id = ? THEN p.receiver_id ELSE p.sender_id END
                 AND receiver_id = ? AND is_read = 0) as unread_count
            FROM (
                SELECT sender_id, receiver_id, content, is_read, created_at,
                       ROW_NUMBER() OVER (
                           PARTITION BY 
                               CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END
                           ORDER BY created_at DESC
                       ) as rn
                FROM private_messages
                WHERE sender_id = ? OR receiver_id = ?
            ) p
            WHERE rn = 1
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (user_id, user_id, user_id, user_id, user_id, user_id, limit, offset)).fetchall()
        
        # 获取每个会话的对方信息
        result = []
        for conv in conversations:
            partner = conn.execute(
                'SELECT id, username, email FROM users WHERE id = ?',
                (conv['partner_id'],)
            ).fetchone()
            
            if partner:
                result.append({
                    'partner_id': conv['partner_id'],
                    'partner_name': partner['username'],
                    'last_message': conv['content'],
                    'last_time': conv['created_at'],
                    'unread_count': conv['unread_count']
                })
        
        conn.close()
        return {'conversations': result}
    
    @staticmethod
    def get_messages(user_id: int, partner_id: int, page: int = 1, limit: int = 50) -> Dict:
        """获取与某用户的聊天记录"""
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        
        offset = (page - 1) * limit
        
        # 获取消息总数
        total = conn.execute('''
            SELECT COUNT(*) FROM private_messages
            WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ''', (user_id, partner_id, partner_id, user_id)).fetchone()[0]
        
        # 获取消息
        messages = conn.execute('''
            SELECT m.*, 
                   sender.username as sender_name,
                   receiver.username as receiver_name
            FROM private_messages m
            JOIN users sender ON m.sender_id = sender.id
            JOIN users receiver ON m.receiver_id = receiver.id
            WHERE (m.sender_id = ? AND m.receiver_id = ?) OR (m.sender_id = ? AND m.receiver_id = ?)
            ORDER BY m.created_at DESC
            LIMIT ? OFFSET ?
        ''', (user_id, partner_id, partner_id, user_id, limit, offset)).fetchall()
        
        # 标记已读
        conn.execute('''
            UPDATE private_messages SET is_read = 1
            WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
        ''', (partner_id, user_id))
        conn.commit()
        conn.close()
        
        return {
            'messages': [dict(m) for m in messages],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """获取未读消息数"""
        conn = sqlite3.connect(get_db_path())
        count = conn.execute('''
            SELECT COUNT(*) FROM private_messages
            WHERE receiver_id = ? AND is_read = 0
        ''', (user_id,)).fetchone()[0]
        conn.close()
        return count
    
    @staticmethod
    def mark_as_read(user_id: int, message_id: int) -> bool:
        """标记消息已读"""
        conn = sqlite3.connect(get_db_path())
        conn.execute('''
            UPDATE private_messages SET is_read = 1
            WHERE id = ? AND receiver_id = ?
        ''', (message_id, user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete_message(message_id: int, user_id: int) -> bool:
        """删除消息（只能删除自己发的）"""
        conn = sqlite3.connect(get_db_path())
        conn.execute('''
            DELETE FROM private_messages WHERE id = ? AND sender_id = ?
        ''', (message_id, user_id))
        conn.commit()
        conn.close()
        return True


# 全局实例
message_service = MessageService()
