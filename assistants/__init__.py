"""
AI Assistant Base - AI 助手基类
"""
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "database.db"

class Assistant:
    """AI 助手基类"""
    
    name = "Assistant"
    description = "AI 助手"
    avatar = "🐱"
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        self.conn.close()
    
    def get_school_by_id(self, school_id):
        """获取学校详情"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM schools WHERE id = ?", (school_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_schools(self, keyword, limit=10):
        """搜索学校"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM schools 
            WHERE name LIKE ? OR name_cn LIKE ? OR country LIKE ?
            LIMIT ?
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_schools_by_region(self, region, limit=50):
        """按地区获取学校"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM schools 
            WHERE region = ?
            LIMIT ?
        """, (region, limit))
        return [dict(row) for row in cursor.fetchall()]


class BadgeExpert(Assistant):
    """校徽鉴定师 - 识别校徽图片"""
    
    name = "校徽鉴定师"
    description = "上传校徽图片，识别是哪所学校"
    avatar = "🐱"
    
    def identify(self, image_url=None, keywords=None):
        """
        识别校徽
        - image_url: 图片 URL
        - keywords: 关键词（颜色、图案等）
        """
        cursor = self.conn.cursor()
        
        # 优先按关键词搜索
        if keywords:
            schools = self.search_schools(keywords, limit=20)
            if schools:
                return {
                    "identified": True,
                    "confidence": 0.85,
                    "school": schools[0],
                    "message": f"根据关键词 '{keywords}' 找到了 {len(schools)} 所可能的学校"
                }
        
        # 如果有图片 URL，搜索有校徽的学校
        if image_url:
            cursor.execute("""
                SELECT * FROM schools 
                WHERE badge_url IS NOT NULL AND badge_url != ''
                ORDER BY RANDOM() LIMIT 5
            """)
            similar = [dict(row) for row in cursor.fetchall()]
            return {
                "identified": False,
                "message": "需要更多图片特征来识别",
                "suggestions": similar
            }
        
        return {
            "identified": False,
            "message": "请提供校徽图片或关键词"
        }


class TravelPlanner(Assistant):
    """旅行规划师 - 推荐学校参观路线"""
    
    name = "旅行规划师"
    description = "推荐学校参观路线"
    avatar = "🌍"
    
    def recommend(self, region=None, country=None, interest=None, days=3):
        """
        推荐路线
        - region: 地区 (Asia, Europe, etc.)
        - country: 国家
        - interest: 兴趣 (history, architecture, culture)
        - days: 天数
        """
        cursor = self.conn.cursor()
        
        # 构建查询
        query = "SELECT * FROM schools WHERE 1=1"
        params = []
        
        if region:
            query += " AND region = ?"
            params.append(region)
        
        if country:
            query += " AND country = ?"
            params.append(country)
        
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(days * 3)
        
        cursor.execute(query, params)
        schools = [dict(row) for row in cursor.fetchall()]
        
        # 生成路线
        itinerary = []
        for i, school in enumerate(schools[:days * 2], 1):
            day = (i - 1) // 2 + 1
            itinerary.append({
                "day": day,
                "school": school,
                "tip": self._get_tip(school, interest)
            })
        
        return {
            "days": days,
            "region": region,
            "itinerary": itinerary,
            "message": f"为你规划了 {days} 天 {region or country} 学校之旅！"
        }
    
    def _get_tip(self, school, interest):
        """获取参观提示"""
        tips = {
            "history": "这所学校有着悠久的历史，建校于 {} 年",
            "architecture": "校园建筑风格独特，值得细细品味",
            "culture": "这里有着丰富的文化底蕴"
        }
        
        founded = school.get("founded")
        if interest == "history" and founded:
            return tips["history"].format(founded)
        return tips.get(interest, tips["culture"])


