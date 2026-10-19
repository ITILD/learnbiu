//! 运算符示例
//! 对应 PPT 页：2-basic-operators.md
//! 本文件展示 Rust 的算术、比较、逻辑、位运算与复合赋值运算符
//!
//! 单独运行：cargo run --bin basic_operators

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    // 算术运算
    let a: i32 = 10;
    let b: i32 = 3;

    println!("=== 算术运算 ===");
    println!("{a} + {b} = {}", a + b); // 加法
    println!("{a} - {b} = {}", a - b); // 减法
    println!("{a} * {b} = {}", a * b); // 乘法
    println!("{a} / {b} = {}", a / b); // 整数除法（直接截断，不是浮点除！）
    println!("{a}.0 / {b}.0 = {:.2}", 10.0 / 3.0); // 浮点除法
    println!("{a} % {b} = {}", a % b); // 取余
    println!("{a}.pow({b}) = {}", a.pow(b as u32)); // 幂运算用方法，Rust 没有 ** 运算符

    // 比较运算
    println!("\n=== 比较运算 ===");
    println!("{a} > {b}: {}", a > b);
    println!("{a} < {b}: {}", a < b);
    println!("{a} == {b}: {}", a == b);
    println!("{a} != {b}: {}", a != b);

    // 逻辑运算（短路求值）
    let x: bool = true;
    let y: bool = false;

    println!("\n=== 逻辑运算 ===");
    println!("x && y: {}", x && y); // 与：全真才真
    println!("x || y: {}", x || y); // 或：有真即真
    println!("!x: {}", !x); // 非：取反

    // 位运算（Rust 特色，Python 中较少直接使用）
    println!("\n=== 位运算 ===");
    let m: u8 = 0b1100; // 12
    let n: u8 = 0b1010; // 10
    println!("{m:04b} & {n:04b} = {:04b}（按位与）", m & n);
    println!("{m:04b} | {n:04b} = {:04b}（按位或）", m | n);
    println!("{m:04b} ^ {n:04b} = {:04b}（异或）", m ^ n);
    println!("{m:04b} << 1 = {:04b}（左移）", m << 1);
    println!("{m:04b} >> 1 = {:04b}（右移）", m >> 1);

    // 复合赋值运算
    println!("\n=== 复合赋值运算 ===");
    let mut val: i32 = 10;
    println!("初始值: {val}");
    val += 5;
    println!("val += 5 → {val}");
    val -= 3;
    println!("val -= 3 → {val}");
    val *= 2;
    println!("val *= 2 → {val}");
    val /= 4;
    println!("val /= 4 → {val}");

    // 溢出保护：debug 模式下溢出会 panic，release 模式下回绕
    // 需要显式行为时使用 checked_* / wrapping_* / saturating_* 系列方法
    println!("\n=== 溢出保护 ===");
    let max = u8::MAX; // 255
    println!("u8::MAX = {max}");
    println!("checked_add(1) = {:?}", max.checked_add(1)); // None（不会崩溃）
    println!("saturating_add(1) = {}", max.saturating_add(1)); // 饱和在 255
    println!("wrapping_add(1) = {}", max.wrapping_add(1)); // 回绕到 0
}

#[allow(dead_code)]
fn main() {
    run();
}
