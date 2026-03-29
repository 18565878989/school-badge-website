"""
Social API Routes - 社交API路由
基于统一的SocialService
"""
from flask import Blueprint, request, jsonify, session
from services.social_service import social_service

social_api_bp = Blueprint('social_api', __name__, url_prefix='/api/social')

def require_login():
    """检查登录"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    return None

# ============ Posts API ============

@social_api_bp.route('/posts', methods=['GET'])
def get_posts():
    """获取帖子列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    sort = request.args.get('sort', 'new')  # new | hot
    author_id = request.args.get('author_id', type=int)
    school_id = request.args.get('school_id', type=int)
    
    result = social_service.get_posts(
        page=page, limit=min(limit, 50),
        sort=sort, author_id=author_id, school_id=school_id
    )
    return jsonify({'success': True, **result})

@social_api_bp.route('/posts', methods=['POST'])
def create_post():
    """创建帖子"""
    auth = require_login()
    if auth: return auth
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    post_id = social_service.create_post(
        author_id=session['user_id'],
        content=content,
        content_type=data.get('content_type', 'text'),
        media_urls=data.get('media_urls'),
        school_id=data.get('school_id'),
        visibility=data.get('visibility', 'public'),
        tags=data.get('tags')
    )
    
    return jsonify({'success': True, 'post_id': post_id})

