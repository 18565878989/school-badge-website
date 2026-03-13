"""
图片收集技能 - 收集校徽和校园图片
"""
import sqlite3
import requests
import os
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
import time
import re

DB_PATH = Path(__file__).parent.parent.parent / "database.db"
BADGE_DIR = Path(__file__).parent.parent.parent / "static" / "images" / "badges"
CAMPUS_DIR = Path(__file__).parent.parent.parent / "static" / "images" / "campus"

# 确保目录存在
BADGE_DIR.mkdir(parents=True, exist_ok=True)
CAMPUS_DIR.mkdir(parents=True, exist_ok=True)

def get_schools_need_badge(limit=100):
    """获取需要收集校徽的学校"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 优先获取大学，没有校徽的学校
    cursor.execute("""
        SELECT id, name, name_cn, country, city, website 
        FROM schools 
        WHERE (badge_url IS NULL OR badge_url = '')
        AND level = 'university'
        ORDER BY RANDOM()
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    conn.close()
    return schools

def get_schools_need_campus(limit=50):
    """获取需要收集校园图片的学校"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 优先获取大学，没有校园图片的学校
    cursor.execute("""
        SELECT id, name, name_cn, country, city, website 
        FROM schools 
        WHERE (campus_image IS NULL OR campus_image = '')
        AND level = 'university'
        ORDER BY RANDOM()
        LIMIT ?
    """, (limit,))
    
    schools = cursor.fetchall()
    conn.close()
    return schools

def search_baidu_image(school_name, image_type="logo"):
    """从百度/Bing图片搜索图片 - 优先Bing(稳定)，备用百度"""
    if image_type == "logo":
        search_query = f"{school_name} university logo"
    else:
        search_query = f"{school_name} campus photo"
    
    # 方法1: Bing图片搜索 (更稳定)
    url = "https://www.bing.com/images/search"
    params = {
        "q": search_query,
        "first": 0,
        "count": 10
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        # 提取图片URL
        img_urls = re.findall(r'mediaurl=([^&"]+)', response.text)
        if img_urls:
            from urllib.parse import unquote
            return unquote(img_urls[0])
    except Exception as e:
        print(f"Bing搜索失败: {e}")
    
    # 方法2: 备用百度图片 (如Bing失败)
    if image_type == "logo":
        search_query = f"{school_name} 校徽 logo"
    else:
        search_query = f"{school_name} 校园 风景"
    
    url = "https://image.baidu.com/search/index"
    params = {"word": search_query, "tn": "baiduimage", "pn": 0, "rn": 10}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://image.baidu.com/",
        "Accept": "text/html,application/xhtml+xml"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if "安全验证" not in response.text and len(response.text) > 5000:
            img_urls = re.findall(r'"thumbURL":"(https?://[^"]+)"', response.text)
            if img_urls:
                return img_urls[0]
    except Exception as e:
        print(f"百度图片搜索失败: {e}")
    
    return None

def search_badge_image(school_name, country):
    """搜索校徽图片 - 优先百度图片，备用Wikipedia"""
    # 1. 优先从百度图片搜索
    print(f"  [百度] 搜索校徽: {school_name}")
    img_url = search_baidu_image(school_name, "logo")
    if img_url:
        print(f"  [百度] 找到校徽!")
        return img_url
    
    # 2. 百度没找到，尝试 Wikipedia
    print(f"  [Wiki] 搜索校徽: {school_name}")
    search_url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{school_name} logo",
        "format": "json",
        "utf8": 1,
        "srlimit": 5
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()
        
        for result in data.get("query", {}).get("search", []):
            page_title = result["title"]
            img_url = get_wikipedia_image(page_title)
            if img_url:
                print(f"  [Wiki] 找到校徽!")
                return img_url
    except Exception as e:
        print(f"  [Wiki] 搜索失败: {e}")
    
    return None

def get_wikipedia_image(title):
    """从 Wikipedia 获取图片"""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "pageimages",
        "pithumbsize": 500,
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "thumbnail" in page_data:
                return page_data["thumbnail"]["source"]
    except:
        pass
    
    return None

def search_campus_image(school_name, country):
    """搜索校园图片 - 优先百度图片，备用Wikipedia"""
    # 1. 优先从百度图片搜索
    print(f"  [百度] 搜索校园: {school_name}")
    img_url = search_baidu_image(school_name, "campus")
    if img_url:
        print(f"  [百度] 找到校园图!")
        return img_url
    
    # 2. 百度没找到，尝试 Wikipedia
    print(f"  [Wiki] 搜索校园: {school_name}")
    search_url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{school_name} campus photo",
        "format": "json",
        "utf8": 1,
        "srlimit": 5
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()
        
        for result in data.get("query", {}).get("search", []):
            page_title = result["title"]
            img_url = get_wikipedia_image(page_title)
            if img_url:
                print(f"  [Wiki] 找到校园图!")
                return img_url
    except Exception as e:
        print(f"  [Wiki] 搜索失败: {e}")
    
    return None

def update_school_badge(school_id, badge_url):
    """更新学校校徽"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE schools SET badge_url = ? WHERE id = ?",
        (badge_url, school_id)
    )
    conn.commit()
    conn.close()

def update_school_campus(school_id, campus_url):
    """更新学校校园图片"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE schools SET campus_image = ? WHERE id = ?",
        (campus_url, school_id)
    )
    conn.commit()
    conn.close()

def collect_badges(limit=100):
    """收集校徽"""
    schools = get_schools_need_badge(limit)
    
    print(f"开始收集校徽，目标: {len(schools)} 所学校")
    
    collected = 0
    for school in schools:
        school_id, name, name_cn, country, city, website = school
        
        print(f"处理: {name} ({country})")
        
        # 搜索校徽
        badge_url = search_badge_image(name_cn or name, country)
        
        if badge_url:
            update_school_badge(school_id, badge_url)
            collected += 1
            print(f"  ✓ 找到校徽: {badge_url[:50]}...")
        else:
            print(f"  ✗ 未找到校徽")
        
        # 避免请求过快
        time.sleep(0.5)
    
    print(f"\n完成! 成功收集 {collected}/{len(schools)} 个校徽")
    return collected

def collect_campus(limit=50):
    """收集校园图片"""
    schools = get_schools_need_campus(limit)
    
    print(f"开始收集校园图片，目标: {len(schools)} 所学校")
    
    collected = 0
    for school in schools:
        school_id, name, name_cn, country, city, website = school
        
        print(f"处理: {name} ({country})")
        
        # 搜索校园图片
        campus_url = search_campus_image(name_cn or name, country)
        
        if campus_url:
            update_school_campus(school_id, campus_url)
            collected += 1
            print(f"  ✓ 找到校园图: {campus_url[:50]}...")
        else:
            print(f"  ✗ 未找到校园图")
        
        # 避免请求过快
        time.sleep(0.5)
    
    print(f"\n完成! 成功收集 {collected}/{len(schools)} 张校园图")
    return collected

def run(mode="badges", limit=100):
    """运行收集"""
    if mode == "badges":
        return collect_badges(limit)
    elif mode == "campus":
        return collect_campus(limit)
    else:
        print(f"未知模式: {mode}")
        return 0

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "badges"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    run(mode, limit)
