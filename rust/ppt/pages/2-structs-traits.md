---
layout: two-cols
layoutClass: gap-8
---

# 结构体与 Trait（对应类）

## 定义结构体与方法

```rust
struct Person {
    name: String,
    age: u32,
}

impl Person {
    fn new(name: &str, age: u32) -> Self {
        Self { name: name.to_string(), age }
    }
    fn introduce(&self) -> String {
        format!("我叫{}，{}岁", self.name, self.age)
    }
    fn have_birthday(&mut self) {
        self.age += 1;
    }
}
```

::right::

## 继承 → 组合 + Trait

```rust
struct Student {
    person: Person,          // 组合
    student_id: String,
    courses: Vec<String>,
}

// trait 定义共享行为（类似接口）
trait Greet {
    fn describe(&self) -> String;
    fn greet(&self) -> String {  // 默认实现
        "大家好！".to_string()
    }
}

impl Greet for Person { /* ... */ }

// 泛型：编译期多态，零开销
fn welcome(g: &impl Greet) { /* ... */ }

// trait 对象：运行时多态
let list: Vec<Box<dyn Greet>> = vec![/* ... */];
```

## 关键概念

| 概念 | 说明 |
|------|------|
| `struct` | 数据定义 |
| `impl` | 方法定义 |
| `trait` | 接口抽象 |
| `&self` | 实例自身引用 |
| 组合 | 替代继承复用代码 |

<div class="mt-2 p-3 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
Rust 没有类继承：<b>组合 + trait + 泛型</b> 是惯用替代。
</div>
