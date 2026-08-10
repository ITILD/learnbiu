# Python 快速入门

欢迎来到 Python 快速入门教程！本教程将引导您完成 Python 开发环境的搭建和基础学习。

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
   - **Python** - Microsoft 官方 Python 支持
   - **Chinese (Simplified) Language Pack** - 中文语言包（可选）
   - **Ruff** - 快速 Python 代码格式化工具

### 1.2 安装开发依赖（Python 版本及依赖管理器）

**安装 uv（现代 Python 包管理器）：**

1. 按 `Win + R` 键，输入 `powershell` 并回车
2. 在 PowerShell 中执行以下命令：

```bash
winget install --id=astral-sh.uv -e
```

**注意事项：**

- 安装过程中会提示确认，输入 `Y` 继续
- 如果下载遇到问题，可能需要切换网络或使用科学上网工具

### 1.3 验证安装

安装完成后，在 PowerShell 中运行以下命令验证安装：

```bash
uv --version
```

如果显示版本号，说明安装成功！

## 2. 规范创建项目和调试

### 2.1 创建项目

**步骤：**

1. 在文件资源管理器中，右键点击任意目录
2. 选择"新建" → "文件夹"，创建一个文件夹，例如 `my_project`
3. 使用 VSCode 打开 `my_project` 文件夹
4. 点击顶部菜单"终端" → "新建终端"
5. 在终端中输入以下命令创建空的 Python 项目：

```bash
uv init
```

### 2.2 配置开发环境

**同步依赖：**

在项目终端中运行以下命令下载 Python 和项目依赖：

```bash
uv sync
```

**配置 Python 解释器：**

1. 打开 `main.py` 文件
2. 点击 VSCode 右下角的 Python 解释器选择器
3. 选择 `.venv` 目录下的 `python.exe`

### 2.3 调试代码

**设置调试配置：**

1. 点击右上角的运行按钮的下拉菜单
2. 选择 "Debug Python File" 或创建调试配置

**设置断点：**

- 在代码行号的左侧点击，设置断点（红色圆点）
- 按 `F5` 启动调试，程序会在断点处暂停

### 2.4 创建示例代码

示例代码已按 PPT 页拆分为多个独立模块（见 `python/source/` 目录）：

- `basic_types.py` / `basic_operators.py` — 变量、数据类型与运算符
- `control_flow.py` — 条件与循环
- `data_structures.py` — 列表、元组、字典、集合
- `functions.py` — 函数定义与参数
- `classes.py` — 类与继承
- `exceptions.py` — 异常处理
- `async_example.py` — 异步编程
- `logging_example.py` — 日志模块
- `pydantic_example.py` — Pydantic 数据模型

可单独运行任一模块，或运行 `main.py` 一次性执行所有示例：

```bash
uv run main.py
```