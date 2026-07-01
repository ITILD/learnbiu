---
layout: two-cols
---

# 进阶：模板与泛型编程

## 函数模板

```cpp
template<typename T>
T max(T a, T b) {
    return (a > b) ? a : b;
}

// 使用时自动推导
int    x = max(3, 5);          // T = int
double y = max(3.14, 2.71);    // T = double
std::string s = max(std::string("abc"),
                    std::string("xyz"));
```

## 类模板

```cpp
template<typename T>
class Stack {
    std::vector<T> data;
public:
    void push(const T& val) { data.push_back(val); }
    T pop() {
        T top = data.back();
        data.pop_back();
        return top;
    }
    bool empty() const { return data.empty(); }
};

Stack<int> intStack;
Stack<std::string> strStack;
```

::right::

## 模板特化

```cpp
// 通用模板
template<typename T>
class Printer {
public:
    static void print(const T& t) {
        std::cout << t << "\n";
    }
};

// 对 bool 的特化版本
template<>
class Printer<bool> {
public:
    static void print(bool b) {
        std::cout << (b ? "true" : "false") << "\n";
    }
};
```

## 变参模板

```cpp
// 递归基
void print_all() {
    std::cout << "\n";
}

// 变参展开
template<typename First, typename... Rest>
void print_all(First&& first, Rest&&... rest) {
    std::cout << first << " ";
    print_all(std::forward<Rest>(rest)...);
}

print_all(1, "hello", 3.14, 'x');
// 输出：1 hello 3.14 x
```

## 概念 (Concepts, C++20)

```cpp
#include <concepts>

// 约束 T 必须支持 + 运算
template<typename T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
};

// 使用 concept
template<Addable T>
T add(T a, T b) {
    return a + b;
}

// 更清晰的错误提示
add(1, 2);          // ✅
// add("a", "b");   // ❌ 编译错误：string 不满足 Addable
```

<div class="mt-2 p-3 bg-cyan-500/10 rounded-lg text-sm">
📐 模板是 C++ <b>泛型编程</b>的基础。STL 的所有容器和算法都是用模板实现的。C++20 的 <b>Concepts</b> 让模板错误更友好。
</div>