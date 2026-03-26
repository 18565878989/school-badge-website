#!/usr/bin/env python3
"""
Scrape campus images for top Asian universities from Wikimedia Commons / Wikipedia.
Uses browser-like headers to avoid 403 blocking.
"""

import os
import re
import time
import sqlite3
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import quote

BASE_DIR = "/Users/wangfeng/.openclaw/workspace/school-badge-website"
STATIC_DIR = os.path.join(BASE_DIR, "static/images/campus")
DB_PATH = os.path.join(BASE_DIR, "database.db")

WIKI_API = "https://en.wikipedia.org/w/api.php"

# Browser-like headers (required by Wikimedia to avoid 403)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://en.wikipedia.org/",
}

session = requests.Session()
session.headers.update(HEADERS)
adapter = HTTPAdapter(max_retries=3, pool_connections=10, pool_maxsize=10)
session.mount("https://", adapter)

SCHOOL_NAMES = {
    13859: "Tsinghua University",
    13858: "Peking University",
    20692: "Fudan University",
    20694: "Shanghai Jiao Tong University",
    20693: "Zhejiang University",
    7136:  "USTC",
    20723: "HKUST",
    11396: "National Taiwan University",
    17881: "NUS",
    13200: "NTU Singapore",
}

WIKI_PAGES = {
    13859: "Tsinghua_University",
    13858: "Peking_University",
    20692: "Fudan_University",
    20694: "Shanghai_Jiao_Tong_University",
    20693: "Zhejiang_University",
    7136:  "University_of_Science_and_Technology_of_China",
    20723: "Hong_Kong_University_of_Science_and_Technology",
    11396: "National_Taiwan_University",
    17881: "National_University_of_Singapore",
    13200: "Nanyang_Technological_University",
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def get_wiki_images(wiki_title, limit=50):
    """Get all image filenames from a Wikipedia article."""
    all_imgs = []
    continue_token = None
    
    while len(all_imgs) < limit:
        params = {
            "action": "query",
            "titles": wiki_title,
            "prop": "images",
            "imlimit": 50,
            "format": "json",
        }
        if continue_token:
            params["imcontinue"] = continue_token
        
        try:
            resp = session.get(WIKI_API, params=params, timeout=15)
            if resp.status_code != 200:
                break
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for page_data in pages.values():
                imgs = page_data.get("images", [])
                for img in imgs:
                    all_imgs.append(img["title"])
            
            continue_token = data.get("continue", {}).get("imcontinue")
            if not continue_token:
                break
        except Exception as e:
            log(f"  Error: {e}")
            break
    
    return all_imgs

def get_image_url_and_size(filename):
    """Get direct URL and size for a Wikipedia image."""
    params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url|size",
        "iiurlwidth": 1920,
        "format": "json",
    }
    try:
        resp = session.get(WIKI_API, params=params, timeout=15)
        if resp.status_code != 200:
            return "", 0
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page_data in pages.values():
            info = page_data.get("imageinfo", [{}])[0]
            # Prefer thumburl for 1920px, fallback to url
            url = info.get("thumburl", "") or info.get("url", "")
            size = info.get("size", 0)
            return url, size
    except Exception as e:
        log(f"  Error getting info for {filename}: {e}")
    return "", 0

def filter_campus_images(images, school_name):
    """Filter out logos/flags/small icons, keep campus images."""
    exclude_patterns = [
        r"logo", r"flag", r"seal", r"crest", r"coat", r"icon",
        r"banner", r"Emblem", r"symbol", r"badge", r"shield",
        r"signature", r"Monogram", r"wordmark", r"letter",
        r"Location\b", r"\bMap\b", r"diagram",
        r"Portrait\b", r"Headquarters",
        r"sparker", r"pictogram", r"COVID",
        r"\d+px", r"Small\b", r"Tiny", r"\d+x\d+",
        r"blazon", r"Pennant", r"ensign",
        r"Green Arrow", r"Arrow Up",
        r"\d{4}px", r"Wiki", r"wiki",
    ]
    
    campus_patterns = [
        r"Campus", r"campus",
        r"Gate", r"gate", r"Gateway",
        r"Library", r"library",
        r"Building", r"building",
        r"Arch", r"arch",
        r"View", r"view", r"Scenery",
        r"Aerial", r"aerial", r"Panorama",
        r"Entrance", r"entrance", r"Exterior",
        r"Tower", r"tower", r"Clock",
        r"Courtyard", r"courtyard", r"Lawn",
        r"Lake", r"lake", r"Garden",
        r"Tsinghua", r"Peking", r"Fudan", r"SJTU", r"Zhejiang",
        r"HKUST", r"NTU\b", r"NUS\b", r"USTC",
        r"University", r"College",
        r"Dormitory", r"dormitory", r"Residence",
        r"Walkway", r"walkway",
        r"Green\b", r"Field", r"field",
        r"Gymnasium", r"Swimming",
        r"Plaza", r"plaza", r"Square",
        r"Reflection", r"Sunset", r"Sunrise",
        r"Night", r"Evening",
        r"樱花", r"梧桐", r"银杏",
        r"Yunnan", r"Nanyang",
        r"Zhongguo", r"China",
    ]
    
    filtered = []
    for img in sorted(images):
        name = img.replace("File:", "")
        
        # Exclude non-matching
        skip = False
        for pat in exclude_patterns:
            if re.search(pat, name, re.IGNORECASE):
                skip = True
                break
        if skip:
            continue
        
        # Must match campus patterns
        for pat in campus_patterns:
            if re.search(pat, name, re.IGNORECASE):
                filtered.append(img)
                break
    
    return filtered

