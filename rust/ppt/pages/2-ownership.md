---
layout: two-cols
layoutClass: gap-8
---

# 所有权：Rust 的灵魂

## 三大规则

1. 每个值都有一个**所有者**
2. 同一时刻只能有**一个**所有者
3. 所有者离开作用域，值被**自动释放**（无需 GC）

## 移动 Move 语义

```rust
let s1 = String::from("hello");
let s2 = s1;      // 所有权移动到 s2
// println!("{s1}");  // 编译错误！s1 已失效

// 需要两份 → 显式 clone
let s3 = String::from("hello");
let s4 = s3.clone();   // 深拷贝，两者都可用

// 栈上简单类型是 Copy（赋值后原值可用）
let x = 42;
let y = x;  // 复制，x 仍可用
```

::right::

## 引用与借用

```rust
fn len(s: &String) -> usize { s.len() }  // 只读借用

let s = String::from("hi");
println!("{}", len(&s));  // s 仍然可用

let mut t = String::from("hello");
push_world(&mut t);       // 可变借用
fn push_world(s: &mut String) {
    s.push_str(", world");
}
```

## 借用规则

- 多个 `&T`（只读）可同时存在
- `&mut T`（可写）必须**独占**
- 编译期检查，杜绝数据竞争

```rust
let r1 = &v; let r2 = &v; // OK
// let r3 = &mut v;       // 编译错误
```

<div class="mt-2 p-3 bg-red-500/10 border-l-4 border-red-500 rounded text-sm">
所有权让 Rust 无需 GC 也能保证内存安全 —— 这是它与 Python 最大的差异。
</div>
