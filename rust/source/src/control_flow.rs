//! 控制流示例
//! 对应 PPT 页：2-control-flow.md
//! 本文件展示 Rust 的条件判断、三种循环（loop/while/for）与循环控制
//!
//! 单独运行：cargo run --bin control_flow

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    println!("=== if / else if / else 条件判断 ===");

    let score: i32 = 85;

    // 条件不需要括号，必须是 bool 类型（Rust 不会把数字隐式转成 bool）
    if score >= 90 {
        println!("成绩优秀！");
    } else if score >= 80 {
        println!("成绩良好！");
    } else if score >= 60 {
        println!("成绩及格！");
    } else {
        println!("成绩不及格！");
    }

    // if 是表达式，可以直接产生值（Python 的三元表达式 a if c else b 对应这里）
    let level = if score >= 60 { "及格" } else { "不及格" };
    println!("结果判定: {level}");

    println!("\n=== for 循环 ===");

    // 遍历数字范围（range 是左闭右开 [1, 6)）
    println!("数字 1-5:");
    for i in 1..=5 {
        println!("  {i}");
    }

    // 遍历集合（对 Vec 的引用遍历，不获取所有权）
    let fruits = vec!["苹果", "香蕉", "橙子"];
    println!("水果列表:");
    for fruit in &fruits {
        println!("  {fruit}");
    }

    // 同时获得索引和值（类似 Python 的 enumerate）
    for (i, fruit) in fruits.iter().enumerate() {
        println!("  [{i}] {fruit}");
    }

    println!("\n=== while 循环 ===");

    let mut count: i32 = 3;
    while count > 0 {
        println!("倒计时: {count}");
        count -= 1;
    }
    println!("开始！");

    println!("\n=== loop 无限循环 ===");

    // loop 循环可以通过 break 返回值（其他语言少见的能力）
    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 3 {
            break counter * 10; // break 带值 → loop 表达式的值
        }
    };
    println!("loop 循环返回值: {result}");

    println!("\n=== 循环控制 ===");

    // break - 跳出整个循环
    print!("break 示例: ");
    for i in 0..10 {
        if i == 5 {
            break;
        }
        print!("{i} ");
    }
    println!();

    // continue - 跳过本次迭代
    print!("continue 示例（只打印奇数）: ");
    for i in 0..10 {
        if i % 2 == 0 {
            continue;
        }
        print!("{i} ");
    }
    println!();

    // 循环标签 - 从嵌套循环中直接跳出外层
    'outer: for i in 1..=3 {
        for j in 1..=3 {
            if i * j > 4 {
                break 'outer; // 直接结束外层循环
            }
            print!("i={i},j={j} ");
        }
    }
    println!("（使用标签跳出嵌套循环）");
}

#[allow(dead_code)]
fn main() {
    run();
}
