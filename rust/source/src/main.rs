//! Rust 基础知识学习示例 - 主入口
//! 按 PPT 页拆分为多个独立模块，本文件按顺序组织执行所有示例。
//!
//! 各模块对应 PPT 页：
//!   - basic_types.rs      → 2-basic-types.md
//!   - basic_operators.rs  → 2-basic-operators.md
//!   - control_flow.rs     → 2-control-flow.md
//!   - data_structures.rs  → 2-data-structures.md
//!   - functions.rs        → 2-functions.md
//!   - ownership.rs        → 2-ownership.md（Rust 特有）
//!   - structs_traits.rs   → 2-structs-traits.md
//!   - enums_matching.rs   → 2-enums-matching.md（Rust 特有）
//!   - error_handling.rs   → 2-error-handling.md
//!   - async_example.rs    → 2-async.md
//!   - logging_example.rs  → 3-logging.md
//!   - serde_example.rs    → 3-serde.md
//!
//! 运行方式：
//!   - 全部示例：cargo run
//!   - 单个示例：cargo run --bin basic_types

mod async_example;
mod basic_operators;
mod basic_types;
mod control_flow;
mod data_structures;
mod enums_matching;
mod error_handling;
mod functions;
mod logging_example;
mod ownership;
mod serde_example;
mod structs_traits;

fn main() {
    println!("🎯 Rust 基础知识学习示例");
    println!("==================================================");

    // 按顺序执行各个示例
    basic_types::run();
    basic_operators::run();
    control_flow::run();
    data_structures::run();
    functions::run();

    // Rust 特色示例
    ownership::run();
    structs_traits::run();
    enums_matching::run();
    error_handling::run();

    // 进阶示例
    logging_example::run();
    serde_example::run();

    // 异步示例：需要 tokio 运行时驱动（对应 Python 的 asyncio.run）
    println!();
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .expect("构建 tokio 运行时")
        .block_on(async_example::async_example());

    println!();
    println!("==================================================");
    println!("✅ 所有示例执行完成！");
    println!("💡 建议：修改代码并运行，观察不同的输出结果");
}
