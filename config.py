import os

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Secret key for session management
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# App configuration
DEBUG = True
