"""
AI审核模块 - 基于Claude Vision API的智能内容审核
"""
import os
import json
import base64
import requests
from pathlib import Path
from datetime import datetime

# Claude API 配置
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

# 审核提示词
BADGE_AUDIT_PROMPT = """你是一个专业的校徽审核专家。请分析这张图片并判断：

1. 这是否是一个有效的校徽图片？
2. 图片质量是否清晰可辨？
3. 图片内容是否与学校名称匹配？
4. 是否有任何不当内容？

请用JSON格式返回审核结果：
{
    "is_valid_badge": true/false,
    "confidence": 0.0-1.0,
    "issues": ["问题描述列表"],
    "suggestion": "修改建议",
    "summary": "一句话总结"
}

注意：
- 只接受真正的校徽/校标/学校标志图片
- 拒绝接受人物照片、风景照、logo截图等非校徽内容
- 对于模糊但可能是校徽的图片，标记为需要人工审核"""

CAMPUS_AUDIT_PROMPT = """你是一个专业的校园图片审核专家。请分析这张图片并判断：

1. 这是否是一个有效的校园图片？
2. 图片内容是否展示校园环境/建筑/风景？
3. 图片质量是否清晰？
4. 是否有任何不当内容？

请用JSON格式返回审核结果：
{
    "is_valid_campus": true/false,
    "confidence": 0.0-1.0,
    "issues": ["问题描述列表"],
    "suggestion": "修改建议",
    "summary": "一句话总结"
}

注意：
- 接受校园全景、建筑、操场、图书馆等校园相关图片
- 拒绝接受人物特写、纯文字截图等非校园内容
- 对于模糊但可能是校园的图片，标记为需要人工审核"""


class AIAuditAssistant:
    """AI审核助手"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or CLAUDE_API_KEY
    
    def _call_claude_vision(self, image_url, prompt):
        """调用Claude Vision API"""
        if not self.api_key:
            return {
                "error": "未配置 CLAUDE_API_KEY",
                "is_valid": None,
                "confidence": 0,
                "needs_manual_review": True
            }
        
        try:
            # 如果是本地文件，读取并转为base64
            if image_url.startswith('/') or image_url.startswith('static/'):
                image_data = self._load_local_image(image_url)
                if image_data:
                    image_media = {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data
                        }
                    }
                else:
                    return {"error": "无法读取本地图片", "needs_manual_review": True}
            else:
                # 远程图片使用URL
                image_media = {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": image_url
                    }
                }
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "anthropic-dangerous-direct-browser-access": "true"
            }
            
            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            image_media,
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                CLAUDE_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('content', [])
                if content and len(content) > 0:
                    text = content[0].get('text', '')
                    return self._parse_audit_result(text)
            else:
                return {
                    "error": f"API错误: {response.status_code}",
                    "needs_manual_review": True
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "needs_manual_review": True
            }
    
    def _load_local_image(self, image_path):
        """加载本地图片并转为base64"""
        try:
            full_path = Path('/Users/wangfeng/.openclaw/workspace/school-badge-website') / image_path.lstrip('/')
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
        return None
    
    def _parse_audit_result(self, text):
        """解析审核结果"""
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "is_valid": result.get("is_valid_badge") or result.get("is_valid_campus"),
                    "confidence": result.get("confidence", 0.5),
                    "issues": result.get("issues", []),
                    "suggestion": result.get("suggestion", ""),
                    "summary": result.get("summary", ""),
                    "needs_manual_review": result.get("confidence", 0.5) < 0.7
                }
        except:
            pass
        
        # 如果解析失败，返回需要人工审核
        return {
            "is_valid": None,
            "confidence": 0,
            "issues": ["无法自动解析审核结果"],
            "needs_manual_review": True
        }
    
    def audit_badge(self, badge_url, school_name=None):
        """审核校徽图片"""
        prompt = BADGE_AUDIT_PROMPT
        if school_name:
            prompt = prompt.replace("学校名称匹配", f"学校名称为'{school_name}'，检查是否匹配")
        
        result = self._call_claude_vision(badge_url, prompt)
        result["badge_url"] = badge_url
        result["school_name"] = school_name
        result["audit_time"] = datetime.now().isoformat()
        result["type"] = "badge"
        return result
    
    def audit_campus(self, campus_url, school_name=None):
        """审核校园图片"""
        prompt = CAMPUS_AUDIT_PROMPT
        if school_name:
            prompt = prompt.replace("校园环境/建筑/风景", f"学校名称为'{school_name}'的校园")
        
        result = self._call_claude_vision(campus_url, prompt)
        result["campus_url"] = campus_url
        result["school_name"] = school_name
        result["audit_time"] = datetime.now().isoformat()
        result["type"] = "campus"
        return result
    
    def batch_audit(self, items, item_type="badge"):
        """批量审核
        
        Args:
            items: list of dicts with 'url' and optionally 'name'
            item_type: 'badge' or 'campus'
        """
        results = []
        for item in items:
            url = item.get('url')
            name = item.get('name', '')
            
            if item_type == "badge":
                result = self.audit_badge(url, name)
            else:
                result = self.audit_campus(url, name)
            
            results.append(result)
            
            # 避免API限流
            import time
            time.sleep(0.5)
        
        return results


def get_audit_stats():
    """获取审核统计"""
    import sqlite3
    
    conn = sqlite3.connect('/Users/wangfeng/.openclaw/workspace/school-badge-website/database.db')
    cursor = conn.cursor()
    
    # 校徽统计
    cursor.execute('''
        SELECT 
            COUNT(*) as total_with_badge,
            SUM(CASE WHEN badge_reviewed = 1 THEN 1 ELSE 0 END) as reviewed,
            SUM(CASE WHEN badge_reviewed = 0 THEN 1 ELSE 0 END) as pending
        FROM schools 
        WHERE badge_url IS NOT NULL AND badge_url != ""
    ''')
    badge_stats = cursor.fetchone()
    
    # 校园图统计
    cursor.execute('''
        SELECT 
            COUNT(*) as total_with_campus,
            SUM(CASE WHEN campus_reviewed = 1 THEN 1 ELSE 0 END) as reviewed,
            SUM(CASE WHEN campus_reviewed = 0 THEN 1 ELSE 0 END) as pending
        FROM schools 
        WHERE campus_image IS NOT NULL AND campus_image != ""
    ''')
    campus_stats = cursor.fetchone()
    
    conn.close()
    
    return {
        "badge": {
            "total": badge_stats[0] or 0,
            "reviewed": badge_stats[1] or 0,
            "pending": badge_stats[2] or 0,
            "review_rate": round((badge_stats[1] or 0) / max(badge_stats[0], 1) * 100, 1)
        },
        "campus": {
            "total": campus_stats[0] or 0,
            "reviewed": campus_stats[1] or 0,
            "pending": campus_stats[2] or 0,
            "review_rate": round((campus_stats[1] or 0) / max(campus_stats[0], 1) * 100, 1)
        }
    }
