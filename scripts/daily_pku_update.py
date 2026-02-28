#!/usr/bin/env python3
"""
北京大学校徽和校园风光定时抓取脚本
每天自动从北京大学官网抓取校徽和校园图片并更新数据库
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import sqlite3
import glob
import re
from datetime import datetime

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
BADGE_DIR = os.path.join(BASE_DIR, 'static/images/badges')
CAMPUS_DIR = os.path.join(BASE_DIR, 'static/images/campus/peking_university')

# 确保目录存在
os.makedirs(BADGE_DIR, exist_ok=True)
os.makedirs(CAMPUS_DIR, exist_ok=True)

# 北京大学相关学校ID
PEKING_UNIVERSITY_IDS = [20691]  # 主校区

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


def log(message):
    """日志输出"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def download_badge():
    """从北京大学官网下载校徽"""
    log("开始下载北京大学校徽...")
    
    # 尝试多个可能的校徽URL
    badge_urls = [
        "https://www.pku.edu.cn/pku_logo_red.png",
        "https://www.pku.edu.cn/pku_logo.png",
        "https://english.pku.edu.cn/Public/logo.png",
    ]
    
    success = False
    for url in badge_urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 1000:
                # 保存校徽
                badge_path = os.path.join(BADGE_DIR, 'peking_university.png')
                with open(badge_path, 'wb') as f:
                    f.write(resp.content)
                
                # 更新数据库
                conn = sqlite3.connect(DATABASE_PATH)
                conn.execute("""
                    UPDATE schools 
                    SET badge_url = '/static/images/badges/peking_university.png'
                    WHERE id = ?
                """, (PEKING_UNIVERSITY_IDS[0],))
                conn.commit()
                conn.close()
                
                log(f"✅ 校徽已更新: {badge_path} ({len(resp.content)} bytes)")
                success = True
                break
        except Exception as e:
            log(f"⚠️ 尝试 {url} 失败: {e}")
            continue
    
    if not success:
        log("❌ 校徽下载失败")
    
    return success


def download_campus_images():
    """从北京大学官网下载校园风光图片"""
    log("开始下载北京大学校园图片...")
    
    # 英文版网站图片
    campus_urls = [
        "https://english.pku.edu.cn/Uploads/Bden/Picture/2024/04/30/s663039e983f60.jpg",
        "https://english.pku.edu.cn/Uploads/Bden/Picture/2024/03/05/s65e6d6437516a.jpg",
        "https://english.pku.edu.cn/Uploads/Bden/Picture/2023/12/01/s656992debe8e5.jpg",
        "https://english.pku.edu.cn/Uploads/Bden/Picture/2023/11/15/s65547a301db5a.jpg",
        "https://english.pku.edu.cn/Uploads/Bden/Picture/2024/06/18/s6671239069653.jpg",
        "https://english.pku.edu.cn/Uploads/Bden/Picture/2024/06/18/s66712bd952b17.jpg",
        "https://english.pku.edu.cn/Uploads/Bden/Picture/2023/11/15/s65547d7d436b4.jpg",
        "https://english.pku.edu.cn/Uploads/Bden/Picture/2021/09/09/s6139bab588092_1845_1173_40_124.jpg",
    ]
    
    downloaded = []
    for i, url in enumerate(campus_urls, 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 1000:
                filename = f"pku_campus_{i}.jpg"
                filepath = os.path.join(CAMPUS_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                downloaded.append(f"/static/images/campus/peking_university/{filename}")
                log(f"✅ 下载: {filename} ({len(resp.content)} bytes)")
        except Exception as e:
            log(f"❌ 下载失败 {url}: {e}")
    
    if downloaded:
        # 更新数据库
        campus_image_str = ','.join(downloaded)
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("""
            UPDATE schools 
            SET campus_image = ?
            WHERE id = ?
        """, (campus_image_str, PEKING_UNIVERSITY_IDS[0]))
        conn.commit()
        conn.close()
        log(f"✅ 校园图片已更新 ({len(downloaded)} 张)")
        return True
    else:
        log("❌ 校园图片下载失败")
        return False


def fetch_latest_images():
    """从官网动态获取最新图片列表"""
    log("尝试从官网获取最新图片列表...")
    
    try:
        # 获取英文版首页
        resp = requests.get('https://english.pku.edu.cn/', headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            return False
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        images = soup.find_all('img')
        
        new_urls = []
        for img in images:
            src = img.get('src', '')
            # 查找校园相关的图片（通常在 Uploads/Bden/Picture 目录下）
            if 'Uploads' in src and ('Picture' in src or 'picture' in src):
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://english.pku.edu.cn' + src
                # 过滤掉图标和logo
                if any(kw in src.lower() for kw in ['campus', 'view', 'photo', 'building', ' scenery']) or 'Picture' in src:
                    if src not in new_urls:
                        new_urls.append(src)
        
        return new_urls[:8]  # 最多返回8张
    except Exception as e:
        log(f"⚠️ 获取最新图片列表失败: {e}")
        return None


def main():
    log("=" * 50)
    log("开始北京大学定时抓取任务")
    log("=" * 50)
    
    # 1. 下载/更新校徽
    download_badge()
    
    # 2. 下载/更新校园图片
    download_campus_images()
    
    log("=" * 50)
    log("任务完成")
    log("=" * 50)


if __name__ == '__main__':
    main()
