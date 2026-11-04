---
layout: two-cols
layoutClass: gap-8
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

```bash
uv init hello-python
cd hello-python
uv sync
```

::right::

## 3. 第一个程序

```python
# main.py
print("Hello, Python!")
```

## 4. 运行

```bash
uv run main.py
```

看到 `Hello, Python!` 就成功了。

## 在 VSCode 里

1. **文件 → 打开文件夹**，选中 `hello-python`
2. 右下角选择解释器：`.venv` 里的 Python
3. 打开 `main.py`，点右上角 ▶ 或按 `F5`
4. 在下方“终端”查看输出

<div class="mt-4 p-3 bg-emerald-500/10 border-l-4 border-emerald-500 rounded text-sm">
uv 会自动处理 Python 版本和虚拟环境，初学者不用手动配 PATH，也不容易把环境装乱。
</div>
