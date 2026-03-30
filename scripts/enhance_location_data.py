#!/usr/bin/env python3
"""
学校地理位置数据补全脚本
为各国学校补充省份/州/城市信息
"""
import sqlite3
import re

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_schools_needing_update():
    """获取需要更新地理位置的学校"""
    conn = get_db_connection()
    schools = conn.execute("""
        SELECT id, name, name_cn, country, region, city
        FROM schools
        WHERE country NOT IN ('Hong Kong', 'China', 'Taiwan', 'Macau')
        AND (region IS NULL OR region = '' OR region = country 
             OR city IS NULL OR city = '')
        ORDER BY country, name
    """).fetchall()
    conn.close()
    return [dict(s) for s in schools]

def parse_location_from_name(name, name_cn):
    """从学校名称中解析地理位置信息"""
    location = {}
    
    # 常见模式匹配
    patterns = {
        'state_us': r'(University|College|Institute)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+',
        'city_country': r'([A-Z][a-z]+)\s+(University|College|Institute)',
        'national': r'National\s+(University|College|Institute)',
    }
    
    return location

def infer_location_from_name(name, country):
    """根据学校名称推断地理位置"""
    location = {'region': None, 'city': None}
    
    name_lower = name.lower()
    
    # 美国州名识别
    us_states = {
        'california': 'California', 'new york': 'New York', 'texas': 'Texas',
        'florida': 'Florida', 'illinois': 'Illinois', 'pennsylvania': 'Pennsylvania',
        'ohio': 'Ohio', 'georgia': 'Georgia', 'michigan': 'Michigan',
        'massachusetts': 'Massachusetts', 'washington': 'Washington',
        'arizona': 'Arizona', 'colorado': 'Colorado', 'virginia': 'Virginia',
        'boston': 'Massachusetts', 'los angeles': 'California', 
        'chicago': 'Illinois', 'new york city': 'New York',
        'san francisco': 'California', 'seattle': 'Washington',
        'philadelphia': 'Pennsylvania', 'miami': 'Florida',
        'atlanta': 'Georgia', 'baltimore': 'Maryland', 'denver': 'Colorado',
        'portland': 'Oregon', 'minneapolis': 'Minnesota', 'detroit': 'Michigan',
        'san diego': 'California', 'dallas': 'Texas', 'houston': 'Texas',
        'austin': 'Texas', 'phoenix': 'Arizona', 'san antonio': 'Texas',
        'san jose': 'California', 'columbus': 'Ohio', 'indianapolis': 'Indiana',
        'charlotte': 'North Carolina', 'memphis': 'Tennessee', 'louisville': 'Kentucky',
        'milwaukee': 'Wisconsin', 'albuquerque': 'New Mexico', 'tucson': 'Arizona',
        'fresno': 'California', 'sacramento': 'California', 'kansas city': 'Missouri',
        'mesa': 'Arizona', 'atlanta': 'Georgia', 'omaha': 'Nebraska',
        'raleigh': 'North Carolina', 'colorado springs': 'Colorado',
        'long beach': 'California', 'virginia beach': 'Virginia',
        'oakland': 'California', 'minneapolis': 'Minnesota',
    }
    
    if country == 'United States':
        for city, state in us_states.items():
            if city in name_lower:
                location['city'] = city.title().replace(' Of ', ' of ')
                location['region'] = state
                return location
    
    # 日本都道府县识别
    japan_prefectures = [
        'Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Nagoya', 'Sapporo', 'Fukuoka',
        'Kobe', 'Sendai', 'Hiroshima', 'Chiba', 'Saitama', 'Kawasaki',
        'Kitakyushu', 'Hamamatsu', 'Nagano', 'Nara', 'Kumamoto',
        'Hokkaido', 'Aomori', 'Iwate', 'Miyagi', 'Akita', 'Yamagata', 'Fukushima',
        'Ibaraki', 'Tochigi', 'Gunma', 'Saitama', 'Chiba', 'Tokyo', 'Kanagawa',
        'Niigata', 'Toyama', 'Ishikawa', 'Fukui', 'Yamanashi', 'Nagano',
        'Gifu', 'Shizuoka', 'Aichi', 'Mie', 'Shiga', 'Kyoto', 'Osaka', 'Hyogo',
        'Nara', 'Wakayama', 'Tottori', 'Shimane', 'Okayama', 'Hiroshima', 'Yamaguchi',
        'Tokushima', 'Kagawa', 'Ehime', 'Kochi', 'Fukuoka', 'Saga', 'Nagasaki',
        'Kumamoto', 'Oita', 'Miyazaki', 'Kagoshima', 'Okinawa'
    ]
    
    if country == 'Japan':
        for pref in japan_prefectures:
            if pref.lower() in name_lower:
                location['region'] = pref
                return location
    
    # 韩国省份识别
    korea_regions = [
        'Seoul', 'Busan', 'Daegu', 'Daejeon', 'Gwangju', 'Incheon', 'Ulsan',
        'Gyeonggi', 'Gangwon', 'Chungbuk', 'Chungnam', 'Jeonbuk', 'Jeonnam',
        'Gyeongbuk', 'Gyeongnam', 'Jeju'
    ]
    
    if country == 'South Korea':
        for region in korea_regions:
            if region.lower() in name_lower:
                location['region'] = region
                return location
    
    # 澳大利亚州识别
    australia_states = {
        'sydney': 'NSW', 'melbourne': 'VIC', 'brisbane': 'QLD',
        'perth': 'WA', 'adelaide': 'SA', 'canberra': 'ACT',
        'hobart': 'TAS', 'darwin': 'NT', 'new south wales': 'NSW',
        'victoria': 'VIC', 'queensland': 'QLD', 'western australia': 'WA',
        'south australia': 'SA', 'tasmania': 'TAS', 'northern territory': 'NT'
    }
    
    if country == 'Australia':
        for city, state in australia_states.items():
            if city in name_lower:
                location['region'] = state
                return location
    
    # 加拿大省份识别
    canada_provinces = {
        'toronto': 'Ontario', 'ottawa': 'Ontario', 'vancouver': 'British Columbia',
        'calgary': 'Alberta', 'edmonton': 'Alberta', 'montreal': 'Quebec',
        'quebec city': 'Quebec', 'winnipeg': 'Manitoba', 'halifax': 'Nova Scotia',
        'ontario': 'Ontario', 'quebec': 'Quebec', 'british columbia': 'British Columbia',
        'alberta': 'Alberta', 'manitoba': 'Manitoba', 'saskatchewan': 'Saskatchewan'
    }
    
    if country == 'Canada':
        for city, prov in canada_provinces.items():
            if city in name_lower:
                location['region'] = prov
                return location
    
    # 英国地区识别
    uk_regions = {
        'london': 'England', 'birmingham': 'England', 'manchester': 'England',
        'leeds': 'England', 'liverpool': 'England', 'bristol': 'England',
        'edinburgh': 'Scotland', 'glasgow': 'Scotland', 'cardiff': 'Wales',
        'cambridge': 'England', 'oxford': 'England', 'bath': 'England',
        'nottingham': 'England', 'sheffield': 'England', 'newcastle': 'England'
    }
    
    if country == 'United Kingdom':
        for city, region in uk_regions.items():
            if city in name_lower:
                location['region'] = region
                return location
    
    return location

