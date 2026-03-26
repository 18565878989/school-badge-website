#!/usr/bin/env python3
"""
Download non-Wikimedia external badge URLs to local storage.
Wikimedia URLs are excluded (they're blocked from this IP).
"""
import os
import sqlite3
import time
import logging
import requests
from urllib.parse import urlparse
from datetime import datetime

PROJECT_DIR = "/Users/wangfeng/.openclaw/workspace/school-badge-website"
BADGES_DIR = os.path.join(PROJECT_DIR, "static/images/badges")
LOG_FILE = os.path.join(PROJECT_DIR, "logs/badge_download.log")
DB_FILE = os.path.join(PROJECT_DIR, "database.db")

BATCH_SIZE = 50
MAX_RETRIES = 3
REQUEST_TIMEOUT = 12
DELAY_BETWEEN_REQUESTS = 1.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def get_extension_from_url(url):
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico']:
        if ext in path:
            return ext
    return '.png'


def download_badge(school_id, url, retry_count=0):
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if response.status_code == 200 and len(response.content) > 500:
            ext = get_extension_from_url(url)
            filepath = os.path.join(BADGES_DIR, f"{school_id}{ext}")
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath, ext
        elif response.status_code == 404:
            return None, None  # URL gone
        elif response.status_code == 429:
            wait = int(response.headers.get('Retry-After', 5))
            if retry_count < MAX_RETRIES - 1:
                log.warning(f"School {school_id}: 429, waiting {wait}s before retry")
                time.sleep(wait)
                return download_badge(school_id, url, retry_count + 1)
            return None, None
        else:
            log.warning(f"School {school_id}: HTTP {response.status_code}")
            return None, None
    except requests.exceptions.Timeout:
        if retry_count < MAX_RETRIES - 1:
            time.sleep(2 ** retry_count)
            return download_badge(school_id, url, retry_count + 1)
        return None, None
    except Exception as e:
        if retry_count < MAX_RETRIES - 1:
            time.sleep(2 ** retry_count)
            return download_badge(school_id, url, retry_count + 1)
        log.error(f"School {school_id}: {e}")
        return None, None


def main():
    log.info("")
    log.info("=" * 60)
    log.info(f"Non-Wikimedia badge download started at {datetime.now()}")
    log.info("=" * 60)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Only non-Wikimedia external URLs
    cur.execute("""
        SELECT id, name, badge_url 
        FROM schools 
        WHERE badge_url LIKE 'https://%' 
          AND badge_url NOT LIKE '%wikimedia.org%'
        ORDER BY id
    """)
    schools = cur.fetchall()
    total = len(schools)
    log.info(f"Non-Wikimedia URLs to download: {total}")

    success = 0
    fail = 0
    skip = 0

    for idx, (school_id, name, url) in enumerate(schools):
        # Check if local file already exists
        ext = get_extension_from_url(url)
        fpath = os.path.join(BADGES_DIR, f"{school_id}{ext}")
        if os.path.exists(fpath) and os.path.getsize(fpath) > 500:
            skip += 1
            log.debug(f"[{idx+1}/{total}] School {school_id}: already exists, skip")
        else:
            log.info(f"[{idx+1}/{total}] School {school_id} ({name[:30]}): {url[:70]}")
            result = download_badge(school_id, url)
            if result[0]:
                filepath, ext = result
                local_url = f"/static/images/badges/{school_id}{ext}"
                cur.execute("UPDATE schools SET badge_url = ? WHERE id = ?", (local_url, school_id))
                conn.commit()
                success += 1
                log.info(f"  ✓ -> {school_id}{ext} ({os.path.getsize(filepath)} bytes)")
            else:
                fail += 1
                log.error(f"  ✗ Failed")

        time.sleep(DELAY_BETWEEN_REQUESTS)

        if (idx + 1) % 50 == 0:
            log.info(f"\n--- Checkpoint {idx+1}/{total}: {success} ok, {fail} fail, {skip} skip ---")

    # Final summary
    conn.commit()
    log.info("")
    log.info("=" * 60)
    log.info(f"Complete at {datetime.now()}")
    log.info(f"Results: {success} downloaded, {fail} failed, {skip} skipped")
    log.info("=" * 60)

    conn.close()


if __name__ == "__main__":
    main()