class HistoryGuide(Assistant):
    """历史讲解员 - 讲述学校历史"""
    
    name = "历史讲解员"
    description = "讲述学校历史、故事、知名校友"
    avatar = "📚"
    
    def answer(self, question, school_name=None):
        """
        回答关于学校历史的问题
        """
        # 如果指定了学校
        if school_name:
            schools = self.search_schools(school_name, limit=1)
            if schools:
                school = schools[0]
                return self._generate_story(school, question)
        
        # 通用回答
        return {
            "answer": "我对很多学校的历史都很了解！请告诉我你想了解哪所学校",
            "suggestions": [
                "清华大学的历史",
                "北京大学的创始人",
                "香港大学的知名校友"
            ]
        }
    
    def _generate_story(self, school, question):
        """生成学校故事"""
        name = school.get("name_cn") or school.get("name")
        founded = school.get("founded")
        motto = school.get("motto")
        country = school.get("country")
        
        story = f"""
## {name}

**{name}** 位于 **{country}**，是一所历史悠久的学府。

"""
        
        if founded:
            story += f"学校创立于 **{founded}** 年，经过多年的发展，已经成为该地区重要的教育机构。\n\n"
        
        if motto:
            story += f"校训：**{motto}**\n\n"
        
        story += f"了解更多学校信息，请访问学校详情页。"
        
        return {
            "school": school,
            "story": story,
            "sources": [f"学校数据库 ID: {school['id']}"]
        }


# 助手工厂
def get_assistant(assistant_type: str) -> Assistant:
    """获取助手实例"""
    assistants = {
        "badge": BadgeExpert,
        "travel": TravelPlanner,
        "history": HistoryGuide,
        "compare": CompareAssistant,
        "recommend": RecommendAssistant,
        "quiz": SchoolQuizAssistant
    }
    
    cls = assistants.get(assistant_type, Assistant)
    return cls()


# ============================================================
# 增强功能
# ============================================================

class CompareAssistant(Assistant):
    """学校对比助手"""
    
    name = "学校对比"
    description = "对比两所学校的详细信息"
    avatar = "⚖️"
    
    def compare(self, school1_id=None, school2_id=None, school1_name=None, school2_name=None):
        """对比两所学校"""
        cursor = self.conn.cursor()
        
        # 获取学校1
        if school1_id:
            cursor.execute("SELECT * FROM schools WHERE id = ?", (school1_id,))
        elif school1_name:
            cursor.execute("SELECT * FROM schools WHERE name LIKE ? LIMIT 1", (f"%{school1_name}%",))
        else:
            return {"error": "请提供学校1的名称或ID"}
        
        s1 = cursor.fetchone()
        if not s1:
            return {"error": f"未找到学校: {school1_name or school1_id}"}
        s1 = dict(s1)
        
        # 获取学校2
        if school2_id:
            cursor.execute("SELECT * FROM schools WHERE id = ?", (school2_id,))
        elif school2_name:
            cursor.execute("SELECT * FROM schools WHERE name LIKE ? LIMIT 1", (f"%{school2_name}%",))
        else:
            return {"error": "请提供学校2的名称或ID"}
        
        s2 = cursor.fetchone()
        if not s2:
            return {"error": f"未找到学校: {school2_name or school2_id}"}
        s2 = dict(s2)
        
        # 生成对比
        comparison = {
            "school1": s1,
            "school2": s2,
            "differences": []
        }
        
        # 比较字段
        fields = ["country", "region", "city", "founded", "level", "website"]
        for field in fields:
            v1 = s1.get(field) or "无"
            v2 = s2.get(field) or "无"
            if v1 != v2:
                comparison["differences"].append({
                    "field": field,
                    "school1": v1,
                    "school2": v2
                })
        
        return comparison


