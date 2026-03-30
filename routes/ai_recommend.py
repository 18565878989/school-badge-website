"""
AI 选校建议功能
使用 MiniMax AI 根据用户偏好推荐学校
"""
from flask import Blueprint, render_template, request, jsonify, session
import sqlite3
import json
import os

ai_recommend_bp = Blueprint('ai_recommend', __name__)

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
        'max_tokens': 500,
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
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('content', [{}])[0].get('text', ''), None
    except Exception as e:
        return None, str(e)

@ai_recommend_bp.route('/ai-recommend')
def ai_recommend_page():
    """AI 选校建议页面"""
    return render_template('ai_recommend.html')

@ai_recommend_bp.route('/api/ai-recommend', methods=['POST'])
def api_ai_recommend():
    """AI 推荐 API"""
    data = request.get_json()
    preferences = data.get('preferences', {})
    
    # 构建用户偏好描述
    district = preferences.get('district', '')
    gender = preferences.get('gender', '')
    finance_type = preferences.get('finance_type', '')
    level = preferences.get('level', '')
    other = preferences.get('other', '')
    
    # 获取候选学校
    conn = get_db_connection()
    
    query = """
        SELECT id, name, name_cn, district, gender, finance_type, level, 
               principal, phone, website, badge_url
        FROM schools
        WHERE country = 'Hong Kong'
    """
    
    conditions = []
    params = []
    
    if district:
        conditions.append("district = ?")
        params.append(district)
    if gender:
        conditions.append("gender = ?")
        params.append(gender)
    if finance_type:
        conditions.append("finance_type = ?")
        params.append(finance_type)
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += " ORDER BY RANDOM() LIMIT 50"
    
    schools = conn.execute(query, params).fetchall()
    conn.close()
    
    if not schools:
        return jsonify({'error': '没有找到符合条件的学校'}), 404
    
    # 构建学校列表
    school_list = []
    for s in schools:
        school_list.append({
            'id': s['id'],
            'name': s['name'],
            'name_cn': s['name_cn'],
            'district': s['district'],
            'gender': s['gender'],
            'finance_type': s['finance_type'],
            'level': s['level']
        })
    
    # 调用 AI 分析
    user_desc = f"""
用户偏好：
- 地区：{district or '不限'}
- 性别：{gender or '不限'}
- 办学类型：{finance_type or '不限'}
- 学校类型：{level or '不限'}
- 其他要求：{other or '无'}
"""
    
    prompt = f"""你是一位香港教育专家，请根据用户偏好从以下学校列表中推荐最合适的学校。

{user_desc}

学校列表（JSON格式）：
{json.dumps(school_list, ensure_ascii=False, indent=2)}

请返回JSON格式的推荐结果：
{{
  "recommended": [
    {{
      "id": 学校ID,
      "reason": "推荐理由（50字以内）",
      "score": 推荐分数(1-100)
    }}
  ],
  "summary": "总体建议（100字以内）"
}}

请选择3-5所最合适的学校，按推荐程度排序。只返回JSON，不要其他内容。"""

    ai_result, error = call_minimax_ai(prompt)
    
    if error:
        return jsonify({
            'error': f'AI服务暂时不可用: {error}',
            'schools': school_list[:10]  # 返回随机学校作为备选
        }), 500
    
    # 解析 AI 结果
    try:
        # 提取 JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', ai_result)
        if json_match:
            recommendation = json.loads(json_match.group())
        else:
            recommendation = {'recommended': [], 'summary': ai_result[:200]}
        
        # 获取推荐学校的详细信息
        recommended_ids = [r['id'] for r in recommendation.get('recommended', [])]
        
        if recommended_ids:
            conn = get_db_connection()
            placeholders = ','.join(['?'] * len(recommended_ids))
            recommended_schools = conn.execute(f"""
                SELECT id, name, name_cn, district, gender, finance_type, 
                       principal, phone, badge_url
                FROM schools
                WHERE id IN ({placeholders})
            """, recommended_ids).fetchall()
            conn.close()
            
            # 合并 AI 评分和理由
            ai_scores = {r['id']: r for r in recommendation.get('recommended', [])}
            
            result_schools = []
            for s in recommended_schools:
                school_dict = dict(s)
                if s['id'] in ai_scores:
                    school_dict['reason'] = ai_scores[s['id']].get('reason', '')
                    school_dict['ai_score'] = ai_scores[s['id']].get('score', 0)
                result_schools.append(school_dict)
        else:
            result_schools = school_list[:5]
        
        return jsonify({
            'summary': recommendation.get('summary', ''),
            'schools': result_schools
        })
        
    except json.JSONDecodeError:
        return jsonify({
            'summary': ai_result[:200],
            'schools': school_list[:5],
            'raw_response': ai_result
        })

@ai_recommend_bp.route('/api/school/<int:school_id>')
def api_school_detail(school_id):
    """获取学校详细信息"""
    conn = get_db_connection()
    school = conn.execute("""
        SELECT s.*, 
               (SELECT COUNT(*) FROM likes WHERE school_id = s.id) as likes_count
        FROM schools s
        WHERE s.id = ?
    """, (school_id,)).fetchone()
    
    if not school:
        conn.close()
        return jsonify({'error': '学校不存在'}), 404
    
    school_dict = dict(school)
    
    # 获取历年数据
    stats = conn.execute("""
        SELECT year, student_count, teacher_count
        FROM school_yearly_stats
        WHERE school_id = ?
        ORDER BY year DESC
        LIMIT 5
    """, (school_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'school': school_dict,
        'yearly_stats': [dict(s) for s in stats]
    })