def update_school_location(school_id, region, city):
    """更新学校地理位置"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if region:
        cursor.execute("UPDATE schools SET region = ? WHERE id = ?", (region, school_id))
    if city:
        cursor.execute("UPDATE schools SET city = ? WHERE id = ?", (city, school_id))
    
    conn.commit()
    conn.close()

def main():
    print("=" * 60)
    print("学校地理位置数据补全工具")
    print("=" * 60)
    
    schools = get_schools_needing_update()
    print(f"\n找到 {len(schools)} 所学校需要更新地理位置")
    
    if not schools:
        print("✅ 所有学校已有完整的地理位置信息")
        return
    
    # 按国家分组统计
    by_country = {}
    for school in schools:
        country = school['country']
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(school)
    
    print(f"涉及 {len(by_country)} 个国家")
    
    updated_count = 0
    
    for country, country_schools in by_country.items():
        print(f"\n处理 {country} ({len(country_schools)} 所学校)...")
        
        for school in country_schools:
            location = infer_location_from_name(school['name'], country)
            
            if location['region'] or location['city']:
                update_school_location(school['id'], location['region'], location['city'])
                updated_count += 1
                print(f"  ✅ {school['name'][:50]}: {location}")
    
    print("\n" + "=" * 60)
    print(f"补全完成: 更新了 {updated_count} 所学校")
    print("=" * 60)
    
    # 验证结果
    conn = get_db_connection()
    remaining = conn.execute("""
        SELECT COUNT(*) as count FROM schools
        WHERE country NOT IN ('Hong Kong', 'China', 'Taiwan', 'Macau')
        AND (region IS NULL OR region = '' OR region = country 
             OR city IS NULL OR city = '')
    """).fetchone()[0]
    conn.close()
    
    print(f"\n剩余需要补全的学校: {remaining} 所")

if __name__ == '__main__':
    main()
