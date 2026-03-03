"""
Claude API 对话助手
"""
import os
import json
import requests
from pathlib import Path

# Claude API 配置
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

# 系统提示词
SCHOOL_SYSTEM_PROMPT = """你是校徽网的 AI 助手，负责帮助用户探索学校世界。

你可以：
1. 回答关于学校的问题
2. 推荐学校
3. 讲解学校历史
4. 帮助用户找到想要的学校
5. 提供学习建议

数据库中有 8,412 所学校，分布在：
- 亚洲: 7,858 所 (93.4%)
- 欧洲: 269 所
- 北美: 159 所
- 其他: ~126 所

学校信息包括：名称、国家、城市、地区、类型、校徽、官网、校训、建校年份等。

请用友好、专业的方式回答用户问题。"""

class ClaudeChatAssistant:
    """Claude API 对话助手"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or CLAUDE_API_KEY
        self.conversations = {}  # user_id -> messages
    
    def chat(self, user_message, user_id="anonymous", school_context=None):
        """发送对话"""
        if not self.api_key:
            return {
                "error": "未配置 Claude API Key",
                "hint": "请设置环境变量 CLAUDE_API_KEY"
            }
        
        # 获取或创建对话历史
        if user_id not in self.conversations:
            self.conversations[user_id] = [
                {"role": "system", "content": SCHOOL_SYSTEM_PROMPT}
            ]
        
        # 添加学校上下文
        messages = self.conversations[user_id].copy()
        
        # 如果有学校上下文，添加到系统提示
        if school_context:
            context_msg = f"\n\n当前查看的学校信息：\n{json.dumps(school_context, ensure_ascii=False)}"
            messages[0] = {"role": "system", "content": SCHOOL_SYSTEM_PROMPT + context_msg}
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用 Claude API
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": messages[-10:]  # 保留最近10条
        }
        
        try:
            response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result["content"][0]["text"]
            
            # 保存对话历史
            messages.append({"role": "assistant", "content": assistant_message})
            self.conversations[user_id] = messages
            
            return {
                "message": assistant_message,
                "model": result.get("model", "claude-3-5-sonnet")
            }
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API 请求失败: {str(e)}"}
    
    def clear_history(self, user_id="anonymous"):
        """清除对话历史"""
        if user_id in self.conversations:
            del self.conversations[user_id]
        return {"message": "对话历史已清除"}
    
    def get_school_info(self, school_name, db_path=None):
        """获取学校信息作为上下文"""
        if not db_path:
            db_path = Path(__file__).parent.parent / "database.db"
        
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, name_cn, country, city, region, level, 
                   founded, motto, website, badge_url
            FROM schools 
            WHERE name LIKE ? OR name_cn LIKE ?
            LIMIT 3
        """, (f"%{school_name}%", f"%{school_name}%"))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return None
        
        schools = []
        for r in results:
            schools.append({
                "name": r[0],
                "name_cn": r[1],
                "country": r[2],
                "city": r[3],
                "region": r[4],
                "level": r[5],
                "founded": r[6],
                "motto": r[7],
                "website": r[8],
                "badge_url": r[9]
            })
        
        return schools


def chat_with_claude(message, user_id="anonymous", school_context=None):
    """快捷对话函数"""
    assistant = ClaudeChatAssistant()
    return assistant.chat(message, user_id, school_context)


if __name__ == "__main__":
    # 测试
    assistant = ClaudeChatAssistant()
    
    # 测试不带 API key
    print("=== 测试 (无 API Key) ===")
    result = assistant.chat("你好！")
    print(result)
    
    # 测试学校查询
    print("\n=== 测试学校查询 ===")
    ctx = assistant.get_school_info("University of Tokyo")
    print(f"学校上下文: {ctx}")
