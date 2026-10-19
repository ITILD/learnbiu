---
layout: two-cols
layoutClass: gap-8
---

# 运算符

## 算术运算符

| 运算符 | 含义 | 示例 `a=10, b=3` |
|--------|------|-------------------|
| `+` | 加 | `10 + 3 = 13` |
| `-` | 减 | `10 - 3 = 7` |
| `*` | 乘 | `10 * 3 = 30` |
| `/` | 整除 | `10 / 3 = 3`（整数直接截断！） |
| `%` | 取余 | `10 % 3 = 1` |
| `a.pow(n)` | 幂 | `10.pow(3) = 1000` |

## 比较运算符

| 运算符 | 含义 |
|--------|------|
| `>` `<` | 大于 / 小于 |
| `>=` `<=` | 大于等于 / 小于等于 |
| `==` `!=` | 等于 / 不等于 |

::right::

## 逻辑运算符

```rust
let (x, y) = (true, false);

x && y   // false  与：全真才真
x || y   // true   或：有真即真
!x       // false  非：取反
```

## 位运算符

```rust
let (m, n) = (0b1100, 0b1010);

m & n   // 按位与
m | n   // 按位或
m ^ n   // 异或
m << 1  // 左移
m >> 1  // 右移
```

## 溢出保护

```rust
u8::MAX.checked_add(1)     // None
u8::MAX.saturating_add(1)  // 255
```

<div class="mt-2 p-3 bg-purple-500/10 border-l-4 border-purple-500 rounded text-sm">
debug 模式下溢出直接 panic，帮你提前抓住 bug。
</div>
