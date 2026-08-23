---
layout: two-cols
layoutClass: gap-8
---

# 环境准备：uv 与项目创建

## 安装 uv

现代 Python 包管理器，替代 pip：

```bash
winget install --id=astral-sh.uv -e
```

验证安装：

```bash
uv --version
```

## 创建项目

```bash
# 1. 新建文件夹并用 VSCode 打开
# 2. 终端中初始化项目
uv init

# 3. 同步依赖（下载 Python + 依赖）
uv sync
```

::right::

## 配置解释器

```mermaid {scale: 0.65}
graph TD
    A[打开 main.py] --> B[点击右下角解释器]
    B --> C[选择 .venv/python.exe]
    C --> D[开始编码!]
```

## 调试代码

- 行号左侧点击 → 设置**断点**（红点）
- 按 `F5` → 启动调试
- 程序在断点处暂停，可查看变量

<div class="mt-4 p-4 bg-green-500/10 border-l-4 border-green-500 rounded text-sm">
uv 自动管理虚拟环境和依赖，无需手动配置。
</div>
