#!/usr/bin/env python3
"""
使用Selenium从学校官网抓取数据 - 改进版
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
import sqlite3
import re
import time
import json

def get_driver():
    """初始化Chrome浏览器"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    chrome_options.add_argument('--enable-javascript')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(10)
        return driver
    except WebDriverException as e:
        print(f"浏览器启动失败: {e}")
        return None

def extract_from_page(driver):
    """从当前页面提取信息"""
    data = {
        'motto': None,
        'principal': None,
        'address': None
    }
    
    page_text = driver.find_element(By.TAG_NAME, 'body').text
    
    # 提取校训 - 多种模式
    motto_patterns = [
        r'校訓[：:\s]+([^\n。]{2,50})',
        r'办学宗旨[：:\s]+([^\n。]{2,50})',
        r'校训[：:\s]+([^\n。]{2,50})',
        r'Motto[：:\s]+([^\n。]{2,50})',
    ]
    for pattern in motto_patterns:
        match = re.search(pattern, page_text)
        if match:
            motto = match.group(1).strip()
            if 2 < len(motto) < 50:
                data['motto'] = motto
                break
    
    # 提取校长 - 多种模式
    principal_patterns = [
        r'校長[：:\s]+([^\n。]{2,30})',
        r'校长[：:\s]+([^\n。]{2,30})',
        r'校監[：:\s]+([^\n。]{2,30})',
        r'Principal[：:\s]+([^\n。]{2,30})',
        r'Headmaster[：:\s]+([^\n。]{2,30})',
        r'Headmistress[：:\s]+([^\n。]{2,30})',
    ]
    for pattern in principal_patterns:
        match = re.search(pattern, page_text)
        if match:
            principal = match.group(1).strip()
            if 1 < len(principal) < 30:
                data['principal'] = principal
                break
    
    # 提取地址
    address_patterns = [
        r'地址[：:\s]+([^\n。]{5,80})',
        r'校址[：:\s]+([^\n。]{5,80})',
        r'Address[：:\s]+([^\n。]{5,80})',
        r'Location[：:\s]+([^\n。]{5,80})',
    ]
    for pattern in address_patterns:
        match = re.search(pattern, page_text)
        if match:
            address = match.group(1).strip()
            if 5 < len(address) < 80:
                data['address'] = address
                break
    
    return data

def scrape_schools(limit=20):
    """抓取学校数据"""
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 获取有官网的中学
    c.execute(f"""
        SELECT id, name, name_cn, website
        FROM schools 
        WHERE region = 'Hong Kong' 
        AND level = 'middle'
        AND website IS NOT NULL 
        AND website != ''
        AND website LIKE 'http%'
        AND (motto IS NULL OR motto = '' OR principal IS NULL OR principal = '')
        ORDER BY name_cn
        LIMIT {limit}
    """)
    
    schools = c.fetchall()
    print(f"准备从 {len(schools)} 所中学抓取数据")
    
    driver = get_driver()
    if not driver:
        conn.close()
        return 0
    
    results = []
    updated = 0
    
    try:
        for i, (school_id, name, name_cn, website) in enumerate(schools, 1):
            print(f"[{i}/{len(schools)}] {name_cn or name}")
            print(f"  → {website}")
            
            try:
                driver.get(website)
                time.sleep(3)  # 等待JavaScript加载
                
                info = extract_from_page(driver)
                results.append({'id': school_id, 'website': website, **info})
                
                print(f"  校训: {info['motto'] or '未找到'}")
                print(f"  校长: {info['principal'] or '未找到'}")
                print(f"  地址: {info['address'] or '未找到'}")
                
                # 更新数据库
                updates = []
                params = []
                
                if info['motto']:
                    updates.append('motto = ?')
                    params.append(info['motto'])
                
                if info['principal']:
                    updates.append('principal = ?')
                    params.append(info['principal'])
                
                if info['address']:
                    updates.append('address = ?')
                    params.append(info['address'])
                
                if updates:
                    params.append(school_id)
                    sql = f"UPDATE schools SET {', '.join(updates)} WHERE id = ?"
                    c.execute(sql, params)
                    updated += 1
                    
            except TimeoutException:
                print(f"  ❌ 页面超时")
            except Exception as e:
                print(f"  ❌ 错误: {str(e)[:50]}")
            
            time.sleep(2)
    
    finally:
        driver.quit()
    
    conn.commit()
    conn.close()
    
    # 保存结果
    with open('scripts/supplement/selenium_scraped.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n完成! 更新 {updated} 所学校")
    return updated

if __name__ == '__main__':
    scrape_schools(limit=30)
