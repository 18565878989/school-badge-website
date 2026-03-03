# 校徽网改进工程计划

## 项目概述
将校徽网从单一功能展示网站升级为 AI 驱动的多用户协作平台

## 改进方向

### 1. 🐱 AI 校徽小助手系统
- **校徽鉴定师**: 图像识别上传的校徽图片
- **旅行规划师**: 推荐学校参观路线
- **历史讲解员**: RAG 知识库问答

### 2. 👥 多用户协作社区
- 用户注册/登录系统
- 收藏功能 → "我的学校清单"
- 用户贡献入口
- 社区评分系统

### 3. 🎨 温馨风格改造
- 猫咪吉祥物
- 动态打招呼
- 节气/节日主题

### 4. 🤖 后台 AI 协作
- Why-First 操作日志
- AI 审核数据完整性
- 自动补全缺失字段

### 5. 📦 Skills 渐进式系统
- skill:school-import
- skill:image-optimize
- skill:data-cleanup
- skill:stats-analyze

---

## 里程碑

### Phase 1: Skills 基础设施 (本周)
- [x] 创建 skills 目录结构
- [x] 定义 skill 格式规范
- [x] 实现 skill:school-import
- [x] 实现 skill:data-cleanup
- [x] 实现 skill:stats-analyze

### Phase 2: AI 助手系统 (持续迭代)
- [x] 设计三个助手角色
- [x] 实现校徽鉴定师 (BadgeExpert)
- [x] 实现旅行规划师 (TravelPlanner)
- [x] 实现历史讲解员 (HistoryGuide)
- [x] 添加 Flask API 路由
- [x] 创建 AI 助手页面

#### Phase 2.x: 增强功能
- [x] 添加学校对比功能 (CompareAssistant)
- [x] 添加智能推荐 (RecommendAssistant)
- [x] 添加问答助手 (SchoolQuizAssistant)
- [x] 添加 Claude API 对话 (ClaudeChatAssistant)
- [x] 添加 TTS 语音播报 (TTSAssistant)
- [x] 添加收藏推荐 (FavoriteRecommendAssistant)

### Phase 3: 用户系统 (下下周)
- [ ] 用户数据库设计
- [ ] 注册/登录 API
- [ ] 收藏功能

### Phase 4: 温馨风格 (第4周)
- [ ] 吉祥物设计
- [ ] 动态 UI 元素

### Phase 5: 后台 AI 协作 (第5周)
- [ ] 操作日志增强
- [ ] AI 审核模块

---

## 当前状态: 进行中
**最后更新**: 2026-03-03

## 图片收集任务

### 数据统计 (2026-03-03)
- 总学校数: 8,412
- 有校徽: 2,753 (32.7%)
- 有校园图: 527 (6.3%)
- 缺失校徽: 5,659
- 缺失校园图: 7,885

### 收集策略
1. **校徽收集优先级**: 大学 > 中学 > 小学
2. **校园图片**: 优先自然风光、高清质量、无人像
3. **数据来源**:
   - 学校官网
   - Wikipedia
   - 官方社交媒体

### 定时任务 (Cron)
- 每天自动执行图片收集
- 优先处理高价值学校

## 待完成任务

### 1. 图片收集自动化
- [ ] 配置每日 Cron 任务
- [ ] 添加更多图片源
- [ ] 优化图片质量筛选
