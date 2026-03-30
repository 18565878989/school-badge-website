#!/usr/bin/env python3
"""
AI 驱动的学校地理位置补全工具
使用 MiniMax API 分析学校名称，提取省份/城市信息
"""
import sqlite3
import json
import re
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# MiniMax API 配置
MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
MINIMAX_BASE_URL = 'https://api.minimaxi.com/anthropic/v1'

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def call_minimax_ai(prompt, model='MiniMax-M2.7'):
    """调用 MiniMax AI API"""
    import urllib.request
    
    if not MINIMAX_API_KEY:
        return None, "No API key configured"
    
    url = f"{MINIMAX_BASE_URL}/messages"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {MINIMAX_API_KEY}',
        'anthropic-version': '2023-06-01'
    }
    
    data = {
        'model': model,
        'max_tokens': 100,
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('content', [{}])[0].get('text', ''), None
    except Exception as e:
        return None, str(e)

def analyze_school_location_batch(schools):
    """使用 AI 分析批量学校的位置信息"""
    
    # 构建提示词
    school_list = "\n".join([
        f"{i+1}. {s['name']} ({s['country']})" 
        for i, s in enumerate(schools)
    ])
    
    prompt = f"""分析以下学校名称，提取省份/州/城市信息。

学校列表：
{school_list}

请以 JSON 格式输出，格式如下：
{{
  "results": [
    {{"id": 学校ID, "city": "城市", "region": "省份/州", "reasoning": "推理过程"}},
    ...
  ]
}}

规则：
- city: 城市名称（英文）
- region: 省份/州/地区名称（英文）
- 如果名称中包含城市/省份名称，请提取
- 如果无法确定，返回 null
- 只返回 JSON，不要其他内容"""

    return call_minimax_ai(prompt)

def get_schools_needing_update():
    """获取需要更新地理位置的学校"""
    conn = get_db_connection()
    schools = conn.execute("""
        SELECT id, name, name_cn, country, region, city
        FROM schools
        WHERE country NOT IN ('Hong Kong', 'China', 'Taiwan', 'Macau')
        AND (region IS NULL OR region = '' OR region = country 
             OR city IS NULL OR city = '')
        ORDER BY country, name
        LIMIT 50
    """).fetchall()
    conn.close()
    return [dict(s) for s in schools]

def update_school_location(school_id, region, city):
    """更新学校地理位置"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if region:
        updates.append("region = ?")
        params.append(region)
    if city:
        updates.append("city = ?")
        params.append(city)
    
    if updates:
        params.append(school_id)
        cursor.execute(f"UPDATE schools SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    
    conn.close()

def main():
    print("=" * 60)
    print("AI 驱动的学校地理位置补全工具")
    print("=" * 60)
    
    # 检查 API key
    if not MINIMAX_API_KEY:
        print("\n⚠️ 未配置 MINIMAX_API_KEY 环境变量")
        print("请设置: export MINIMAX_API_KEY=your_key")
        return
    
    schools = get_schools_needing_update()
    
    if not schools:
        print("\n✅ 所有学校已有完整的地理位置信息")
        return
    
    print(f"\n找到 {len(schools)} 所学校需要补全地理位置")
    
    # 按国家分组
    by_country = {}
    for school in schools:
        country = school['country']
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(school)
    
    print(f"涉及 {len(by_country)} 个国家")
    
    total_updated = 0
    
    for country, country_schools in by_country.items():
        print(f"\n处理 {country} ({len(country_schools)} 所学校)...")
        
        # 分批处理，每批10所
        for i in range(0, len(country_schools), 10):
            batch = country_schools[i:i+10]
            
            result, error = analyze_school_location_batch(batch)
            
            if error:
                print(f"  ⚠️ API 错误: {error}")
                continue
            
            # 解析 JSON 结果
            try:
                data = json.loads(result)
                for item in data.get('results', []):
                    school_id = item.get('id')
                    city = item.get('city')
                    region = item.get('region')
                    reasoning = item.get('reasoning', '')
                    
                    if school_id and (city or region):
                        update_school_location(school_id, region, city)
                        total_updated += 1
                        
                        # 找到学校名
                        school_name = next((s['name'][:30] for s in batch if s['id'] == school_id), '')
                        print(f"  ✅ {school_name}: {city or region} ({reasoning[:50]})")
                
                time.sleep(0.5)  # 避免请求过快
                
            except json.JSONDecodeError as e:
                print(f"  ⚠️ JSON 解析错误: {e}")
                continue
    
    print("\n" + "=" * 60)
    print(f"补全完成: 更新了 {total_updated} 所学校")
    print("=" * 60)

if __name__ == '__main__':
    main()
