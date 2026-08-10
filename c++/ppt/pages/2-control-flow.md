---
layout: two-cols
---

# 控制流：条件与循环

## if / else if / else

```cpp
int score = 85;

if (score >= 90) {
    std::cout << "优秀！\n";
} else if (score >= 80) {
    std::cout << "良好！\n";
} else if (score >= 60) {
    std::cout << "及格！\n";
} else {
    std::cout << "不及格！\n";
}
```

## switch 语句

```cpp
char grade = 'B';
switch (grade) {
    case 'A': std::cout << "优秀\n"; break;
    case 'B': std::cout << "良好\n"; break;
    case 'C': std::cout << "及格\n"; break;
    default:  std::cout << "不及格\n"; break;
}
```

::right::

## for 循环

```cpp
// 经典 for
for (int i = 0; i < 5; i++) {
    std::cout << i << " ";  // 0 1 2 3 4
}

// 范围 for（C++11）
std::vector<int> v{1, 2, 3, 4, 5};
for (int n : v) {
    std::cout << n << " ";  // 1 2 3 4 5
}

// 带引用的范围 for
for (int& n : v) {
    n *= 2;  // 修改原值
}
```

## while 循环

```cpp
// while：先判断后执行
int count = 3;
while (count > 0) {
    std::cout << "倒计时: " << count << "\n";
    count--;
}

// do-while：先执行后判断
int x = 0;
do {
    std::cout << x << " ";
    x++;
} while (x < 5);
```

## 循环控制

```cpp
// break：跳出循环
for (int i = 0; i < 10; i++) {
    if (i == 5) break;
}

// continue：跳过本次迭代
for (int i = 0; i < 10; i++) {
    if (i % 2 == 0) continue;
    std::cout << i;  // 只打印奇数
}
```

<div class="mt-2 p-3 bg-teal-500/10 rounded-lg text-sm">
🔄 C++ 使用<b>大括号 {}</b> 定义代码块，使用 <b>break</b> 跳出 switch。
</div>