---
layout: two-cols
---

# 环境搭建：CMake 构建系统

## 为什么用 CMake？

CMake 是 C++ 生态最流行的构建系统：
- 跨平台（Windows / Linux / macOS）
- IDE 无关（VSCode、CLion、VS 都支持）
- 依赖管理方便

## 安装 CMake

1. 下载：https://cmake.org/download/
2. 选择 Windows x64 Installer
3. 安装时勾选「Add CMake to system PATH」

验证安装：
```bash
cmake --version
```

::right::

## CMakeLists.txt 示例

```cmake
cmake_minimum_required(VERSION 3.20)
project(HelloCpp)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(main main.cpp)
```

## 构建流程

```bash
# 在项目目录下执行
mkdir build && cd build
cmake ..
cmake --build .
```

```mermaid {scale: 0.6}
graph LR
    A[CMakeLists.txt] --> B[cmake 配置]
    B --> C[生成构建文件]
    C --> D[cmake --build 编译]
    D --> E[可执行文件 .exe]
```

<div class="mt-4 p-4 bg-emerald-500/10 rounded-lg">
📦 本教程所有示例都可用 <b>单个 main.cpp 直接编译</b>，无需 CMake。CMake 用于大型项目管理。
</div>