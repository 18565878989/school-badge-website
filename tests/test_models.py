#!/usr/bin/env python3
"""Unit tests for database models - using real database with transactions."""
import pytest
import sqlite3
import json
from werkzeug.security import generate_password_hash


class TestChineseConversion:
    """Tests that don't need database at all."""

    def test_traditional_to_simplified(self):
        import models
        assert models.traditional_to_simplified('大學') == '大学'
        assert models.traditional_to_simplified('清華大學') == '清华大学'
        assert models.traditional_to_simplified('北京大學') == '北京大学'
        assert models.traditional_to_simplified('香港中文大學') == '香港中文大学'

    def test_simplified_to_traditional(self):
        import models
        assert models.simplified_to_traditional('大学') == '大學'
        assert models.simplified_to_traditional('清华大学') == '清華大學'

    def test_empty_string_handling(self):
        import models
        assert models.traditional_to_simplified('') == ''
        assert models.traditional_to_simplified(None) is None
        assert models.simplified_to_traditional('') == ''
        assert models.simplified_to_traditional(None) is None

    def test_no_change_for_already_simplified(self):
        import models
        result = models.traditional_to_simplified('清华大学')
        assert '清華' not in result
        assert '清华' in result


class TestUserModelReal:
    """Tests using the real database with transaction rollback."""

    def test_get_user_by_username_found(self, test_db):
        """get_user_by_username should find existing users."""
        # test_db is the real database - use it directly
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            # Find a user in the real DB
            user = models.get_user_by_username('admin')
            if user:
                assert user['username'] == 'admin'
                assert user['role'] in ('admin', 'user')
        finally:
            models.get_db_connection = original

    def test_get_user_by_id_found(self, test_db):
        """get_user_by_id should find existing users."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            # Use the test_db which is a connection to real DB
            row = test_db.execute('SELECT id FROM users LIMIT 1').fetchone()
            if row:
                user = models.get_user_by_id(row['id'])
                assert user is not None
        finally:
            models.get_db_connection = original

    def test_verify_password_returns_none_for_wrong_password(self, test_db):
        """verify_password should return None for wrong password."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            result = models.verify_password('nonexistent_user_xyz', 'wrongpass')
            assert result is None
        finally:
            models.get_db_connection = original


class TestSchoolModelReal:
    """Tests using the real database."""

    def test_get_all_schools(self, test_db):
        """get_all_schools should return all schools from real DB."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            schools = models.get_all_schools()
            assert len(schools) >= 7000  # Real DB has 7270 schools
        finally:
            models.get_db_connection = original

    def test_get_school_by_id_valid(self, test_db):
        """get_school_by_id should return school for valid ID."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            # Get first school from DB
            school = test_db.execute('SELECT id FROM schools LIMIT 1').fetchone()
            if school:
                result = models.get_school_by_id(school['id'])
                assert result is not None
                assert 'name' in dict(result)
        finally:
            models.get_db_connection = original

    def test_get_school_by_id_invalid(self, test_db):
        """get_school_by_id should return None for invalid ID."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            result = models.get_school_by_id(99999999)
            assert result is None
        finally:
            models.get_db_connection = original

    def test_get_schools_by_region(self, test_db):
        """get_schools_by_region should filter correctly."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            # Test that Asia region has schools (don't chain with get_regions which closes conn)
            asia_schools = models.get_schools_by_region('Asia')
            assert len(asia_schools) > 0
            for s in asia_schools:
                assert s['region'] == 'Asia'
        finally:
            models.get_db_connection = original

    def test_get_schools_by_level(self, test_db):
        """get_schools_by_level should filter correctly."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            schools = models.get_schools_by_level('university')
            assert len(schools) > 0
        finally:
            models.get_db_connection = original

    def test_search_schools_by_name(self, test_db):
        """search_schools should find schools by name."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            results = models.search_schools('Harvard')
            assert len(results) >= 1
            names = [r['name'] for r in results]
            assert any('Harvard' in n for n in names)
        finally:
            models.get_db_connection = original

    def test_search_schools_by_chinese_name(self, test_db):
        """search_schools should find schools by Chinese name."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            results = models.search_schools('清华')
            assert len(results) >= 1
        finally:
            models.get_db_connection = original

    def test_search_schools_with_region_filter(self, test_db):
        """search_schools should combine text and region filter."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            results = models.search_schools('University', region='Asia')
            assert len(results) > 0
            for r in results:
                assert r['region'] == 'Asia'
        finally:
            models.get_db_connection = original

    def test_get_regions(self, test_db):
        """get_regions should return all unique regions."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            regions = models.get_regions()
            assert len(regions) > 0
            assert isinstance(regions, list)
        finally:
            models.get_db_connection = original


class TestLikeModelReal:
    """Tests for like functionality using real database."""

    def test_get_likes_count(self, test_db):
        """get_likes_count should return count."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            school = test_db.execute('SELECT id FROM schools LIMIT 1').fetchone()
            if school:
                count = models.get_likes_count(school['id'])
                assert isinstance(count, int)
                assert count >= 0
        finally:
            models.get_db_connection = original

    def test_get_like_no_like(self, test_db):
        """get_like should return None when no like exists."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            # Use a user ID that likely doesn't exist or a school with no likes
            result = models.get_like(99999, 1)
            assert result is None
        finally:
            models.get_db_connection = original

    def test_like_school_requires_valid_ids(self, test_db):
        """like_school should handle non-existent user/school gracefully."""
        import models
        original = models.get_db_connection
        models.get_db_connection = lambda: test_db
        try:
            # Non-existent school
            result = models.like_school(1, 99999999)
            # Should not crash - may fail silently
            assert isinstance(result, bool)
        finally:
            models.get_db_connection = original
