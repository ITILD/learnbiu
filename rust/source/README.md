# Rust 快速入门

欢迎来到 Rust 快速入门教程！本教程将引导您完成 Rust 开发环境的搭建和基础学习。

## 1. 环境准备

### 1.1 安装 Visual Studio Code（通用开发 IDE）

**下载地址：** [https://code.visualstudio.com/download](https://code.visualstudio.com/download)

**安装步骤：**

1. 访问上述链接下载 Windows 版本
2. 双击运行下载的 `VSCodeUserSetup-x64-版本号.exe` 文件
3. 按照安装向导提示，选择默认设置完成安装

**安装必备插件：**

安装完成后，启动 VSCode 并安装以下扩展：

1. 点击左侧活动栏的**扩展图标**（四个方块图标）
2. 在搜索框中分别搜索并安装：
   - **rust-analyzer** - Rust 官方语言服务器（代码补全/类型检查/重构）
   - **CodeLLDB** - 调试器（断点/单步/变量查看）
   - **Even Better TOML** - Cargo.toml 语法支持
   - **Chinese (Simplified) Language Pack** - 中文语言包（可选）
   - **rustfmt** 格式化已内置在 rustup 中，无需额外插件

### 1.2 安装开发工具链（rustup 与 cargo）

**安装 rustup（官方安装器，自带 cargo 包管理器）：**

1. 按 `Win + R` 键，输入 `powershell` 并回车
2. 在 PowerShell 中执行以下命令：

```powershell
winget install --id=Rustlang.Rustup -e
```

或在任意终端访问 [https://rustup.rs](https://rustup.rs) 按提示安装。

**（可选）配置国内镜像加速：**

将以下内容写入 `%USERPROFILE%\.cargo\config.toml`（Linux/macOS 为 `~/.cargo/config.toml`）：

```toml
[source.crates-io]
replace-with = 'rsproxy-sparse'

[source.rsproxy-sparse]
registry = 'sparse+https://rsproxy.cn/index/'
```

**注意事项：**

- 安装过程中会提示确认，输入 `Y` 继续
- 安装完成后**重开终端**使 PATH 生效

### 1.3 验证安装

安装完成后，在终端中运行以下命令验证安装：

```bash
rustc --version
cargo --version
```

如果显示版本号，说明安装成功！

## 2. 规范创建项目和调试

### 2.1 创建项目

**步骤：**

1. 在文件资源管理器中，右键点击任意目录
2. 选择"新建" → "文件夹"，创建一个文件夹，例如 `my_project`
3. 使用 VSCode 打开 `my_project` 文件夹
4. 点击顶部菜单"终端" → "新建终端"
5. 在终端中输入以下命令创建 Rust 项目：

```bash
cargo init
```

### 2.2 常用命令

**编译与运行：**

```bash
cargo run      # 编译并运行（开发阶段最常用）
cargo check    # 只做类型检查，不生成二进制（速度最快）
cargo build    # 编译，产物在 target/debug/
cargo build --release  # 优化编译，产物在 target/release/
```

**代码质量：**

```bash
cargo fmt      # 自动格式化（类似 Python 的 ruff format）
cargo clippy   # 静态检查与惯用法建议（类似 Python 的 ruff check）
```

### 2.3 调试代码

**设置调试配置：**

1. 安装好 CodeLLDB 插件后，点击左侧"运行和调试"图标
2. 点击"创建 launch.json"，选择 `LLDB` → `Cargo: launch`
3. 也可以直接用本目录 `.vscode/launch.json` 中的现成配置

**设置断点：**

- 在代码行号的左侧点击，设置断点（红色圆点）
- 按 `F5` 启动调试，程序会在断点处暂停

### 2.4 创建示例代码

示例代码已按 PPT 页拆分为多个独立模块（见本目录 `src/`），每个模块既是被 `main.rs` 引用的模块，也是可独立运行的二进制：

- `basic_types.rs` / `basic_operators.rs` — 变量、数据类型与运算符
- `control_flow.rs` — 条件与循环
- `data_structures.rs` — 数组、Vec、元组、HashMap、HashSet
- `functions.rs` — 函数定义、参数与闭包
- `ownership.rs` — 所有权、借用与切片（Rust 特有）
- `structs_traits.rs` — 结构体、impl 与 trait
- `enums_matching.rs` — 枚举、Option 与模式匹配
- `error_handling.rs` — panic!、Result 与 ? 运算符
- `async_example.rs` — tokio 异步编程
- `logging_example.rs` — tracing 日志
- `serde_example.rs` — serde 数据模型

运行方式：

```bash
# 一次性执行所有示例
cargo run

# 单独运行某个示例（每个模块都是独立二进制）
cargo run --bin basic_types
cargo run --bin ownership
cargo run --bin async_example

# 查看 debug 级别日志
RUST_LOG=debug cargo run --bin logging_example
```