def download_image(url, filepath):
    """Download image from URL, return True if successful."""
    if not url:
        return False
    try:
        resp = session.get(url, timeout=30)
        if resp.status_code != 200:
            log(f"    HTTP {resp.status_code}")
            return False
        
        content = resp.content
        if len(content) < 5000:
            log(f"    Too small: {len(content)} bytes")
            return False
        
        with open(filepath, "wb") as f:
            f.write(content)
        
        actual = os.path.getsize(filepath)
        if actual < 5000:
            os.remove(filepath)
            log(f"    File too small after save: {actual}")
            return False
        
        log(f"    SUCCESS ({actual//1024}KB)")
        return True
    except Exception as e:
        log(f"    Exception: {e}")
        return False

def count_images(school_dir):
    if not os.path.exists(school_dir):
        return 0
    return len([f for f in os.listdir(school_dir) 
                if re.match(rf"school_\d+_\d+\.(jpg|jpeg|png|webp)", f)])

def update_db(school_id, paths_list):
    paths_str = ",".join(paths_list)
    for attempt in range(3):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute(
                "UPDATE schools SET campus_image = ?, campus_updated = 'Y' WHERE id = ?",
                (paths_str, school_id)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.OperationalError as e:
            if "locked" in str(e) and attempt < 2:
                time.sleep(3)
            else:
                log(f"  DB error: {e}")
                return False
    return False

def scrape_school(school_id, wiki_title, needed_slots, school_name):
    log(f"\n{'='*60}")
    log(f"Scraping: {school_name} (school_{school_id})")
    log(f"Need slots: {needed_slots}")
    
    school_dir = os.path.join(STATIC_DIR, f"school_{school_id}")
    os.makedirs(school_dir, exist_ok=True)
    
    log(f"Fetching images from: {wiki_title}")
    all_images = get_wiki_images(wiki_title, limit=100)
    log(f"Total images found: {len(all_images)}")
    
    campus_imgs = filter_campus_images(all_images, school_name)
    log(f"Campus images after filter: {len(campus_imgs)}")
    for i, img in enumerate(campus_imgs[:12]):
        log(f"  [{i}] {img}")
    
    # Find images that already exist
    existing = {}
    for fname in os.listdir(school_dir):
        m = re.match(rf"school_{school_id}_(\d+)\.(jpg|jpeg|png|webp)", fname)
        if m:
            slot = int(m.group(1))
            existing[slot] = fname
    
    downloaded_slots = []
    
    for slot in needed_slots:
        if slot in existing:
            log(f"  Slot {slot}: already exists ({existing[slot]}), skipping")
            downloaded_slots.append(slot)
            continue
        
        filepath = os.path.join(school_dir, f"school_{school_id}_{slot}.webp")
        
        found = False
        tried = 0
        for img_title in campus_imgs:
            fname = img_title.replace("File:", "")
            tried += 1
            
            url, wiki_size = get_image_url_and_size(fname)
            if not url:
                continue
            
            log(f"  Slot {slot} [{tried}]: {fname} ({wiki_size//1024}KB)")
            
            ok = download_image(url, filepath)
            if ok:
                downloaded_slots.append(slot)
                found = True
                break
            time.sleep(0.5)
        
        if not found:
            log(f"  Slot {slot}: No suitable image found")
        
        time.sleep(1)
    
    # Update DB with all images
    files = sorted([f for f in os.listdir(school_dir) 
                   if re.match(rf"school_{school_id}_\d+\.(jpg|jpeg|png|webp)", f)])
    if files:
        base = f"/static/images/campus/school_{school_id}/"
        paths = [base + f for f in files]
        update_db(school_id, paths)
        log(f"DB updated: {files}")
    
    return downloaded_slots

def main():
    log("=" * 60)
    log("Campus Image Scraper - Top Asian Universities")
    log("=" * 60)
    
    schools = {
        13859: ("Tsinghua_University", [1]),
        13858: ("Peking_University", [1]),
        20692: ("Fudan_University", [1, 2]),
        20694: ("Shanghai_Jiao_Tong_University", list(range(1, 7))),
        20693: ("Zhejiang_University", [2, 3, 4, 5, 6]),
        7136:  ("University_of_Science_and_Technology_of_China", [1, 2]),
        20723: ("Hong_Kong_University_of_Science_and_Technology", [1]),
        11396: ("National_Taiwan_University", [2, 3, 4, 5, 6]),
        17881: ("National_University_of_Singapore", [1]),
        13200: ("Nanyang_Technological_University", [1, 2]),
    }
    
    results = {}
    for school_id, (wiki_title, needed) in schools.items():
        school_name = SCHOOL_NAMES.get(school_id, f"School {school_id}")
        downloaded = scrape_school(school_id, wiki_title, needed, school_name)
        results[school_id] = downloaded
        time.sleep(3)
    
    log("\n" + "=" * 60)
    log("COMPLETE - Summary")
    log("=" * 60)
    for school_id, downloaded in results.items():
        name = SCHOOL_NAMES.get(school_id, f"School {school_id}")
        total = count_images(os.path.join(STATIC_DIR, f"school_{school_id}"))
        log(f"  {name}: {len(downloaded)} new, {total} total")

if __name__ == "__main__":
    main()
