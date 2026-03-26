#!/usr/bin/env python3
"""
Download non-Wikimedia external badge URLs using curl (better timeout handling).
"""
import os
import sqlite3
import subprocess
import time
import logging
from urllib.parse import urlparse
from datetime import datetime

PROJECT_DIR = "/Users/wangfeng/.openclaw/workspace/school-badge-website"
BADGES_DIR = os.path.join(PROJECT_DIR, "static/images/badges")
LOG_FILE = os.path.join(PROJECT_DIR, "logs/badge_download.log")
DB_FILE = os.path.join(PROJECT_DIR, "database.db")

MAX_TIMEOUT = 15  # seconds per request (curl handles this reliably)
DELAY_BETWEEN_REQUESTS = 1.0

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


def download_with_curl(school_id, url):
    """Download badge using curl with reliable timeout."""
    ext = get_extension_from_url(url)
    outfile = os.path.join(BADGES_DIR, f"{school_id}{ext}")
    
    cmd = [
        'curl', '-s', '-L', '-o', outfile,
        '-m', str(MAX_TIMEOUT),  # max time in seconds
        '-w', '%{http_code}:%{size_download}',
        '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
        '--connect-timeout', '8',
        '--max-filesize', '5000000',  # 5MB max
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=MAX_TIMEOUT + 10)
        output = result.stdout.strip()
        
        if result.returncode != 0:
            return None, f"curl error (exit {result.returncode})"
        
        if ':' in output:
            status_code, size = output.split(':')
            status_code = int(status_code)
            size = int(size)
            
            if status_code == 200 and size > 500:
                return outfile, None
            elif status_code == 404:
                return None, f"HTTP 404"
            elif status_code == 403:
                return None, f"HTTP 403"
            elif status_code == 429:
                wait = 10
                log.warning(f"School {school_id}: HTTP 429, waiting {wait}s")
                time.sleep(wait)
                return download_with_curl(school_id, url)  # retry once
            else:
                return None, f"HTTP {status_code} ({size} bytes)"
        
        # Fallback: check file size
        if os.path.exists(outfile) and os.path.getsize(outfile) > 500:
            return outfile, None
        return None, f"No output ({output[:30]})"
        
    except subprocess.TimeoutExpired:
        return None, f"Timeout after {MAX_TIMEOUT}s"
    except Exception as e:
        return None, str(e)


def main():
    log.info("")
    log.info("=" * 60)
    log.info(f"Curl-based download started at {datetime.now()}")
    log.info("=" * 60)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

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
        # Skip if local file exists
        ext = get_extension_from_url(url)
        fpath = os.path.join(BADGES_DIR, f"{school_id}{ext}")
        if os.path.exists(fpath) and os.path.getsize(fpath) > 500:
            skip += 1
            log.debug(f"[{idx+1}/{total}] School {school_id}: already exists, skip")
        else:
            log.info(f"[{idx+1}/{total}] School {school_id} ({name[:30]}): {url[:70]}")
            filepath, err = download_with_curl(school_id, url)
            
            if filepath:
                local_url = f"/static/images/badges/{school_id}{ext}"
                cur.execute("UPDATE schools SET badge_url = ? WHERE id = ?", (local_url, school_id))
                conn.commit()
                success += 1
                sz = os.path.getsize(filepath)
                log.info(f"  ✓ -> {school_id}{ext} ({sz} bytes)")
            else:
                fail += 1
                log.error(f"  ✗ Failed: {err}")

        time.sleep(DELAY_BETWEEN_REQUESTS)

        if (idx + 1) % 50 == 0:
            log.info(f"\n--- Checkpoint {idx+1}/{total}: {success} ok, {fail} fail, {skip} skip ---")

    conn.commit()
    log.info("")
    log.info("=" * 60)
    log.info(f"Complete at {datetime.now()}")
    log.info(f"Results: {success} downloaded, {fail} failed, {skip} skipped")
    log.info("=" * 60)
    conn.close()


if __name__ == "__main__":
    main()
