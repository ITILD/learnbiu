---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# 运算符：计算与比较

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
先记住：<code>=</code> 是赋值，<code>==</code> 才是“判断是否相等”。
</div>

## 算术运算

```python
a, b = 10, 3

print(a + b)    # 13    加法
print(a / b)    # 3.33  除法（结果一定是小数）
print(a // b)   # 3     整除
print(a % b)    # 1     取余
print(a ** b)   # 1000  幂运算
```

## 比较运算

```python
print(a > b)    # True
print(a == b)   # False  ← 判断相等
print(a != b)   # True
```

::right::

## 逻辑运算

```python
x, y = True, False

print(x and y)  # False：全真才真
print(x or y)   # True：有真即真
print(not x)    # False：取反
```

## 赋值简写

```python
val = 10
val += 5    # 15
val -= 3    # 12
val *= 2    # 24
val /= 4    # 6.0（除法会让它变成小数）
```

<div class="mt-3 p-3 bg-purple-500/10 border-l-4 border-purple-500 rounded text-sm">
优先级：括号 → 幂 → 乘除 → 加减。不确定就加括号，可读性比“炫技”重要。
</div>

<div class="mt-3 text-xs opacity-50">
对应示例：source/basic_operators.py · <code>uv run basic_operators.py</code>
</div>
