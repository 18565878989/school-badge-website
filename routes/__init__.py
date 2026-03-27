"""
Routes package - all route modules
"""

from .admin import admin_bp, register_routes as register_admin
from .auth import auth_bp, register_routes as register_auth
from .schools import schools_bp, register_routes as register_schools
from .rankings import rankings_bp, register_routes as register_rankings
from .api import api_bp, register_routes as register_api
from .main import main_bp, register_routes as register_main

def register_all_routes(app):
    """Register all route blueprints with the Flask app."""
    register_admin(app)
    register_auth(app)
    register_schools(app)
    register_rankings(app)
    register_api(app)
    register_main(app)

__all__ = ['register_all_routes']
