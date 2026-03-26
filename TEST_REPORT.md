# 测试报告 - school-badge-website

**生成时间:** 2026-03-26  
**测试框架:** pytest 9.0.2  
**Python版本:** 3.14.2  
**测试结果:** ✅ 71 passed

---

## 📊 测试概览

| 测试文件 | 测试数 | 通过 | 失败 | 跳过 |
|---------|--------|------|------|------|
| test_i18n.py | 11 | 11 | 0 | 0 |
| test_models.py | 17 | 17 | 0 | 0 |
| test_routes.py | 43 | 43 | 0 | 0 |
| **总计** | **71** | **71** | **0** | **0** |

---

## 📁 测试文件结构

```
tests/
├── __init__.py        # 测试包初始化
├── conftest.py        # pytest fixtures 配置
├── test_i18n.py      # 国际化模块测试
├── test_models.py     # 数据库模型测试
└── test_routes.py     # Flask 路由集成测试
```

---

## 🧪 详细测试覆盖

### 1. test_i18n.py (11 tests) ✅

测试国际化模块功能:
- `TestI18nModule` - get_locale() 返回值类型、语言名称字典、_()翻译函数
- `TestI18nContent` - 英语/中文/繁体中文翻译存在性
- `TestLocalePersistence` - 语言切换路由重定向 (en, zh, zh_TW)

### 2. test_models.py (17 tests) ✅

测试数据库模型函数:
- `TestChineseConversion` (4 tests) - 简繁转换功能
  - 繁体→简体转换
  - 简体→繁体转换
  - 空字符串处理
  - 已是简体的文本不改变
- `TestUserModelReal` (3 tests) - 用户模型
  - 按用户名查找用户
  - 按ID查找用户
  - 错误密码验证
- `TestSchoolModelReal` (9 tests) - 学校模型
  - 获取所有学校
  - 按ID获取学校
  - 按地区筛选
  - 按级别筛选
  - 按名称搜索
  - 按中文名搜索
  - 组合搜索(名称+地区)
  - 获取地区列表
- `TestLikeModelReal` (3 tests) - 点赞模型
  - 获取点赞数
  - 无点赞时返回None
  - 点赞有效性验证

### 3. test_routes.py (43 tests) ✅

测试 Flask 路由功能:
- `TestIndexRoute` (5 tests) - 首页路由
  - GET / 返回200
  - 搜索查询
  - 地区筛选
  - 分页
  - 级别筛选
- `TestSchoolDetailRoute` (3 tests) - 学校详情
  - 有效ID
  - 无效ID (404/重定向)
  - 负数ID处理
- `TestLikeRoute` (2 tests) - 点赞路由
  - 未登录重定向
  - 已登录用户点赞
- `TestMyLikesRoute` (2 tests) - 我的收藏
  - 未登录重定向
  - 已登录返回200
- `TestLoginRoute` (2 tests) - 登录
  - GET 返回200
  - 空凭据处理
- `TestRegisterRoute` (2 tests) - 注册
  - GET 返回200
  - 空数据处理
- `TestLogoutRoute` (1 test) - 登出
- `TestLanguageRoute` (3 tests) - 语言切换 (en, zh, zh_TW)
- `TestBadgeHubRoute` (1 test) - 校徽中心
- `TestRankingsRoute` (1 test) - 排行榜
- `TestCampusRoutes` (7 tests) - 校区列表
  - /campus 全局
  - /campus/north-america
  - /campus/europe
  - /campus/asia
  - /campus/oceania
  - /campus/south-america
  - /campus/africa
- `TestSocialRoute` (1 test) - 社交
- `TestAdminRoutes` (4 tests) - 管理后台
  - 需管理员权限验证
  - init-db 可访问
- `TestAPIRoutes` (2 tests) - API端点
- `TestEdgeCases` (6 tests) - 边界情况
  - 404无效路由
  - SQL注入防护
  - XSS防护
  - 大页码处理
  - 负数页码处理
  - 中文特殊字符搜索

---

## 🔐 安全测试

✅ SQL注入测试通过 - `?q=' OR '1'='1` 被安全处理  
✅ XSS测试通过 - `<script>` 标签被安全处理  
✅ 管理员路由需认证 - 未认证用户被重定向  
✅ 点赞需登录 - 未登录用户被重定向

---

## ⚠️ 测试限制与改进建议

1. **集成测试为主**: 由于模型函数关闭连接的模式，使用真实数据库进行测试
2. **认证测试**: 当前使用session_transaction模拟认证，真实OAuth/WeChat登录需手动测试
3. **性能测试**: 未包含大规模数据性能测试
4. **前端测试**: 未包含JavaScript/浏览器端测试 (建议使用Playwright)

---

## 🚀 运行测试

```bash
# 安装测试依赖
./venv/bin/pip install pytest

# 运行所有测试
./venv/bin/python -m pytest tests/ -v

# 运行特定测试文件
./venv/bin/python -m pytest tests/test_models.py -v

# 生成覆盖率报告 (需安装pytest-cov)
./venv/bin/python -m pytest tests/ --cov=. --cov-report=html
```
