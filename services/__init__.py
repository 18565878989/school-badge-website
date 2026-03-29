# Services package

# Ranking service
from .ranking_service import get_latest_rankings, get_school_rankings_all

# School service
from .school_service import get_schools_by_criteria, get_school_with_details, get_school_statistics

# Search service
from .search_service import search_schools, get_similar_schools

# OAuth service
from .oauth_service import get_oauth_provider, generate_oauth_state, OAuthProvider

# Chat service
from .chat_service import chat_with_ai, get_chat_provider, ChatProvider

__all__ = [
    # Ranking
    'get_latest_rankings',
    'get_school_rankings_all',
    # School
    'get_schools_by_criteria',
    'get_school_with_details',
    'get_school_statistics',
    # Search
    'search_schools',
    'get_similar_schools',
    # OAuth
    'get_oauth_provider',
    'generate_oauth_state',
    'OAuthProvider',
    # Chat
    'chat_with_ai',
    'get_chat_provider',
    'ChatProvider',
]
