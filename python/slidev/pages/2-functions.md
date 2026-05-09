---
layout: two-cols
---

# 函数：定义与参数

## 基本定义

```python
def greet(name: str) -> str:
    """向某人问好"""
    return f"你好, {name}!"

print(greet("王五"))
# 输出：你好, 王五!
```

## 参数类型

```python
# 默认参数
def area(length: float, width: float = 1.0):
    return length * width

# 可变参数 *args
def sum_all(*numbers: int) -> int:
    return sum(numbers)

# 关键字参数 **kwargs
def info(**kwargs):
    for k, v in kwargs.items():
        print(f"{k}: {v}")
```

::right::

## 调用示例

```python
# 默认参数
area(5)        # width=1.0, 结果=5.0
area(5, 3)     # 结果=15.0

# 可变参数
sum_all(1, 2, 3, 4, 5)  # 结果=15

# 关键字参数
info(name="张三", age=25)
# name: 张三
# age: 25
```

## 返回值

```python
# 单返回值
def add(a, b): return a + b

# 多返回值（元组）
def divide(a, b):
    return a // b, a % b

q, r = divide(10, 3)  # q=3, r=1
```

<div class="mt-4 p-4 bg-indigo-500/10 rounded-lg">
🎯 函数是代码复用的基本单元，Python 函数支持灵活的参数传递方式。
</div>