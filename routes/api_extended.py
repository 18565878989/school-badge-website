"""
Extended API Routes - 额外的API路由
"""
from flask import Blueprint, request, jsonify, session
import sqlite3
import os
import re
import json as json_lib

from services.search_service import search_schools as local_search_schools

api_ext_bp = Blueprint('api_ext', __name__)

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@api_ext_bp.route('/api/chat', methods=['POST'])
def chat():
    """AI Chat API"""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # 简单的响应（实际项目中应调用AI服务）
    response = {
        'reply': f'您发送了: {message[:50]}... 这是一个模拟响应',
        'timestamp': '2026-03-29'
    }
    
    return jsonify(response)

@api_ext_bp.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    session.pop('chat_history', None)
    return jsonify({'success': True})

@api_ext_bp.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Text to Speech API"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    # 返回模拟音频URL
    return jsonify({
        'success': True,
        'audio_url': f'/static/audio/tts_{hash(text)}.mp3'
    })

@api_ext_bp.route('/api/recommend/favorites', methods=['GET'])
def recommend_favorites():
    """Get favorite recommendations"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401
    
    conn = get_db_connection()
    
    # 获取用户点赞的学校
    liked = conn.execute('''
        SELECT school_id FROM likes WHERE user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    liked_ids = [l['school_id'] for l in liked]
    
    # 简单推荐：同地区同类型的其他学校
    if liked_ids:
        first_school = conn.execute(
            'SELECT region, level FROM schools WHERE id = ?',
            (liked_ids[0],)
        ).fetchone()
        
        if first_school:
            recommended = conn.execute('''
                SELECT * FROM schools 
                WHERE region = ? AND level = ? AND id NOT IN ({})
                ORDER BY RANDOM()
                LIMIT 10
            '''.format(','.join('?' * len(liked_ids))),
                (first_school['region'], first_school['level'], *liked_ids)
            ).fetchall()
        else:
            recommended = []
    else:
        recommended = conn.execute('''
            SELECT * FROM schools ORDER BY RANDOM() LIMIT 10
        ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'recommendations': [dict(r) for r in recommended]
    })

@api_ext_bp.route('/api/similar/<int:school_id>', methods=['GET'])
def similar_schools(school_id):
    """Get similar schools"""
    conn = get_db_connection()
    
    school = conn.execute(
        'SELECT * FROM schools WHERE id = ?', (school_id,)
    ).fetchone()
    
    if not school:
        conn.close()
        return jsonify({'error': 'School not found'}), 404
    
    # 找同地区同类型的学校
    similar = conn.execute('''
        SELECT * FROM schools 
        WHERE region = ? AND level = ? AND id != ?
        ORDER BY RANDOM()
        LIMIT 10
    ''', (school['region'], school['level'], school_id)).fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'similar': [dict(s) for s in similar]
    })

@api_ext_bp.route('/api/deep-search', methods=['POST'])
def deep_search():
    """Deep search API - AI powered search with local DB + LLM
    AI Provider 优先级: MiniMax -> Ollama -> Cloudflare -> Local Search
    """
    data = request.get_json()
    query = data.get('query', '')
    use_ai = data.get('use_ai', True)  # 是否使用AI
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    conn = get_db_connection()
    
    # 获取学校总数用于系统提示
    total_schools = conn.execute('SELECT COUNT(*) FROM schools').fetchone()[0]
    
    # 张雪峰报考知识库
    zhangxuefeng_knowledge = """
【张雪峰报考观点】
1. 城市选择：大城市优先，北上广深 > 二线城市
2. 专业选择：计算机、电子信息、口腔医学、电气工程、师范类优先；生化环材、市场营销谨慎
3. 考研建议：985/211优先，技术能力 > 学校牌子
4. 报考策略：冲(排名+10-20%)、稳(相当)、保(排名-10-20%)、垫(排名-30%+)
5. 就业导向：选专业要看就业，不是看名字好听
6. 医学/法律：必须考研
7. 师范类：稳定但薪资有限
8. 计算机：就业好、薪资高、转行容易
"""
    
    # 构建系统提示词
    system_prompt = f"""你是校徽网的智能搜索助手。数据库中共有 {total_schools} 所学校，包含以下字段：
- id: 学校ID
- name: 学校英文名  
- name_cn: 学校中文名
- country: 国家
- city: 城市
- region: 地区 (Asia, North America, Europe, Oceania, Africa, South America)
- level: 类型 (university, middle, elementary, kindergarten)
- motto: 校训
- founded: 建校年份
- website: 官网
- qs_rank: QS世界大学排名
- the_rank: THE世界大学排名
- usnews_rank: US News排名

{zhangxuefeng_knowledge}

请分析用户查询，返回匹配的JSON格式：
{{
    "analysis": "你对用户查询的分析",
    "search_type": "university/middle/elementary/country/region/ranking/all",
    "keywords": ["关键词1", "关键词2"],
    "filters": {{"region": "Asia", "level": "university"}},
    "is_baokao_query": true/false  // 是否是高考/志愿/报考相关问题
}}

