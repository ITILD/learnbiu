---
layout: two-cols
---

# 函数：声明、定义与重载

## 函数声明与定义

```cpp
// 声明（放在 .h 文件中）
int add(int a, int b);

// 定义（放在 .cpp 文件中）
int add(int a, int b) {
    return a + b;
}
```

## 参数传递方式

```cpp
// 值传递：复制一份（不修改原值）
void by_value(int x) { x += 10; }

// 引用传递：别名（修改原值）
void by_ref(int& x) { x += 10; }

// 常量引用：只读，不复制（高效）
void by_cref(const int& x) {
    std::cout << x;  // 只能读
}

// 指针传递（C 风格，参见指针章节）
void by_ptr(int* x) { *x += 10; }
```

::right::

## 默认参数

```cpp
double area(double length, double width = 1.0) {
    return length * width;
}

area(5);       // width=1.0 → 5.0
area(5, 3);    // → 15.0

// 注意：默认参数必须从右向左连续
```

## 函数重载

```cpp
int max(int a, int b)      { return a > b ? a : b; }
double max(double a, double b) { return a > b ? a : b; }
int max(int a, int b, int c)   {
    return max(max(a, b), c);
}
// 同名函数，参数不同 = 重载
```

## 内联函数

```cpp
inline int square(int x) {
    return x * x;
}
// 编译器会将调用处展开，减少函数调用开销
```

## Lambda 表达式

```cpp
auto add = [](int a, int b) -> int {
    return a + b;
};

int x = 10;
auto inc = [&x]() { x++; };   // 引用捕获
auto copy = [x]() { return x; }; // 值捕获
```

<div class="mt-2 p-3 bg-indigo-500/10 rounded-lg text-sm">
🎯 C++ 支持<b>函数重载</b>和<b>默认参数</b>，不像 C 那样必须用不同函数名。
</div>