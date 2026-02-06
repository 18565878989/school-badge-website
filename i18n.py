# Flask Multilingual Support

from flask import Flask, request, session, g

# Language translations
TRANSLATIONS = {
    'zh': {
        # Navigation
        'home': '首页',
        'my_likes': '我的收藏',
        'login': '登录',
        'register': '注册',
        'logout': '退出',
        'language': '语言',
        
        # Home
        'hero_title': '探索全球名校校徽',
        'hero_subtitle': 'Discover School Badges from Around the World',
        'search_placeholder': '搜索学校名称、城市或国家...',
        'all_regions': '所有地区',
        'all_types': '所有类型',
        'university': '大学',
        'middle_school': '中学',
        'elementary_school': '小学',
        'kindergarten': '幼儿园',
        'clear_filters': '清除筛选',
        'schools_count': '共 {} 所学校',
        'no_schools': '没有找到符合条件的学校',
        'view_all': '查看全部学校',
        
        # School Card
        'founded': '建校年份',
        'principal': '现任校长',
        'location': '位置',
        'region': '地区',
        
        # School Detail
        'back': '返回学校列表',
        'like': '收藏',
        'liked': '已收藏',
        'download': '下载校徽',
        'likes_count': '{} 人收藏',
        'motto_label': '校训',
        'website': '官方网站',
        'visit_website': '访问 {} 官网',
        'view_on_maps': '在 Google Maps 中查看',
        'map_location': '地图位置',
        'description_title': '学校简介',
        
        # Auth
        'username': '用户名',
        'password': '密码',
        'email': '邮箱',
        'all_required': '所有字段都为必填项。',
        'register_success': '注册成功！请登录。',
        'username_exists': '用户名或邮箱已被注册。',
        'login_error': '用户名或密码错误。',
        'welcome_back': '欢迎回来，{}！',
        'logout_success': '您已退出登录。',
        'please_login': '请先登录后再访问此页面。',
        'already_account': '已有账号？',
        'no_account': '还没有账号？',
        
        # Footer
        'copyright': '© 2024 校徽网 · School Badge Collection',
    },
    'en': {
        # Navigation
        'home': 'Home',
        'my_likes': 'My Likes',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'language': 'Language',
        
        # Home
        'hero_title': 'Discover School Badges',
        'hero_subtitle': 'Explore prestigious institutions worldwide',
        'search_placeholder': 'Search by school name, city or country...',
        'all_regions': 'All Regions',
        'all_types': 'All Types',
        'university': 'University',
        'middle_school': 'Middle School',
        'elementary_school': 'Elementary School',
        'kindergarten': 'Kindergarten',
        'clear_filters': 'Clear Filters',
        'schools_count': '{} schools found',
        'no_schools': 'No schools found matching your criteria',
        'view_all': 'View All Schools',
        
        # School Card
        'founded': 'Founded',
        'principal': 'President / Principal',
        'location': 'Location',
        'region': 'Region',
        
        # School Detail
        'back': 'Back to All Schools',
        'like': 'Like',
        'liked': 'Liked',
        'download': 'Download Badge',
        'likes_count': '{} likes',
        'motto_label': 'Motto',
        'website': 'Official Website',
        'visit_website': 'Visit {} Website',
        'view_on_maps': 'View on Google Maps',
        'map_location': 'Map Location',
        'description_title': 'About',
        
        # Auth
        'username': 'Username',
        'password': 'Password',
        'email': 'Email',
        'all_required': 'All fields are required.',
        'register_success': 'Registration successful! Please login.',
        'username_exists': 'Username or email already exists.',
        'login_error': 'Invalid username or password.',
        'welcome_back': 'Welcome back, {}!',
        'logout_success': 'You have been logged out.',
        'please_login': 'Please login to access this page.',
        'already_account': 'Already have an account?',
        'no_account': "Don't have an account?",
        
        # Footer
        'copyright': '© 2024 School Badge Collection',
    },
    'fr': {
        # Navigation
        'home': 'Accueil',
        'my_likes': 'Mes favoris',
        'login': 'Connexion',
        'register': 'Inscription',
        'logout': 'Déconnexion',
        'language': 'Langue',
        
        # Home
        'hero_title': 'Découvrez les écussons scolaires',
        'hero_subtitle': 'Explorez les établissements prestigieux du monde entier',
        'search_placeholder': 'Rechercher par nom, ville ou pays...',
        'all_regions': 'Toutes les régions',
        'all_types': 'Tous les types',
        'university': 'Université',
        'middle_school': 'Collège',
        'elementary_school': 'École primaire',
        'kindergarten': 'Maternelle',
        'clear_filters': 'Effacer les filtres',
        'schools_count': '{} établissements trouvés',
        'no_schools': 'Aucun établissement trouvé',
        'view_all': 'Voir tous',
        
        # School Card
        'founded': 'Fondé',
        'principal': 'Directeur / Présidente',
        'location': 'Localisation',
        'region': 'Région',
        
        # School Detail
        'back': 'Retour à tous les établissements',
        'like': 'Favoris',
        'liked': 'Dans vos favoris',
        'download': 'Télécharger',
        'likes_count': '{} mentions J\'aime',
        'motto_label': 'Devise',
        'website': 'Site officiel',
        'visit_website': 'Visiter le site de {}',
        'view_on_maps': 'Voir sur Google Maps',
        'map_location': 'Emplacement sur la carte',
        'description_title': 'À propos',
        
        # Auth
        'username': 'Nom d\'utilisateur',
        'password': 'Mot de passe',
        'email': 'Email',
        'all_required': 'Tous les champs sont requis.',
        'register_success': 'Inscription réussie! Veuillez vous connecter.',
        'username_exists': 'Nom d\'utilisateur ou email déjà utilisé.',
        'login_error': 'Nom d\'utilisateur ou mot de passe incorrect.',
        'welcome_back': 'Bienvenue, {}!',
        'logout_success': 'Vous avez été déconnecté.',
        'please_login': 'Veuillez vous connecter pour accéder à cette page.',
        'already_account': 'Vous avez déjà un compte?',
        'no_account': 'Pas de compte?',
        
        # Footer
        'copyright': '© 2024 Collection d\'écussons scolaires',
    },
    'de': {
        # Navigation
        'home': 'Startseite',
        'my_likes': 'Meine Favoriten',
        'login': 'Anmelden',
        'register': 'Registrieren',
        'logout': 'Abmelden',
        'language': 'Sprache',
        
        # Home
        'hero_title': 'Entdecken Sie Schulwappen',
        'hero_subtitle': 'Prestigeträchtige Institutionen weltweit erkunden',
        'search_placeholder': 'Suchen nach Name, Stadt oder Land...',
        'all_regions': 'Alle Regionen',
        'all_types': 'Alle Typen',
        'university': 'Universität',
        'middle_school': 'Gymnasium',
        'elementary_school': 'Grundschule',
        'kindergarten': 'Kindergarten',
        'clear_filters': 'Filter löschen',
        'schools_count': '{} Schulen gefunden',
        'no_schools': 'Keine Schulen gefunden',
        'view_all': 'Alle anzeigen',
        
        # School Card
        'founded': 'Gegründet',
        'principal': 'Rektor / Direktorin',
        'location': 'Standort',
        'region': 'Region',
        
        # School Detail
        'back': 'Zurück zu allen Schulen',
        'like': 'Merken',
        'liked': 'Gemerkt',
        'download': 'Herunterladen',
        'likes_count': '{} Likes',
        'motto_label': 'Wahlspruch',
        'website': 'Offizielle Website',
        'visit_website': '{} Website besuchen',
        'view_on_maps': 'Auf Google Maps ansehen',
        'map_location': 'Kartenstandort',
        'description_title': 'Über',
        
        # Auth
        'username': 'Benutzername',
        'password': 'Passwort',
        'email': 'E-Mail',
        'all_required': 'Alle Felder sind erforderlich.',
        'register_success': 'Registrierung erfolgreich! Bitte anmelden.',
        'username_exists': 'Benutzername oder E-Mail bereits vergeben.',
        'login_error': 'Ungültiger Benutzername oder Passwort.',
        'welcome_back': 'Willkommen zurück, {}!',
        'logout_success': 'Sie wurden abgemeldet.',
        'please_login': 'Bitte anmelden, um auf diese Seite zuzugreifen.',
        'already_account': 'Bereits registriert?',
        'no_account': 'Noch kein Konto?',
        
        # Footer
        'copyright': '© 2024 Schulwappen-Sammlung',
    },
    'ja': {
        # Navigation
        'home': 'ホーム',
        'my_likes': 'マイリスト',
        'login': 'ログイン',
        'register': '登録',
        'logout': 'ログアウト',
        'language': '言語',
        
        # Home
        'hero_title': '校章コレクション',
        'hero_subtitle': '世界の名門校を探ろう',
        'search_placeholder': '学校名、都市、国で検索...',
        'all_regions': 'すべての地域',
        'all_types': 'すべてのタイプ',
        'university': '大学',
        'middle_school': '中学校',
        'elementary_school': '小学校',
        'kindergarten': '幼稚園',
        'clear_filters': 'フィルターをクリア',
        'schools_count': '{} 校見つかりました',
        'no_schools': '条件に一致する学校がありません',
        'view_all': 'すべて見る',
        
        # School Card
        'founded': '創立',
        'principal': '学園長 / 校長',
        'location': '所在地',
        'region': '地域',
        
        # School Detail
        'back': '学校リストに戻る',
        'like': 'お気に入りに追加',
        'liked': 'お気に入り済み',
        'download': 'ダウンロード',
        'likes_count': '{} 件のいいね',
        'motto_label': '校訓',
        'website': '公式サイト',
        'visit_website': '{} 公式サイトを見る',
        'view_on_maps': 'Google マップで見る',
        'map_location': '地図位置',
        'description_title': '学校について',
        
        # Auth
        'username': 'ユーザー名',
        'password': 'パスワード',
        'email': 'メールアドレス',
        'all_required': 'すべての項目を入力してください。',
        'register_success': '登録完了！ログインしてください。',
        'username_exists': 'ユーザー名またはメールアドレスは既に使われています。',
        'login_error': 'ユーザー名またはパスワードが正しくありません。',
        'welcome_back': 'おかえりなさい、{}さん！',
        'logout_success': 'ログアウトしました。',
        'please_login': 'このサイトにアクセスするにはログインしてください。',
        'already_account': 'アカウントをお持ちですか？',
        'no_account': 'アカウントをお持ちでないですか？',
        
        # Footer
        'copyright': '© 2024 校章コレクション',
    }
}

# Language names for selector
LANGUAGE_NAMES = {
    'zh': '中文',
    'en': 'English',
    'fr': 'Français',
    'de': 'Deutsch',
    'ja': '日本語'
}

def get_locale():
    """Get current locale from session or request."""
    if 'lang' in session:
        return session['lang']
    
    # Check Accept-Language header
    accept_language = request.headers.get('Accept-Language', '')
    for lang in accept_language.split(','):
        lang_code = lang.split(';')[0].strip().lower()
        if lang_code.startswith('zh'):
            return 'zh'
        elif lang_code.startswith('en'):
            return 'en'
        elif lang_code.startswith('fr'):
            return 'fr'
        elif lang_code.startswith('de'):
            return 'de'
        elif lang_code.startswith('ja'):
            return 'ja'
    
    return 'zh'  # Default to Chinese

def _(key):
    """Translate a key to the current language."""
    locale = get_locale()
    translations = TRANSLATIONS.get(locale, TRANSLATIONS['zh'])
    return translations.get(key, TRANSLATIONS['zh'].get(key, key))
