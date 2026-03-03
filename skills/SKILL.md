# SKILL.md - 校徽网技能系统

> 渐进式任务封装，按需加载

## 技能格式

```yaml
name: skill-name
description: 技能描述
trigger_keywords:
  - 关键词1
  - 关键词2
steps:
  - name: step1
    command: python script.py
    description: 步骤描述
```

## 可用技能

### school-import
- 触发: "导入学校"、"批量添加"
- 功能: 批量导入学校数据

### data-cleanup  
- 触发: "清理数据"、"去重"
- 功能: 数据去重和清理

### image-optimize
- 触发: "优化图片"、"压缩校徽"
- 功能: 优化校徽图片

### stats-analyze
- 触发: "统计分析"、"数据报告"
- 功能: 生成统计报告
