---
layout: two-cols
layoutClass: gap-8
---

# 控制流：条件与循环

## if / else if / else

```rust
let score = 85;

if score >= 90 {
    println!("优秀！");
} else if score >= 80 {
    println!("良好！");
} else if score >= 60 {
    println!("及格！");
} else {
    println!("不及格！");
}

// if 是表达式（类似三元运算符）
let level = if score >= 60 { "及格" } else { "不及格" };
```

## for 循环

```rust
// 遍历范围（左闭右开）
for i in 1..=5 { print!("{i} "); }  // 1 2 3 4 5

// 遍历集合（& 借用，不拿所有权）
let fruits = vec!["苹果", "香蕉", "橙子"];
for fruit in &fruits { println!("{fruit}"); }
```

::right::

## while 与 loop

```rust
let mut count = 3;
while count > 0 {
    println!("倒计时: {count}");
    count -= 1;
}

// loop 无限循环，break 可带返回值
let n = loop {
    count += 1;
    if count == 10 { break count * 2; }
};
```

## 循环控制

```rust
// break / continue 与其他语言一致

// 标签：跳出嵌套外层循环
'outer: for i in 1..3 {
    for j in 1..3 {
        if i * j > 2 { break 'outer; }
    }
}
```

<div class="mt-4 p-4 bg-teal-500/10 border-l-4 border-teal-500 rounded text-sm">
条件必须是 <b>bool</b> 类型，Rust 不会把数字隐式当布尔值（区别于 Python/C）。
</div>
