/*
 * C++ 基础语法学习示例
 * 本文件展示了 C++ 的基础语法、STL 容器、类和对象等核心概念
 * 编译: g++ -std=c++20 -o main_base main_base.cpp
 */

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <memory>
#include <algorithm>

// =============================================================================
// 1. 基础语法示例
// =============================================================================

void basic_syntax_examples()
{
    // 变量和数据类型
    std::string name{"张三"};   // 字符串类型
    int age{25};                 // 整数类型
    double height{1.75};         // 双精度浮点
    bool is_student{true};       // 布尔类型

    std::cout << "=== 基础数据类型 ===" << std::endl;
    std::cout << "姓名: " << name << std::endl;
    std::cout << "年龄: " << age << std::endl;
    std::cout << "身高: " << height << "米" << std::endl;
    std::cout << "是否学生: " << (is_student ? "是" : "否") << std::endl;

    // 算术运算
    int a{10};
    int b{3};

    std::cout << "\n=== 算术运算 ===" << std::endl;
    std::cout << a << " + " << b << " = " << a + b << std::endl;
    std::cout << a << " - " << b << " = " << a - b << std::endl;
    std::cout << a << " * " << b << " = " << a * b << std::endl;
    std::cout << a << " / " << b << " = " << a / b << "（整数除）" << std::endl;
    std::cout << a << " / " << b << ".0 = " << static_cast<double>(a) / b << "（浮点除）" << std::endl;
    std::cout << a << " % " << b << " = " << a % b << std::endl;

    // 比较运算
    std::cout << "\n=== 比较运算 ===" << std::endl;
    std::cout << a << " > " << b << ": " << (a > b) << std::endl;
    std::cout << a << " < " << b << ": " << (a < b) << std::endl;
    std::cout << a << " == " << b << ": " << (a == b) << std::endl;
    std::cout << a << " != " << b << ": " << (a != b) << std::endl;

    // 逻辑运算
    bool x{true};
    bool y{false};

    std::cout << "\n=== 逻辑运算 ===" << std::endl;
    std::cout << "x && y: " << (x && y) << std::endl;
    std::cout << "x || y: " << (x || y) << std::endl;
    std::cout << "!x: " << (!x) << std::endl;
}

// =============================================================================
// 2. 控制流示例
// =============================================================================

void control_flow_examples()
{
    std::cout << "\n=== if/else 条件判断 ===" << std::endl;

    int score{85};

    if (score >= 90)
    {
        std::cout << "成绩优秀！" << std::endl;
    }
    else if (score >= 80)
    {
        std::cout << "成绩良好！" << std::endl;
    }
    else if (score >= 60)
    {
        std::cout << "成绩及格！" << std::endl;
    }
    else
    {
        std::cout << "成绩不及格！" << std::endl;
    }

    std::cout << "\n=== switch 语句 ===" << std::endl;

    char grade{'B'};
    switch (grade)
    {
    case 'A':
        std::cout << "优秀" << std::endl;
        break;
    case 'B':
        std::cout << "良好" << std::endl;
        break;
    case 'C':
        std::cout << "及格" << std::endl;
        break;
    default:
        std::cout << "不及格" << std::endl;
        break;
    }

    std::cout << "\n=== for 循环 ===" << std::endl;

    std::cout << "数字 1-5: ";
    for (int i{1}; i <= 5; i++)
    {
        std::cout << i << " ";
    }
    std::cout << std::endl;

    std::vector<std::string> fruits{"苹果", "香蕉", "橙子"};
    std::cout << "水果列表: ";
    for (const auto& fruit : fruits)
    {
        std::cout << fruit << " ";
    }
    std::cout << std::endl;

    std::cout << "\n=== while 循环 ===" << std::endl;

    int count{3};
    while (count > 0)
    {
        std::cout << "倒计时: " << count << std::endl;
        count--;
    }
    std::cout << "开始！" << std::endl;
}

// =============================================================================
// 3. 数据结构示例（STL 容器）
// =============================================================================

