---
layout: two-cols
---

# 指针详解（上）：基础概念

## 什么是指针？

指针是一个变量，它存储的是另一个变量的**内存地址**。

```cpp
int x = 42;
int* p = &x;      // p 存储 x 的地址
// p → x的内存地址

std::cout << x;   // 42（值）
std::cout << &x;  // 0x7ff...（地址）
std::cout << p;   // 0x7ff...（同地址）
std::cout << *p;  // 42（解引用取到值）
```

## 核心运算符

| 符号 | 名称 | 含义 |
|------|------|------|
| `&` | 取地址 | 获取变量的内存地址 |
| `*` | 解引用 | 通过地址访问值 |

```cpp
int a = 10;
int* ptr = &a;    // & 取 a 的地址
*ptr = 20;        // * 通过地址修改 a
std::cout << a;   // 20 — a 被修改了！
```

::right::

## 指针的声明

```cpp
int* p1;           // 指向 int 的指针（未初始化⚠️）
int* p2 = nullptr; // 空指针（C++11 推荐）
int* p3 = &x;      // 指向 x
auto* p4 = &x;     // auto 自动推导

// 常量与指针组合
const int* p5;     // 指向常量：不能改值
int* const p6 = &x;// 常量指针：不能改指向
const int* const p7 = &x; // 都不能改
```

## 指针的初始化 ⚠️

```cpp
int* p;            // ❌ 野指针！未初始化
*p = 5;            // ❌ 未定义行为！

int* p = nullptr;  // ✅ 初始化为空
int* p = &x;       // ✅ 指向已有变量
```

## 指针 vs 引用

```cpp
// 指针：
int* p = &x;       // 可以重新指向
p = &y;            // ✅ 指向其他变量

// 引用：
int& r = x;        // 必须在声明时初始化
r = y;             // 这是赋值（x=y），不是改绑定
// 引用不可重新绑定！
```

| 特性 | 指针 | 引用 |
|------|------|------|
| 可为空 | ✅ | ❌ |
| 可重新指向 | ✅ | ❌ |
| 语法 | `*p` `&x` | 直接用 |
| 必须初始化 | ❌ | ✅ |
| 本质 | 存储地址 | 变量的别名 |

---

## 指针详解（下）：进阶用法

## 指针与数组

```cpp
int arr[5] = {10, 20, 30, 40, 50};
int* p = arr;         // 数组名 = 首元素地址

std::cout << *p;      // 10
std::cout << *(p+1);  // 20
std::cout << p[2];    // 30 — 指针也可用下标！

// 遍历数组
for (int* it = arr; it != arr + 5; ++it) {
    std::cout << *it << " ";
}
```

## 指针算术运算

```cpp
int arr[] = {10, 20, 30};
int* p = arr;

p++;       // 指向下一个元素（地址 + sizeof(int)）
p--;       // 指向上一个元素
p += 2;    // 前进 2 个元素
int diff = p - arr;  // 元素个数差 = 2
```

| 运算 | 效果 |
|------|------|
| `p + n` | 后移 n 个元素 |
| `p - n` | 前移 n 个元素 |
| `p++` | 指向下一个 |
| `p2 - p1` | 两指针间的元素数 |

## 动态内存分配

```cpp
// C 风格（不推荐）
int* p = (int*)malloc(sizeof(int));
free(p);

// C++ 风格
int* p = new int{42};       // 分配单个
delete p;                   // 释放单个

int* arr = new int[100]{};  // 分配数组
delete[] arr;               // 释放数组！注意 []
```

## 二级指针（指针的指针）

```cpp
int x = 10;
int* p = &x;       // 一级指针
int** pp = &p;     // 二级指针

**pp = 20;         // 两次解引用，修改 x
std::cout << x;    // 20
```

## 函数指针

```cpp
int add(int a, int b) { return a + b; }

int (*func)(int, int) = &add;  // 函数指针
int result = func(3, 5);       // 调用 = 8

// 使用 auto 简化
auto f = &add;
```

## 常见指针陷阱

```cpp
// 1. 空指针解引用
int* p = nullptr;
*p = 5;            // ❌ 崩溃！

// 2. 悬垂指针（指向已释放的内存）
int* p = new int{10};
delete p;
*p = 20;           // ❌ 未定义行为！

// 3. 内存泄漏（忘记 delete）
int* p = new int{10};
// 忘了 delete p;  → 内存泄漏！

// 4. 数组与标量混用
int* p = new int;
delete[] p;        // ❌ 不匹配！
```

<div class="mt-2 p-3 bg-red-500/10 rounded-lg text-sm">
⚠️ 裸指针（raw pointer）容易出错。现代 C++ 推荐用<b>智能指针</b>（下页）替代。
</div>