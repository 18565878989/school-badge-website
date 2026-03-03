# image-collect 技能

> 收集学校校徽和校园图片

## 功能

### badge-collect
收集学校校徽图片

```bash
python -m skills.image-collect badges --limit 100
```

### campus-collect
收集校园风光图片

```bash
python -m skills.image-collect campus --limit 50
```

## 收集策略

1. **校徽**: 官方logo、高清质量
2. **校园风光**: 
   - 学校建筑（教学楼、图书馆、礼堂等）
   - 学校活动（开学典礼、毕业典礼、体育活动等）
   - 校园环境（操场、花园、校门等）
3. **数据来源**:
   - 学校官网
   - Wikipedia
   - 官方社交媒体
