---
layout: two-cols
---

# 类与对象：面向对象编程

## 定义类

```python
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def introduce(self) -> str:
        return f"我叫{self.name}，{self.age}岁"

    def have_birthday(self):
        self.age += 1
```

## 创建和使用对象

```python
p = Person("张三", 25)
print(p.introduce())
# 我叫张三，今年25岁

p.have_birthday()
# 张三过生日啦！现在26岁
```

::right::

## 继承

```python
class Student(Person):
    def __init__(self, name, age, sid: str):
        super().__init__(name, age)
        self.student_id = sid
        self.courses: list[str] = []

    def enroll(self, course: str):
        self.courses.append(course)

# 使用
s = Student("李四", 20, "S001")
s.enroll("Python编程")
s.introduce()  # 继承自 Person
```

## 关键概念

| 概念 | 说明 |
|------|------|
| `__init__` | 构造函数 |
| `self` | 实例自身引用 |
| `super()` | 调用父类方法 |
| 继承 | 子类复用父类代码 |