//! 错误处理示例（对应 Python 的异常处理，但机制完全不同）
//! 对应 PPT 页：2-error-handling.md
//! 本文件展示 panic!、Result<T, E>、? 运算符与自定义错误类型
//!
//! 单独运行：cargo run --bin error_handling

use std::fmt;

/// 自定义错误枚举：枚举每个失败原因（对应 Python 的多种 Exception 子类）
#[derive(Debug)]
enum ParseError {
    NotANumber(String), // 对应 ValueError：字符串无法解析为数字
    ZeroDivision,       // 对应 ZeroDivisionError：除以零
}

/// 实现 Display：定义错误的可读信息（对应 Python 的 str(e)）
impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::NotANumber(s) => write!(f, "无效数字: {s:?}"),
            ParseError::ZeroDivision => write!(f, "不能除以零！"),
        }
    }
}

/// 实现 Error trait：让它成为正式的错误类型，可配合 Box<dyn Error> 使用
impl std::error::Error for ParseError {}

/// 返回 Result 的函数：Ok(成功值) 或 Err(错误)
/// 对应 Python 中 raise ValueError 的场景，但错误在类型系统中可见
fn divide_100_by(input: &str) -> Result<f64, ParseError> {
    // parse 失败时用 map_err 把标准库错误转成自定义错误
    let number: f64 = input
        .parse()
        .map_err(|_| ParseError::NotANumber(input.to_string()))?;

    if number == 0.0 {
        return Err(ParseError::ZeroDivision); // 对应 raise ZeroDivisionError
    }

    Ok(100.0 / number) // 对应正常 return
}

/// ? 运算符链：错误会自动逐层向上传播（类似 Python 的异常冒泡，但显式可见）
fn calculate(input: &str) -> Result<String, ParseError> {
    let result = divide_100_by(input)?;
    Ok(format!("100 ÷ {input} = {result:.2}"))
}

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    println!("=== 两种错误处理策略 ===");
    println!("panic! → 不可恢复的 bug（数组越界等），程序直接终止");
    println!("Result → 可预期的失败（IO、解析、网络），必须显式处理");
    println!();

    println!("=== panic!（不可恢复） ===");

    let numbers = [1, 2, 3];
    // 越界访问会 panic：numbers[10];
    println!("数组 {numbers:?}");
    println!(
        "安全访问第10个元素: {:?}（get 返回 None 而不是崩溃）",
        numbers.get(10)
    );
    // 需要主动崩溃时：
    // panic!("致命错误：数据已损坏");

    println!("\n=== Result<T, E>（可恢复） ===");

    // 用 match 精确处理每种情况（对应 try/except）
    for input in ["5", "abc", "0"] {
        match divide_100_by(input) {
            Ok(result) => println!("输入 {input:?} → 成功: {result:.2}"),
            Err(e) => println!("输入 {input:?} → 出错: {e}"),
        }
    }

    println!("\n=== 快捷方法 ===");

    // unwrap：Ok 返回值，Err 直接 panic（原型开发用，生产慎用）
    let ok = divide_100_by("4").unwrap();
    println!("unwrap: {ok}");

    // expect：同 unwrap 但带自定义信息
    let ok = divide_100_by("4").expect("输入一定是合法的");
    println!("expect: {ok}");

    // unwrap_or 系列：提供默认值
    let fallback = divide_100_by("x").unwrap_or(-1.0);
    println!("unwrap_or 默认值: {fallback}");

    println!("\n=== ? 运算符（错误传播） ===");

    // ? 遇到 Err 立即 return，遇到 Ok 继续执行
    match calculate("2") {
        Ok(msg) => println!("{msg}"),
        Err(e) => println!("{e}"),
    }
    match calculate("xyz") {
        Ok(msg) => println!("{msg}"),
        Err(e) => println!("{e}（错误经 ? 运算符向上传播）"),
    }

    println!("\n=== 对比 Python try/except ===");
    println!("Python: 异常可能从任何地方抛出（EAFP 风格）");
    println!("Rust:   错误写进函数签名，忘记处理则编译不过（EAFP → 编译期保证）");
}

#[allow(dead_code)]
fn main() {
    run();
}
