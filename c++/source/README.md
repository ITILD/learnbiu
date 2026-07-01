# C++ 快速入门

欢迎来到 C++ 快速入门教程！本教程将引导您完成 C++ 开发环境的搭建和基础学习。

## 1. 环境准备

### 1.1 安装 Visual Studio Code

**下载地址：** https://code.visualstudio.com/download

安装必备插件：
- **C/C++** (Microsoft) — 代码补全、调试支持
- **CMake Tools** — CMake 项目支持

### 1.2 安装 C++ 编译器

**推荐方式**：安装 Visual Studio 2022 Community
- 下载：https://visualstudio.microsoft.com/zh-hans/downloads/
- 安装时勾选「使用 C++ 的桌面开发」工作负载

### 1.3 直接编译（无需 CMake）

```bash
# 使用 MSVC 编译器
cl /std:c++20 /EHsc main_base.cpp /Fe:main_base.exe
main_base.exe

# 或使用 g++
g++ -std=c++20 -o main_base main_base.cpp
./main_base
```

### 1.4 使用 CMake 编译

```bash
mkdir build && cd build
cmake ..
cmake --build .
./Debug/main_base.exe
```

## 2. 学习路径

1. **main_base.cpp** — 基础语法：类型、控制流、STL、函数、类、异常、裸指针
2. **main_middle.cpp** — 进阶语法：智能指针（unique_ptr、shared_ptr、weak_ptr）、模板、RAII

## 3. 文件说明

| 文件 | 内容 |
|------|------|
| `main_base.cpp` | 基础语法全示例 |
| `main_middle.cpp` | 智能指针、模板、RAII 进阶示例 |
| `CMakeLists.txt` | CMake 构建配置 |