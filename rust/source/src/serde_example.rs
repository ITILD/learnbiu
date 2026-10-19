//! serde 数据模型示例（对应 Python 的 pydantic）
//! 对应 PPT 页：3-serde.md
//! 本文件参考数据结构示例，使用 serde 派生宏定义数据模型，替代 HashMap
//! serde 是 Rust 序列化的事实标准（如同 pydantic 之于 Python）
//!
//! 单独运行：cargo run --bin serde_example

use serde::{Deserialize, Serialize};

/// 成绩数据模型
/// derive 宏在编译期自动生成序列化/反序列化代码（零运行时反射，性能极高）
#[derive(Debug, Serialize, Deserialize)]
struct Score {
    math: i32,
    english: i32,
}

/// 学生数据模型
/// serde 属性注解类似 pydantic 的 Field：
/// - default：缺失字段使用默认值
/// - rename：JSON 字段名与 Rust 字段名映射
#[derive(Debug, Serialize, Deserialize)]
struct Student {
    name: String,
    age: i32,
    major: String,
    #[serde(rename = "avgScore")]
    average_score: Score,
}

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    println!("=== HashMap 方式（对应 Python 的 dict） ===");

    // HashMap - 键值对集合，无类型保证，值只能是同一类型
    use std::collections::HashMap;
    let mut student: HashMap<&str, &str> = HashMap::new();
    student.insert("姓名", "李四");
    student.insert("年龄", "20"); // 年龄也只能存字符串，无法表达嵌套结构
    println!("学生信息: {student:?}");
    println!("姓名: {}", student["姓名"]);
    println!("问题：无类型检查、无嵌套能力、IDE 无补全");

    println!("\n=== serde 定义数据模型（对应 pydantic） ===");

    // 创建学生实例
    let student1 = Student {
        name: "李四".to_string(),
        age: 20,
        major: "计算机科学".to_string(),
        average_score: Score {
            math: 90,
            english: 85,
        },
    };
    println!("学生信息: {student1:?}");
    println!("姓名: {}", student1.name);
    println!("年龄: {}", student1.age);
    println!("专业: {}", student1.major);
    println!("数学成绩: {}", student1.average_score.math);
    println!("英语成绩: {}", student1.average_score.english);

    println!("\n=== 序列化：结构体 → JSON ===");

    // 序列化（对应 pydantic 的 model_dump_json）
    let json = serde_json::to_string_pretty(&student1).expect("序列化成功");
    println!("{json}");

    println!("\n=== 反序列化：JSON → 结构体（含数据校验） ===");

    // 反序列化（对应 pydantic 的 model_validate_json）
    let ok_json = r#"{
        "name": "王五",
        "age": 22,
        "major": "软件工程",
        "avgScore": { "math": 95, "english": 88 }
    }"#;
    let parsed: Student = serde_json::from_str(ok_json).expect("合法 JSON");
    println!(
        "解析成功: {} - {}岁 - 数学{}",
        parsed.name, parsed.age, parsed.average_score.math
    );

    // 非法数据：age 传字符串，serde 直接报错（对应 pydantic 的 ValidationError）
    let bad_json = r#"{ "name": "赵六", "age": "不是数字", "major": "x", "avgScore": {"math": 1, "english": 1} }"#;
    match serde_json::from_str::<Student>(bad_json) {
        Ok(s) => println!("解析成功: {s:?}"),
        Err(e) => println!("校验失败: {e}"),
    }

    // 缺失字段：没有 default 注解时缺失即报错
    let missing_json = r#"{ "name": "钱七", "age": 20, "major": "x" }"#;
    match serde_json::from_str::<Student>(missing_json) {
        Ok(s) => println!("解析成功: {s:?}"),
        Err(e) => println!("缺失字段: {e}"),
    }
}

#[allow(dead_code)]
fn main() {
    run();
}
