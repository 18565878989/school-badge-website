#!/bin/bash
# 校园图片Cron脚本 (改进版)
# 避免与校徽抓取冲突

LOG_FILE="/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/campus_cron_v2.log"
PYTHON="/usr/bin/python3"
SCRIPT="/Users/wangfeng/.openclaw/workspace/school-badge-website/scripts/batch_fetch_campus.py"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Campus cron started" >> "$LOG_FILE"

# 检查是否有其他抓取脚本在运行
while pgrep -f "optimized_badge_batch.py" > /dev/null || pgrep -f "batch_fetch_campus.py" > /dev/null; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Another crawler running, waiting..." >> "$LOG_FILE"
    sleep 30
done

# 运行校园图片抓取
$PYTHON $SCRIPT >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Campus cron finished" >> "$LOG_FILE"
