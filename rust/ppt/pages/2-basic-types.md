---
layout: two-cols
layoutClass: gap-8
---

# 变量与数据类型

## let 与可变性

```rust
let name: &str = "张三";   // 字符串（默认不可变！）
let mut age: i32 = 25;    // mut 才能修改
let height: f64 = 1.75;   // 浮点数
let ok: bool = true;      // 布尔值

age += 1;  // OK
// name = "李四";  // 编译错误！
```

## 类型推断与标注

```rust
let x = 30;            // 推断为 i32（默认整数）
let y: u8 = 255;       // 显式标注（0~255）
let list: Vec<String> = vec![];
```

::right::

## 类型转换

```rust
// 字符串 → 数字（parse 返回 Result）
let n: i32 = "42".parse().unwrap();
let pi: f64 = "3.14".parse().unwrap();

// 数字 → 字符串
let s: String = 100.to_string();

// 数字之间用 as（注意截断）
let big = 100_000i64 as i16; // 溢出!
```

## 格式化输出

```rust
println!("我叫{name}，今年{age}岁");
println!("{:.2}", 3.14159);   // 3.14
println!("{:?}", (1, 2, 3));  // 调试格式
```

<div class="mt-4 p-4 bg-yellow-500/10 border-l-4 border-yellow-500 rounded text-sm">
Rust 是<b>静态强类型</b>语言：类型在编译期确定，且不会隐式转换。
</div>
