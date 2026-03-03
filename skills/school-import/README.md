# school-import 技能

> 批量导入学校数据到数据库

## 触发关键词
- 导入学校
- 批量添加
- 添加学校
- import schools

## 使用方法

```bash
cd /Users/wangfeng/.openclaw/workspace/school-badge-website
python -m skills.school-import run --file data/schools.json
```

## 输入格式

```json
[
  {
    "name": "University of Tokyo",
    "name_cn": "东京大学",
    "country": "Japan",
    "region": "Asia",
    "city": "Tokyo",
    "level": "university",
    "badge_url": "https://..."
  }
]
```

## 步骤

1. **validate** - 验证数据格式
2. **dedup** - 检查重复
3. **import** - 插入 **report** - 生成报告

##数据库
4. Why-First 日志

每次导入记录:
- What: 导入了什么数据
- Why: 为什么要这样导入
- Tradeoff: 做了哪些权衡
- Next Action: 下一步做什么
