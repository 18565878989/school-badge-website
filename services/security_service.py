"""
Security Service - 校徽网安全加固服务
提供全面的Web应用安全防护
"""
import os
import re
import time
import hashlib
import hmac
import secrets
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from flask import request, session, jsonify, current_app

class SecurityService:
    """安全服务类"""
    
    # 密码策略
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # 登录限制
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_DURATION = 15 * 60  # 15分钟
    
    # 会话配置
    SESSION_LIFETIME = 24 * 60 * 60  # 24小时
    SESSION_refresh_TIME = 30 * 60  # 30分钟无活动刷新
    
    # API限流
    API_RATE_LIMIT = 100  # 每分钟请求数
    API_RATE_WINDOW = 60  # 时间窗口(秒)
    
    def __init__(self):
        self._login_attempts = {}  # 存储登录尝试记录
        self._api_usage = {}  # 存储API使用记录
        self._rate_limit_cache = {}  # 缓存IP访问记录
        
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        验证密码强度
        返回: (是否通过, 错误信息)
        """
        if len(password) < SecurityService.MIN_PASSWORD_LENGTH:
            return False, f"密码长度至少{SecurityService.MIN_PASSWORD_LENGTH}位"
        
        if len(password) > SecurityService.MAX_PASSWORD_LENGTH:
            return False, f"密码长度不能超过{SecurityService.MAX_PASSWORD_LENGTH}位"
        
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        strength_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if strength_score < 2:
            return False, "密码需包含字母和数字"
        
        # 检查常见弱密码
        weak_passwords = [
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'password123', 'admin123', 'letmein', 'welcome',
            'monkey', '1234567890', 'password1'
        ]
        if password.lower() in weak_passwords:
            return False, "密码太简单，请使用更复杂的密码"
        
        return True, ""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """生成安全的随机令牌"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """对令牌进行哈希存储"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def verify_csrf_token(token: str, salt: str = '') -> bool:
        """验证CSRF令牌"""
        if not token or not salt:
            return False
        
        expected = SecurityService._generate_csrf_token(salt)
        return hmac.compare_digest(token, expected)
    
    @staticmethod
    def _generate_csrf_token(salt: str) -> str:
        """生成CSRF令牌"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        return session.get('csrf_token', '')
    
    @staticmethod
    def generate_csrf_token() -> str:
        """获取或生成CSRF令牌"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        return session['csrf_token']
    
    def check_login_attempts(self, identifier: str) -> Tuple[bool, int]:
        """
        检查登录尝试次数
        返回: (是否允许尝试, 剩余锁定时间秒数)
        """
        now = time.time()
        if identifier in self._login_attempts:
            attempts, first_attempt = self._login_attempts[identifier]
            
            # 检查是否在锁定期间
            if now - first_attempt < self.LOGIN_LOCKOUT_DURATION:
                if attempts >= self.MAX_LOGIN_ATTEMPTS:
                    remaining = int(self.LOGIN_LOCKOUT_DURATION - (now - first_attempt))
                    return False, remaining
            
            # 清除过期的记录
            if now - first_attempt >= self.LOGIN_LOCKOUT_DURATION:
                del self._login_attempts[identifier]
        
        return True, 0
    
    def record_login_attempt(self, identifier: str, success: bool = False):
        """记录登录尝试"""
        if success:
            # 成功登录，清除记录
            if identifier in self._login_attempts:
                del self._login_attempts[identifier]
        else:
            now = time.time()
            if identifier in self._login_attempts:
                attempts, first_attempt = self._login_attempts[identifier]
                self._login_attempts[identifier] = (attempts + 1, first_attempt)
            else:
                self._login_attempts[identifier] = (1, now)
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """清理输入，防止XSS"""
        if not text:
            return ''
        
        # 移除危险的HTML标签
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # 限制长度
        text = text[:max_length]
        
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号格式（国际格式）"""
        pattern = r'^\+?[1-9]\d{6,14}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
    
    def check_api_rate_limit(self, identifier: str = None) -> Tuple[bool, int]:
        """
        检查API速率限制
        返回: (是否允许请求, 剩余请求数)
        """
        if identifier is None:
            identifier = request.remote_addr
        
        now = time.time()
        key = f"rate:{identifier}"
        
        if key not in self._rate_limit_cache:
            self._rate_limit_cache[key] = []
        
        # 清理过期的记录
        self._rate_limit_cache[key] = [
            t for t in self._rate_limit_cache[key]
            if now - t < self.API_RATE_WINDOW
        ]
        
        current_count = len(self._rate_limit_cache[key])
        
        if current_count >= self.API_RATE_LIMIT:
            return False, 0
        
        self._rate_limit_cache[key].append(now)
        return True, self.API_RATE_LIMIT - current_count - 1
    
    @staticmethod
    def get_client_ip() -> str:
        """获取客户端真实IP"""
        # 检查代理头
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        else:
            ip = request.remote_addr
        return ip
    
    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: List[str] = None) -> bool:
        """检查重定向URL是否安全"""
        if not url:
            return True
        
        if url.startswith('/'):
            return True
        
        if allowed_hosts is None:
            allowed_hosts = ['127.0.0.1', 'localhost']
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc in allowed_hosts
        except Exception:
            return False
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """生成安全的文件名"""
        import os
        
        # 获取扩展名
        ext = os.path.splitext(original_filename)[1].lower()
        
        # 白名单扩展名
        allowed_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        if ext not in allowed_exts:
            ext = '.txt'
        
        # 生成安全文件名
        timestamp = int(time.time())
        random_suffix = secrets.token_hex(4)
        safe_name = f"upload_{timestamp}_{random_suffix}{ext}"
        
        return safe_name


# 全局实例
security_service = SecurityService()


def csrf_protect(f):
    """CSRF保护装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            session_token = session.get('csrf_token', '')
            
            if not token or not security_service.verify_csrf_token(token, session_token):
                if request.is_json:
                    return jsonify({'error': 'CSRF token invalid'}), 403
                else:
                    return 'CSRF token invalid', 403
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(limit: int = None, per: int = 60):
    """速率限制装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = request.remote_addr
            allowed, remaining = security_service.check_api_rate_limit(identifier)
            
            if not allowed:
                if request.is_json:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'retry_after': per
                    }), 429
                else:
                    return 'Rate limit exceeded', 429
            
            response = f(*args, **kwargs)
            
            # 添加速率限制头
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Remaining'] = str(remaining)
            
            return response
        return decorated_function
    return decorator


def require_membership(*required_tiers):
    """会员等级要求装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Login required'}), 401
                else:
                    return redirect(url_for('auth.login'))
            
            # TODO: 从数据库检查用户会员等级
            user_tier = session.get('membership_tier', 'free')
            
            tier_hierarchy = {'free': 0, 'basic': 1, 'pro': 2}
            user_level = tier_hierarchy.get(user_tier, 0)
            
            for tier in required_tiers:
                required_level = tier_hierarchy.get(tier, 0)
                if user_level < required_level:
                    if request.is_json:
                        return jsonify({
                            'error': 'Membership required',
                            'required': tier
                        }), 403
                    else:
                        flash(f'需要{required_level}级别会员', 'warning')
                        return redirect(url_for('shop.membership'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
