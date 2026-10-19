//! 所有权示例（Rust 核心概念，Python 中没有对应机制）
//! 对应 PPT 页：2-ownership.md
//! 本文件展示所有权、移动语义、克隆、借用与引用
//!
//! 单独运行：cargo run --bin ownership

/// 接收 String 所有权：函数结束后 s 被释放
fn takes_ownership(s: String) {
    println!("takes_ownership 拿到了: {s}");
} // s 离开作用域，内存在这里自动释放（无需 GC）

/// 接收 i32：Copy 类型按值复制，调用方仍可使用
fn makes_copy(n: i32) {
    println!("makes_copy 拿到了: {n}");
}

/// 借用：&String 只读借用，不获取所有权
fn calculate_length(s: &String) -> usize {
    s.len()
}

/// 可变借用：&mut String 可以修改原数据
fn push_world(s: &mut String) {
    s.push_str(", world");
}

/// 返回字符串切片：不移动所有权，只借用其中一段
fn first_word(s: &str) -> &str {
    // 按空格切分，返回第一个单词
    match s.split_once(' ') {
        Some((word, _)) => word,
        None => s,
    }
}

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    println!("=== 所有权三大规则 ===");
    println!("1. 每个值都有一个所有者");
    println!("2. 同一时刻只能有一个所有者");
    println!("3. 所有者离开作用域，值被自动释放");
    println!();

    println!("=== 移动 (Move) 语义 ===");

    let s1 = String::from("hello");
    let s2 = s1; // 所有权从 s1 移动到 s2（堆数据不复制，只转移指针）
    // println!("{s1}"); // 取消注释会编译错误：s1 的值已被移动
    println!("s2 = {s2}（s1 已失效，编译器阻止再次使用）");

    println!("\n=== 克隆 (Clone) ===");

    let s3 = String::from("hello");
    let s4 = s3.clone(); // 深拷贝堆数据，两个变量各自有效
    println!("s3 = {s3}, s4 = {s4}（clone 后两者都可用）");

    println!("\n=== Copy 类型 ===");

    // 栈上的简单类型（整数、浮点、bool、char）赋值时自动复制
    let x = 42;
    let y = x; // 复制，不是移动
    println!("x = {x}, y = {y}（Copy 类型赋值后原值仍可用）");

    println!("\n=== 所有权与函数 ===");

    let s = String::from("被带走的数据");
    takes_ownership(s);
    // println!("{s}"); // 编译错误：所有权已被移入函数

    let num = 5;
    makes_copy(num);
    println!("调用后 num 依然可用: {num}");

    println!("\n=== 引用与借用 ===");

    let s = String::from("借用我");
    let len = calculate_length(&s); // & 创建借用，不转移所有权
    println!("字符串 '{s}' 的长度是 {len}（s 仍然可用）");

    let mut s = String::from("hello");
    push_world(&mut s); // &mut 可变借用
    println!("可变借用修改后: {s}");

    // 借用规则：同一时刻要么多个不可变借用，要么一个可变借用
    let mut v = vec![1, 2, 3];
    let r1 = &v;
    let r2 = &v; // OK：多个不可变借用共存
    println!("不可变借用: {r1:?} {r2:?}");
    // let r3 = &mut v; // 编译错误：存在不可变借用时不能可变借用
    println!("（多个只读借用 OK，与可变借用互斥）");
    let r3 = &mut v; // 前面的借用已经用完（NLL 规则），这里可以
    r3.push(4);
    println!("可变借用修改后: {v:?}");

    println!("\n=== 切片 (Slice) ===");

    let s = String::from("hello world");
    let hello = first_word(&s); // 借用其中一段，零拷贝
    let world = &s[6..]; // 索引切片
    println!("first_word: {hello}");
    println!("s[6..]: {world}");
}

#[allow(dead_code)]
fn main() {
    run();
}
