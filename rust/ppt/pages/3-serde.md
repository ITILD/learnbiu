---
layout: two-cols
layoutClass: gap-8
---

# 进阶：serde 数据模型

## HashMap vs serde

**传统 HashMap：**
```rust
let mut student: HashMap<&str, &str> =
    HashMap::new();
student.insert("姓名", "李四");
// 无类型检查，无法嵌套
// IDE 无法提示
```

**serde 模型（派生宏）：**
```rust
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct Score { math: i32, english: i32 }

#[derive(Serialize, Deserialize)]
struct Student {
    name: String,
    age: i32,
    major: String,
    #[serde(rename = "avgScore")]
    average_score: Score,
}
```

::right::

## 序列化 / 反序列化

```rust
// 结构体 → JSON（对应 model_dump_json）
let json = serde_json::to_string_pretty(&s)?;
// { "name": "李四", "age": 20, ... }

// JSON → 结构体（对应 model_validate_json）
let s: Student = serde_json::from_str(json)?;

// 数据校验：类型不对直接报错
// invalid type: string, expected i32
// missing field `avgScore`
```

## serde 优势

| 特性 | 说明 |
|------|------|
| 类型安全 | 编译期生成校验代码 |
| 零反射 | 派生宏，性能极高 |
| 格式丰富 | JSON/YAML/TOML/二进制 |
| 生态标准 | Web 框架/数据库全支持 |

<div class="mt-2 p-3 bg-emerald-500/10 border-l-4 border-emerald-500 rounded text-sm">
serde 之于 Rust，如同 pydantic 之于 Python —— 数据建模的事实标准。
</div>
