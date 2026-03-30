#!/usr/bin/env python3
"""
AI 驱动的学校信息增强工具
使用 MiniMax API 为学校添加描述、校训、办学特色等信息
"""
import sqlite3
import json
import time
import os

DATABASE_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def call_minimax_ai(prompt, model='MiniMax-M2.7'):
    """调用 MiniMax AI API"""
    import urllib.request
    
    MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
    MINIMAX_BASE_URL = 'https://api.minimaxi.com/anthropic/v1'
    
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
        'max_tokens': 200,
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

def enhance_schools_batch(schools):
    """使用 AI 增强批量学校的信息"""
    
    school_list = "\n".join([
        f"{i+1}. {s['name']} ({s['country']}) - {s.get('level', 'school')}" 
        for i, s in enumerate(schools)
    ])
    
    prompt = f"""为以下学校生成简短描述（50字以内）和校训（如果是知名大学）。

学校列表：
{school_list}

请以 JSON 格式输出：
{{
  "results": [
    {{
      "id": 学校ID,
      "description": "学校描述（50字以内）",
      "motto": "校训（如果有）",
      "founded": 创立年份（如果能确定）,
      "note": "备注"
    }},
    ...
  ]
}}

规则：
- description: 用中文简述学校特色/优势/地位
- motto: 如果是知名大学，提取或推断校训
- founded: 尽可能推断创立年份
- 如果信息不足，字段返回 null"""

    return call_minimax_ai(prompt)

def get_schools_needing_enhancement():
    """获取需要增强信息的学校"""
    conn = get_db_connection()
    schools = conn.execute("""
        SELECT id, name, name_cn, country, level, motto, description, founded
        FROM schools
        WHERE (motto IS NULL OR motto = '' OR description IS NULL OR description = '')
        AND country IN ('United States', 'United Kingdom', 'Japan', 'South Korea', 
                        'Australia', 'Canada', 'Germany', 'France', 'Singapore')
        ORDER BY RANDOM()
        LIMIT 20
    """).fetchall()
    conn.close()
    return [dict(s) for s in schools]

def update_school(school_id, description=None, motto=None, founded=None):
    """更新学校信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if description:
        updates.append("description = ?")
        params.append(description)
    if motto:
        updates.append("motto = ?")
        params.append(motto)
    if founded:
        updates.append("founded = ?")
        params.append(founded)
    
    if updates:
        params.append(school_id)
        cursor.execute(f"UPDATE schools SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    
    conn.close()

def main():
    print("=" * 60)
    print("AI 驱动的学校信息增强工具")
    print("=" * 60)
    
    MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
    if not MINIMAX_API_KEY:
        print("\n⚠️ 未配置 MINIMAX_API_KEY 环境变量")
        print("请设置: export MINIMAX_API_KEY=your_key")
        return
    
    schools = get_schools_needing_enhancement()
    
    if not schools:
        print("\n✅ 所有学校信息已完整")
        return
    
    print(f"\n找到 {len(schools)} 所学校需要增强信息")
    
    # 分批处理
    batch_size = 5
    total_updated = 0
    
    for i in range(0, len(schools), batch_size):
        batch = schools[i:i+batch_size]
        print(f"\n处理第 {i//batch_size + 1} 批 ({len(batch)} 所学校)...")
        
        result, error = enhance_schools_batch(batch)
        
        if error:
            print(f"  ⚠️ API 错误: {error}")
            continue
        
        try:
            data = json.loads(result)
            for item in data.get('results', []):
                school_id = item.get('id')
                description = item.get('description')
                motto = item.get('motto')
                founded = item.get('founded')
                
                if school_id and (description or motto):
                    update_school(school_id, description, motto, founded)
                    total_updated += 1
                    
                    school_name = next((s['name'][:30] for s in batch if s['id'] == school_id), '')
                    print(f"  ✅ {school_name}")
                    if motto:
                        print(f"     校训: {motto}")
            
            time.sleep(1)
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON 解析错误")
            continue
    
    print("\n" + "=" * 60)
    print(f"增强完成: 更新了 {total_updated} 所学校")
    print("=" * 60)

if __name__ == '__main__':
    main()
