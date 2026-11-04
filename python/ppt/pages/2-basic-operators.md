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
10 + 3    # 13
10 / 3    # 3.333...  除法（结果一定是小数）
10 // 3   # 3         整除（向下取整）
10 % 3    # 1         取余
10 ** 3   # 1000      幂
```

## 比较运算

```python
10 > 3     # True
10 <= 3    # False
10 == 10   # True  ← 判断相等
10 != 3    # True
```

::right::

## 逻辑运算

```python
x, y = True, False

x and y   # False：全真才真
x or y    # True：有真即真
not x     # False：取反
```

## 赋值简写

```python
x = 10
x += 5    # 等价于 x = x + 5
x -= 3    # 等价于 x = x - 3
x *= 2    # 等价于 x = x * 2
```

<div class="mt-3 p-3 bg-purple-500/10 border-l-4 border-purple-500 rounded text-sm">
优先级：括号 → 幂 → 乘除 → 加减。不确定就加括号，可读性比“炫技”重要。
</div>
