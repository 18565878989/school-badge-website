# 校徽网系统架构文档
> 版本: 1.0 | 更新日期: 2026-03-26 | 状态: 草稿

---

## 一、项目概述

**校徽网 (school-badge-website)** 是一个收集和展示全球学校校徽的 Web 应用，当前已收录超过 **7,270 所学校**，支持按地区/国家/城市/类型多维筛选，提供校徽鉴定 AI 助手、收藏排行、多语言(i18n)等功能。

**GitHub**: https://github.com/18565878989/school-badge-website

---

## 二、当前系统架构

### 2.1 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端框架** | Flask 3.0.0 | 单文件 `app.py` (3750+ 行) |
| **WSGI 服务器** | Gunicorn 21.2.0 | Railway 部署配置 |
| **数据库** | SQLite (`database.db`) | ~4MB，当前含 7270 条学校记录 |
| **前端模板** | Jinja2 | 30+ HTML 模板 |
| **静态资源** | Flask static | CSS/JS/images/badges |
| **国际化** | 自实现 i18n 模块 | 简繁转换、中英双语 |
| **AI 能力** | Claude API / TTS | assistants 模块 |
| **部署平台** | Railway (V2 Runtime) | `railway.json` 配置 |

### 2.2 核心模块

```
school-badge-website/
├── app.py              # 主应用 (3750+ 行，含 140+ 路由)
├── models.py           # 数据库模型 & 数据访问函数 (~700 行)
├── i18n.py             # 国际化模块：简繁转换、翻译函数 (~750 行)
├── config.py           # 配置 (极简，仅 DATABASE_PATH/SECRET_KEY)
│
├── assistants/         # AI 助手模块
│   ├── claude_chat.py  # Claude API 对话
│   ├── tts_helper.py   # TTS 语音播报
│   └── favorite_recommend.py  # 收藏推荐
│
├── scripts/            # 数据批处理脚本 (~50+ 个)
│   ├── batch_*.py      # 学校数据批量导入
│   ├── import_batch_*.py  # 增量导入
│   ├── fetch_*.py      # 网页爬虫获取校徽/校园图片
│   ├── daily_*.py      # 每日定时任务
│   └── *.sh            # Shell cron 脚本
│
├── templates/          # Jinja2 模板 (30+ 个)
│   ├── index.html      # 首页
│   ├── index_apple.html # Apple 风格首页
│   ├── school.html     # 学校详情页
│   ├── campus*.html    # 校园风采页 (按地区分)
│   ├── rankings.html   # 排行榜页
│   ├── social*.html    # 社交页面
│   ├── shop.html       # 商城页
│   ├── admin/          # 管理后台模板
│   └── ...
│
├── static/
│   ├── badges/         # 校徽图片存储
│   ├── css/            # 样式文件
│   ├── js/             # 前端 JS
│   └── images/         # 通用图片
│
├── data/               # 样本数据 JSON
├── docs/               # 设计研究文档
├── logs/               # 运行时日志
├── screenshots/        # UI 截图
├── skills/             # OpenClaw Skills (可选扩展)
└── memory/             # 开发记忆文档
```

### 2.3 数据库 Schema

**核心表**:

| 表名 | 行数(约) | 说明 |
|------|---------|------|
| `users` | ~50 | 用户表，含 role/oauth/permissions |
| `schools` | **7,270** | 学校主表，字段 13 个 |
| `likes` | ~500 | 用户-学校点赞关联 |
| `admin_logs` | ~200 | 管理员操作审计日志 |

**缺失字段 (值得注意)**:
- `schools` 表无独立的 `campus_image_url` 字段（校园图单独存储）
- 无专属的 `comments` / `reviews` 表（社交功能用 `posts` API）
- 无 `notifications` 存储表（纯 API 内存 or session）

### 2.4 数据分布

```
地区分布:
  Asia:        6,517 (89.6%)  ← 严重偏科
  Europe:        364 (5.0%)
  North America: 224 (3.1%)
  South America:  83 (1.1%)
  Oceania:        43 (0.6%)
  Africa:         39 (0.5%)

类型分布:
  university:  4,361 (60%)
  middle:        805 (11%)
  kindergarten:  491 (6.8%)
  elementary:    292 (4.0%)
  其他/空:     1,321 (18%)

校徽覆盖率: 3,374 / 7,270 = 46.4%
校园图覆盖率: 极低 (~6.3%)
```

---

## 三、问题评估 (Critical Issues)

### 🔴 高优先级

#### 1. **单体架构过度膨胀 — app.py (3750 行)**
   - 140+ 路由全堆在一个文件里
   - 路由处理函数平均 20-50 行，但被大量 HTML 渲染代码打断
   - 违反 Flask 最佳实践：每个 Blueprint 应独立文件
   - **影响**: 代码无法复用，测试几乎不可能，团队协作困难

