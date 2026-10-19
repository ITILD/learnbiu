//! 枚举与模式匹配示例（Rust 核心特性）
//! 对应 PPT 页：2-enums-matching.md
//! 本文件展示 enum（可携带数据）、Option<T>、match 表达式、if let
//!
//! 单独运行：cargo run --bin enums_matching

/// 枚举的每个变体都可以携带不同类型和数量的数据
/// 这是 Rust 与 C/Python 枚举最大的区别：它是真正的代数数据类型
#[derive(Debug)]
enum Shape {
    Circle(f64),                  // 携带一个半径
    Rectangle { w: f64, h: f64 }, // 携带命名字段
    Triangle(f64, f64, f64),      // 携带三条边
}

impl Shape {
    fn area(&self) -> f64 {
        // match 按变体拆解数据（解构匹配）
        match self {
            Shape::Circle(r) => std::f64::consts::PI * r * r,
            Shape::Rectangle { w, h } => w * h,
            Shape::Triangle(a, b, c) => {
                // 海伦公式
                let s = (a + b + c) / 2.0;
                (s * (s - a) * (s - b) * (s - c)).sqrt()
            }
        }
    }
}

/// 交通信号灯：最简单的枚举（不带数据）
#[derive(Debug)]
enum Light {
    Red,
    Yellow,
    Green,
}

/// Option<T> 是标准库内置枚举：Some(T) 或 None
/// Rust 没有 null，用 Option 表达"可能没有值"
fn find_user(id: u32) -> Option<String> {
    match id {
        1 => Some("张三".to_string()),
        2 => Some("李四".to_string()),
        _ => None, // 通配符：其余所有情况
    }
}

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    println!("=== 枚举定义（可携带数据） ===");

    let shapes = vec![
        Shape::Circle(2.0),
        Shape::Rectangle { w: 3.0, h: 4.0 },
        Shape::Triangle(3.0, 4.0, 5.0),
    ];
    for s in &shapes {
        println!("{s:?} 面积 = {:.2}", s.area());
    }

    println!("\n=== match 表达式 ===");

    // match 必须穷举所有情况，否则编译不通过（编译器替你查漏）
    for light in [Light::Red, Light::Yellow, Light::Green] {
        let action = match light {
            Light::Red => "停",
            Light::Yellow => "注意",
            Light::Green => "行",
        };
        println!("{light:?} → {action}");
    }

    // match 还能匹配字面量、范围、元组、守卫条件
    let score = 85;
    let grade = match score {
        90..=100 => "优秀",
        80..=89 if score >= 85 => "良好+",
        80..=89 => "良好",
        60..=79 => "及格",
        _ => "不及格",
    };
    println!("分数 {score} → {grade}（match 支持范围和 if 守卫）");

    let point = (0, -2);
    match point {
        (0, 0) => println!("点在原点"),
        (x, 0) => println!("点在 x 轴上, x={x}"),
        (0, y) => println!("点在 y 轴上, y={y}"),
        (x, y) => println!("普通点 ({x}, {y})"),
    }

    println!("\n=== Option<T>：替代 null ===");

    // Rust 没有 null，避免了 Python 的 None 陷阱和 Java 的 NPE
    let user1 = find_user(1);
    let user3 = find_user(3);
    println!("id=1 → {user1:?}");
    println!("id=3 → {user3:?}");

    // 处理 Option 的惯用方法链
    let name_len = find_user(1).map(|name| name.len()).unwrap_or(0);
    println!("名字长度: {name_len}");

    // match 处理 Option
    match find_user(3) {
        Some(name) => println!("找到用户: {name}"),
        None => println!("用户不存在"),
    }

    println!("\n=== if let：只关心一种情况 ===");

    // 当只关心一个分支时，if let 比 match 更简洁
    if let Some(name) = find_user(2) {
        println!("if let 找到用户: {name}");
    } else {
        println!("if let 未找到");
    }

    // let else 语法（Rust 1.65+）：提前返回的风格
    let Some(name) = find_user(1) else {
        println!("let else：未找到，提前结束");
        return;
    };
    println!("let else 拿到用户: {name}");

    // while let：持续处理直到为 None
    let mut stack = vec![1, 2, 3];
    while let Some(top) = stack.pop() {
        print!("{top} ");
    }
    println!("（while let 循环弹出栈元素）");
}

#[allow(dead_code)]
fn main() {
    run();
}
