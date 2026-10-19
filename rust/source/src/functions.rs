//! 函数示例
//! 对应 PPT 页：2-functions.md
//! 本文件展示 Rust 的函数定义、参数与返回值、闭包，以及与 Python 参数机制的差异
//!
//! 单独运行：cargo run --bin functions

/// 基本函数：参数和返回值都必须显式标注类型
fn greet(name: &str) -> String {
    // 向某人问好；最后一行表达式就是返回值（无需 return，分号可省略）
    format!("你好, {name}!")
}

/// 带默认行为的函数：Rust 没有默认参数，惯用方法是提供多个函数或包装函数
fn calculate_area(length: f64, width: f64) -> f64 {
    // 计算矩形面积
    length * width
}

/// 宽度默认为 1.0 的包装函数（模拟 Python 的默认参数）
fn calculate_area_default(length: f64) -> f64 {
    calculate_area(length, 1.0)
}

/// 可变数量参数：Rust 用切片 &[i32] 对应 Python 的 *args
fn sum_numbers(numbers: &[i32]) -> i32 {
    // 计算任意数量数字的和
    numbers.iter().sum()
}

/// 多返回值：Rust 用元组对应 Python 的多返回值
fn divide(a: i32, b: i32) -> (i32, i32) {
    // 返回商和余数
    (a / b, a % b)
}

/// 提前返回用 return（例如参数校验）
fn check_positive(n: i32) -> bool {
    if n <= 0 {
        return false; // 提前返回
    }
    n > 0
}

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    println!("=== 函数定义和调用 ===");

    println!("{}", greet("王五"));
    println!("矩形面积(长5宽3): {}", calculate_area(5.0, 3.0));
    println!("矩形面积(长5默认宽): {}", calculate_area_default(5.0));

    println!("\n=== 切片参数（对应 Python 的 *args） ===");
    let nums = [1, 2, 3, 4, 5];
    println!("数字和: {}", sum_numbers(&nums));

    println!("\n=== 返回值 ===");
    println!("单返回值: 3 + 4 = {}", 3 + 4);

    let (q, r) = divide(10, 3);
    println!("多返回值 divide(10, 3) → 商={q}, 余={r}");

    println!("提前返回: check_positive(-5) = {}", check_positive(-5));

    println!("\n=== 闭包（对应 Python 的 lambda） ===");

    // 闭包语法：|参数| 表达式，类型通常可推断
    let add_one = |x: i32| x + 1;
    let square = |x| x * x;
    println!("add_one(5) = {}", add_one(5));
    println!("square(4) = {}", square(4));

    // 闭包可以捕获环境中的变量（lambda 也能，但 Rust 会检查所有权）
    let factor = 10;
    let multiply = |x: i32| x * factor;
    println!("multiply(5) = {}（捕获了 factor={factor}）", multiply(5));

    // 作为参数传给迭代器方法（函数式编程的日常）
    let doubled: Vec<i32> = nums.iter().map(|x| x * 2).collect();
    let evens: Vec<i32> = nums.iter().copied().filter(|x| x % 2 == 0).collect();
    println!("map 翻倍: {doubled:?}");
    println!("filter 偶数: {evens:?}");
}

#[allow(dead_code)]
fn main() {
    run();
}
