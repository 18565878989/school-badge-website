# 校徽网代码重构方案

**版本**: V1.5.0-refactored
**更新日期**: 2026-03-27
**状态**: 规划中

---

## 📌 重构原则

1. **保持向后兼容**: 重构期间不影响现有功能
2. **渐进式迁移**: 每次只迁移一个模块
3. **充分测试**: 每个阶段都有测试覆盖
4. **版本管理**: 语义化版本号

---

## 📊 当前状态

| 组件 | 行数 | 路由数 | 问题 |
|------|------|--------|------|
| app.py | 3,945 | 114 | 过于臃肿 |
| models.py | 650+ | - | 尚可 |
| templates/ | 27个 | - | 需适配 |

---

## 🔢 版本规划

### 当前版本
- **V1.5.0**: 模块化目录结构创建完成

### 重构版本
- **V1.6.0**: 新模块与主app共存，新功能用新模块
- **V1.7.0**: 辅助模块迁移完成 (utils/)
- **V1.8.0**: 服务层迁移完成 (services/)
- **V1.9.0**: 路由Blueprint迁移完成
- **V2.0.0**: app.py精简完成，完整模块化

---

## 🚀 重构策略

### Phase 1: 准备阶段 (已完成 ✅)

**目标**: 创建模块化目录结构

**已完成**:
```bash
mkdir -p routes/ services/ models/ utils/
```

**创建的模块**:
- `routes/` - 6个路由模块
- `services/` - 2个服务模块
- `utils/` - 3个工具模块
- `scripts/legacy/` - 旧脚本归档

---

### Phase 2: 并行开发阶段 (V1.6.0) 🔄

**目标**: 新功能使用新模块开发，与主app共存

**策略**:
1. 新功能开发 → 新模块
2. 旧功能修改 → 逐步迁移
3. 主app保持不变

**新模块使用示例**:
```python
# 在 app.py 中导入
from services.school_service import get_schools_by_criteria
from utils.validators import validate_email
```

---

### Phase 3: 辅助模块迁移 (V1.7.0)

**目标**: utils/ 模块完全可用

**迁移顺序**:
1. `utils/decorators.py` - 装饰器迁移
2. `utils/validators.py` - 验证器迁移
3. `utils/formatters.py` - 格式化函数迁移

**验证**: 运行测试套件，确保功能一致

---

### Phase 4: 服务层迁移 (V1.8.0)

**目标**: services/ 模块完全可用

**迁移顺序**:
1. `services/ranking_service.py` - 排名服务
2. `services/school_service.py` - 学校服务

**验证**: API测试通过

---

### Phase 5: 路由Blueprint迁移 (V1.9.0)

**目标**: 使用Flask Blueprint

**迁移顺序**:
1. 独立路由 → `/rankings` → `routes/rankings.py`
2. 独立路由 → `/search` → `routes/search.py`
3. 独立路由 → 其他...

**关键代码**:
```python
# app.py
from routes import register_all_routes

def create_app():
    app = Flask(__name__)
    register_all_routes(app)  # 一行注册所有蓝图
    return app
```

---

### Phase 6: 主文件精简 (V2.0.0)

**目标**: app.py 从 3,945行 → ~300行

**最终结构**:
```python
# app.py (~300行)
from flask import Flask
from routes import register_all_routes

def create_app():
    app = Flask(__name__)
    register_all_routes(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
```

---

## 📋 迁移检查清单

### 每个模块迁移后检查:
- [ ] 功能测试通过
- [ ] API接口正常
- [ ] 性能无明显下降
- [ ] 文档更新

### 版本发布检查:
- [ ] 完整测试套件通过
- [ ] 更新 CHANGELOG.md
- [ ] Git tag 打好
- [ ] 飞书通知发布

---

## ⚠️ 风险和对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 迁移过程中功能损坏 | 高 | 保持主app可回滚 |
| 测试覆盖不足 | 中 | 添加单元测试 |
| 性能下降 | 低 | 性能测试对比 |

---

## 📝 版本日志格式

```markdown
## [V1.6.0] - 2026-04-01

### 新增
- utils/validators.py 模块

### 更改
- 搜索功能使用新服务层

### 修复
- 修复搜索页加载慢的问题
```

---

## 🎯 成功标准

| 指标 | 当前 | 目标 |
|------|------|------|
| app.py 行数 | 3,945 | ~300 |
| 模块耦合度 | 高 | 低 |
| 可测试性 | 困难 | 容易 |
| 新功能开发速度 | 慢 | 快 |
