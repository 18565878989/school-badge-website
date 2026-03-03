"""
收藏推荐助手
"""
import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "database.db"

class FavoriteRecommendAssistant:
    """基于收藏的智能推荐"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        self.conn.close()
    
    def get_user_favorites(self, user_id):
        """获取用户收藏"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.* FROM schools s
            JOIN likes ul ON s.id = ul.school_id
            WHERE ul.user_id = ?
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def analyze_preferences(self, user_id):
        """分析用户偏好"""
        favorites = self.get_user_favorites(user_id)
        
        if not favorites:
            return {
                "has_favorites": False,
                "message": "还没有收藏，快去收藏喜欢的学校吧！"
            }
        
        # 统计偏好
        regions = defaultdict(int)
        countries = defaultdict(int)
        levels = defaultdict(int)
        
        for school in favorites:
            regions[school.get("region", "Unknown")] += 1
            countries[school.get("country", "Unknown")] += 1
            levels[school.get("level", "Unknown")] += 1
        
        # 找出最偏好
        top_region = max(regions.items(), key=lambda x: x[1])
        top_country = max(countries.items(), key=lambda x: x[1])
        top_level = max(levels.items(), key=lambda x: x[1])
        
        return {
            "has_favorites": True,
            "favorites_count": len(favorites),
            "preferences": {
                "region": {"name": top_region[0], "count": top_region[1]},
                "country": {"name": top_country[0], "count": top_country[1]},
                "level": {"name": top_level[0], "count": top_level[1]}
            }
        }
    
    def recommend_based_on_favorites(self, user_id, limit=10):
        """基于收藏推荐相似学校"""
        favorites = self.get_user_favorites(user_id)
        
        if not favorites:
            return self._recommend_popular(limit)
        
        # 分析偏好
        prefs = self.analyze_preferences(user_id)
        
        # 构建推荐查询
        cursor = self.conn.cursor()
        
        # 优先推荐同地区/同类型的未收藏学校
        top_region = prefs["preferences"]["region"]["name"]
        top_level = prefs["preferences"]["level"]["name"]
        
        # 获取用户收藏的ID
        favorite_ids = [s["id"] for s in favorites]
        placeholders = ",".join(["?"] * len(favorite_ids)) if favorite_ids else "0"
        
        # 查询推荐
        query = f"""
            SELECT * FROM schools 
            WHERE region = ? 
            AND level = ?
            AND id NOT IN ({placeholders})
            AND badge_url IS NOT NULL AND badge_url != ''
            ORDER BY RANDOM()
            LIMIT ?
        """
        
        params = [top_region, top_level] + favorite_ids + [limit]
        cursor.execute(query, params)
        recommendations = [dict(row) for row in cursor.fetchall()]
        
        # 如果不够，换其他条件
        if len(recommendations) < limit:
            query2 = """
                SELECT * FROM schools 
                WHERE region = ?
                AND id NOT IN ({})
                AND badge_url IS NOT NULL AND badge_url != ''
                ORDER BY RANDOM()
                LIMIT ?
            """.format(placeholders)
            
            params2 = [top_region] + favorite_ids + [limit]
            cursor.execute(query2, params2)
            more = [dict(row) for row in cursor.fetchall()]
            
            # 合并去重
            seen = set(r["id"] for r in recommendations)
            for r in more:
                if r["id"] not in seen and len(recommendations) < limit:
                    recommendations.append(r)
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "based_on": {
                "region": top_region,
                "level": top_level
            },
            "message": f"根据你收藏的 {len(favorites)} 所学校，为你推荐相似学校"
        }
    
    def _recommend_popular(self, limit=10):
        """推荐热门学校"""
        cursor = self.conn.cursor()
        
        # 随机推荐有校徽的学校
        cursor.execute("""
            SELECT * FROM schools 
            WHERE badge_url IS NOT NULL AND badge_url != ''
            ORDER BY RANDOM()
            LIMIT ?
        """, (limit,))
        
        schools = [dict(row) for row in cursor.fetchall()]
        
        return {
            "recommendations": schools,
            "count": len(schools),
            "message": "为你推荐热门学校"
        }
    
    def get_similar_schools(self, school_id, limit=5):
        """获取相似学校"""
        cursor = self.conn.cursor()
        
        # 获取目标学校信息
        cursor.execute("SELECT * FROM schools WHERE id = ?", (school_id,))
        school = cursor.fetchone()
        
        if not school:
            return {"error": "未找到该学校"}
        
        school = dict(school)
        
        # 查找同地区同类型的其他学校
        cursor.execute("""
            SELECT * FROM schools 
            WHERE region = ? 
            AND level = ?
            AND id != ?
            AND badge_url IS NOT NULL AND badge_url != ''
            ORDER BY RANDOM()
            LIMIT ?
        """, (school["region"], school["level"], school_id, limit))
        
        similar = [dict(row) for row in cursor.fetchall()]
        
        return {
            "target_school": school,
            "similar_schools": similar,
            "count": len(similar)
        }


# 快捷函数
def recommend_for_user(user_id, limit=10):
    """为用户推荐"""
    assistant = FavoriteRecommendAssistant()
    result = assistant.recommend_based_on_favorites(user_id, limit)
    assistant.close()
    return result


if __name__ == "__main__":
    # 测试
    print("=== 收藏推荐测试 ===")
    
    # 测试没有收藏的用户
    assistant = FavoriteRecommendAssistant()
    result = assistant.recommend_based_on_favorites(user_id=99999, limit=5)
    print(f"新用户推荐: {result['message']}")
    print(f"推荐了 {result['count']} 所学校")
    assistant.close()
