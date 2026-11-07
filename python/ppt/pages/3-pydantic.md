---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# Pydantic：数据模型

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
字典是“散装数据”，Pydantic 模型是<b>自带质检员的数据容器</b>：类型错了会立刻报错。
</div>

## 普通字典：没人把关

```python
student: dict = {
    "姓名": "李四",
    "年龄": 20,
    "专业": "计算机科学",
    "成绩": {"数学": 90, "英语": 85},
}
```

拼错键名、类型不对，都要运行到那行才发现。

## Pydantic 模型：定义即校验

```python
from pydantic import BaseModel

class Score(BaseModel):
    math: int
    english: int

class Student(BaseModel):
    name: str
    age: int
    major: str
    average_score: Score = Score(math=0, english=0)  # 默认值
```

::right::

## 使用

```python
student1 = Student(
    name="李四",
    age=20,
    major="计算机科学",
    average_score=Score(math=90, english=85),
)

student1.name                  # 李四
student1.average_score.math    # 90
```

试一试：`age="二十"` 会立刻抛出 `ValidationError`，不用等到运行那行才发现。

<div class="mt-4 p-3 bg-emerald-500/10 border-l-4 border-emerald-500 rounded text-sm">
<b>好处：</b>类型安全、IDE 自动补全、输入校验、轻松转 JSON。<br/>
运行前先装依赖：<code>uv add pydantic</code>
</div>

<div class="mt-3 text-xs opacity-50">
对应示例：source/pydantic_example.py · <code>uv run pydantic_example.py</code>
</div>
