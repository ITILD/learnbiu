---
layout: two-cols
layoutClass: gap-8
---

# 数据结构：列表与元组

## 列表 list — 可变序列

```python
numbers = [1, 2, 3, 4, 5]

# 常用操作
numbers.append(6)       # 末尾添加
numbers.insert(0, 0)    # 指定位置插入
numbers.remove(3)       # 删除元素
numbers.pop()           # 弹出末尾
len(numbers)            # 长度
numbers[0]              # 索引访问
numbers[-1]             # 倒数第一个
numbers[1:3]            # 切片 [2, 3]
```

## 元组 tuple — 不可变序列

```python
point = (10.5, 20.3)
x, y = point            # 解包
```

::right::

## 字典 dict — 键值对

```python
student = {
    "姓名": "李四",
    "年龄": 20,
    "专业": "计算机科学",
    "成绩": {"数学": 90, "英语": 85}
}

student["班级"] = "一班"   # 添加
student["年龄"]            # 访问
student.get("性别", "未知") # 安全访问
```

## 集合 set — 无序不重复

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

a | b   # 并集 {1,2,3,4,5,6,7,8}
a & b   # 交集 {4, 5}
a - b   # 差集 {1, 2, 3}
```

<div class="mt-2 p-3 bg-orange-500/10 border-l-4 border-orange-500 rounded text-sm">
四种核心数据结构覆盖了绝大多数使用场景。
</div>
