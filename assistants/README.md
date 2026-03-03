# AI 校徽小助手系统

> 三个 AI 助手角色，帮你探索学校世界

## 助手角色

### 🐱 校徽鉴定师 (Badge Expert)
- **能力**: 图像识别
- **功能**: 上传校徽图片，识别是哪所学校
- **技能**: 校徽数据库匹配、相似度计算

### 🌍 旅行规划师 (Travel Planner)
- **能力**: 推荐系统
- **功能**: 根据位置和兴趣推荐学校参观路线
- **技能**: 地理位置排序、行程规划

### 📚 历史讲解员 (History Guide)
- **能力**: RAG 知识库
- **功能**: 讲述学校历史、故事、知名校友
- **技能**: 问答系统、信息检索

## 使用方法

```
GET /api/assistant/identify?image_url=xxx
GET /api/assistant/recommend?region=Asia&interest=history
GET /api/assistant/ask?q=清华大学的历史
```

## 对接

- 使用 Claude API 进行自然语言处理
- 本地数据库进行学校匹配
