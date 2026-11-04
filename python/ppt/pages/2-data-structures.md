---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# 数据结构：列表与字典

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
日常写代码，<b>list（列表）</b>和 <b>dict（字典）</b>能覆盖 80% 的场景；先掌握这两个。
</div>

## list 列表：有顺序的一排盒子

```python
numbers = [1, 2, 3, 4, 5]

numbers.append(6)      # 末尾添加
len(numbers)           # 长度

numbers[0]             # 第一个
numbers[-1]            # 最后一个
numbers[1:3]           # 切片：取下标 1、2 → [2, 3]
```

## tuple 元组：创建后不能改

```python
point = (10.5, 20.3)
x, y = point           # 解包
```

::right::

## dict 字典：按“名字”查数据

```python
student = {
    "姓名": "李四",
    "年龄": 20,
    "成绩": {"数学": 90, "英语": 85}
}

student["班级"] = "一班"     # 添加 / 修改
student["年龄"]              # 访问 → 20
student.get("性别", "未知")  # 不存在时返回默认值
```

## set 集合：自动去重

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

a | b   # 并集
a & b   # 交集 {4, 5}
```

<div class="mt-3 p-3 bg-orange-500/10 border-l-4 border-orange-500 rounded text-sm">
选型：有顺序用 <b>list</b>，按名字查用 <b>dict</b>，去重用 <b>set</b>，不想被改就用 <b>tuple</b>。<br/>
字典用 <code>[]</code> 取不存在的键会报 <code>KeyError</code>，不确定时用 <code>.get()</code>。
</div>
