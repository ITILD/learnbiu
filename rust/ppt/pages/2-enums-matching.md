---
layout: two-cols
layoutClass: gap-8
---

# 枚举与模式匹配

## 枚举可携带数据

```rust
enum Shape {
    Circle(f64),
    Rectangle { w: f64, h: f64 },
    Triangle(f64, f64, f64),
}

// match 解构每种情况
fn area(s: &Shape) -> f64 {
    match s {
        Shape::Circle(r) => 3.14159 * r * r,
        Shape::Rectangle { w, h } => w * h,
        Shape::Triangle(a, b, c) => { /* 海伦公式 */ }
    }
}
```

## match 穷举检查

```rust
match light {
    Light::Red => "停",
    Light::Yellow => "注意",
    Light::Green => "行",
    // 少一种情况 → 编译不通过！
}

// 支持范围与守卫
match score {
    90..=100 => "优秀",
    80..=89 if score >= 85 => "良好+",
    _ => "其他",
}
```

::right::

## Option\<T\>：替代 null

```rust
// Rust 没有 null！
enum Option<T> {
    Some(T),
    None,
}

fn find_user(id: u32) -> Option<String> {
    match id {
        1 => Some("张三".to_string()),
        _ => None,
    }
}

match find_user(3) {
    Some(name) => println!("找到: {name}"),
    None => println!("用户不存在"),
}

// 方法链处理
find_user(1).map(|n| n.len()).unwrap_or(0);
```

## if let / let else

```rust
// 只关心一种情况时更简洁
if let Some(name) = find_user(2) {
    println!("{name}");
}

// let else：提前返回风格
let Some(name) = find_user(1) else {
    return;
};
```

<div class="mt-2 p-3 bg-fuchsia-500/10 border-l-4 border-fuchsia-500 rounded text-sm">
模式匹配 + 枚举 = Rust 表达力核心，编译器保证不漏分支。
</div>
