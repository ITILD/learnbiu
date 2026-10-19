---
layout: two-cols
layoutClass: gap-8
---

# 函数与闭包

## 基本定义（类型必标）

```rust
fn greet(name: &str) -> String {
    // 最后一行表达式即返回值
    format!("你好, {name}!")
}

// 多返回值用元组
fn divide(a: i32, b: i32) -> (i32, i32) {
    (a / b, a % b)
}

let (q, r) = divide(10, 3);  // q=3, r=1
```

## 参数差异：没有默认参数 / *args

```rust
// Python: def area(l, w=1.0)
// Rust 惯用法：包装函数或结构体参数
fn area(l: f64, w: f64) -> f64 { l * w }
fn area_default(l: f64) -> f64 { area(l, 1.0) }

// Python: *args → Rust 用切片
fn sum_all(nums: &[i32]) -> i32 {
    nums.iter().sum()
}
```

::right::

## 闭包（对应 lambda）

```rust
let add_one = |x: i32| x + 1;
let square = |x| x * x;

// 可捕获环境变量
let factor = 10;
let mul = |x: i32| x * factor;
```

## 配合迭代器（函数式风格）

```rust
let nums = [1, 2, 3, 4, 5];

let doubled: Vec<_> =
    nums.iter().map(|x| x * 2).collect();
// [2, 4, 6, 8, 10]

let evens: Vec<_> =
    nums.iter().copied()
        .filter(|x| x % 2 == 0)
        .collect();
// [2, 4]
```

<div class="mt-4 p-4 bg-indigo-500/10 border-l-4 border-indigo-500 rounded text-sm">
map / filter / collect 组合是 Rust 日常代码的核心写法。
</div>
