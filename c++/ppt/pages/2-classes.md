---
layout: two-cols
---

# 类与对象：面向对象编程

## 定义类

```cpp
class Person {
private:
    std::string name;
    int age;

public:
    Person(std::string n, int a)
        : name{n}, age{a} {}   // 初始化列表

    void introduce() const {
        std::cout << "我叫" << name
                  << "，" << age << "岁\n";
    }

    void have_birthday() {
        age++;
    }
};
```

::right::

## 继承

```cpp
class Student : public Person {
    std::string student_id;
    std::vector<std::string> courses;

public:
    Student(std::string name, int age, std::string sid)
        : Person{name, age}
        , student_id{sid} {}

    void enroll(const std::string& course) {
        courses.push_back(course);
    }
};
```

## 多态（虚函数）

```cpp
class Animal {
public:
    virtual void speak() const {
        std::cout << "...\n";
    }
    virtual ~Animal() = default;
};

class Dog : public Animal {
public:
    void speak() const override {
        std::cout << "汪汪！\n";
    }
};

// 基类指针调用派生类方法
std::unique_ptr<Animal> pet = std::make_unique<Dog>();
pet->speak();  // 汪汪！
```

## 访问控制

| 关键字 | 类内 | 子类 | 外部 |
|--------|------|------|------|
| `public` | ✅ | ✅ | ✅ |
| `protected` | ✅ | ✅ | ❌ |
| `private` | ✅ | ❌ | ❌ |

<div class="mt-2 p-3 bg-pink-500/10 rounded-lg text-sm">
🏗️ 构造函数使用<b>初始化列表</b>更高效。析构函数加 <code>virtual</code> 防止资源泄漏。
</div>