#### 2. **SQLite 单文件数据库**
   - Railway 单副本部署时可用，但无法水平扩展
   - 无连接池，高并发写入（如批量 import）会锁库
   - 无原生 JSON 字段，权限/配置用字符串 JSON 模拟
   - **迁移路径**: PostgreSQL (Railway 已支持)

#### 3. **无测试体系**
   - 无 pytest/unittest
   - 无 CI/CD (除 push_to_github.sh 手动脚本)
   - 每次重构风险极高

#### 4. **重复性脚本爆炸 — ~50 个 batch_*.py / import_batch_*.py**
   - 代码高度相似（几乎都是学校数据导入）
   - 无统一的数据导入框架
   - 建议: 统一为一个 `scripts/import.py --batch=N` CLI 工具

### 🟡 中优先级

#### 5. **数据质量问题**
   - 89.6% 数据集中在亚洲，且 Asia 内中国学校占绝大多数
   - `level` 字段有大量非标准化值 ("University", "academy", "K-12"...)
   - `district` 只对 Hong Kong 有意义，通用性差
   - 5,659 所学校缺失校徽 (53.6%)

#### 6. **无缓存层**
   - 所有列表页直接查 SQLite，无 Redis/Memcached
   - 热门筛选（Asia + university）每次重新查询
   - 建议: Flask-Caching + Redis

#### 7. **OAuth 实现与 OAUTH_CONFIG.md 脱节**
   - 代码里写了 WeChat/Alipay/Twitter/Facebook OAuth，但无实际完成配置
   - `OAUTH_CONFIG.md` 存在但功能未启用

#### 8. ** assistants 模块未集成到主流程**
   - Claude/TTS/Favorite 模块存在但只能在管理后台手动触发
   - 无 WebSocket/流式响应，用户体验差（同步等待）

### 🟢 低优先级

#### 9. **i18n 实现原始**
   - `i18n.py` 700+ 行手写翻译函数，无 gettext 框架
   - 模板中 `{{ _(...) }}` 写法侵入性强

#### 10. **无 API 文档**
   - 大量 `/api/*` 路由无 OpenAPI/Swagger 文档

#### 11. **社交/商城/Membership 功能半成品**
   - 这些功能路由已写但无完整业务闭环
   - 可能造成维护负担

---

## 四、推荐优化方案

### 4.1 架构重构路线图

```
Phase 0: 整理 & 文档化 (1-2 周)
    ├── 编写完整架构文档 (本文档) ← 当前
    ├── 建立测试框架 (pytest + coverage)
    └── GitHub Actions CI/CD

Phase 1: 代码结构拆分 (2-3 周)
    ├── 将 app.py 拆分为 Flask Blueprints
    │   ├── bp_auth:      认证相关
    │   ├── bp_schools:   学校浏览/搜索
    │   ├── bp_admin:     管理后台
    │   ├── bp_social:    社交功能
    │   ├── bp_api:       REST API
    │   └── bp_assistants: AI 助手
    ├── models.py → 使用 SQLAlchemy ORM
    └── 提取配置到 config.yaml

Phase 2: 数据层升级 (1-2 周)
    ├── SQLite → PostgreSQL (通过 Railway)
    ├── 添加 Redis 缓存层
    └── 数据清洗 pipeline

Phase 3: 前端现代化 (2-4 周)
    ├── Tailwind CSS 统一样式
    ├── 提取公共组件
    └── 移动端适配

Phase 4: AI 功能深化 (持续)
    ├── 流式对话 (WebSocket)
    ├── 校徽图像识别自动化
    └── RAG 知识库
```

### 4.2 Blueprint 拆分建议

```
app/
├── __init__.py          # create_app() 工厂
├── routes/
│   ├── __init__.py
│   ├── auth.py          # /login, /register, /auth/*
│   ├── schools.py       # /, /school/<id>, /rankings
│   ├── admin.py         # /admin/*
│   ├── api.py           # /api/*
│   ├── campus.py        # /campus/*
│   └── assistants.py    # /assistants/*
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── school.py
│   └── like.py
├── services/
│   ├── school_service.py
│   ├── badge_fetcher.py
│   └── ai_service.py
└── utils/
    ├── cache.py
    └── i18n.py
```

### 4.3 依赖升级建议

