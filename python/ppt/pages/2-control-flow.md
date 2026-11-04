---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# 控制流：判断与循环

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
Python 用<b>缩进</b>（通常 4 个空格）表示代码块，行尾还必须有冒号 <code>:</code>。
</div>

## if / elif / else：做选择

```python
score = 85

if score >= 90:
    print("优秀！")
elif score >= 80:
    print("良好！")
elif score >= 60:
    print("及格！")
else:
    print("不及格！")
```

从上往下判断，命中一个就结束。`elif` 可以有多个，`else` 最多一个。

::right::

## for：按顺序重复

```python
for i in range(1, 6):
    print(i)          # 1 2 3 4 5

fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(fruit)
```

## while：条件成立就一直做

```python
count = 3
while count > 0:
    print(count)
    count -= 1        # 别忘改变条件，否则死循环
```

## break / continue

```python
for i in range(10):
    if i == 5: break       # 提前结束整个循环
    if i % 2 == 0: continue  # 跳过本次
    print(i)               # 只打印奇数
```

<div class="mt-2 p-2 bg-teal-500/10 border-l-4 border-teal-500 rounded text-xs">
缩进错了，Python 会直接报 <code>IndentationError</code>——新手最常见的报错之一。
</div>
