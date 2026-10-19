---
layout: two-cols
layoutClass: gap-8
---

# 环境准备：rustup 与项目创建

## 安装 rustup（自带 Cargo）

官方工具链安装器，Cargo 是配套的包管理器与构建工具：

```bash
winget install --id=Rustlang.Rustup -e
```

验证安装（需重开终端）：

```bash
rustc --version
cargo --version
```

## 创建项目

```bash
# 1. 新建文件夹并用 VSCode 打开
# 2. 终端中初始化项目
cargo init

# 3. 编译并运行
cargo run
```

::right::

## 常用 Cargo 命令

| 命令 | 用途 |
|------|------|
| `cargo run` | 编译并运行 |
| `cargo check` | 只检查类型，速度最快 |
| `cargo build` | 编译到 target/ |
| `cargo fmt` | 自动格式化 |
| `cargo clippy` | 静态检查与惯用法建议 |

## 调试代码

- 安装 CodeLLDB → 配置 `launch.json`
- 行号左侧点击 → 设置**断点**（红点）
- 按 `F5` → 启动调试，可查看变量

<div class="mt-4 p-4 bg-green-500/10 border-l-4 border-green-500 rounded text-sm">
Cargo 集构建、依赖管理、测试、文档于一体，类似 Python 的 uv + pip + pytest 合体。
</div>
