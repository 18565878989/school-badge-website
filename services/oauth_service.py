"""
OAuth service - social login providers
"""

import os
import secrets
import hashlib
import hmac
import time
import urllib.parse
from urllib.parse import urlencode


class OAuthProvider:
    """Base OAuth provider."""
    
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state):
        """Get the authorization URL to redirect user."""
        raise NotImplementedError
    
    def get_access_token(self, code):
        """Exchange authorization code for access token."""
        raise NotImplementedError
    
    def get_user_info(self, access_token):
        """Get user info from the provider."""
        raise NotImplementedError


class WeChatProvider(OAuthProvider):
    """WeChat OAuth provider."""
    
    def __init__(self):
        super().__init__(
            client_id=os.environ.get('WECHAT_APPID', ''),
            client_secret=os.environ.get('WECHAT_APPSECRET', ''),
            redirect_uri=os.environ.get('WECHAT_REDIRECT_URI', 'http://127.0.0.1:5001/auth/wechat/callback')
        )
        self.auth_url = 'https://open.weixin.qq.com/connect/qrconnect'
        self.token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        self.user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
    
    def get_authorization_url(self, state):
        params = {
            'appid': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'snsapi_login',
            'state': state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_access_token(self, code):
        import requests
        params = {
            'appid': self.client_id,
            'secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        resp = requests.get(self.token_url, params=params)
        return resp.json()
    
    def get_user_info(self, access_token, openid):
        import requests
        params = {'access_token': access_token, 'openid': openid}
        resp = requests.get(self.user_info_url, params=params)
        return resp.json()


class AlipayProvider(OAuthProvider):
    """Alipay OAuth provider."""
    
    def __init__(self):
        super().__init__(
            client_id=os.environ.get('ALIPAY_APPID', ''),
            client_secret=os.environ.get('ALIPAY_PRIVATE_KEY', ''),
            redirect_uri=os.environ.get('ALIPAY_REDIRECT_URI', 'http://127.0.0.1:5001/auth/alipay/callback')
        )
        self.auth_url = 'https://openauth.alipay.com/oauth2/publicAppAuthorize.htm'
    
    def get_authorization_url(self, state):
        params = {
            'app_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'auth_user',
            'state': state
        }
        return f"{self.auth_url}?{urlencode(params)}"


class FacebookProvider(OAuthProvider):
    """Facebook OAuth provider."""
    
    def __init__(self):
        super().__init__(
            client_id=os.environ.get('FACEBOOK_APPID', ''),
            client_secret=os.environ.get('FACEBOOK_APPSECRET', ''),
            redirect_uri='http://127.0.0.1:5001/auth/facebook/callback'
        )
        self.auth_url = 'https://www.facebook.com/v18.0/dialog/oauth'
        self.token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
        self.user_info_url = 'https://graph.facebook.com/me'
    
    def get_authorization_url(self, state):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'email,public_profile',
            'state': state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_access_token(self, code):
        import requests
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        resp = requests.get(self.token_url, params=params)
        return resp.json()
    
    def get_user_info(self, access_token):
        import requests
        params = {
            'access_token': access_token,
            'fields': 'id,name,email,picture'
        }
        resp = requests.get(self.user_info_url, params=params)
        return resp.json()


class TwitterProvider(OAuthProvider):
    """Twitter/X OAuth provider."""
    
    def __init__(self):
        super().__init__(
            client_id=os.environ.get('TWITTER_CLIENT_KEY', ''),
            client_secret=os.environ.get('TWITTER_CLIENT_SECRET', ''),
            redirect_uri='http://127.0.0.1:5001/auth/twitter/callback'
        )
        self.auth_url = 'https://twitter.com/i/oauth2/authorize'
        self.token_url = 'https://api.twitter.com/2/oauth2/token'
        self.user_info_url = 'https://api.twitter.com/2/users/me'
    
    def get_authorization_url(self, state):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'users.read',
            'state': state,
            'response_type': 'code'
        }
        return f"{self.auth_url}?{urlencode(params)}"


def get_oauth_provider(provider_name):
    """Get OAuth provider by name."""
    providers = {
        'wechat': WeChatProvider,
        'alipay': AlipayProvider,
        'facebook': FacebookProvider,
        'twitter': TwitterProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if provider_class:
        return provider_class()
    return None


def generate_oauth_state():
    """Generate a random state for OAuth security."""
    return secrets.token_urlsafe(32)


def verify_oauth_state(state):
    """Verify OAuth state (simple implementation)."""
    # In production, store state in session or Redis with expiration
    return len(state) > 20
