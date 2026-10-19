//! tracing 日志示例（对应 Python 的 logging 模块）
//! 对应 PPT 页：3-logging.md
//! 本文件参考基础语法示例，改用不同级别 log 输出，替代 println!
//!
//! 单独运行：cargo run --bin logging_example
//! 通过环境变量调整级别：RUST_LOG=debug cargo run --bin logging_example

use tracing::{debug, error, info, trace, warn};

/// 初始化日志订阅器（对应 Python 的 logging.basicConfig）
/// EnvFilter 默认级别 info，可通过 RUST_LOG 环境变量覆盖
fn init_logging() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive(tracing::Level::INFO.into()),
        )
        .with_target(false) // 不打印模块名，输出更简洁
        .init();
}

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    init_logging();

    // 变量和数据类型
    let name: &str = "张三"; // 字符串类型
    let age: i32 = 25; // 整数类型
    let height: f64 = 1.75; // 浮点数类型
    let is_student: bool = true; // 布尔类型

    // 不同级别日志输出（对应 Python 的 logging.info 等）
    info!(姓名 = name, "记录信息");
    warn!(年龄 = age, "记录警告");
    error!(身高 = height, "记录错误");
    // tracing 有 5 个级别：trace < debug < info < warn < error
    // 下面两条因为默认级别是 INFO，低于 INFO 不会输出
    debug!(是否学生 = is_student, "调试信息（默认不输出）");
    trace!("追踪信息（默认不输出）");

    println!();
    println!("提示：RUST_LOG=debug cargo run --bin logging_example 可看到 debug 日志");
}

#[allow(dead_code)]
fn main() {
    run();
}