void data_structure_examples()
{
    std::cout << "\n=== std::vector（动态数组）===" << std::endl;

    std::vector<int> numbers{1, 2, 3, 4, 5};
    std::cout << "原始: ";
    for (int n : numbers)
        std::cout << n << " ";
    std::cout << std::endl;

    numbers.push_back(6);
    numbers.insert(numbers.begin(), 0);
    numbers.erase(numbers.begin() + 3);

    std::cout << "修改后: ";
    for (int n : numbers)
        std::cout << n << " ";
    std::cout << std::endl;

    std::cout << "长度: " << numbers.size() << std::endl;
    std::cout << "第一个: " << numbers.front() << std::endl;
    std::cout << "最后一个: " << numbers.back() << std::endl;

    std::cout << "\n=== std::map（有序键值对）===" << std::endl;

    std::map<std::string, int> scores;
    scores["数学"] = 90;
    scores["英语"] = 85;
    scores["编程"] = 95;

    for (const auto& [subject, score] : scores)
    {
        std::cout << subject << ": " << score << "分" << std::endl;
    }

    std::cout << "\n=== std::set（集合）===" << std::endl;

    std::set<int> set_a{1, 2, 3, 4, 5};
    std::set<int> set_b{4, 5, 6, 7, 8};

    std::cout << "集合a: ";
    for (int n : set_a)
        std::cout << n << " ";
    std::cout << std::endl;

    std::cout << "集合b: ";
    for (int n : set_b)
        std::cout << n << " ";
    std::cout << std::endl;

    // 检查元素是否存在
    std::cout << "3在a中: " << (set_a.count(3) ? "是" : "否") << std::endl;
    std::cout << "9在a中: " << (set_a.count(9) ? "是" : "否") << std::endl;

    std::cout << "\n=== std::string ===" << std::endl;

    std::string s{"Hello"};
    s += " C++";
    std::cout << "拼接: " << s << std::endl;
    std::cout << "长度: " << s.length() << std::endl;
    std::cout << "子串: " << s.substr(0, 5) << std::endl;
}

// =============================================================================
// 4. 函数示例
// =============================================================================

// 基本函数
std::string greet(const std::string& name)
{
    return "你好, " + name + "!";
}

// 带默认参数的函数
double calculate_area(double length, double width = 1.0)
{
    return length * width;
}

// 函数重载
int max_val(int a, int b) { return a > b ? a : b; }
double max_val(double a, double b) { return a > b ? a : b; }
int max_val(int a, int b, int c) { return max_val(max_val(a, b), c); }

void function_examples()
{
    std::cout << "\n=== 函数定义和调用 ===" << std::endl;

    std::cout << greet("王五") << std::endl;
    std::cout << "矩形面积(长5宽3): " << calculate_area(5, 3) << std::endl;
    std::cout << "矩形面积(长5默认宽): " << calculate_area(5) << std::endl;

    std::cout << "max(3, 5) = " << max_val(3, 5) << std::endl;
    std::cout << "max(3.1, 2.7) = " << max_val(3.1, 2.7) << std::endl;
    std::cout << "max(1, 5, 3) = " << max_val(1, 5, 3) << std::endl;

    // Lambda 表达式
    auto square = [](int x) { return x * x; };
    std::cout << "6的平方 = " << square(6) << std::endl;

    int counter{0};
    auto increment = [&counter]() { counter++; };
    increment();
    increment();
    std::cout << "counter = " << counter << std::endl;
}

// =============================================================================
// 5. 类和对象示例
// =============================================================================

class Person
{
private:
    std::string name;
    int age;

public:
    Person(std::string n, int a) : name{std::move(n)}, age{a} {}

    void introduce() const
    {
        std::cout << "我叫" << name << "，今年" << age << "岁。" << std::endl;
    }

    void have_birthday()
    {
        age++;
        std::cout << name << "过生日啦！现在" << age << "岁。" << std::endl;
    }
};

class Student : public Person
{
private:
    std::string student_id;
    std::vector<std::string> courses;

public:
    Student(std::string n, int a, std::string sid)
        : Person{std::move(n), a}, student_id{std::move(sid)} {}

