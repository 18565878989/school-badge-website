#!/bin/bash
# 每2小时运行一次抓取校徽和校园风光
cd /Users/wangfeng/.openclaw/workspace/school-badge-website
/usr/bin/python3 scripts/batch_fetch_campus.py >> logs/campus_fetch.log 2>&1
