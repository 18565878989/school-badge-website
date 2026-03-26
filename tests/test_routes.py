#!/usr/bin/env python3
"""Integration tests for Flask routes."""
import pytest


class TestIndexRoute:
    def test_index_get(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_index_search_query(self, client):
        response = client.get('/?q=Harvard')
        assert response.status_code == 200

    def test_index_region_filter(self, client):
        response = client.get('/?region=Asia')
        assert response.status_code == 200

    def test_index_pagination(self, client):
        response = client.get('/?page=2')
        assert response.status_code == 200

    def test_index_level_filter(self, client):
        response = client.get('/?level=university')
        assert response.status_code == 200


class TestSchoolDetailRoute:
    def test_school_detail_valid_id(self, client, test_db):
        school = test_db.execute('SELECT id FROM schools LIMIT 1').fetchone()
        if school:
            response = client.get(f'/school/{school["id"]}')
            assert response.status_code in (200, 302)

    def test_school_detail_invalid_id(self, client):
        response = client.get('/school/999999')
        assert response.status_code in (302, 404)

    def test_school_detail_negative_id(self, client):
        response = client.get('/school/-1')
        assert response.status_code in (302, 404)


class TestLikeRoute:
    def test_like_not_authenticated_redirects(self, client):
        """POST /like/<id> without auth should redirect to login."""
        response = client.post('/like/1', follow_redirects=False)
        assert response.status_code == 302

    def test_like_authenticated_valid_school(self, authenticated_client, test_db):
        """POST /like/<id> with auth should work."""
        school = test_db.execute('SELECT id FROM schools LIMIT 1').fetchone()
        if school:
            response = authenticated_client.post(f'/like/{school["id"]}', follow_redirects=False)
            assert response.status_code in (200, 302)


class TestMyLikesRoute:
    def test_my_likes_not_authenticated_redirects(self, client):
        """GET /my-likes without auth should redirect."""
        response = client.get('/my-likes')
        assert response.status_code == 302

    def test_my_likes_authenticated_returns_200(self, authenticated_client):
        """GET /my-likes with auth should return 200."""
        response = authenticated_client.get('/my-likes')
        assert response.status_code == 200


class TestLoginRoute:
    def test_login_get_returns_200(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_post_empty_credentials(self, client):
        """POST with empty credentials should not crash."""
        response = client.post('/login', data={
            'type': 'password',
            'username': '',
            'password': ''
        }, follow_redirects=False)
        assert response.status_code in (200, 302)


class TestRegisterRoute:
    def test_register_get_returns_200(self, client):
        response = client.get('/register')
        assert response.status_code == 200

    def test_register_post_empty(self, client):
        """POST with empty data should handle gracefully."""
        response = client.post('/register', data={
            'username': '',
            'password': '',
            'email': ''
        }, follow_redirects=False)
        assert response.status_code in (200, 302)


class TestLogoutRoute:
    def test_logout_redirects(self, authenticated_client):
        """GET /logout should clear session and redirect."""
        response = authenticated_client.get('/logout', follow_redirects=False)
        assert response.status_code == 302


class TestLanguageRoute:
    def test_set_language_en_redirects(self, client):
        response = client.get('/lang/en', follow_redirects=False)
        assert response.status_code == 302

    def test_set_language_zh_redirects(self, client):
        response = client.get('/lang/zh', follow_redirects=False)
        assert response.status_code == 302

    def test_set_language_zh_tw_redirects(self, client):
        response = client.get('/lang/zh_TW', follow_redirects=False)
        assert response.status_code == 302


class TestBadgeHubRoute:
    def test_badge_hub_returns_200(self, client):
        response = client.get('/badges')
        assert response.status_code == 200


class TestRankingsRoute:
    def test_rankings_returns_200(self, client):
        response = client.get('/rankings')
        assert response.status_code == 200


class TestCampusRoutes:
    def test_campus_global_returns_200(self, client):
        response = client.get('/campus')
        assert response.status_code == 200

    def test_campus_north_america_returns_200(self, client):
        response = client.get('/campus/north-america')
        assert response.status_code == 200

    def test_campus_europe_returns_200(self, client):
        response = client.get('/campus/europe')
        assert response.status_code == 200

    def test_campus_asia_returns_200(self, client):
        response = client.get('/campus/asia')
        assert response.status_code == 200

    def test_campus_oceania_returns_200(self, client):
        response = client.get('/campus/oceania')
        assert response.status_code == 200

    def test_campus_south_america_returns_200(self, client):
        response = client.get('/campus/south-america')
        assert response.status_code == 200

    def test_campus_africa_returns_200(self, client):
        response = client.get('/campus/africa')
        assert response.status_code == 200


class TestSocialRoute:
    def test_social_returns_200(self, client):
        response = client.get('/social')
        assert response.status_code == 200


class TestAdminRoutes:
    def test_admin_dashboard_requires_admin(self, client):
        """GET /admin without admin session should redirect."""
        response = client.get('/admin')
        assert response.status_code == 302

    def test_admin_schools_requires_admin(self, client):
        """GET /admin/schools without admin session should redirect."""
        response = client.get('/admin/schools')
        assert response.status_code == 302

    def test_admin_users_requires_admin(self, client):
        """GET /admin/users without admin session should redirect."""
        response = client.get('/admin/users')
        assert response.status_code == 302

    def test_admin_init_db_accessible(self, client):
        """GET /init-db should be accessible."""
        response = client.get('/init-db')
        assert response.status_code in (200, 302)


class TestAPIRoutes:
    def test_api_share_config_accessible(self, client):
        """GET /api/share/config should be accessible."""
        response = client.get('/api/share/config')
        assert response.status_code in (200, 302)

    def test_api_posts_accessible(self, client):
        """GET /api/posts should be accessible."""
        response = client.get('/api/posts')
        assert response.status_code in (200, 302)


class TestEdgeCases:
    def test_invalid_route_returns_404(self, client):
        response = client.get('/nonexistent/route/that/does/not/exist')
        assert response.status_code == 404

    def test_sql_injection_in_search_does_not_crash(self, client):
        """Search with SQL injection should be handled gracefully."""
        response = client.get("/?q=' OR '1'='1")
        assert response.status_code == 200

    def test_xss_in_search_does_not_crash(self, client):
        """Search with XSS should be handled gracefully."""
        response = client.get("/?q=<script>alert('xss')</script>")
        assert response.status_code == 200

    def test_large_page_number_handled(self, client):
        """Large page number should be handled gracefully."""
        response = client.get('/?page=999999')
        assert response.status_code == 200

    def test_negative_page_number_handled(self, client):
        """Negative page number should be handled gracefully."""
        response = client.get('/?page=-5')
        assert response.status_code in (200, 302)

    def test_special_chars_in_search(self, client):
        """Search with special characters should be handled."""
        response = client.get('/?q=北京大学')
        assert response.status_code == 200
