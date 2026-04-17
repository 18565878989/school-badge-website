# 校徽网 V2.0 - app.py 重构计划

## 📊 当前状态
- **app.py**: 4674 行, 130 路由, 139 函数
- **目标**: 拆分到 routes/ 模块，app.py 保留核心配置

---

## 📅 迭代计划 (5天冲刺)

### Phase 1: 认证与核心功能 (Day 1 - 4月18日)

| 任务 | 负责人 | 路由/功能 | 交付物 |
|------|--------|-----------|--------|
| Auth模块 | @张飞 | `/login`, `/register`, `/logout`, `/send-sms`, `/auth/<provider>` | routes/auth.py |
| 装饰器 | @张飞 | `login_required`, `admin_required`, `security_headers`, `check_api_rate_limit` | utils/decorators.py |
| 主页面 | @张飞 | `/`, `/rankings` | routes/main.py |
| 学校详情 | @张飞 | `/school/<id>`, `/badge-history/<id>` | routes/schools.py |
| 用户页面 | @张飞 | `/my-likes` | routes/user.py (新建) |

### Phase 2: API路由 (Day 2 - 4月19日)

| 任务 | 负责人 | 路由/功能 | 交付物 |
|------|--------|-----------|--------|
| 学校API | @张飞 | `/api/schools`, `/api/schools/search`, `/api/schools/<id>` | routes/api.py |
| 点赞API | @张飞 | `/api/schools/<id>/like` | 合并到 api.py |
| 排名API | @张飞 | `/api/schools/rankings`, `/api/schools/levels` | routes/api.py |
| 地区API | @张飞 | `/api/schools/regions` | 合并到 api.py |
| 推荐API | @张飞 | `/api/recommend/favorites`, `/api/similar/<id>` | routes/recommendation_api.py |
| Deep Search | @张飞 | `/deep-search`, `/api/deep-search` | routes/ai_recommend.py |

### Phase 3: 社交与内容 (Day 3 - 4月20日)

| 任务 | 负责人 | 路由/功能 | 交付物 |
|------|--------|-----------|--------|
| 社交页面 | @王菲 | `/social`, `/social-v2` | routes/social.py |
| 话题功能 | @王菲 | `/create_topic`, `/topic/<id>/reply`, `/topic/<id>/like` | 合并到 social.py |
| 社交API | @王菲 | `/api/social/*`, `/api/topics/*` | routes/social_api.py |
| 校园风光 | @王菲 | `/campus`, `/campus/<region>` | routes/campus.py (新建) |
| 校园API | @王菲 | `/api/campus/*` | 合并到 campus.py |
| 香港学校 | @张飞 | `/hk-schools/*` | routes/hk_schools.py |
| 新闻页面 | @王菲 | `/news/*` | routes/news.py |

### Phase 4: 管理后台 (Day 4 - 4月21日)

| 任务 | 负责人 | 路由/功能 | 交付物 |
|------|--------|-----------|--------|
| Admin主页面 | @张飞 | `/admin`, `/admin/dashboard` | routes/admin.py |
| 学校管理 | @张飞 | `/admin/schools`, `/admin/school/add`, `/admin/school/<id>/edit`, `/admin/school/<id>/delete` | routes/admin.py |
| 用户管理 | @张飞 | `/admin/users`, `/admin/user/<id>/*` | 合并到 admin.py |
| 校园图片审核 | @张飞 | `/admin/campus-images`, `/admin/campus-edit/<id>`, `/admin/campus-approve/<id>` | routes/admin_extended.py |
| 校徽审核 | @张飞 | `/admin/badge-images`, `/admin/badge-edit/<id>`, `/admin/badge-approve/<id>` | routes/admin_extended.py |
| Admin API | @张飞 | `/api/admin/*` | routes/admin_extended.py |

### Phase 5: 整合与测试 (Day 5 - 4月22日)

| 任务 | 负责人 | 说明 |
|------|--------|------|
| 路由注册 | @张飞 | 确保所有 blueprints 正确注册到 app.py |
| 依赖注入 | @张飞 | 统一 service 层调用 |
| 单元测试 | @马斯克 | 编写核心功能测试用例 |
| 集成测试 | @马斯克 | API 端到端测试 |
| 部署验证 | @爱因斯坦 | 验证生产环境部署 |
| Bug修复 | 全员 | 根据测试结果修复 |

---

## 📋 每日站立会议

**时间**: 每天 9:00 AM
**形式**: 群组语音/文字
**内容**:
1. 昨日完成 ✅
2. 今日计划 🎯
3. 阻塞问题 🚧

---

## ✅ 验收标准

1. **app.py 压缩到 500 行以内** (当前 4674 行)
2. **所有路由正确注册** - 无 404
3. **所有功能测试通过** - 马斯克验证
4. **无回归问题** - 现有功能正常

---

## 🔧 技术规范

### 文件结构
```
routes/
├── __init__.py          # Blueprint 注册
├── auth.py              # 认证相关
├── main.py              # 主页面
├── schools.py           # 学校详情
├── rankings.py          # 排行榜
├── campus.py            # 校园风光
├── social.py            # 社交
├── news.py              # 新闻
├── hk_schools.py        # 香港学校
├── admin.py             # 管理后台
├── admin_extended.py    # 扩展管理
├── api.py               # 核心API
├── api_extended.py      # 扩展API
├── api_full.py          # 完整API
├── social_api.py        # 社交API
├── user_api.py          # 用户API
├── recommendation_api.py # 推荐API
├── misc.py              # 其他杂项
├── message_api.py       # 消息API
├── shop_membership.py   # 会员商城
└── compare.py           # 选校对比
```

### 依赖原则
- 路由层只做请求/响应处理
- 业务逻辑下沉到 services/
- 共享工具函数放到 utils/

---

## 📞 联系方式

| 角色 | ID | 职责 |
|------|-----|------|
| 乔布斯 (Tech Lead) | ou_f9b4cd66b753c84778c2218b1feefabf | 统筹协调 |
| 张飞 (Backend) | ou_857ae9321d5094d5e3f31bbf1878bef5 | 核心后端 |
| 王菲 (Frontend) | ou_bfcec6215a50b5104e2bc77c96b50ca6 | 前端实现 |
| 马斯克 (QA) | ou_1660e528de179464d6026677bcfb3023 | 测试验证 |
| 爱因斯坦 (DevOps) | ou_18a4563b90269bc3c27363482a00a4f7 | 部署运维 |
