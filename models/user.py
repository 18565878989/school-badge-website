"""
User Model - 用户相关数据访问
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# ============ 简繁转换函数 ============

def traditional_to_simplified(text):
    """繁体转简体"""
    if not text:
        return text
    mapping = {
        '大學': '大学', '學院': '学院', '學校': '学校',
        '北京': '北京', '清華': '清华', '交通': '交通',
        '復旦': '复旦', '浙江': '浙江', '南京': '南京',
        '上海': '上海', '武漢': '武汉', '成都': '成都',
        '西安': '西安', '哈爾濱': '哈尔滨', '廣州': '广州',
        '中山': '中山', '廈門': '厦门', '天津': '天津',
        '蘇州': '苏州', '重慶': '重庆', '香港': '香港',
        '澳門': '澳门', '臺灣': '台湾', '臺北': '台北',
        '高雄': '高雄', '新竹': '新竹', '師範': '师范',
        '工業': '工业', '科技': '科技', '醫學': '医学',
        '農業': '农业', '海洋': '海洋', '石油': '石油',
        '理工': '理工', '財經': '财经', '政法': '政法',
        '外語': '外语', '語言': '语言', '音樂': '音乐',
        '美術': '美术', '體育': '体育', '軍事': '军事',
        '航空': '航空', '航天': '航天', '電子': '电子',
        '機械': '机械', '化工': '化工', '建築': '建筑',
        '水利': '水利', '電力': '电力', '鐵路': '铁路',
        '郵電': '邮电', '林業': '林业', '畜牧': '畜牧',
        '醫藥': '医药', '中醫': '中医', '藥學': '药学',
        '護理': '护理', '工商': '工商', '管理': '管理',
        '人力': '人力', '資源': '资源', '環境': '环境',
        '材料': '材料', '能源': '能源', '動力': '动力',
        '計算機': '计算机', '信息': '信息', '軟件': '软件',
        '網絡': '网络', '自動化': '自动化', '光電': '光电',
        '精密': '精密', '儀器': '仪器', '物理': '物理',
        '化學': '化学', '數學': '数学', '生物': '生物',
    }
    result = text
    for trad, simp in mapping.items():
        result = result.replace(trad, simp)
    return result

def simplified_to_traditional(text):
    """简体转繁体"""
    if not text:
        return text
    mapping = {
        '大学': '大學', '学院': '學院', '学校': '學校',
        '清华': '清華', '复旦': '復旦', '师范': '師範',
        '工业': '工業', '科技': '科技', '医学': '醫學',
        '农业': '農業', '海洋': '海洋', '理工': '理工',
        '财经': '財經', '政法': '政法', '外语': '外語',
        '语言': '語言', '音乐': '音樂', '美术': '美術',
        '体育': '體育', '军事': '軍事', '航空': '航空',
        '航天': '航天', '电子': '電子', '机械': '機械',
        '化工': '化工', '建筑': '建築', '水利': '水利',
        '电力': '電力', '铁路': '鐵路', '邮电': '郵電',
        '林业': '林業', '畜牧': '畜牧', '医药': '醫藥',
        '中医': '中醫', '药学': '藥學', '护理': '護理',
        '工商': '工商', '管理': '管理', '人力': '人力',
        '资源': '資源', '环境': '環境', '材料': '材料',
        '能源': '能源', '动力': '動力', '计算机': '計算機',
        '信息': '信息', '软件': '軟件', '网络': '網絡',
        '自动化': '自動化', '光电': '光電', '精密': '精密',
        '仪器': '儀器', '物理': '物理', '化学': '化學',
        '数学': '數學', '生物': '生物',
    }
    result = text
    for simp, trad in mapping.items():
        result = result.replace(simp, trad)
    return result

def get_db_connection():
    """获取数据库连接"""
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ============ 用户查询 ============

def get_user_by_username(username):
    """根据用户名查询用户"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """根据ID查询用户"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_phone(phone):
    """根据手机号查询用户"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE phone = ?', (phone,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_oauth(provider, oauth_id):
    """根据OAuth信息查询用户"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE oauth_provider = ? AND oauth_id = ?',
        (provider, oauth_id)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users():
    """获取所有用户"""
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(u) for u in users]

