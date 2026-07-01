---
layout: two-cols
---

# 基础语法：变量与数据类型

## 基本类型

```cpp
int age = 25;              // 整数（4 字节）
float height = 1.75f;      // 单精度浮点
double pi = 3.1415926;     // 双精度浮点
char grade = 'A';          // 单个字符
bool is_student = true;    // 布尔值
std::string name = "张三";  // 字符串（std 命名空间）
```

## auto 自动推导

```cpp
auto x = 42;               // int
auto y = 3.14;             // double
auto z = "hello"s;         // std::string
auto vec = std::vector{1, 2, 3};  // std::vector<int>
```

::right::

## 类型转换

```cpp
// C 风格（不推荐）
int a = (int)3.14;

// C++ 风格（推荐）
int b = static_cast<int>(3.14);
auto s = std::to_string(42);  // int → string
auto n = std::stoi("42");     // string → int
```

## 变量初始化（统一初始化）

```cpp
int x{42};                  // 推荐：大括号初始化
double y{3.14};
std::vector<int> v{1, 2, 3};

// 防止窄化转换
int z{3.14};                // ❌ 编译错误！
int z = 3.14;               // ⚠️ 静默截断为 3
```

<div class="mt-4 p-4 bg-yellow-500/10 rounded-lg">
📌 C++ 是<b>静态类型</b>语言，变量类型在编译时确定，无法改变。使用 <code>{}</code> 初始化更安全。
</div>

## 常用类型大小

| 类型 | 大小 | 范围 |
|------|------|------|
| `int` | 4B | ±21亿 |
| `long long` | 8B | ±9×10¹⁸ |
| `size_t` | 8B | 0~2⁶⁴-1 |
| `double` | 8B | 15位精度 |