@social_api_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """获取帖子详情"""
    post = social_service.get_post(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # 检查当前用户是否点赞/收藏
    if 'user_id' in session:
        post['is_liked'] = social_service.is_liked(post_id, session['user_id'])
    
    return jsonify({'success': True, 'post': post})

@social_api_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """更新帖子"""
    auth = require_login()
    if auth: return auth
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    social_service.update_post(post_id, session['user_id'], content)
    return jsonify({'success': True})

@social_api_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """删除帖子"""
    auth = require_login()
    if auth: return auth
    
    social_service.delete_post(post_id, session['user_id'])
    return jsonify({'success': True})

# ============ Likes API ============

@social_api_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """点赞帖子"""
    auth = require_login()
    if auth: return auth
    
    success = social_service.like_post(post_id, session['user_id'])
    count = social_service.get_like_count(post_id)
    
    return jsonify({
        'success': True,
        'action': 'liked' if success else 'already_liked',
        'like_count': count
    })

@social_api_bp.route('/posts/<int:post_id>/like', methods=['DELETE'])
def unlike_post(post_id):
    """取消点赞"""
    auth = require_login()
    if auth: return auth
    
    social_service.unlike_post(post_id, session['user_id'])
    count = social_service.get_like_count(post_id)
    
    return jsonify({
        'success': True,
        'action': 'unliked',
        'like_count': count
    })

# ============ Collections API ============

@social_api_bp.route('/posts/<int:post_id>/collect', methods=['POST'])
def collect_post(post_id):
    """收藏帖子"""
    auth = require_login()
    if auth: return auth
    
    success = social_service.collect_post(post_id, session['user_id'])
    
    return jsonify({
        'success': True,
        'action': 'collected' if success else 'already_collected'
    })

@social_api_bp.route('/posts/<int:post_id>/collect', methods=['DELETE'])
def uncollect_post(post_id):
    """取消收藏"""
    auth = require_login()
    if auth: return auth
    
    social_service.uncollect_post(post_id, session['user_id'])
    return jsonify({'success': True, 'action': 'uncollected'})

@social_api_bp.route('/users/me/collections', methods=['GET'])
def get_my_collections():
    """获取我的收藏"""
    auth = require_login()
    if auth: return auth
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = social_service.get_user_collections(session['user_id'], page, limit)
    return jsonify({'success': True, **result})

# ============ Comments API ============

@social_api_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """获取评论列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = social_service.get_comments(post_id, page, min(limit, 50))
    return jsonify({'success': True, **result})

@social_api_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    """添加评论"""
    auth = require_login()
    if auth: return auth
    
    data = request.get_json()
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    comment_id = social_service.add_comment(
        post_id, session['user_id'], content, parent_id
    )
    
    # 发送通知
    post = social_service.get_post(post_id)
    if post and post['author_id'] != session['user_id']:
        social_service.create_notification(
            user_id=post['author_id'],
            notif_type='comment',
            source_type='post',
            source_id=post_id,
            title='新评论',
            content=f'有人评论了你的帖子'
        )
    
    return jsonify({'success': True, 'comment_id': comment_id})

@social_api_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """删除评论"""
    auth = require_login()
    if auth: return auth
    
    social_service.delete_comment(comment_id, session['user_id'])
    return jsonify({'success': True})

# ============ Follows API ============

@social_api_bp.route('/users/<int:user_id>/follow', methods=['POST'])
def follow_user(user_id):
    """关注用户"""
    auth = require_login()
    if auth: return auth
    
    success = social_service.follow_user(session['user_id'], user_id)
    
    if success:
        social_service.create_notification(
            user_id=user_id,
            notif_type='follow',
            source_type='user',
            source_id=session['user_id'],
            title='新粉丝',
            content='有人关注了你'
        )
    
    return jsonify({
        'success': True,
        'action': 'followed' if success else 'already_following'
    })

@social_api_bp.route('/users/<int:user_id>/follow', methods=['DELETE'])
def unfollow_user(user_id):
    """取消关注"""
    auth = require_login()
    if auth: return auth
    
    social_service.unfollow_user(session['user_id'], user_id)
    return jsonify({'success': True, 'action': 'unfollowed'})

@social_api_bp.route('/users/<int:user_id>/followers', methods=['GET'])
def get_followers(user_id):
    """获取粉丝列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = social_service.get_followers(user_id, page, min(limit, 50))
    
    # 检查当前用户是否关注
    if 'user_id' in session:
        for u in result['users']:
            u['is_following'] = social_service.is_following(session['user_id'], u['id'])
    
    return jsonify({'success': True, **result})

@social_api_bp.route('/users/<int:user_id>/followings', methods=['GET'])
def get_followings(user_id):
    """获取关注列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = social_service.get_followings(user_id, page, min(limit, 50))
    
    if 'user_id' in session:
        for u in result['users']:
            u['is_following'] = social_service.is_following(session['user_id'], u['id'])
    
    return jsonify({'success': True, **result})

# ============ Notifications API ============

@social_api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """获取通知列表"""
    auth = require_login()
    if auth: return auth
    
    notif_type = request.args.get('type')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    result = social_service.get_notifications(
        session['user_id'], notif_type, page, min(limit, 50)
    )
    
    # 获取未读数
    result['unread_count'] = social_service.get_unread_count(session['user_id'])
    
    return jsonify({'success': True, **result})

@social_api_bp.route('/notifications/read-all', methods=['POST'])
def mark_all_read():
    """标记所有通知已读"""
    auth = require_login()
    if auth: return auth
    
    count = social_service.mark_all_read(session['user_id'])
    return jsonify({'success': True, 'count': count})

@social_api_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
def mark_read(notif_id):
    """标记单条通知已读"""
    auth = require_login()
    if auth: return auth
    
    social_service.mark_notification_read(notif_id, session['user_id'])
    return jsonify({'success': True})

# ============ Reports API ============

@social_api_bp.route('/reports', methods=['POST'])
def report_content():
    """举报内容"""
    auth = require_login()
    if auth: return auth
    
    data = request.get_json()
    target_type = data.get('target_type')  # post | comment
    target_id = data.get('target_id')
    reason = data.get('reason', '')
    
    if not target_type or not target_id:
        return jsonify({'error': 'Missing parameters'}), 400
    
    report_id = social_service.report_content(
        session['user_id'], target_type, target_id, reason
    )
    
    return jsonify({'success': True, 'report_id': report_id})

# ============ Stats API ============

@social_api_bp.route('/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """获取用户社交统计"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    
    # 发帖数
    post_count = conn.execute(
        "SELECT COUNT(*) FROM posts WHERE author_id = ? AND status = 'published'",
        (user_id,)
    ).fetchone()[0]
    
    # 粉丝数
    follower_count = conn.execute(
        'SELECT COUNT(*) FROM follows WHERE following_id = ?',
        (user_id,)
    ).fetchone()[0]
    
    # 关注数
    following_count = conn.execute(
        'SELECT COUNT(*) FROM follows WHERE follower_id = ?',
        (user_id,)
    ).fetchone()[0]
    
    # 收藏数
    collection_count = conn.execute(
        'SELECT COUNT(*) FROM post_collections WHERE user_id = ?',
        (user_id,)
    ).fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'posts': post_count,
            'followers': follower_count,
            'following': following_count,
            'collections': collection_count
        }
    })

import sqlite3
import os

def get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