    void enroll_course(const std::string& course_name)
    {
        courses.push_back(course_name);
        std::cout << student_id << "选了课程: " << course_name << std::endl;
    }

    void show_courses() const
    {
        if (courses.empty())
        {
            std::cout << student_id << "还没有选课" << std::endl;
        }
        else
        {
            std::cout << student_id << "的课程: ";
            for (size_t i{0}; i < courses.size(); i++)
            {
                std::cout << courses[i];
                if (i < courses.size() - 1)
                    std::cout << ", ";
            }
            std::cout << std::endl;
        }
    }
};

void class_object_examples()
{
    std::cout << "\n=== 类和对象 ===" << std::endl;

    Person person1("张三", 25);
    person1.introduce();
    person1.have_birthday();

    Student student1("李四", 20, "S001");
    student1.introduce();  // 继承自 Person
    student1.enroll_course("Python编程");
    student1.enroll_course("数据结构");
    student1.show_courses();
}

// =============================================================================
// 6. 异常处理示例
// =============================================================================

void exception_examples()
{
    std::cout << "\n=== 异常处理 ===" << std::endl;

    auto safe_divide = [](int a, int b) -> double
    {
        if (b == 0)
        {
            throw std::runtime_error("除数不能为零！");
        }
        return static_cast<double>(a) / b;
    };

    try
    {
        std::cout << "10 / 2 = " << safe_divide(10, 2) << std::endl;
        std::cout << "10 / 0 = " << safe_divide(10, 0) << std::endl;
    }
    catch (const std::runtime_error& e)
    {
        std::cerr << "运行时错误: " << e.what() << std::endl;
    }
    catch (const std::exception& e)
    {
        std::cerr << "标准异常: " << e.what() << std::endl;
    }

    std::cout << "异常处理完毕，程序继续运行。" << std::endl;
}

// =============================================================================
// 7. 指针示例（裸指针 - 仅供理解，实际应使用智能指针）
// =============================================================================

void pointer_examples()
{
    std::cout << "\n=== 指针基础 ===" << std::endl;

    int value{42};
    int* ptr{&value};

    std::cout << "value 的值: " << value << std::endl;
    std::cout << "value 的地址: " << &value << std::endl;
    std::cout << "ptr 存储的地址: " << ptr << std::endl;
    std::cout << "ptr 解引用的值: " << *ptr << std::endl;

    // 通过指针修改原值
    *ptr = 100;
    std::cout << "修改后 value = " << value << std::endl;

    // 指针与数组
    std::cout << "\n=== 指针与数组 ===" << std::endl;

    int arr[5]{10, 20, 30, 40, 50};
    int* arr_ptr{arr};  // 数组名即首元素地址

    std::cout << "通过指针遍历数组: ";
    for (int i{0}; i < 5; i++)
    {
        std::cout << *(arr_ptr + i) << " ";
    }
    std::cout << std::endl;

    // 动态内存分配
    std::cout << "\n=== new / delete ===" << std::endl;

    int* dyn_int{new int{999}};
    std::cout << "动态分配的整数: " << *dyn_int << std::endl;
    delete dyn_int;
    // dyn_int = nullptr;  // 防止悬垂指针

    // 空指针检查
    std::cout << "\n=== 空指针 ===" << std::endl;

    int* null_ptr{nullptr};
    if (null_ptr)
    {
        std::cout << "指针有效" << std::endl;
    }
    else
    {
        std::cout << "指针为空（nullptr）" << std::endl;
    }
}

// =============================================================================
// 主函数
// =============================================================================

int main()
{
    basic_syntax_examples();
    control_flow_examples();
    data_structure_examples();
    function_examples();
    class_object_examples();
    exception_examples();
    pointer_examples();

    std::cout << "\n✅ 所有基础示例执行完成！" << std::endl;
    std::cout << "💡 建议：修改代码并运行，观察不同的输出结果" << std::endl;

    return 0;
}