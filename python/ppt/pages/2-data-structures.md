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
numbers: list[int] = [1, 2, 3, 4, 5]

numbers.append(6)     # 末尾添加
numbers.insert(0, 0)  # 在指定位置插入
numbers.remove(3)     # 按值删除
# 结果：[0, 1, 2, 4, 5, 6]

len(numbers)          # 长度 6
numbers[0]            # 第一个：0
numbers[-1]           # 最后一个：6
numbers[1:3]          # 切片 → [1, 2]
```

## tuple 元组：创建后不能改

```python
coordinates: tuple[float, float] = (10.5, 20.3)
x, y = coordinates    # 解包
```

::right::

## dict 字典：按“名字”查数据

```python
student: dict = {
    "姓名": "李四",
    "年龄": 20,
    "专业": "计算机科学",
    "成绩": {"数学": 90, "英语": 85},
}

student["班级"] = "一班"     # 添加新键值对
student["年龄"]              # 访问 → 20
student.get("性别", "未知")  # 不存在时返回默认值
```

## set 集合：自动去重

```python
set1 = {1, 2, 3, 4, 5}
set2 = {4, 5, 6, 7, 8}

set1 | set2   # 并集
set1 & set2   # 交集 {4, 5}
set1 - set2   # 差集 {1, 2, 3}
```

<div class="mt-3 p-3 bg-orange-500/10 border-l-4 border-orange-500 rounded text-sm">
选型：有顺序用 <b>list</b>，按名字查用 <b>dict</b>，去重用 <b>set</b>，不想被改就用 <b>tuple</b>。
</div>

<div class="mt-3 text-xs opacity-50">
对应示例：source/data_structures.py · <code>uv run data_structures.py</code>
</div>
