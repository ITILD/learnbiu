---
layout: two-cols
---

# 环境搭建：VSCode 配置

## 安装 Visual Studio Code

**下载地址：** https://code.visualstudio.com/download

安装步骤：
1. 下载 Windows 版本安装包
2. 双击运行，按向导完成安装

## 必备插件

| 插件 | 用途 |
|------|------|
| **C/C++** (Microsoft) | 代码补全、调试、IntelliSense |
| **CMake Tools** | CMake 项目支持 |
| **clangd** | 更快的补全和代码分析（可选替代） |
| **Chinese (Simplified)** | 中文语言包（可选） |

::right::

## C++ 编译器选择

Windows 上三大编译器：

| 编译器 | 来源 | 特点 |
|--------|------|------|
| **MSVC** | Visual Studio | Windows 原生，推荐 |
| **GCC** | MinGW-w64 | 跨平台，轻量 |
| **Clang** | LLVM | 错误信息友好 |

## 安装 MSVC（推荐）

方式一：安装 **Visual Studio 2022 Community**
- 勾选「使用 C++ 的桌面开发」工作负载
- 免费使用

方式二：仅安装 **Build Tools**
- 搜索 "Visual Studio Build Tools"
- 勾选 "MSVC v143" 和 "Windows 11 SDK"

<div class="mt-4 p-4 bg-blue-500/10 rounded-lg">
💡 推荐使用 <b>MSVC</b> 编译器，与 Windows 系统集成最佳。
</div>