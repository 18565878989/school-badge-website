#!/usr/bin/env python3
"""
优化版批量校徽抓取脚本 v2
策略：
1. 优先抓取有官网的学校校徽（通过favicon/HTML提取）
2. 学校官网失败后，尝试Wikipedia
3. Wikipedia失败后，尝试Google Favicon API
4. 对于HK学校，尝试schooland.hk
5. 验证并重新下载已有的远程badge_url（可能已失效）
6. 下载到本地 static/images/badges/
"""

import sqlite3
import os
import re
import requests
import time
import json
from urllib.parse import urlparse, urljoin, quote
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
BADGES_DIR = '/Users/wangfeng/.openclaw/workspace/school-badge-website/static/images/badges'
DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}
TIMEOUT = 15
MAX_WORKERS = 6

os.makedirs(BADGES_DIR, exist_ok=True)

log_file = '/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/badge_batch.log'
CHECKPOINT_FILE = '/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/badge_batch_checkpoint.json'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(log_file, 'a') as f:
        f.write(line + '\n')

def load_checkpoint():
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'processed': [], 'last_run': None}

def save_checkpoint(processed_ids):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'processed': processed_ids, 'last_run': datetime.now().isoformat()}, f)

def clear_checkpoint():
    try:
        os.remove(CHECKPOINT_FILE)
    except:
        pass


# ========== 策略1: 学校官网抓取 ==========

def get_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return None


