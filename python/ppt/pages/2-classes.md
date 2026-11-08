---
layout: two-cols
layoutClass: gap-8 medium
class: text-sm
---

# 类与对象：模具与实例

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
<b>类</b>是模具，<b>对象</b>是用模具造出来的实例。比如 <code>Person</code> 是模具，张三、李四是一个个对象。
</div>

## 定义类

```python
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def introduce(self) -> str:
        return f"我叫{self.name}，今年{self.age}岁。"

    def have_birthday(self) -> None:
        self.age += 1       # 过生日，年龄加 1
```

## 创建和使用对象

```python
person1 = Person("张三", 25)
print(person1.introduce())
# 输出：我叫张三，今年25岁。
```

::right::

## 继承：子类复用父类

```python
class Student(Person):
    def __init__(self, name: str, age: int, student_id: str):
        super().__init__(name, age)   # 调用父类构造函数
        self.student_id = student_id
        self.courses: list[str] = []

    def enroll_course(self, course_name: str):
        self.courses.append(course_name)

student1 = Student("李四", 20, "S001")
print(student1.introduce())   # 继承自 Person
```

## 三个关键词

| 关键词 | 作用 |
|--------|------|
| `class` | 定义一个类（模具） |
| `__init__` | 创建对象时自动执行的构造函数 |
| `self` | 指“当前这个对象” |

<div class="mt-2 text-xs opacity-50">
对应示例：source/classes.py · <code>uv run classes.py</code>
</div>
