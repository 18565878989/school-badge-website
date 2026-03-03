#!/usr/bin/env python3
"""
图片收集定时任务
每天自动收集校徽和校园图片
"""
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/Users/wangfeng/.openclaw/workspace/school-badge-website')

# 禁用 SSL 警告
import warnings
warnings.filterwarnings('ignore')

from skills.image_collect import collect_badges, collect_campus

LOG_FILE = '/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/image_collect.log'
REPORT_FILE = '/Users/wangfeng/.openclaw/workspace/school-badge-website/logs/image_collect_report.log'

def log(msg):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def main():
    start_time = datetime.now()
    log("=" * 50)
    log("图片收集任务开始")
    log("=" * 50)
    
    # 收集校徽 (每次50个)
    log("[1/2] 收集校徽...")
    try:
        badges_collected = collect_badges(limit=50)
        log(f"校徽收集完成: +{badges_collected}")
    except Exception as e:
        log(f"校徽收集失败: {e}")
        badges_collected = 0
    
    # 收集校园图片 (每次30个)
    log("[2/2] 收集校园图片...")
    try:
        campus_collected = collect_campus(limit=30)
        log(f"校园图片收集完成: +{campus_collected}")
    except Exception as e:
        log(f"校园图片收集失败: {e}")
        campus_collected = 0
    
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    
    # 生成报告
    log("=" * 50)
    log("任务完成 - 执行报告")
    log("=" * 50)
    log(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"执行时长: {duration} 秒")
    log("-" * 50)
    log(f"校徽收集: +{badges_collected}")
    log(f"校园图片: +{campus_collected}")
    log(f"总计新增: +{badges_collected + campus_collected}")
    log("=" * 50)
    
    # 同时输出到报告文件
    with open(REPORT_FILE, 'a') as f:
        f.write("\n" + "=" * 50 + "\n")
        f.write(f"图片收集报告 - {end_time.strftime('%Y-%m-%d')}\n")
        f.write("=" * 50 + "\n")
        f.write(f"校徽: +{badges_collected}\n")
        f.write(f"校园图: +{campus_collected}\n")
        f.write(f"总计: +{badges_collected + campus_collected}\n")

if __name__ == "__main__":
    main()
