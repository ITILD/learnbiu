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

message = greet("王五")
print(message)      # 你好, 王五!
```

- `def` 定义函数，`name` 是参数
- `return` 返回结果
- 定义时不执行，**调用时才执行**
- 默认参数：`def area(length, width=1.0)`

::right::

## 返回多个值

```python
def divide(a, b):
    return a // b, a % b    # 本质是返回元组

q, r = divide(10, 3)        # q=3, r=1
```

## 进阶参数（先了解）

```python
def sum_all(*nums):         # *args：任意多个位置参数
    return sum(nums)

sum_all(1, 2, 3)            # 6
```

```python
def info(**kwargs):         # **kwargs：任意多个关键字参数
    print(kwargs)

info(name="张三", age=25)
```

<div class="mt-3 p-3 bg-indigo-500/10 border-l-4 border-indigo-500 rounded text-sm">
没写 <code>return</code> 时，函数默认返回 <code>None</code>。<br/>
命名习惯：小写字母 + 下划线，如 <code>get_user_name</code>。
</div>
