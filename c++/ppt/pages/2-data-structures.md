---
layout: two-cols
---

# 数据结构：STL 容器

## std::string — 字符串

```cpp
#include <string>
std::string s = "Hello";
s += " C++";           // 拼接
s.length();            // 长度
s.substr(0, 5);        // 截取 "Hello"
s.find("C++");         // 查找位置
s.replace(0, 5, "Hi"); // 替换
```

## std::vector — 动态数组

```cpp
#include <vector>
std::vector<int> v{1, 2, 3, 4, 5};

v.push_back(6);        // 末尾添加
v.pop_back();          // 末尾删除
v.size();              // 大小
v[0];                  // 索引访问
v.at(0);               // 安全访问（抛异常）
v.front(); v.back();   // 首 / 尾元素

// C++20 删除元素
std::erase(v, 3);      // 删除所有等于 3 的元素
```

::right::

## std::map — 有序键值对

```cpp
#include <map>
std::map<std::string, int> scores;
scores["math"] = 90;
scores["english"] = 85;

for (auto& [key, val] : scores) {
    std::cout << key << ": " << val << "\n";
}
```

## std::unordered_map — 哈希表

```cpp
#include <unordered_map>
std::unordered_map<std::string, int> cache;
cache["key1"] = 100;           // O(1) 平均
```

## std::set — 有序集合

```cpp
#include <set>
std::set<int> s{1, 3, 5, 7};
s.insert(9);
s.count(3);             // 是否存在

// 并交差运算
#include <algorithm>
std::set<int> a{1,2,3}, b{2,3,4};
// 使用 set_union / set_intersection / set_difference
```

## 容器对比

| 容器 | 底层 | 访问 | 插入 |
|------|------|------|------|
| `vector` | 数组 | O(1) | O(n) |
| `map` | 红黑树 | O(log n) | O(log n) |
| `unordered_map` | 哈希表 | O(1) 均摊 | O(1) 均摊 |
| `set` | 红黑树 | - | O(log n) |

<div class="mt-2 p-3 bg-orange-500/10 rounded-lg text-sm">
📦 STL 提供丰富的容器，<b>vector</b> 是最常用的动态数组。
</div>