"""
Search service - local database search logic for deep search
"""

from models import get_db_connection

# Country name mapping (Chinese -> English)
COUNTRY_MAP = {
    '日本': 'Japan', '中国': 'China', '美国': 'United States',
    '英国': 'United Kingdom', '德国': 'Germany', '法国': 'France',
    '加拿大': 'Canada', '澳大利亚': 'Australia', '韩国': 'South Korea',
    '新加坡': 'Singapore', '香港': 'Hong Kong', '台湾': 'Taiwan',
    '欧洲': 'Europe', '亚洲': 'Asia', '北美': 'North America'
}

# Level name mapping
LEVEL_MAP = {
    '大学': 'university', '学院': 'college', '中学': 'middle',
    '高中': 'middle', '小学': 'elementary', '幼儿园': 'kindergarten'
}

# Keywords to exclude from name search (ranking systems, generic terms)
EXCLUDED_KEYWORDS = {
    'top', 'ranking', 'best', 'qs', 'the', 'usnews', 'arwu', 'cwur',
    '最好', '前五', '前10', '前20', '排名', 'world', 'global', 'international'
}


def search_schools(query=None, keywords=None, filters=None, limit=30):
    """
    Local database search for schools.
    
    Args:
        query: Original user query string
        keywords: List of processed keywords from AI
        filters: Dict with filters from AI (country, level, region)
        limit: Maximum results to return
    
    Returns:
        List of school dictionaries
    """
    if keywords is None:
        keywords = []
    if filters is None:
        filters = {}
    
    conn = get_db_connection()
    
    # Process keywords
    processed_keywords = _process_keywords(keywords)
    
    # Apply country name mapping to filters
    if filters.get('region') and filters['region'] in COUNTRY_MAP:
        filters['region'] = COUNTRY_MAP[filters['region']]
    if filters.get('country') and filters['country'] in COUNTRY_MAP:
        filters['country'] = COUNTRY_MAP[filters['country']]
    
    # Build SQL query
    sql, params = _build_search_sql(processed_keywords, filters, limit)
    
    # Execute query
    results = conn.execute(sql, params).fetchall()
    conn.close()
    
    # Format results
    school_results = []
    for school in results:
        school_dict = dict(school)
        # Clean badge_url
        if school_dict.get('badge_url') and not school_dict['badge_url'].startswith(('http://', 'https://')):
            school_dict['badge_url'] = f"/static/images/{school_dict['badge_url']}"
        school_results.append(school_dict)
    
    return school_results


def _process_keywords(keywords):
    """Process keywords and categorize them."""
    processed = []
    
    for kw in keywords:
        kw_lower = kw.lower()
        
        # Check if it's a country
        if kw in COUNTRY_MAP:
            processed.append(('country', COUNTRY_MAP[kw]))
        elif kw_lower in [c.lower() for c in COUNTRY_MAP.values()]:
            for cn, en in COUNTRY_MAP.items():
                if en.lower() == kw_lower:
                    processed.append(('country', en))
                    break
        
        # Check if it's a level
        elif kw in LEVEL_MAP:
            processed.append(('level', LEVEL_MAP[kw]))
        elif kw_lower in LEVEL_MAP.values():
            processed.append(('level', kw_lower))
        
        # Check if it's excluded
        elif kw_lower in EXCLUDED_KEYWORDS:
            continue
        
        # Otherwise it's a search keyword
        else:
            processed.append(('keyword', kw))
    
    return processed


def _build_search_sql(processed_keywords, filters, limit):
    """Build SQL query from processed keywords and filters."""
    core_filters = []
    core_params = []
    keyword_filters = []
    keyword_params = []
    
    # Process keywords
    for kw_type, kw_value in processed_keywords:
        if kw_type == 'country':
            core_filters.append('(country LIKE ? OR name_cn LIKE ?)')
            core_params.extend([f'%{kw_value}%', f'%{kw_value}%'])
        elif kw_type == 'level':
            core_filters.append('level = ?')
            core_params.append(kw_value)
        elif kw_type == 'keyword':
            keyword_filters.append('(name LIKE ? OR name_cn LIKE ? OR motto LIKE ? OR city LIKE ?)')
            keyword_params.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%', f'%{kw}%'])
    
    # Apply filters
    if filters.get('country'):
        core_filters.append('country LIKE ?')
        core_params.append(f'%{filters["country"]}%')
    if filters.get('level'):
        core_filters.append('level = ?')
        core_params.append(filters['level'])
    if filters.get('region'):
        core_filters.append('region = ?')
        core_params.append(filters['region'])
    
    # Build SQL
    base_sql = '''
        SELECT *, 
            CASE 
                WHEN qs_rank IS NOT NULL THEN qs_rank 
                WHEN the_rank IS NOT NULL THEN the_rank 
                WHEN usnews_rank IS NOT NULL THEN usnews_rank 
                ELSE 99999 
            END as ranking_score
        FROM schools WHERE 1=1
    '''
    
    if core_filters:
        base_sql += ' AND ' + ' AND '.join(core_filters)
    
    if keyword_filters:
        base_sql += ' AND (' + ' OR '.join(keyword_filters) + ')'
    
    base_sql += ' ORDER BY ranking_score LIMIT ?'
    params = core_params + keyword_params + [limit]
    
    return base_sql, params


def get_school_by_id(school_id):
    """Get a single school by ID."""
    conn = get_db_connection()
    school = conn.execute('SELECT * FROM schools WHERE id = ?', (school_id,)).fetchone()
    conn.close()
    return dict(school) if school else None


def get_similar_schools(school_id, limit=10):
    """Get similar schools based on region and level."""
    conn = get_db_connection()
    
    school = conn.execute(
        'SELECT region, level FROM schools WHERE id = ?', (school_id,)
    ).fetchone()
    
    if not school:
        conn.close()
        return []
    
    similar = conn.execute('''
        SELECT * FROM schools 
        WHERE region = ? AND level = ? AND id != ?
        ORDER BY RANDOM()
        LIMIT ?
    ''', (school['region'], school['level'], school_id, limit)).fetchall()
    
    conn.close()
    return [dict(s) for s in similar]
