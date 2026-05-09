# Welcome to [Slidev](https://github.com/slidevjs/slidev)!

To start the slide show:

- `pnpm install`
- `pnpm run dev`
- visit <http://localhost:3030>

Edit the [slides.md](./slides.md) to see the changes.

# export


pnpm exec playwright install chromium


## 📊 PPT 结构总览

### 第一部分：环境搭建（2页）

| 文件 | 内容 |
|------|------|
| [1-env-vscode.md](pages/1-env-vscode.md) | VSCode 安装、必备插件（Python/Ruff/中文包） |
| [1-env-uv.md](pages/1-env-uv.md) | uv 安装、项目创建、解释器配置、调试方法 |

### 第二部分：基础语法（8页）

| 文件 | 内容 |
|------|------|
| [2-basic-types.md](pages/2-basic-types.md) | 四种基本类型、类型注解新语法、f-string |
| [2-basic-operators.md](pages/2-basic-operators.md) | 算术/比较/逻辑/赋值运算符 |
| [2-control-flow.md](pages/2-control-flow.md) | if/elif/else、for/while 循环、break/continue |
| [2-data-structures.md](pages/2-data-structures.md) | list/tuple/dict/set 四种核心数据结构 |
| [2-functions.md](pages/2-functions.md) | 函数定义、默认参数、*args/**kwargs、多返回值 |
| [2-classes.md](pages/2-classes.md) | 类定义、继承、super()、面向对象核心概念 |
| [2-exceptions.md](pages/2-exceptions.md) | try/except/else/finally、常见异常类型、流程图 |
| [2-async.md](pages/2-async.md) | asyncio 异步编程、同步vs异步对比、协程关键字 |

### 第三部分：进阶技巧（2页）

| 文件 | 内容 |
|------|------|
| [3-logging.md](pages/3-logging.md) | logging 五级日志、级别过滤、替代 print 的优势 |
| [3-pydantic.md](pages/3-pydantic.md) | Pydantic 数据模型、dict 对比、类型安全优势 |

---

**共计 12 个新页面**，全部采用 `two-cols` 双栏布局，包含代码示例、Mermaid 图表和知识点提示框。主文件 [slides.md](slides.md) 已更新，按三大部分组织引用。