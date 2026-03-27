#!/usr/bin/env python3
"""
AI自动审核校园图片 - 批量处理版
使用图像分析API进行智能审核
"""

import os
import sqlite3
import json
import time
import base64
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_API_ENDPOINT = os.environ.get('OPENAI_API_ENDPOINT', 'https://api.openai.com/v1/chat/completions')
BATCH_SIZE = 100

def get_image_base64(path):
    """获取图片base64"""
    try:
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except:
        return None

def analyze_with_openai(image_path, school_name, api_key):
    """使用OpenAI Vision API分析图片"""
    if not api_key:
        return analyze_heuristic(image_path)
    
    try:
        img_b64 = get_image_base64(image_path)
        if not img_b64:
            return {"valid": False, "reason": "无法读取图片"}
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    },
                    {
                        "type": "text",
                        "text": f"""你是校园图片审核员。判断这张图片是否适合作为校园展示图片。

学校名称：{school_name}

分析要点：
1. 图片是否是校园实景/建筑/风景？（而非logo、图标、截图等）
2. 图片内容是否与学校名称匹配？
3. 图片质量是否可用？

返回JSON：
{{"valid": true/false, "reason": "简要原因", "issues": ["问题1"]}}

如果图片是错误的学校内容、logo、图标、新闻横幅、界面截图等，返回valid=false"""
                    }
                ]
            }],
            "max_tokens": 200
        }
        
        resp = requests.post(OPENAI_API_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            import re
            match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return data
            return {"valid": False, "reason": "AI解析失败"}
        else:
            return {"valid": False, "reason": f"API错误{resp.status_code}"}
            
    except Exception as e:
        return {"valid": False, "reason": f"分析异常: {str(e)}"}

def analyze_heuristic(image_path):
    """启发式分析（无API时使用）"""
    size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
    size_kb = size / 1024
    
    # 文件太小可能是损坏的图片
    if size_kb < 5:
        return {"valid": False, "reason": "文件太小"}
    
    # 文件太大可能是异常
    if size_kb > 5000:
        return {"valid": True, "reason": "大文件需复核", "needs_review": True}
    
    return {"valid": True, "reason": "文件正常"}

def get_batch():
    """获取待审核批次"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.id, s.name, s.name_cn, s.campus_image
        FROM schools s
        WHERE s.campus_image IS NOT NULL 
          AND s.campus_image != ''
          AND (s.campus_reviewed = 0 OR s.campus_reviewed IS NULL)
        ORDER BY s.id
        LIMIT ?
    """, (BATCH_SIZE,))
    
    schools = []
    for row in cursor.fetchall():
        images = row[3].split(',')
        schools.append({
            "id": row[0],
            "name": row[2] or row[1],
            "first_image": images[0] if images else None
        })
    
    conn.close()
    return schools

def mark_reviewed(school_id, valid, reason=""):
    """标记审核状态"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if valid:
        cursor.execute("""
            UPDATE schools 
            SET campus_reviewed = 1, 
                campus_reviewed_at = CURRENT_TIMESTAMP,
                campus_updated = 'N'
            WHERE id = ?
        """, (school_id,))
    else:
        cursor.execute("""
            UPDATE schools 
            SET campus_reviewed = 0,
                campus_updated = 'Y'
            WHERE id = ?
        """, (school_id,))
    
    conn.commit()
    conn.close()
    return valid

def process_school(school, api_key):
    """处理单个学校"""
    if not school["first_image"]:
        return school["id"], False, "无图片"
    
    base_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website'
    full_path = base_path + school["first_image"]
    
    if not os.path.exists(full_path):
        return school["id"], False, "文件不存在"
    
    result = analyze_with_openai(full_path, school["name"], api_key)
    valid = result.get("valid", False)
    reason = result.get("reason", "")
    
    return school["id"], valid, reason

def main():
    print("=" * 60)
    print("🤖 AI自动审核校园图片")
    print("=" * 60)
    
    schools = get_batch()
    if not schools:
        print("✅ 没有待审核的学校")
        return
    
    print(f"\n📊 本批待审核: {len(schools)} 所")
    print(f"🔑 API Key: {'已配置' if OPENAI_API_KEY else '未配置（使用启发式）'}")
    
    approved = 0
    rejected = 0
    errors = 0
    
    for i, school in enumerate(schools, 1):
        school_id, valid, reason = process_school(school, OPENAI_API_KEY)
        
        if valid:
            approved += 1
            print(f"[{i}/{len(schools)}] ✅ {school['name']}: {reason}")
        else:
            rejected += 1
            print(f"[{i}/{len(schools)}] ❌ {school['name']}: {reason}")
        
        time.sleep(0.3)  # 避免API限流
    
    print("\n" + "=" * 60)
    print("📊 审核完成!")
    print(f"  ✅ 通过: {approved}")
    print(f"  ❌ 待更新: {rejected}")
    print(f"  ⚠️ 错误: {errors}")
    print("=" * 60)

if __name__ == '__main__':
    main()
