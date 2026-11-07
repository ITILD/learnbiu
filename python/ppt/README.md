# Welcome to [Slidev](https://github.com/slidevjs/slidev)!

To start the slide show:

- `pnpm install`
- `pnpm run dev`
- visit <http://localhost:3030>

Edit the [slides.md](./slides.md) to see the changes.

# export


pnpm exec playwright install chromium


## 📊 PPT 结构总览

### 与教程源码的对应关系

每页 PPT 的代码示例与 `python/source/` 中的教程源码一一对应（变量名、示例数据、输出注释保持一致），页面底部标注了对应文件和运行命令；也可用 `uv run main.py` 一次跑全部示例：

| PPT 页 | 源码文件 |
|--------|----------|
| 2-basic-types.md | source/basic_types.py |
| 2-basic-operators.md | source/basic_operators.py |
| 2-control-flow.md | source/control_flow.py |
| 2-data-structures.md | source/data_structures.py |
| 2-functions.md | source/functions.py |
| 2-classes.md | source/classes.py |
| 2-exceptions.md | source/exceptions.py |
| 2-async.md | source/async_example.py |
| 3-logging.md | source/logging_example.py |
| 3-pydantic.md | source/pydantic_example.py |

### 第零部分：计算机基础（2页）

| 文件 | 内容 |
|------|------|
| [0-how-code-runs.md](pages/0-how-code-runs.md) | 源码 → 解释器 → 字节码 → 虚拟机的执行流程，编译型 vs 解释型 |
| [0-ide-interpreter.md](pages/0-ide-interpreter.md) | 解释器、IDE、终端分别是什么，它们如何配合，虚拟环境与常见报错 |

### 第一部分：环境搭建（2页）

| 文件 | 内容 |
|------|------|
| [1-env-vscode.md](pages/1-env-vscode.md) | VSCode 安装、必备插件（Python/Ruff/中文包） |
| [1-env-uv.md](pages/1-env-uv.md) | uv 安装、项目创建、第一个程序、运行与调试 |

### 第二部分：基础语法（8页）

| 文件 | 内容 |
|------|------|
| [2-basic-types.md](pages/2-basic-types.md) | 四种基本类型、类型注解、类型转换、f-string |
| [2-basic-operators.md](pages/2-basic-operators.md) | 算术/比较/逻辑/赋值运算符 |
| [2-control-flow.md](pages/2-control-flow.md) | if/elif/else、for/while 循环、break/continue |
| [2-data-structures.md](pages/2-data-structures.md) | list/tuple/dict/set，重点讲 list 与 dict |
| [2-functions.md](pages/2-functions.md) | 函数定义、默认参数、*args/**kwargs、多返回值 |
| [2-classes.md](pages/2-classes.md) | 类定义、继承、super()、面向对象核心概念 |
| [2-exceptions.md](pages/2-exceptions.md) | try/except/else/finally、常见异常、执行流程图 |
| [2-async.md](pages/2-async.md) | 同步 vs 异步、asyncio 基本用法、适用场景 |

### 第三部分：进阶技巧（2页）

| 文件 | 内容 |
|------|------|
| [3-logging.md](pages/3-logging.md) | logging 五级日志、级别过滤、替代 print 的优势 |
| [3-pydantic.md](pages/3-pydantic.md) | Pydantic 数据模型、dict 对比、类型安全优势 |

---

**共计 14 个内容页面（17 张幻灯片）**，面向零基础初学者：每页一个核心概念，代码示例尽量短，配合生活类比、提示框和对比表。主文件 [slides.md](slides.md) 按四大部分组织引用。