# Welcome to [Slidev](https://github.com/slidevjs/slidev)!

To start the slide show:

- `pnpm install`
- `pnpm run dev`
- visit <http://localhost:50004>

Edit the [slides.md](./slides.md) to see the changes.

# export


pnpm exec playwright install chromium


## 📊 PPT 结构总览

### 第一部分：环境搭建（2页）

| 文件 | 内容 |
|------|------|
| [1-env-vscode.md](pages/1-env-vscode.md) | VSCode 安装、必备插件（rust-analyzer/CodeLLDB/TOML） |
| [1-env-cargo.md](pages/1-env-cargo.md) | rustup 安装、cargo 项目创建、常用命令、调试方法 |

### 第二部分：基础语法（10页）

| 文件 | 内容 |
|------|------|
| [2-basic-types.md](pages/2-basic-types.md) | let 与可变性、基本类型、类型转换、格式化输出 |
| [2-basic-operators.md](pages/2-basic-operators.md) | 算术/比较/逻辑/位运算符、溢出保护 |
| [2-control-flow.md](pages/2-control-flow.md) | if/else、loop/while/for、break/continue、循环标签 |
| [2-data-structures.md](pages/2-data-structures.md) | 数组/Vec/元组/HashMap/HashSet 五种核心数据结构 |
| [2-functions.md](pages/2-functions.md) | 函数定义、参数差异、闭包、迭代器链 |
| [2-ownership.md](pages/2-ownership.md) | 所有权三大规则、Move/Clone、引用与借用 |
| [2-structs-traits.md](pages/2-structs-traits.md) | struct/impl、trait、组合替代继承、多态 |
| [2-enums-matching.md](pages/2-enums-matching.md) | 携带数据的枚举、Option、match、if let |
| [2-error-handling.md](pages/2-error-handling.md) | panic!/Result/? 运算符、处理方法、流程图 |
| [2-async.md](pages/2-async.md) | tokio 异步编程、同步vs异步对比、与 asyncio 对照 |

### 第三部分：进阶技巧（2页）

| 文件 | 内容 |
|------|------|
| [3-logging.md](pages/3-logging.md) | tracing 五级日志、结构化日志、级别过滤 |
| [3-serde.md](pages/3-serde.md) | serde 数据模型、HashMap 对比、序列化校验 |

---

**共计 14 个内容页面**，全部采用 `two-cols` 双栏布局，包含代码示例、Mermaid 图表和知识点提示框。主文件 [slides.md](slides.md) 已更新，按三大部分组织引用。

配套源码见 `../source/`，每个 PPT 页对应一个可独立运行的示例模块（`cargo run --bin basic_types`）。
