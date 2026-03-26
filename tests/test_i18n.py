#!/usr/bin/env python3
"""Unit tests for i18n module (i18n.py)."""
import pytest


class TestI18nModule:
    def test_get_locale_returns_string(self, app):
        """get_locale() should return a locale string."""
        with app.app_context():
            from i18n import get_locale
            result = get_locale()
            assert isinstance(result, str)
            assert result in ('en', 'zh', 'zh-TW', 'ja', 'ko', 'fr', 'de')

    def test_language_names_dict_exists(self, app):
        """LANGUAGE_NAMES should be a non-empty dict."""
        with app.app_context():
            from i18n import LANGUAGE_NAMES
            assert isinstance(LANGUAGE_NAMES, dict)
            assert len(LANGUAGE_NAMES) > 0
            assert 'en' in LANGUAGE_NAMES
            assert 'zh' in LANGUAGE_NAMES

    def test_underscore_function_returns_string(self, app):
        """_() function should return a string translation."""
        with app.app_context():
            from i18n import _
            result = _('welcome')
            assert isinstance(result, str)


class TestI18nContent:
    def test_english_translations_exist(self, app):
        """English translations should exist."""
        with app.app_context():
            from i18n import TRANSLATIONS
            assert 'en' in TRANSLATIONS

    def test_chinese_translations_exist(self, app):
        """Chinese translations should exist."""
        with app.app_context():
            from i18n import TRANSLATIONS
            assert 'zh' in TRANSLATIONS

    def test_traditional_chinese_translations_exist(self, app):
        """Traditional Chinese translations should exist."""
        with app.app_context():
            from i18n import TRANSLATIONS
            assert 'zh-TW' in TRANSLATIONS

    def test_translation_keys_common(self, app):
        """Common translation keys should exist."""
        with app.app_context():
            from i18n import TRANSLATIONS
            en = TRANSLATIONS.get('en', {})
            assert isinstance(en, dict)


class TestLocalePersistence:
    def test_set_language_en_redirects(self, client):
        """Setting English language should redirect."""
        response = client.get('/lang/en', follow_redirects=False)
        assert response.status_code == 302

    def test_set_language_zh_redirects(self, client):
        """Setting Chinese language should redirect."""
        response = client.get('/lang/zh', follow_redirects=False)
        assert response.status_code == 302

    def test_set_language_zh_tw_redirects(self, client):
        """Setting Traditional Chinese language should redirect."""
        response = client.get('/lang/zh-TW', follow_redirects=False)
        assert response.status_code == 302