class RecommendAssistant(Assistant):
    """智能推荐助手"""
    
    name = "智能推荐"
    description = "根据用户偏好推荐学校"
    avatar = "✨"
    
    def recommend_for_user(self, user_preferences=None):
        """
        智能推荐
        - user_preferences: {region, country, level, interests}
        """
        cursor = self.conn.cursor()
        
        # 默认推荐（随机热门）
        query = "SELECT * FROM schools WHERE 1=1"
        params = []
        
        if user_preferences:
            if user_preferences.get("region"):
                query += " AND region = ?"
                params.append(user_preferences["region"])
            
            if user_preferences.get("country"):
                query += " AND country = ?"
                params.append(user_preferences["country"])
            
            if user_preferences.get("level"):
                query += " AND level = ?"
                params.append(user_preferences["level"])
        
        # 有校徽的优先
        query += " AND badge_url IS NOT NULL AND badge_url != ''"
        
        query += " ORDER BY RANDOM() LIMIT 10"
        
        cursor.execute(query, params)
        schools = [dict(row) for row in cursor.fetchall()]
        
        return {
            "recommendations": schools,
            "count": len(schools),
            "message": "为你推荐这些学校！" if schools else "没有找到符合条件的学校"
        }


class SchoolQuizAssistant(Assistant):
    """学校问答助手"""
    
    name = "学校问答"
    description = "回答关于学校的问题"
    avatar = "❓"
    
    def answer_question(self, question):
        """回答问题"""
        question = question.lower()
        cursor = self.conn.cursor()
        
        # 分析问题类型
        if "多少" in question or "数量" in question:
            # 统计问题
            if "亚洲" in question or "asia" in question:
                cursor.execute("SELECT COUNT(*) FROM schools WHERE region = 'Asia'")
                return {"answer": f"亚洲共有 {cursor.fetchone()[0]} 所学校"}
            elif "大学" in question or "university" in question:
                cursor.execute("SELECT COUNT(*) FROM schools WHERE level = 'university'")
                return {"answer": f"数据库中共有 {cursor.fetchone()[0]} 所大学"}
            else:
                cursor.execute("SELECT COUNT(*) FROM schools")
                return {"answer": f"数据库中共有 {cursor.fetchone()[0]} 所学校"}
        
        elif "哪个" in question or "哪所" in question:
            # 寻找问题
            for country in ["香港", "日本", "韩国", "美国", "英国", "中国"]:
                if country in question:
                    cursor.execute("""
                        SELECT name, name_cn FROM schools 
                        WHERE country = ? AND level = 'university'
                        ORDER BY RANDOM() LIMIT 1
                    """, (country,))
                    row = cursor.fetchone()
                    if row:
                        return {"answer": f"给你推荐一所{country}的大学：{row[0]} ({row[1] or ''})"}
            
            return {"answer": "请具体说明你想了解哪个国家或地区的学校"}
        
        elif "排名" in question or "top" in question:
            # Top 学校
            cursor.execute("""
                SELECT name, country, region FROM schools 
                WHERE badge_url IS NOT NULL AND badge_url != ''
                ORDER BY RANDOM() LIMIT 5
            """)
            schools = cursor.fetchall()
            answer = "以下是一些优秀的学校：\n"
            for s in schools:
                answer += f"- {s[0]} ({s[1]})\n"
            return {"answer": answer}
        
        else:
            return {
                "answer": "我可以回答以下问题：\n" +
                         "- 数据库有多少学校？\n" +
                         "- 亚洲有多少学校？\n" +
                         "- 推荐一所XX国家的大学\n" +
                         "- 给我看看Top学校"
            }


# 导出所有助手
AVAILABLE_ASSISTANTS = {
    "badge": BadgeExpert,
    "travel": TravelPlanner,
    "history": HistoryGuide,
    "compare": CompareAssistant,
    "recommend": RecommendAssistant,
    "quiz": SchoolQuizAssistant
}

def get_all_assistants():
    """获取所有助手列表"""
    return [
        {
            "type": k,
            "name": v.name,
            "description": v.description,
            "avatar": v.avatar
        }
        for k, v in AVAILABLE_ASSISTANTS.items()
    ]


if __name__ == "__main__":
    # 测试
    history = get_assistant("history")
    result = history.answer("清华大学的历史")
    print(result["story"])
    history.close()
