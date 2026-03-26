#!/usr/bin/env python3
"""
Download all external badge URLs to local storage and update database.
Enhanced with Wikimedia rate-limit handling and retry-backoff.
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
MAX_RETRIES = 4
REQUEST_TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 1.5  # base delay between requests
DELAY_AFTER_429 = 10          # delay after receiving 429

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Setup logging
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
    """Extract file extension from URL."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico']:
        if ext in path:
            return ext
    return '.png'


def is_wikimedia_url(url):
    """Check if URL is from Wikimedia Commons (most commonly rate-limited)."""
    return 'wikimedia.org' in url


def download_badge(school_id, url, session, retry_count=0):
    """Download a single badge image with retry-backoff logic."""
    try:
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        
        if response.status_code == 429:
            wait_time = int(response.headers.get('Retry-After', DELAY_AFTER_429))
            log.warning(f"School {school_id}: HTTP 429 (rate-limited), waiting {wait_time}s")
            if retry_count < MAX_RETRIES - 1:
                time.sleep(wait_time)
                return download_badge(school_id, url, session, retry_count + 1)
            return None
            
        if response.status_code == 200 and len(response.content) > 500:
            ext = get_extension_from_url(url)
            filename = f"{school_id}{ext}"
            filepath = os.path.join(BADGES_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        else:
            log.warning(f"School {school_id}: HTTP {response.status_code}, size={len(response.content)}")
            return None
            
    except requests.exceptions.Timeout:
        if retry_count < MAX_RETRIES - 1:
            log.info(f"School {school_id}: Timeout, retry {retry_count + 1}")
            time.sleep(2 ** retry_count)
            return download_badge(school_id, url, session, retry_count + 1)
    except Exception as e:
        if retry_count < MAX_RETRIES - 1:
            log.info(f"School {school_id}: {e}, retry {retry_count + 1}")
            time.sleep(2 ** retry_count)
            return download_badge(school_id, url, session, retry_count + 1)
        log.error(f"School {school_id}: Failed after {MAX_RETRIES} attempts - {e}")
        return None


def main():
    log.info("")
    log.info("=" * 60)
    log.info(f"Badge download started at {datetime.now()}")
    log.info("=" * 60)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT id, name, badge_url FROM schools WHERE badge_url LIKE 'https://%'")
    schools = cur.fetchall()
    total = len(schools)
    log.info(f"Total external URLs to download: {total}")

    success_count = 0
    fail_count = 0
    skip_count = 0
    rate_limited_count = 0

    session = requests.Session()
    session.headers.update(HEADERS)

    for idx, (school_id, name, url) in enumerate(schools):
        # Check if local file already exists with reasonable size
        ext = get_extension_from_url(url)
        local_filename = f"{school_id}{ext}"
        local_path = os.path.join(BADGES_DIR, local_filename)

        if os.path.exists(local_path) and os.path.getsize(local_path) > 500:
            log.debug(f"School {school_id}: Already exists ({os.path.getsize(local_path)} bytes), skipping")
            skip_count += 1
        else:
            log.info(f"[{idx+1}/{total}] School {school_id} ({name[:35]}): {url[:80]}")
            filepath = download_badge(school_id, url, session)
            
            if filepath:
                local_url = f"/static/images/badges/{school_id}{ext}"
                cur.execute("UPDATE schools SET badge_url = ? WHERE id = ?", (local_url, school_id))
                conn.commit()
                success_count += 1
                log.info(f"  ✓ -> {local_filename} ({os.path.getsize(filepath)} bytes)")
            else:
                fail_count += 1
                log.error(f"  ✗ FAILED")

        # Polite delay between requests
        delay = DELAY_BETWEEN_REQUESTS
        if is_wikimedia_url(url):
            delay = 2.5  # longer delay for Wikimedia
        time.sleep(delay)

        # Progress checkpoint every 100 items
        if (idx + 1) % 100 == 0:
            log.info(f"\n=== Checkpoint at {idx+1}/{total}: {success_count} ok, {fail_count} fail, {skip_count} skip ===\n")

    log.info("")
    log.info("=" * 60)
    log.info(f"Download complete at {datetime.now()}")
    log.info(f"Results: {success_count} downloaded, {fail_count} failed, {skip_count} skipped (already existed)")
    log.info("=" * 60)

    conn.close()


if __name__ == "__main__":
    main()
