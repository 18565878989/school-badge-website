#!/bin/bash
# 校徽批量抓取Cron脚本
# 避免与 campus/batch_fetch_campus.py 冲突（每4小时运行一次）

LOG_FILE="/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/badge_cron.log"
PYTHON="/usr/bin/python3"
SCRIPT="/Users/wangfeng/.openclaw/workspace/school-badge-website/scripts/optimized_badge_batch.py"
DB="/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Badge cron started" >> "$LOG_FILE"

# 检查 batch_fetch_campus.py 是否在运行（避免数据库锁）
while pgrep -f "batch_fetch_campus.py" > /dev/null; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] batch_fetch_campus.py is running, waiting..." >> "$LOG_FILE"
    sleep 60
done

# 运行校徽抓取 (400所学校)
$PYTHON $SCRIPT 400 >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Badge cron finished" >> "$LOG_FILE"
