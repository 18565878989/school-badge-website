"""
Formatting utilities
"""

def format_number(num):
    """Format number with thousand separators."""
    if num is None:
        return 'N/A'
    return f"{num:,}"

def format_year(year):
    """Format year for display."""
    if year is None:
        return 'N/A'
    return str(year)

def truncate_text(text, max_length=100, suffix='...'):
    """Truncate text to max length."""
    if text is None:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def format_percentage(value, total):
    """Calculate and format percentage."""
    if total == 0:
        return '0%'
    return f"{round(value / total * 100, 1)}%"

def format_rank(rank):
    """Format ranking number with ordinal suffix."""
    if rank is None:
        return 'N/A'
    
    rank = int(rank)
    if rank % 100 in [11, 12, 13]:
        return f"{rank}th"
    
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(rank % 10, 'th')
    return f"{rank}{suffix}"