```txt
# requirements.txt 建议升级为:
Flask==3.0.0
Flask-SQLAlchemy==3.1.0      # ORM 替代直接 sqlite3
Flask-Migrate==4.0.0         # 数据库迁移
Flask-Caching==2.3.0         # 缓存
Flask-BabelEx==0.9.4         # 国际化
Gunicorn==21.2.0
psycopg2-binary==2.9.9       # PostgreSQL
redis==5.0.0                 # 缓存后端
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.0
lxml==4.9.0
anthropic==0.25.0            # Claude API
pytest==8.0.0
pytest-cov==4.1.0
```

### 4.4 数据库 ER 优化建议

```sql
-- 建议新增字段/表
ALTER TABLE schools ADD COLUMN campus_images TEXT;  -- JSON 数组
ALTER TABLE schools ADD COLUMN tags TEXT;            -- JSON 数组
ALTER TABLE schools ADD COLUMN view_count INTEGER DEFAULT 0;
ALTER TABLE schools ADD COLUMN updated_at DATETIME;

-- 新增表
CREATE TABLE school_reviews (
    id SERIAL PRIMARY KEY,
    school_id INTEGER REFERENCES schools(id),
    user_id INTEGER REFERENCES users(id),
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 五、未来功能扩展规划

### 5.1 AI 驱动的核心功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| **校徽图像识别** | P0 | 用户上传图片 → AI 识别匹配学校 |
| **RAG 知识库问答** | P1 | 学校历史、校训、知名校友等知识问答 |
| **旅行规划师** | P2 | 按地理位置规划校徽参观路线 |
| **智能推荐** | P1 | 基于收藏/浏览记录的个性化推荐 |
| **流式 AI 对话** | P1 | WebSocket 实时流式响应 |

### 5.2 社区与UGC

| 功能 | 优先级 | 说明 |
|------|--------|------|
| **用户投稿入口** | P1 | 用户提交新学校/校徽，AI 预审 |
| **评论与评分** | P2 | 学校详情页评论系统 |
| **成就徽章系统** | P2 | 用户收藏里程碑激励 |
| **问答社区** | P3 | 围绕学校的 Q&A |

### 5.3 数据增强

| 功能 | 优先级 | 说明 |
|------|--------|------|
| **自动补全学校信息** | P1 | AI 自动从公开来源补全 description/motto |
| **校徽覆盖率达到 80%** | P0 | 持续爬虫 + AI 识别 |
| **校园图批量采集** | P1 | Wikipedia + 学校官网爬取 |
| **多语言名称** | P2 | 英文名、本地语言名 |

### 5.4 平台化

| 功能 | 优先级 | 说明 |
|------|--------|------|
| **开放 API** | P2 | 供第三方应用查询校徽数据 |
| **小程序/移动端** | P2 | 微信小程序或 React Native |
| **开放数据下载** | P3 | CC 许可的校徽数据集 |

---

## 六、技术债务清单

| # | 债务项 | 影响 | 修复成本 | 优先级 |
|---|--------|------|---------|--------|
| 1 | app.py 3750 行单文件 | 高 | 高 (重构) | P1 |
| 2 | 无测试覆盖 | 高 | 中 | P1 |
| 3 | SQLite 无连接池/无法扩展 | 高 | 中 (迁PG) | P1 |
| 4 | 50+ 重复 batch 脚本 | 中 | 中 | P2 |
| 5 | 校徽缺失率 53.6% | 中 | 高 (爬虫) | P1 |
| 6 | Asia 数据占比 89.6% | 中 | 低 (优先爬) | P2 |
| 7 | OAuth 功能未完成 | 低 | 中 | P3 |
| 8 | 无缓存层 | 中 | 低 | P2 |
| 9 | i18n 无框架支撑 | 低 | 中 | P3 |
| 10 | 无 API 文档 | 低 | 低 | P3 |

---

## 七、部署架构 (当前)

```
                    ┌─────────────┐
                    │   Railway   │
                    │  (V2 Runtime)│
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Gunicorn     Gunicorn     Gunicorn
         (Worker)     (Worker)     (Worker)
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │   SQLite    │
                    │ (database)  │
                    └─────────────┘
```

**建议演进**:

```
当前: Railway + SQLite
↓ 短期: Railway + PostgreSQL
↓ 中期: Railway + Redis Cache
↓ 长期: K8s + PostgreSQL + Redis + CDN
```

---

## 八、总结

校徽网是一个功能丰富、数据积累可观的项目（7270+ 学校，46% 校徽覆盖率），但由于早期快速迭代，积累了大量技术债务。最核心的问题是 **app.py 单体膨胀** 和 **缺乏测试体系**，这两点直接制约了后续开发速度和代码质量。

建议优先推进 **Phase 1 代码结构拆分** + **Phase 0 测试框架建立**，为后续所有功能开发打下坚实基础。

---

*文档维护: 请在每次重大架构变更后更新此文档*
