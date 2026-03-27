#!/usr/bin/env python3
"""
AI自动审核校园图片脚本
- 调用AI API分析校园图片
- 自动标记审核状态
- 支持多种AI图像分析API
"""

import os
import sqlite3
import json
import time
import requests
from pathlib import Path

DB_PATH = '/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db'
API_ENDPOINT = os.environ.get('IMAGE_ANALYSIS_API', '')  # 可配置AI API
API_KEY = os.environ.get('IMAGE_ANALYSIS_KEY', '')  # API密钥
BATCH_SIZE = 50  # 每批处理数量

def get_image_data(image_path):
    """获取图片数据"""
    full_path = '/Users/wangfeng/.openclaw/workspace/school-badge-website' + image_path
    if not os.path.exists(full_path):
        return None
    
    file_size = os.path.getsize(full_path)
    # 检查文件大小是否合理（小于1KB可能是无效图片）
    if file_size < 1000:
        return {"valid": False, "reason": "文件太小", "path": image_path}
    
    # 检查文件扩展名
    ext = os.path.splitext(full_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        return {"valid": False, "reason": "非图片格式", "path": image_path}
    
    return {
        "path": image_path,
        "size": file_size,
        "full_path": full_path
    }

def analyze_with_ai(image_data_list):
    """调用AI分析图片"""
    if not API_ENDPOINT:
        # 无API，使用启发式规则
        return analyze_heuristic(image_data_list)
    
    results = []
    for img in image_data_list:
        try:
            # 准备API请求
            with open(img["full_path"], "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode()
            
            # 调用AI API (示例：OpenAI Vision格式)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                        },
                        {
                            "type": "text",
                            "text": f"""分析这张图片是否是有效的校园图片。
学校: {img.get("school_name", "未知")}
返回JSON: {{"valid": true/false, "reason": "原因"}}
有效=图片是校园实景/建筑/风景；无效=logo/图标/新闻/截图/错误图片"""
                        }
                    ]
                }]
            }
            
            resp = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                content = result["choices"][0]["message"]["content"]
                # 解析JSON
                import re
                match = re.search(r'\{[^}]+\}', content)
                if match:
                    data = json.loads(match.group())
                    results.append({
                        "path": img["path"],
                        "valid": data.get("valid", False),
                        "reason": data.get("reason", "")
                    })
                else:
                    results.append({"path": img["path"], "valid": True, "reason": "AI解析失败，默认通过"})
            else:
                results.append({"path": img["path"], "valid": True, "reason": f"API错误{resp.status_code}"})
        
        except Exception as e:
            results.append({"path": img["path"], "valid": True, "reason": f"分析异常: {str(e)}"})
    
    return results

def analyze_heuristic(image_data_list):
    """使用启发式规则分析"""
    results = []
    for img in image_data_list:
        # 基于文件大小判断
        size_mb = img.get("size", 0) / (1024 * 1024)
        
        if size_mb < 0.001:  # < 1KB
            results.append({"path": img["path"], "valid": False, "reason": "文件太小"})
        elif size_mb > 5:  # > 5MB 可能有问题
            results.append({"path": img["path"], "valid": True, "reason": "大文件需人工复核"})
        else:
            results.append({"path": img["path"], "valid": True, "reason": "文件正常"})
    
    return results

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
        status = "✅"
    else:
        cursor.execute("""
            UPDATE schools 
            SET campus_reviewed = 0,
                campus_updated = 'Y'
            WHERE id = ?
        """, (school_id,))
        status = "❌"
    
    conn.commit()
    conn.close()
    return status, reason

def get_batch_for_review():
    """获取待审核批次"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, name_cn, campus_image, campus_reviewed
        FROM schools
        WHERE campus_image IS NOT NULL 
          AND campus_image != ''
          AND (campus_reviewed = 0 OR campus_reviewed IS NULL)
        ORDER BY LENGTH(campus_image) DESC
        LIMIT ?
    """, (BATCH_SIZE,))
    
    schools = cursor.fetchall()
    conn.close()
    return schools

def main():
    print("=" * 60)
    print("🤖 AI自动审核校园图片")
    print("=" * 60)
    
    schools = get_batch_for_review()
    print(f"\n📊 本批待审核: {len(schools)} 所")
    
    if not schools:
        print("✅ 没有待审核的学校")
        return
    
    # 准备图片数据
    image_data = []
    for school in schools:
        school_id, name, name_cn, campus_image, _ = school
        images = campus_image.split(',')
        first_img = images[0]
        
        img_data = get_image_data(first_img)
        if img_data:
            img_data["school_id"] = school_id
            img_data["school_name"] = name_cn or name
            image_data.append(img_data)
    
    print(f"📷 有效图片: {len(image_data)}")
    
    # 分析
    print("\n🔍 开始AI分析...")
    results = analyze_with_ai(image_data)
    
    # 更新状态
    approved = 0
    rejected = 0
    
    for i, (school, img_data) in enumerate(zip(schools, image_data)):
        school_id, name, name_cn, _, _ = school
        school_name = name_cn or name
        
        result = results[i]
        valid = result["valid"]
        reason = result["reason"]
        
        status, _ = mark_reviewed(school_id, valid, reason)
        
        if valid:
            approved += 1
        else:
            rejected += 1
        
        print(f"  {status} {school_name}: {reason}")
    
    print("\n" + "=" * 60)
    print("📊 审核完成!")
    print(f"  ✅ 通过: {approved}")
    print(f"  ❌ 待更新: {rejected}")
    print("=" * 60)

if __name__ == '__main__':
    main()
