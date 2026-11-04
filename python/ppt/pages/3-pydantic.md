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
student = {"姓名": "李四", "年龄": "20", "专业": "计算机科学"}
# 年龄写成了字符串，但没人检查
```

拼错键名、类型不对，都要运行到那行才发现。

## Pydantic 模型：定义即校验

```python
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    age: int
    major: str
```

::right::

## 使用

```python
s = Student(name="李四", age=20, major="计算机科学")

print(s.name)     # 李四
```

自动校验：

```python
Student(name="李四", age="二十", major="计算机科学")
# ❌ ValidationError：age 需要是整数
```

<div class="mt-4 p-3 bg-emerald-500/10 border-l-4 border-emerald-500 rounded text-sm">
<b>好处：</b>类型安全、IDE 自动补全、输入校验、轻松转 JSON。<br/>
Pydantic 是 FastAPI 的核心依赖；初学阶段先“会用”，不必深究底层。
</div>