注意：
- 如果是高考/志愿/报考相关问题，is_baokao_query设为true
- 只返回keywords用于搜索，不要返回school_ids
- 如果是闲聊/问候，analysis应包含"闲聊"
- search_type: university(大学), middle(中学), elementary(小学), kindergarten(幼儿园), country(国家), region(地区), ranking(排名), all(全部)
"""
    
    ai_response = None
    
    # 1. 尝试 MiniMax API
    if use_ai and not ai_response:
        try:
            import requests
            api_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            api_key = os.environ.get('MINIMAX_API_KEY', '')
            model_name = os.environ.get('MINIMAX_MODEL', 'MiniMax-M2.1')
            
            if api_key:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"用户查询: {query}\n\n请分析并返回JSON结果。"}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"[DeepSearch] MiniMax response: {ai_response[:100]}...")
        except Exception as e:
            print(f"[DeepSearch] MiniMax error: {e}")
    
    # 2. 尝试 Ollama (本地)
    if use_ai and not ai_response:
        try:
            import requests
            ollama_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434') + '/api/chat'
            ollama_payload = {
                "model": os.environ.get('OLLAMA_MODEL', 'llama3.2'),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"用户查询: {query}\n\n请分析并返回JSON结果。"}
                ],
                "stream": False
            }
            ollama_response = requests.post(ollama_url, json=ollama_payload, timeout=30)
            if ollama_response.status_code == 200:
                ollama_result = ollama_response.json()
                ai_response = ollama_result.get('message', {}).get('content', '')
                print(f"[DeepSearch] Ollama response: {ai_response[:100]}...")
        except Exception as e:
            print(f"[DeepSearch] Ollama error: {e}")
    
    # 3. 尝试 Cloudflare Workers AI
    if use_ai and not ai_response:
        try:
            import requests
            cf_token = os.environ.get('CF_API_TOKEN', '')
            cf_account = os.environ.get('CF_ACCOUNT_ID', '')
            
            if cf_token and cf_account:
                cf_url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/run/@cf/meta/llama-3.1-8b-instruct"
                cf_headers = {
                    'Authorization': f'Bearer {cf_token}',
                    'Content-Type': 'application/json'
                }
                cf_payload = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"用户查询: {query}\n\n请分析并返回JSON结果。"}
                    ],
                    "max_tokens": 500
                }
                cf_response = requests.post(cf_url, headers=cf_headers, json=cf_payload, timeout=60)
                if cf_response.status_code == 200:
                    cf_result = cf_response.json()
                    ai_response = cf_result.get('result', {}).get('response', '')
                    print(f"[DeepSearch] Cloudflare response: {ai_response[:100]}...")
        except Exception as e:
            print(f"[DeepSearch] Cloudflare error: {e}")
    
    # 解析AI响应或使用本地搜索
    search_type = 'all'
    keywords = []
    filters = {}
    
    if ai_response:
        try:
            import re
            import json as json_lib
            
            # 尝试提取JSON部分
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
            if json_match:
                parsed = json_lib.loads(json_match.group())
                analysis = parsed.get('analysis', '')
                search_type = parsed.get('search_type', 'all')
                keywords = parsed.get('keywords', [])
                filters = parsed.get('filters', {})
                
                # 如果是闲聊
                if '闲聊' in analysis or '问候' in analysis:
                    conn.close()
                    return jsonify({
                        'success': True,
                        'is_chat': True,
                        'analysis': analysis,
                        'message': '你好！我是校徽网的智能搜索助手。请问您在找什么学校？'
                    })
        except Exception as e:
            print(f"[DeepSearch] Parse error: {e}")
            keywords = query.split()
    else:
        # 本地搜索：基于关键词分割
        keywords = query.replace('大学', 'university').replace('学院', 'college').split()
    
    # 本地数据库搜索 - 使用优先级匹配
    # 先尝试精确匹配，再模糊匹配
    search_results = []
    
    # 国家/地区名称映射（中文 -> 英文）
    country_map = {
        '日本': 'Japan', '中国': 'China', '美国': 'United States', 
        '英国': 'United Kingdom', '德国': 'Germany', '法国': 'France',
        '加拿大': 'Canada', '澳大利亚': 'Australia', '韩国': 'South Korea',
        '新加坡': 'Singapore', '香港': 'Hong Kong', '台湾': 'Taiwan',
        '欧洲': 'Europe', '亚洲': 'Asia', '北美': 'North America'
    }
    
    # 类型名称映射
    level_map = {
        '大学': 'university', '学院': 'college', '中学': 'middle', 
        '高中': 'middle', '小学': 'elementary', '幼儿园': 'kindergarten'
    }
    
    # 处理关键词
    processed_keywords = []
    for kw in keywords:
        kw_lower = kw.lower()
        # 检查是否是国家
        if kw in country_map:
            processed_keywords.append(('country', country_map[kw]))
        elif kw_lower in [c.lower() for c in country_map.values()]:
            for cn, en in country_map.items():
                if en.lower() == kw_lower:
                    processed_keywords.append(('country', en))
                    break
        # 检查是否是类型
        elif kw in level_map:
            processed_keywords.append(('level', level_map[kw]))
        elif kw_lower in ['university', 'college', 'middle', 'elementary', 'kindergarten']:
            processed_keywords.append(('level', kw_lower))
        else:
            processed_keywords.append(('keyword', kw))
    
    # 构建多条件查询 - 分离核心过滤和关键词
    core_filters = []
    core_params = []
    keyword_filters = []
    keyword_params = []
    
    # 排除的关键词（排名系统、泛化词）
    excluded_keywords = {'top', 'ranking', 'best', 'qs', 'the', 'usnews', 'arwu', 'cwur',
                        '最好', '前五', '前10', '前20', '排名', 'world', 'global', 'international'}
    
    # 过滤词（严格匹配）
    for kw_type, kw_value in processed_keywords:
        if kw_type == 'country':
            core_filters.append('(country LIKE ? OR name_cn LIKE ?)')
            core_params.extend([f'%{kw_value}%', f'%{kw_value}%'])
        elif kw_type == 'level':
            core_filters.append('level = ?')
            core_params.append(kw_value)
        elif kw_type == 'keyword' and kw.lower() not in excluded_keywords:
            # 排除过于泛化的关键词和排名系统名称
            keyword_filters.append('(name LIKE ? OR name_cn LIKE ? OR motto LIKE ? OR city LIKE ?)')
            keyword_params.extend([f'%{kw}%', f'%{kw}%', f'%{kw}%', f'%{kw}%'])
    
    # 处理 filters
    if filters.get('country'):
        core_filters.append('country LIKE ?')
        core_params.append(f'%{filters["country"]}%')
    if filters.get('level'):
        core_filters.append('level = ?')
        core_params.append(filters['level'])
    if filters.get('region'):
        core_filters.append('region = ?')
        core_params.append(filters['region'])
    
    # 构建 SQL
    base_sql = '''
        SELECT *, 
            CASE 
                WHEN qs_rank IS NOT NULL THEN qs_rank 
                WHEN the_rank IS NOT NULL THEN the_rank 
                WHEN usnews_rank IS NOT NULL THEN usnews_rank 
                ELSE 99999 
            END as ranking_score
        FROM schools WHERE 1=1
    '''
    
    # 添加核心过滤
    if core_filters:
        base_sql += ' AND ' + ' AND '.join(core_filters)
    
    # 添加关键词搜索（OR 关系，拓宽搜索）
    if keyword_filters:
        base_sql += ' AND (' + ' OR '.join(keyword_filters) + ')'
    
    params = core_params + keyword_params
    
    # 如果有特定关键词，优先显示匹配度高的
    if any(k[0] == 'keyword' for k in processed_keywords):
        base_sql += ' ORDER BY ranking_score LIMIT 30'
    else:
        base_sql += ' ORDER BY ranking_score LIMIT 30'
    
    results = conn.execute(base_sql, params).fetchall()
    conn.close()
    
    # 构建响应
    school_results = []
    for school in results:
        school_dict = dict(school)
        # 清理badge_url
        if school_dict.get('badge_url') and not school_dict['badge_url'].startswith(('http://', 'https://')):
            school_dict['badge_url'] = f"/static/images/{school_dict['badge_url']}"
        # 移除内部字段
        school_dict.pop('ranking_score', None)
        school_results.append(school_dict)
    
    ai_provider = 'none'
    if ai_response:
        if os.environ.get('MINIMAX_API_KEY'):
            ai_provider = 'minimax'
        elif os.environ.get('OLLAMA_BASE_URL'):
            ai_provider = 'ollama'
        elif os.environ.get('CF_API_TOKEN'):
            ai_provider = 'cloudflare'
    
    # 判断是否是报考相关问题
    is_baokao = any(kw in query.lower() for kw in ['高考', '志愿', '报考', '专业', '就业', '考研', '选学校', '选专业', '大学怎么选'])
    
    # 张雪峰报考建议
    zhangxuefeng_tip = None
    if is_baokao:
        zhangxuefeng_tip = {
            'title': '💡 张雪峰报考建议',
            'tips': [
                '能去大城市就去大城市，北上广深优先',
                '计算机、电子信息、口腔医学就业好',
                '生化环材天坑专业，谨慎选择',
                '理工科专业优先，文科学校优先',
                '医学、法律必须考研，考虑清楚',
                '师范类稳定但薪资有限',
                '看就业选专业，不是看名字好听'
            ]
        }
    
    return jsonify({
        'success': True,
        'query': query,
        'ai_provider': ai_provider,
        'results': school_results,
        'total': len(school_results),
        'zhangxuefeng_tip': zhangxuefeng_tip,
        'analysis': {
            'keywords': keywords,
            'search_type': search_type,
            'filters': filters
        }
    })


def register_routes(app):
    """Register extended API routes"""
    app.register_blueprint(api_ext_bp, url_prefix='')
