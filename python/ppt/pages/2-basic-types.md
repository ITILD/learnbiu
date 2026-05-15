---
layout: two-cols
---

# 基础语法：变量与数据类型

## 四种基本类型

```python
name: str = "张三"       # 字符串
age: int = 25            # 整数
height: float = 1.75     # 浮点数
is_student: bool = True  # 布尔值
```

## 类型注解（新语法）

Python 3.12+ 推荐使用简洁的类型注解：

```python
# 旧写法
from typing import List, Dict
names: List[str] = ["a", "b"]

# 新写法（推荐）
names: list[str] = ["a", "b"]
scores: dict[str, int] = {"math": 90}
```

::right::

## 类型转换

```python
int("42")       # "42" → 42
float("3.14")   # "3.14" → 3.14
str(100)        # 100 → "100"
bool(1)         # 1 → True
bool(0)         # 0 → False
```

## f-string 格式化

```python
name = "张三"
age = 25
print(f"我叫{name}，今年{age}岁")
# 输出：我叫张三，今年25岁
```

<div class="mt-4 p-4 bg-yellow-500/10 rounded-lg">
📌 Python 是<b>动态类型</b>语言，变量无需声明类型即可使用，但添加类型注解能提高代码可读性。
</div>