def download_image_to_local(url, school_id, attempt=1):
    """下载图片到本地，返回本地路径或None"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            return None
        
        content = resp.content
        if len(content) < 1000:
            return None
        
        # 检测文件类型
        if content[:3] == b'\xff\xd8\xff':
            ext = 'jpg'
        elif content[:4] == b'\x89PNG':
            ext = 'png'
        elif content[:4] == b'RIFF' and b'WEBP' in content[:12]:
            ext = 'webp'
        elif b'<svg' in content[:20]:
            ext = 'svg'
        else:
            ct = resp.headers.get('Content-Type', '').lower()
            if 'jpeg' in ct or 'jpg' in ct:
                ext = 'jpg'
            elif 'png' in ct:
                ext = 'png'
            elif 'webp' in ct:
                ext = 'webp'
            elif 'svg' in ct:
                ext = 'svg'
            else:
                ext = 'png'
        
        filepath = os.path.join(BADGES_DIR, f"{school_id}.{ext}")
        with open(filepath, 'wb') as f:
            f.write(content)
        
        return f"/static/images/badges/{school_id}.{ext}"
    except Exception as e:
        return None


def try_school_website(school_id, website):
    """从学校官网抓取校徽"""
    domain = get_domain(website)
    if not domain:
        return None
    
    base_url = website
    if not base_url.startswith('http'):
        base_url = 'https://' + base_url
    
    tried_urls = set()
    
    # 策略A: 直接获取 /favicon.ico
    favicon_url = f"{base_url.rstrip('/')}/favicon.ico"
    if favicon_url not in tried_urls:
        tried_urls.add(favicon_url)
        result = download_image_to_local(favicon_url, school_id, 1)
        if result:
            return result
    
    # 策略B: 从HTML中提取logo
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 查找og:image
            og_img = soup.find('meta', property='og:image')
            if og_img and og_img.get('content'):
                result = download_image_to_local(og_img['content'], school_id)
                if result:
                    return result
            
            # 查找Apple touch icon
            for rel in ['apple-touch-icon', 'apple-touch-icon-precomposed', 'icon', 'shortcut icon']:
                imgs = soup.find_all('link', rel=rel)
                for img in imgs:
                    href = img.get('href')
                    if href and not href.startswith('data:'):
                        full_url = urljoin(base_url, href)
                        result = download_image_to_local(full_url, school_id)
                        if result:
                            return result
            
            # 查找class/id含logo的img
            for sel in ['.logo img', '#logo', 'header .logo', '.school-logo img']:
                imgs = soup.select(sel)
                for img in imgs:
                    src = img.get('src') or img.get('data-src')
                    if src:
                        full_url = urljoin(base_url, src)
                        result = download_image_to_local(full_url, school_id)
                        if result:
                            return result
    except:
        pass
    
    # 策略C: 尝试 Google Favicon API (作为备用)
    try:
        favicon_api_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        result = download_image_to_local(favicon_api_url, school_id)
        if result:
            return result
    except:
        pass
    
    return None


# ========== 策略2: Wikipedia ==========

def try_wikipedia(school_id, name, name_cn):
    """从Wikipedia获取校徽"""
    search_name = name_cn if name_cn else name
    if not search_name:
        return None
    
    # 尝试英文名
    names_to_try = [search_name]
    if name and name != search_name:
        names_to_try.append(name)
    
    for query_name in names_to_try:
        try:
            # 搜索
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': f"{query_name} logo",
                'format': 'json',
                'origin': '*',
                'srlimit': 3
            }
            url = f"https://en.wikipedia.org/w/api.php?{requests.utils.urlencode(params)}"
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT)
            data = resp.json()
            
            for result in data.get('query', {}).get('search', []):
                title = result['title']
                # 获取图片
                img_params = {
                    'action': 'query',
                    'titles': title,
                    'prop': 'pageimages',
                    'pithumbsize': 500,
                    'format': 'json',
                    'origin': '*'
                }
                img_url = f"https://en.wikipedia.org/w/api.php?{requests.utils.urlencode(img_params)}"
                img_resp = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT)
                img_data = img_resp.json()
                
                pages = img_data.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    if page_id != '-1' and 'thumbnail' in page_info:
                        thumb_url = page_info['thumbnail']['source']
                        result = download_image_to_local(thumb_url, school_id)
                        if result:
                            return result
                break  # 只试第一个
            time.sleep(0.3)
        except:
            pass
    
    return None


# ========== 策略3: schooland.hk (香港学校) ==========

def try_schooland_hk(school_id, name):
    """从schooland.hk获取香港学校校徽"""
    slug = name.lower().replace(' ', '-').replace("'", '').replace('&', '')
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    
    for prefix in ['ss', 'ps']:
        url = f"https://www.schooland.hk/{prefix}/{slug}"
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}, timeout=TIMEOUT)
            if resp.status_code != 200:
                continue
            
            # 查找校徽图片
            matches = re.findall(r'https://www\.schooland\.hk/img/(ssb|psb)/[^"]+\.jpg', resp.text)
            if matches:
                result = download_image_to_local(matches[0], school_id)
                if result:
                    return result
            
            # 查找普通学校图片
            matches = re.findall(r'https://www\.schooland\.hk/img/(ss|ps)/[^"]+\.jpg', resp.text)
            if matches:
                result = download_image_to_local(matches[0], school_id)
                if result:
                    return result
        except:
            pass
        time.sleep(0.2)
    
    return None


# ========== 验证已有远程badge_url ==========

def verify_remote_url(badge_url):
    """验证远程URL是否仍然有效"""
    if not badge_url or badge_url.startswith('/'):
        return badge_url
    
    try:
        resp = requests.head(badge_url, headers=HEADERS, timeout=5, allow_redirects=True)
        if resp.status_code == 200:
            return badge_url
    except:
        pass
    return None


# ========== 主处理函数 ==========

def process_school(school_data):
    """处理单个学校，返回成功/失败信息"""
    school_id, name, name_cn, country, website, source = school_data
    
    local_path = None
    
    # 跳过没有名称的学校
    if not name and not name_cn:
        return (school_id, None, 'no_name')
    
    # 优先：直接从官网抓取
    if website and website.startswith('http'):
        local_path = try_school_website(school_id, website)
        if local_path:
            return (school_id, local_path, 'website')
        time.sleep(0.3)
    
    # 其次：schooland.hk (HK学校)
    if country == 'Hong Kong':
        local_path = try_schooland_hk(school_id, name)
        if local_path:
            return (school_id, local_path, 'schooland')
        time.sleep(0.3)
    
    # 最后：Wikipedia (大学优先)
    if 'university' in str(name).lower() or 'university' in str(name_cn).lower():
        local_path = try_wikipedia(school_id, name, name_cn)
        if local_path:
            return (school_id, local_path, 'wikipedia')
        time.sleep(0.3)
    
    return (school_id, None, 'failed')


def update_school_badge(school_id, badge_url):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        c = conn.cursor()
        c.execute("UPDATE schools SET badge_url = ? WHERE id = ? AND (badge_reviewed IS NULL OR badge_reviewed = 0)", (badge_url, school_id))
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        if 'locked' in str(e):
            time.sleep(1)
            conn = sqlite3.connect(DB_PATH, timeout=15)
            c = conn.cursor()
            c.execute("UPDATE schools SET badge_url = ? WHERE id = ? AND (badge_reviewed IS NULL OR badge_reviewed = 0)", (badge_url, school_id))
            conn.commit()
            conn.close()


def main(limit=200, verify_only=False):
    log("=" * 60)
    log("优化版校徽批量抓取 v2")
    log("=" * 60)
    
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    
    if verify_only:
        # 验证已有远程URL
        cursor.execute("""
            SELECT id, name, badge_url 
            FROM schools 
            WHERE badge_url IS NOT NULL AND badge_url != ''
            AND badge_url NOT LIKE '/static%%'
            AND badge_url NOT LIKE 'https://www.google.com%%'
            LIMIT ?
        """, (limit,))
    else:
        # 获取需要抓取校徽的学校（优先大学，跳过香港幼教/中小学）
        cursor.execute("""
            SELECT id, name, name_cn, country, website, source
            FROM schools 
            WHERE (badge_url IS NULL OR badge_url = '') AND (badge_reviewed IS NULL OR badge_reviewed = 0)
            AND website IS NOT NULL AND website != ''
            AND website LIKE 'http%%'
            -- 跳过香港幼教/中小学（基本无校徽资源）
            AND NOT (country = 'Hong Kong' AND level IN ('kindergarten', 'elementary', 'Primary', 'middle', 'Middle', 'Secondary'))
            ORDER BY 
                -- 优先处理大学（校徽资源丰富）
                CASE WHEN level IN ('university', 'University', 'Institute', 'College', 'college', 'Academy', 'academy', 'high_school', 'high') THEN 0
                     WHEN country IN ('United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 'France', 'Japan', 'South Korea', 'China') THEN 1
                     ELSE 2 END,
                RANDOM()
            LIMIT ?
        """, (limit,))
    
    schools = cursor.fetchall()
    log(f"处理学校数量: {len(schools)}")
    conn.close()
    time.sleep(0.5)  # Give any concurrent process time to release locks
    
    success_by_method = {'website': 0, 'schooland': 0, 'wikipedia': 0, 'verified': 0}
    failed = 0
    processed_ids = []
    checkpoint_interval = 10  # 每10个学校保存一次断点
    
    for i, school_data in enumerate(schools):
        school_id = school_data[0]
        
        if verify_only:
            school_id, name, badge_url = school_data
            verified = verify_remote_url(badge_url)
            if verified:
                success_by_method['verified'] += 1
                log(f"[{i+1}/{len(schools)}] ✓ 验证通过: {name[:40]}")
            else:
                # 下载失效，尝试重新获取
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT name, name_cn, country, website, source FROM schools WHERE id = ?", (school_id,))
                row = c.fetchone()
                conn.close()
                if row:
                    result = process_school((school_id,) + row)
                    if result[1]:
                        update_school_badge(school_id, result[1])
                        success_by_method[result[2]] += 1
                        log(f"[{i+1}/{len(schools)}] ↻ 重新获取成功: {row[0][:40]} [{result[2]}]")
                    else:
                        failed += 1
                        log(f"[{i+1}/{len(schools)}] ✗ 失效且无法恢复: {name[:40]}")
                else:
                    failed += 1
        else:
            result = process_school(school_data)
            if result[1]:
                update_school_badge(school_id, result[1])
                success_by_method[result[2]] += 1
                log(f"[{i+1}/{len(schools)}] ✓ [{result[2]}] {school_data[1][:40]}")
            else:
                failed += 1
                log(f"[{i+1}/{len(schools)}] ✗ {school_data[1][:40]}")
        
        # 每10个学校保存一次断点
        if (i + 1) % checkpoint_interval == 0:
            log(f"--- 进度: {i+1}/{len(schools)} (已保存断点) ---")
        
        # 每次处理完都更新已处理ID列表
        processed_ids.append(school_id)
        if (i + 1) % checkpoint_interval == 0:
            save_checkpoint(processed_ids)
            log(f"--- 进度: {i+1}/{len(schools)} ---")
    
    log("=" * 60)
    log("执行结果")
    log("=" * 60)
    total_success = sum(success_by_method.values())
    for method, count in success_by_method.items():
        if count > 0:
            log(f"  {method}: +{count}")
    log(f"  失败: {failed}")
    log(f"  总成功: +{total_success}")
    
    # 统计
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM schools WHERE badge_url IS NOT NULL AND badge_url != ''")
    total_with_badge = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM schools")
    total = c.fetchone()[0]
    conn.close()
    log(f"总计: {total_with_badge}/{total} 已有校徽 ({100*total_with_badge/total:.1f}%)")
    clear_checkpoint()  # 完成后清除断点
    log("=" * 60)


if __name__ == '__main__':
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    verify = '--verify' in sys.argv
    main(limit=limit, verify_only=verify)
