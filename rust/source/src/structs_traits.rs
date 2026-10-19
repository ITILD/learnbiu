//! 结构体与特征示例（对应 Python 的类与继承）
//! 对应 PPT 页：2-structs-traits.md
//! 本文件展示 struct 定义、impl 方法、trait 定义与实现、trait 对象与泛型
//!
//! 单独运行：cargo run --bin structs_traits

use std::fmt;

/// 人类结构体 - 演示结构体定义与关联函数
/// 对应 Python 的 class Person
struct Person {
    name: String,
    age: u32,
}

/// Person 的实现块：所有方法都写在这里
impl Person {
    /// 关联函数（对应 Python 的 __init__ + 工厂方法），通过 Self:: 调用
    fn new(name: &str, age: u32) -> Self {
        Self {
            name: name.to_string(),
            age,
        }
    }

    /// 不可变方法：&self 只读借用自身（对应 Python 的 self）
    fn introduce(&self) -> String {
        format!("我叫{}，今年{}岁。", self.name, self.age)
    }

    /// 可变方法：&mut self 可以修改自身
    fn have_birthday(&mut self) {
        self.age += 1;
        println!("{}过生日啦！现在{}岁。", self.name, self.age);
    }
}

/// 学生结构体 - Rust 没有 extends 继承，用组合代替（has-a 关系）
/// 对应 Python 的 class Student(Person)
struct Student {
    person: Person,     // 组合：持有一个人
    student_id: String, // 自己的字段
    courses: Vec<String>,
}

impl Student {
    fn new(name: &str, age: u32, student_id: &str) -> Self {
        Self {
            person: Person::new(name, age),
            student_id: student_id.to_string(),
            courses: Vec::new(),
        }
    }

    /// 选课方法
    fn enroll_course(&mut self, course_name: &str) {
        self.courses.push(course_name.to_string());
        println!("{}选了课程: {course_name}", self.student_id);
    }

    /// 显示所选课程
    fn show_courses(&self) {
        if self.courses.is_empty() {
            println!("{}还没有选课", self.student_id);
        } else {
            println!("{}的课程: {}", self.student_id, self.courses.join(", "));
        }
    }

    /// 手动转发：组合模式下需要显式委托（Rust 无自动继承）
    fn introduce(&self) -> String {
        self.person.introduce()
    }
}

/// 特征（trait）- 定义共享行为的接口（类似 Python 的抽象基类/协议）
/// trait 只声明方法签名，由各类型分别实现
trait Greet {
    /// trait 方法可以有默认实现（子类不重写时就用它）
    fn greet(&self) -> String {
        "大家好！".to_string()
    }

    fn describe(&self) -> String;
}

impl Greet for Person {
    /// 覆盖默认实现
    fn greet(&self) -> String {
        format!("你好，我是{}", self.name)
    }

    fn describe(&self) -> String {
        format!("一个 {} 岁的人", self.age)
    }
}

impl Greet for Student {
    fn describe(&self) -> String {
        format!("学号 {} 的学生", self.student_id)
    }
}

/// 实现 Display trait：让结构体支持 {} 打印（类似 Python 的 __str__）
impl fmt::Display for Person {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Person({}, {}岁)", self.name, self.age)
    }
}

/// 泛型函数：任何实现了 Greet 的类型都能传入（类似 Python 的鸭子类型，但编译期检查）
fn welcome(g: &impl Greet) {
    println!("{} —— {}", g.greet(), g.describe());
}

/// trait 对象：运行时多态（类似 Python 变量天然的多态）
fn welcome_all(greeters: &[Box<dyn Greet>]) {
    for g in greeters {
        println!("{} —— {}", g.greet(), g.describe());
    }
}

/// 示例主体：被 main.rs 调用，也可通过本文件的 main 独立运行
pub fn run() {
    println!("=== 结构体和方法 ===");

    // 创建 Person 对象（对应 Python 的 Person("张三", 25)）
    let person1 = Person::new("张三", 25);
    println!("{}", person1.introduce());
    println!("Display 打印: {person1}");

    // 创建 Student 对象（组合代替继承）
    let mut student1 = Student::new("李四", 20, "S001");
    println!("{}", student1.introduce());

    // 调用对象方法
    student1.enroll_course("Rust编程");
    student1.enroll_course("数据结构");
    student1.show_courses();

    // 过生日
    student1.person.have_birthday();

    println!("\n=== trait 与多态 ===");

    // 静态分发：泛型参数，编译期单态化，零开销
    welcome(&person1);
    welcome(&student1);

    // 动态分发：trait 对象，运行时查表（类似 Python 的方法解析）
    let greeters: Vec<Box<dyn Greet>> = vec![
        Box::new(Person::new("王五", 30)),
        Box::new(Student::new("赵六", 22, "S002")),
    ];
    welcome_all(&greeters);

    println!("\n=== 组合 vs 继承 ===");
    println!("Rust 没有类继承，推荐：组合 + trait + 泛型");
    println!("impl 块 → 方法定义 | trait → 接口抽象 | 组合 → 代码复用");
}

#[allow(dead_code)]
fn main() {
    run();
}