def get_users_with_roles():
    """获取所有用户及其角色"""
    conn = get_db_connection()
    users = conn.execute('''
        SELECT u.*, 
               COALESCE(r.permissions, '{}') as permissions,
               COALESCE(r.data_scope, '["own"]') as data_scope
        FROM users u
        LEFT JOIN user_roles r ON u.role = r.role_name
        ORDER BY u.created_at DESC
    ''').fetchall()
    conn.close()
    return [dict(u) for u in users]

# ============ 用户创建/更新/删除 ============

def create_user(username, password, email, role='user', phone=None, 
                oauth_provider=None, oauth_id=None, avatar_url=None):
    """创建新用户"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            INSERT INTO users (username, password_hash, email, phone, role, 
                             oauth_provider, oauth_id, avatar_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (username, generate_password_hash(password), email, phone, role,
              oauth_provider, oauth_id, avatar_url))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except Exception as e:
        conn.close()
        raise e

def verify_password(username, password):
    """验证密码"""
    user = get_user_by_username(username)
    if not user:
        return None
    if check_password_hash(user['password_hash'], password):
        return user
    return None

def verify_phone_code(phone, code):
    """验证手机验证码"""
    # 实际项目中应使用Redis存储验证码
    # 这里简化处理
    return True

def update_user_role(user_id, new_role, data_scope='["all"]'):
    """更新用户角色"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET role = ? WHERE id = ?',
        (new_role, user_id)
    )
    conn.commit()
    conn.close()

def update_user_avatar(user_id, avatar_url):
    """更新用户头像"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET avatar_url = ? WHERE id = ?',
        (avatar_url, user_id)
    )
    conn.commit()
    conn.close()

def delete_user(user_id):
    """删除用户"""
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

# ============ 权限相关 ============

def is_admin(user_id):
    """检查用户是否为管理员"""
    user = get_user_by_id(user_id)
    return user and user['role'] == 'admin'

def get_user_role(user_id):
    """获取用户角色"""
    user = get_user_by_id(user_id)
    return user['role'] if user else None

def get_user_permissions(user_id):
    """获取用户权限"""
    user = get_user_by_id(user_id)
    if not user:
        return []
    import json
    try:
        return json.loads(user.get('permissions', '[]'))
    except:
        return []

def has_permission(user_id, permission_code):
    """检查用户是否有指定权限"""
    perms = get_user_permissions(user_id)
    return permission_code in perms or 'admin:all' in perms

def get_all_roles():
    """获取所有角色"""
    conn = get_db_connection()
    roles = conn.execute('SELECT DISTINCT role FROM users').fetchall()
    conn.close()
    return [r['role'] for r in roles]

def get_all_permissions():
    """获取所有权限定义"""
    conn = get_db_connection()
    perms = conn.execute('SELECT * FROM permission_definitions WHERE is_active = 1').fetchall()
    conn.close()
    return [dict(p) for p in perms]

def get_role_permissions_db(role):
    """获取角色权限"""
    conn = get_db_connection()
    perms = conn.execute(
        'SELECT permission_code FROM role_permissions WHERE role = ? AND granted = 1',
        (role,)
    ).fetchall()
    conn.close()
    return [p['permission_code'] for p in perms]

def update_role_permissions(role, permissions):
    """更新角色权限"""
    conn = get_db_connection()
    # 清除现有权限
    conn.execute('DELETE FROM role_permissions WHERE role = ?', (role,))
    # 添加新权限
    for perm in permissions:
        conn.execute(
            'INSERT INTO role_permissions (role, permission_code, granted) VALUES (?, ?, 1)',
            (role, perm)
        )
    conn.commit()
    conn.close()

def update_user_permissions(user_id, permissions):
    """更新用户权限"""
    conn = get_db_connection()
    import json
    conn.execute(
        'UPDATE users SET permissions = ? WHERE id = ?',
        (json.dumps(permissions), user_id)
    )
    conn.commit()
    conn.close()
