---
layout: two-cols
layoutClass: gap-8 compact
class: text-sm
---

# 创建项目并运行

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
<b>uv</b> 是 Python 的“管家”：自动下载 Python、创建虚拟环境、安装依赖、运行程序。
</div>

## 1. 安装 uv

```bash
# Windows
winget install --id=astral-sh.uv -e

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

验证：`uv --version`

## 2. 创建项目

在 VSCode 中打开新文件夹，在终端执行：

```bash
uv init     # 创建 Python 项目
uv sync     # 下载 Python 并创建 .venv
```

## 3. 第一个程序

```python
# main.py
print("Hello, Python!")
```

::right::

## 4. 运行

```bash
uv run main.py
```

看到 `Hello, Python!` 就成功了。

## 跑本教程的示例

示例代码在 `python/source/`，按 PPT 页拆分：

```bash
uv run main.py            # 一次跑全部示例
uv run basic_types.py     # 只跑某一页的示例
```

每页 PPT 底部都标注了对应的示例文件。

## 在 VSCode 里

1. 右下角选择解释器：`.venv` 里的 Python
2. 打开文件，点右上角 ▶ 运行，或按 `F5` 调试
3. 在行号左侧点击可设置**断点**

<div class="mt-3 p-3 bg-emerald-500/10 border-l-4 border-emerald-500 rounded text-sm">
uv 自动处理 Python 版本和虚拟环境，不用手动配 PATH，也不容易把环境装乱。
</div>
