---
layout: two-cols
---

# 进阶：Pydantic 数据模型

## 字典 vs Pydantic

**传统字典：**
```python
student = {
    "姓名": "李四",
    "年龄": 20,
    "专业": "计算机科学"
}
# 无类型检查，IDE 无法提示
```

**Pydantic 模型：**
```python
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    age: int
    major: str
```

::right::

## 完整示例

```python
from pydantic import BaseModel

class Score(BaseModel):
    math: int
    english: int

class Student(BaseModel):
    name: str
    age: int
    major: str
    scores: Score = Score(math=0, english=0)

# 创建实例
s = Student(
    name="李四", age=20,
    major="计算机科学",
    scores=Score(math=90, english=85)
)

print(s.name)           # 李四
print(s.scores.math)    # 90
```

## Pydantic 优势

| 特性 | 说明 |
|------|------|
| 类型安全 | 自动校验数据类型 |
| IDE 提示 | 属性自动补全 |
| 数据校验 | 自动验证输入合法性 |
| 序列化 | 轻松转 JSON / dict |

<div class="mt-2 p-3 bg-emerald-500/10 rounded-lg text-sm">
🔒 Pydantic 是 FastAPI 的核心依赖，已成为 Python 数据建模的事实标准。
</div>