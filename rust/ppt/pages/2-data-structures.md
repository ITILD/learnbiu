---
layout: two-cols
layoutClass: gap-8
---

# 数据结构：数组与 Vec

## 数组 — 固定长度 `[T; N]`

```rust
let fib: [i32; 5] = [1, 1, 2, 3, 5];
fib[0]              // 1
fib.get(10)         // None（安全访问）
```

## Vec — 可变增长（对应 list）

```rust
let mut nums = vec![1, 2, 3, 4, 5];

nums.push(6);        // 末尾添加
nums.insert(0, 0);   // 指定位置插入
nums.remove(3);      // 删除并返回
nums.pop();          // 弹出末尾 Option
nums.len();          // 长度
nums.contains(&4);   // 是否包含
&nums[1..3]          // 切片 [2, 3]
```

## 元组 — 可混装类型

```rust
let point = (10.5, 20.3);
let (x, y) = point;  // 解构
point.0              // 索引访问
```

::right::

## HashMap — 键值对（对应 dict）

```rust
use std::collections::HashMap;

let mut scores = HashMap::new();
scores.insert("数学", 90);
scores.insert("英语", 85);

scores["数学"]                // 90（键缺失会 panic）
scores.get("语文")            // None（安全访问）
scores.entry("体育").or_insert(60);  // setdefault
```

## HashSet — 无序不重复（对应 set）

```rust
use std::collections::HashSet;

let a: HashSet<i32> = [1,2,3,4,5].into();
let b: HashSet<i32> = [4,5,6,7,8].into();

a.union(&b)         // 并集
a.intersection(&b)  // 交集 {4, 5}
a.difference(&b)    // 差集 {1, 2, 3}
```

<div class="mt-2 p-3 bg-orange-500/10 border-l-4 border-orange-500 rounded text-sm">
HashMap/HashSet 位于标准库，使用前需 use 导入。
</div>
