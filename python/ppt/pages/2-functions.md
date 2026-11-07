---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# 函数：打包与复用

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
函数像一台榨汁机：<b>参数</b>是水果，<b>返回值</b>是果汁。
</div>

## 定义与调用

```python
def greet(name: str) -> str:
    """向某人问好"""
    return f"你好, {name}!"

print(greet("王五"))
# 输出：你好, 王五!
```

## 默认参数

```python
def calculate_area(length: float, width: float = 1.0) -> float:
    return length * width

calculate_area(5)      # 5.0（宽度用默认值）
calculate_area(5, 3)   # 15.0
```

- `def` 定义函数，`return` 返回结果
- 定义时不执行，**调用时才执行**

::right::

## 返回多个值

```python
def divide(a: int, b: int) -> tuple[int, int]:
    return a // b, a % b    # 本质是返回元组

q, r = divide(10, 3)        # 商=3, 余=1
```

## 可变参数（先了解）

```python
def sum_numbers(*numbers: int) -> int:
    return sum(numbers)     # *args：任意多个位置参数

sum_numbers(1, 2, 3, 4, 5)  # 15

def show_info(**kwargs):    # **kwargs：任意多个关键字参数
    ...

show_info(name="张三", age=25)
```

<div class="mt-3 p-3 bg-indigo-500/10 border-l-4 border-indigo-500 rounded text-sm">
没写 <code>return</code> 时，函数默认返回 <code>None</code>。
</div>

<div class="mt-3 text-xs opacity-50">
对应示例：source/functions.py · <code>uv run functions.py</code>
</div>
