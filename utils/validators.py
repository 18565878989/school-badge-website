"""
Validators for user input
"""

import re

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format."""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if it's between 10-15 digits
    return 10 <= len(digits) <= 15

def validate_url(url):
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None

def validate_username(username):
    """Validate username format."""
    if len(username) < 3 or len(username) > 30:
        return False
    # Only alphanumeric and underscore
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, username) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 128:
        return False, "Password is too long"
    return True, "Valid"
