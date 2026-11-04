---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# 类与对象：模具与实例

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
<b>类</b>是模具，<b>对象</b>是用模具造出来的实例。比如 <code>Person</code> 是模具，张三、李四是一个个对象。
</div>

## 定义类

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"我叫{self.name}，{self.age}岁"
```

## 创建和使用对象

```python
p = Person("张三", 25)   # 自动调用 __init__
print(p.introduce())     # 我叫张三，25岁
```

::right::

## 继承：子类复用父类

```python
class Student(Person):
    def __init__(self, name, age, sid):
        super().__init__(name, age)   # 先按父类初始化
        self.sid = sid

s = Student("李四", 20, "S001")
print(s.introduce())  # 继承自 Person → 我叫李四，20岁
```

## 三个关键词

| 关键词 | 作用 |
|--------|------|
| `class` | 定义一个类（模具） |
| `__init__` | 创建对象时自动执行的构造函数 |
| `self` | 指“当前这个对象” |

<div class="mt-3 p-2 bg-cyan-500/10 border-l-4 border-cyan-500 rounded text-xs">
方法里的第一个参数必须写 <code>self</code>，但调用时不用传，Python 会自动把对象传进去。继承用 <code>super()</code> 调父类。
</div>
