# 校徽网代码架构分析与优化建议

**日期**: 2026-03-27  
**项目**: 校徽网 (school-badge-website)  
**状态**: 需要优化

---

## 📊 当前项目规模

| 项目 | 数量 |
|------|------|
| Python 文件 | 217 个 |
| HTML 模板 | 27 个 |
| CSS 文件 | 4 个 |
| JavaScript | 1 个 |
| 路由数量 | 114 个 |
| 函数数量 | 122 个 |
| app.py 行数 | 3,955 行 |
| 数据库记录 | 7,313 所学校 |

---

## ⚠️ 主要问题

### 1. app.py 过于臃肿 (3,955行)

**问题**：
- 单文件包含所有路由、业务逻辑、配置
- 难以维护、测试、协作
- 违背单一职责原则

**建议**：
```
当前: app.py (3955行)
目标: 
  app.py          (精简到 ~200行，主入口)
  routes/         (路由模块化)
  services/       (业务逻辑)
  utils/          (工具函数)
```

### 2. 缺少分层架构

**当前结构**：
```
app.py          # 路由 + 业务逻辑 + SQL 混在一起
models.py       # 数据访问
templates/      # 视图
```

**建议结构**：
```
├── app.py                 # Flask 主入口
├── config.py             # 配置
├── routes/               # 路由层
│   ├── __init__.py
│   ├── api.py            # API 路由
│   ├── admin.py          # 管理后台
│   ├── schools.py        # 学校相关
│   ├── auth.py           # 认证相关
│   └── rankings.py       # 排名相关
├── services/             # 业务逻辑层
│   ├── school_service.py
│   ├── ranking_service.py
│   ├── user_service.py
│   └── cache_service.py
├── models/               # 数据模型 (当前为 models.py)
│   ├── __init__.py
│   ├── school.py
│   ├── user.py
│   └── ranking.py
├── utils/                 # 工具函数
│   ├── decorators.py
│   ├── validators.py
│   └── helpers.py
├── templates/             # 视图模板
├── static/               # 静态资源
├── scripts/              # 工具脚本 (108个，需要整理)
└── tests/                # 测试
```

### 3. 脚本目录混乱 (108个Python脚本)

**问题**：
- 大部分是一次性批量导入脚本
- 命名不规范 (batch_xxx.py, add_batch_xxx.py, import_batch_xxx.py)
- 难以区分哪些是有效脚本

**建议**：
```
scripts/
├── legacy/               # 归档旧脚本
│   ├── batch_001.py
│   └── ...
├── active/               # 仍在使用的脚本
│   ├── scrape_rankings.py
│   ├── scrape_badges.py
│   └── ...
└── cron/                 # 定时任务脚本
```

### 4. 静态资源缺少管理

**问题**：
- 所有 CSS 混在一个文件 (style.css)
- JS 只有1个文件 (main.js)
- 没有图片资源管理规范

**建议**：
```
static/
├── css/
│   ├── variables.css     # CSS 变量
│   ├── base.css          # 基础样式
│   ├── components.css    # 组件样式
│   ├── pages/            # 页面特定样式
│   └── admin.css
├── js/
│   ├── modules/         # JS 模块化
│   ├── utils.js
│   └── main.js
├── images/
│   ├── badges/          # 校徽图片
│   ├── campus/           # 校园图片
│   └── ui/              # UI 资源
└── fonts/               # 字体文件
```

### 5. 缺少测试和文档

**问题**：
- tests/ 目录存在但内容有限
- 没有 API 文档
- 没有架构文档

**建议**：
```
docs/
├── ARCHITECTURE.md       # 架构文档
├── API.md               # API 文档
├── DEPLOY.md            # 部署文档
└── CHANGELOG.md         # 变更记录
```

---

## ✅ 推荐的重构计划

### Phase 1: 模块化拆分 (1-2周)

1. **创建目录结构**
```bash
mkdir -p routes services models utils
```

2. **拆分 app.py**
- 路由移到 routes/
- 业务逻辑移到 services/
- 工具函数移到 utils/

3. **整理脚本目录**
- 创建 legacy/ 归档旧脚本
- 保留活跃脚本在根目录

### Phase 2: 基础设施完善 (1周)

1. 添加单元测试
2. 配置 CI/CD
3. 添加日志系统
4. 添加缓存层

### Phase 3: 性能优化 (1周)

1. 数据库查询优化
2. 添加索引
3. 图片 CDN 化
4. 前端资源压缩

---

## 📝 具体重构步骤

### Step 1: 创建 routes 包
```python
# routes/__init__.py
from flask import Blueprint

def register_routes(app):
    from . import admin, schools, auth, rankings, api
    admin.register(app)
    schools.register(app)
    # ...
```

### Step 2: 提取路由
```python
# routes/admin.py
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    # ...
```

### Step 3: 提取服务层
```python
# services/school_service.py
def get_school_with_rankings(school_id):
    school = get_school_by_id(school_id)
    rankings = get_school_rankings(school_id)
    return {...}
```

---

## 🎯 预期收益

| 指标 | 当前 | 优化后 |
|------|------|--------|
| app.py 行数 | 3,955 | ~200 |
| 模块耦合度 | 高 | 低 |
| 可测试性 | 困难 | 容易 |
| 团队协作 | 困难 | 容易 |
| 新功能开发速度 | 慢 | 快 |

---

## ⚠️ 风险和注意事项

1. **保持向后兼容**: 重构期间不改变 API
2. **逐步迁移**: 每次只迁移一个模块
3. **充分测试**: 每个阶段都要有测试覆盖
4. **版本控制**: 频繁提交，便于回滚

---

## 📋 待办清单

- [ ] 创建 routes/ 目录结构
- [ ] 创建 services/ 目录结构
- [ ] 创建 utils/ 目录结构
- [ ] 拆分 admin 路由
- [ ] 拆分学校相关路由
- [ ] 拆分认证路由
- [ ] 整理 scripts/ 目录
- [ ] 添加单元测试
- [ ] 编写 ARCHITECTURE.md
