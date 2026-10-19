//! 异步编程示例（对应 Python 的 asyncio，基于 tokio 运行时）
//! 对应 PPT 页：2-async.md
//! 本文件展示 async/await、join! 并发、spawn 任务，通过并发提升 IO 密集型任务性能
//!
//! 单独运行：cargo run --bin async_example

use std::time::{Duration, Instant};

/// 点餐并上菜：模拟异步任务（async fn 定义异步函数，await 等待完成）
/// 对应 Python 的 async def order_and_serve + await asyncio.sleep
async fn order_and_serve(dish_name: &str, prepare_time_secs: u64) {
    // tokio 的 sleep 是异步的：等待时不阻塞线程（对应 asyncio.sleep）
    tokio::time::sleep(Duration::from_secs(prepare_time_secs)).await;
    println!("{dish_name} 已准备完成！");
    println!("{dish_name} 已服务完成！");
}

/// 串行执行：一道菜做完再做下一道（作为对比）
async fn sync_example() {
    println!("--- 串行执行（一道一道做）---");
    let start = Instant::now();
    order_and_serve("鱼香肉丝", 1).await;
    order_and_serve("红烧肉", 1).await;
    order_and_serve("青椒肉丝", 1).await;
    println!("串行总耗时: {:.2}秒", start.elapsed().as_secs_f64());
}

/// 并发执行：三道菜同时开始做
async fn concurrent_example() {
    println!("\n--- 并发执行（三道菜同时做）---");
    let start = Instant::now();
    // tokio::join! 等待所有 future 完成（对应 asyncio.gather）
    tokio::join!(
        order_and_serve("鱼香肉丝", 1),
        order_and_serve("红烧肉", 1),
        order_and_serve("青椒肉丝", 1),
    );
    println!("并发总耗时: {:.2}秒", start.elapsed().as_secs_f64());
}

/// spawn：把任务交给运行时调度，返回 JoinHandle（类似 asyncio.create_task）
async fn spawn_example() {
    println!("\n--- spawn 任务（后台执行）---");
    let handle = tokio::spawn(async {
        tokio::time::sleep(Duration::from_millis(100)).await;
        "后台任务的结果"
    });
    println!("spawn 后立即继续执行主逻辑...");
    let result = handle.await.expect("任务正常完成");
    println!("拿到后台结果: {result}");
}

/// 示例主体：被 main.rs 调用
/// 注意：async 函数需要运行时驱动，main.rs 中统一用 #[tokio::main] 入口
pub async fn async_example() {
    println!("=== 异步编程（tokio） ===");
    sync_example().await;
    concurrent_example().await;
    spawn_example().await;
}

/// 本 bin 的入口：独立运行时需要自己的运行时
#[allow(dead_code)]
#[tokio::main]
async fn main() {
    async_example().await;
}
