---
layout: two-cols
layoutClass: gap-8
---

# 控制流：条件与循环

## if / elif / else

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

## for 循环

```python
# 遍历范围
for i in range(1, 6):
    print(i)  # 1 2 3 4 5

# 遍历列表
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(fruit)
```

::right::

## while 循环

```python
count = 3
while count > 0:
    print(f"倒计时: {count}")
    count -= 1
print("开始！")
```

## 循环控制

```python
# break - 跳出整个循环
for i in range(10):
    if i == 5:
        break

# continue - 跳过本次迭代
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 只打印奇数
```

<div class="mt-4 p-4 bg-teal-500/10 border-l-4 border-teal-500 rounded text-sm">
Python 使用<b>缩进</b>（4个空格）来定义代码块，而不是大括号。
</div>
