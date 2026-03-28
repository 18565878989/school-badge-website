"""
Integration Tests - 集成测试
测试完整的用户流程
"""
import pytest
import sqlite3
import os

# 测试配置
TEST_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

@pytest.fixture(scope='module')
def app():
    """获取Flask应用"""
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def db():
    """获取测试数据库连接"""
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

# ============ 首页集成测试 ============

class TestHomepageIntegration:
    """首页集成测试"""
    
    def test_homepage_loads(self, app):
        """首页能正常加载"""
        response = app.get('/')
        assert response.status_code == 200
    
    def test_homepage_has_schools(self, app):
        """首页显示学校数据"""
        response = app.get('/')
        assert b'schools' in response.data or b'School' in response.data
    
    def test_homepage_search(self, app):
        """首页搜索功能"""
        response = app.get('/?q=Harvard')
        assert response.status_code == 200
    
    def test_homepage_region_filter(self, app):
        """首页地区筛选"""
        response = app.get('/?region=Asia')
        assert response.status_code == 200
    
    def test_homepage_pagination(self, app):
        """首页分页"""
        response = app.get('/?page=1')
        assert response.status_code == 200

# ============ 学校详情集成测试 ============

class TestSchoolDetailIntegration:
    """学校详情集成测试"""
    
    def test_school_detail_valid(self, app, db):
        """学校详情页"""
        # 获取一个有效的学校ID
        school = db.execute('SELECT id FROM schools LIMIT 1').fetchone()
        if school:
            response = app.get(f'/school/{school["id"]}')
            assert response.status_code == 200
    
    def test_school_detail_invalid(self, app):
        """无效学校ID"""
        response = app.get('/school/99999999')
        assert response.status_code in [404, 302]

# ============ 认证集成测试 ============

class TestAuthIntegration:
    """认证集成测试"""
    
    def test_login_page(self, app):
        """登录页面"""
        response = app.get('/login')
        assert response.status_code == 200
    
    def test_register_page(self, app):
        """注册页面"""
        response = app.get('/register')
        assert response.status_code == 200
    
    def test_logout_redirects(self, app):
        """登出跳转"""
        response = app.get('/logout', follow_redirects=True)
        assert response.status_code == 200

# ============ 管理后台集成测试 ============

class TestAdminIntegration:
    """管理后台集成测试"""
    
    def test_admin_requires_login(self, app):
        """管理后台需要登录"""
        response = app.get('/admin')
        # 未登录应该跳转
        assert response.status_code in [302, 401]
    
    def test_admin_access_with_session(self, app):
        """管理后台会话访问"""
        with app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'test'
            sess['role'] = 'admin'
        
        response = app.get('/admin')
        assert response.status_code == 200

# ============ API集成测试 ============

class TestAPIIntegration:
    """API集成测试"""
    
    def test_api_share_config(self, app):
        """分享配置API"""
        response = app.get('/api/share/config')
        assert response.status_code == 200
    
    def test_api_posts(self, app):
        """帖子API"""
        response = app.get('/api/posts')
        assert response.status_code == 200
    
    def test_api_regions(self, app):
        """地区API"""
        response = app.get('/api/schools/regions')
        assert response.status_code == 200

# ============ 排行榜集成测试 ============

class TestRankingsIntegration:
    """排行榜集成测试"""
    
    def test_rankings_page(self, app):
        """排行榜页面"""
        response = app.get('/rankings')
        assert response.status_code == 200
    
    def test_rankings_qs_tab(self, app):
        """QS排名标签"""
        response = app.get('/rankings?tab=qs')
        assert response.status_code == 200

# ============ 点赞功能集成测试 ============

class TestLikeIntegration:
    """点赞功能集成测试"""
    
    def test_like_requires_auth(self, app):
        """点赞需要认证"""
        response = app.post('/like/1')
        # 未登录返回JSON错误
        assert response.status_code == 401 or response.status_code == 302
    
    def test_like_with_session(self, app, db):
        """带会话的点赞"""
        with app.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'test'
        
        # 点赞时应该返回JSON
        response = app.post('/like/1', follow_redirects=True)
        assert response.status_code == 200

# ============ 国际化集成测试 ============

class TestI18nIntegration:
    """国际化集成测试"""
    
    def test_language_switch_en(self, app):
        """切换到英语"""
        response = app.get('/lang/en', follow_redirects=True)
        assert response.status_code == 200
    
    def test_language_switch_zh(self, app):
        """切换到中文"""
        response = app.get('/lang/zh', follow_redirects=True)
        assert response.status_code == 200

# ============ 错误处理集成测试 ============

class TestErrorHandling:
    """错误处理集成测试"""
    
    def test_404_page(self, app):
        """404页面"""
        response = app.get('/this-does-not-exist')
        assert response.status_code == 404
    
    def test_sql_injection_handled(self, app):
        """SQL注入被处理"""
        response = app.get('/?q=Robert\'; DROP TABLE schools;--')
        # 不应该崩溃
        assert response.status_code in [200, 400]
    
    def test_xss_handled(self, app):
        """XSS被处理"""
        response = app.get('/?q=<script>alert(1)</script>')
        # XSS payload应该被转义（不是执行）
        # 检查响应中没有未转义的<script>alert(1)</script>
        assert b'<script>alert(1)</script>' not in response.data

# ============ 性能集成测试 ============

class TestPerformance:
    """性能集成测试"""
    
    def test_homepage_load_time(self, app):
        """首页加载时间"""
        import time
        start = time.time()
        response = app.get('/')
        elapsed = time.time() - start
        # 应该在2秒内加载
        assert elapsed < 2.0
        assert response.status_code == 200
    
    def test_search_performance(self, app):
        """搜索性能"""
        import time
        start = time.time()
        response = app.get('/?q=university')
        elapsed = time.time() - start
        # 搜索应该在1秒内完成
        assert elapsed < 1.0
        assert response.status_code == 200

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
