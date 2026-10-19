//! 变量与数据类型示例
//! 对应 PPT 页：2-basic-types.md
//! 本文件展示 Rust 的变量与可变性、基本数据类型、类型转换与格式化输出
//!
//! 单独运行：cargo run --bin basic_types

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    // 变量和数据类型（let 默认不可变，这是 Rust 与 Python 最大的区别之一）
    let name: &str = "张三"; // 字符串切片（字符串字面量的类型）
    let mut age: i32 = 25; // 整数类型，mut 表示可变
    let height: f64 = 1.75; // 浮点数类型
    let is_student: bool = true; // 布尔类型

    println!("=== 基础数据类型 ===");
    println!("姓名: {name}");
    println!("年龄: {age}");
    println!("身高: {height}米 是否学生: {is_student}");

    age += 1; // 只有 mut 变量才能修改
    println!("明年年龄: {age}");

    // 类型标注与类型推断
    println!("\n=== 类型推断与标注 ===");
    let inferred = 30; // 编译器自动推断为 i32（默认整数类型）
    let explicit: u8 = 255; // 显式标注为无符号 8 位整数（0~255）
    let list: Vec<String> = vec!["a".to_string(), "b".to_string()]; // 泛型集合标注
    let scores: Vec<(String, i32)> = vec![("math".to_string(), 90)];
    println!("推断类型: {inferred}（i32）");
    println!("标注类型: {explicit}（u8）");
    println!("字符串列表: {list:?}");
    println!("成绩元组: {scores:?}");

    // 类型转换
    println!("\n=== 类型转换 ===");
    // 字符串 → 数字：parse 返回 Result（解析可能失败，必须处理）
    let n: i32 = "42".parse().expect("合法数字");
    let pi: f64 = "3.14".parse().expect("合法浮点数");
    // 数字 → 字符串
    let s: String = 100.to_string();
    // 数字之间的转换：as 关键字（可能截断/溢出，需谨慎）
    let big: i64 = 100_000;
    let small = big as i16;
    println!(r#""42".parse::<i32>() = {n}"#);
    println!(r#""3.14".parse::<f64>() = {pi}"#);
    println!("100.to_string() = {s:?}");
    println!("100_000 as i16 = {small}（发生溢出截断！）");

    // 格式化输出（println! 宏）
    println!("\n=== 格式化输出 ===");
    let name = "张三";
    let age = 25;
    println!("我叫{name}，今年{age}岁"); // 直接内插（Rust 1.58+）
    println!("我叫{}，今年{}岁", name, age); // 位置参数写法
    println!("保留两位小数: {:.2}", 3.14159); // 3.14
    println!("右对齐宽度8: |{:^8}|", "居中"); //    居中
    println!("调试格式: {:?}", (1, 2, 3)); // 元组需要 {:?}
}

// 本文件的独立运行入口（cargo run --bin basic_types）
// 作为模块被 main.rs 引用时编译器视为未使用，故显式允许
#[allow(dead_code)]
fn main() {
    run();
}
