//! 数据结构示例
//! 对应 PPT 页：2-data-structures.md
//! 本文件展示 Rust 的数组、Vec（动态数组）、元组、HashMap 与 HashSet
//!
//! 单独运行：cargo run --bin data_structures

use std::collections::{HashMap, HashSet};

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    println!("=== 数组 (Array) — 固定长度 ===");

    // 数组：长度固定、栈分配，类型写作 [T; N]
    let fib: [i32; 5] = [1, 1, 2, 3, 5];
    println!("数组: {fib:?}");
    println!("第一个元素: {}", fib[0]);
    println!("最后一个元素: {}", fib[fib.len() - 1]);
    // 越界访问会 panic，get 返回 Option 更安全
    println!("安全访问第10个元素: {:?}", fib.get(10));

    println!("\n=== 动态数组 (Vec) — 对应 Python 的 list ===");

    // Vec - 可增长的有序集合
    let mut numbers: Vec<i32> = vec![1, 2, 3, 4, 5];
    println!("原始列表: {numbers:?}");

    // 常用操作
    numbers.push(6); // 末尾添加
    numbers.insert(0, 0); // 指定位置插入
    numbers.remove(3); // 删除指定位置的元素（返回被删值）
    let popped = numbers.pop(); // 弹出末尾
    println!("修改后列表: {numbers:?}");
    println!("pop 弹出: {popped:?}");
    println!("列表长度: {}", numbers.len());
    println!("是否包含 4: {}", numbers.contains(&4));
    // 切片语法（对应 Python 的 numbers[1:3]）
    println!("切片 [1..3]: {:?}", &numbers[1..3]);
    println!("切片 [..2]: {:?}", &numbers[..2]);

    println!("\n=== 元组 (Tuple) ===");

    // 元组 - 可以组合不同类型，长度固定
    let coordinates: (f64, f64) = (10.5, 20.3);
    println!("坐标: {coordinates:?}");
    println!("X坐标: {}", coordinates.0);
    println!("Y坐标: {}", coordinates.1);
    // 解构（对应 Python 的 x, y = coordinates）
    let (x, y) = coordinates;
    println!("解构: x={x}, y={y}");

    println!("\n=== 哈希表 (HashMap) — 对应 Python 的 dict ===");

    // HashMap - 键值对集合
    let mut student: HashMap<&str, i32> = HashMap::new();
    student.insert("数学", 90);
    student.insert("英语", 85);
    println!("成绩: {student:?}");
    println!("数学成绩: {}", student["数学"]); // 键不存在会 panic
    println!("安全访问语文: {:?}", student.get("语文")); // 返回 None

    // entry API：不存在则插入默认值（类似 Python 的 setdefault）
    student.entry("体育").or_insert(60);
    println!("entry 插入体育后: {student:?}");

    // 嵌套结构：值可以是任何类型（如 String、Vec 等）
    let mut profile: HashMap<&str, String> = HashMap::new();
    profile.insert("姓名", "李四".to_string());
    println!("学生信息: {profile:?}");

    println!("\n=== 集合 (HashSet) — 对应 Python 的 set ===");

    // HashSet - 无序不重复元素集合
    let set1: HashSet<i32> = [1, 2, 3, 4, 5].into();
    let set2: HashSet<i32> = [4, 5, 6, 7, 8].into();

    println!("集合1: {set1:?}");
    println!("集合2: {set2:?}");
    // 并集、交集、差集（返回迭代器，collect 转为 Vec 便于打印）
    let union: Vec<_> = set1.union(&set2).collect();
    let inter: Vec<_> = set1.intersection(&set2).collect();
    let diff: Vec<_> = set1.difference(&set2).collect();
    println!("并集: {union:?}");
    println!("交集: {inter:?}");
    println!("差集: {diff:?}");
}

#[allow(dead_code)]
fn main() {
    run();
}
