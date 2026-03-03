#!/usr/bin/env python3
"""
图片收集定时任务
每天自动收集校徽和校园图片
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/wangfeng/.openclaw/workspace/school-badge-website')

from skills.image_collect import collect_badges, collect_campus

def main():
    print(f"=== 图片收集任务开始 {datetime.now()} ===")
    
    # 收集校徽 (每次50个)
    print("\n[1/2] 收集校徽...")
    badges_collected = collect_badges(limit=50)
    print(f"校徽收集完成: {badges_collected}")
    
    # 收集校园图片 (每次30个)
    print("\n[2/2] 收集校园图片...")
    campus_collected = collect_campus(limit=30)
    print(f"校园图片收集完成: {campus_collected}")
    
    print(f"\n=== 任务完成 ===")
    print(f"校徽: +{badges_collected}")
    print(f"校园图: +{campus_collected}")

if __name__ == "__main__":
    from datetime import datetime
    main()
