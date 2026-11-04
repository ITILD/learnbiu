---
layout: default
class: text-sm
title: IDE、解释器与终端
---

# 计算机基础②：IDE、解释器、终端是什么？

<div class="grid grid-cols-3 gap-3 mt-3">

<div class="rounded-lg border border-orange-400/30 bg-orange-500/10 p-3">
<div class="text-xl">⚙️</div>
<h3 class="mt-1 text-sm">解释器（Python）</h3>
<p class="mt-1 text-xs opacity-80">真正<b>执行代码</b>的程序。没有它，<code>.py</code> 只是普通文本。</p>
<p class="mt-1 text-xs opacity-60">命令：<code>python</code> / <code>python3</code></p>
</div>

<div class="rounded-lg border border-blue-400/30 bg-blue-500/10 p-3">
<div class="text-xl">🖥️</div>
<h3 class="mt-1 text-sm">IDE（VSCode）</h3>
<p class="mt-1 text-xs opacity-80">写代码的<b>工作台</b>：编辑器 + 终端 + 调试 + 插件。</p>
<p class="mt-1 text-xs opacity-60">不是必须，但能大幅提高效率</p>
</div>

<div class="rounded-lg border border-emerald-400/30 bg-emerald-500/10 p-3">
<div class="text-xl">⌨️</div>
<h3 class="mt-1 text-sm">终端（Terminal）</h3>
<p class="mt-1 text-xs opacity-80">用<b>命令</b>和电脑对话的窗口，程序输出也在这里。</p>
<p class="mt-1 text-xs opacity-60"><code>python main.py</code></p>
</div>

</div>

## 它们怎么配合？

<div class="mt-2 flex items-center justify-center gap-2 text-center text-xs">
<div class="rounded-lg border border-white/15 bg-white/5 px-3 py-2">
你在 <b>IDE</b> 里写<br/><code>main.py</code>
</div>
<div class="opacity-40 text-base">→</div>
<div class="rounded-lg border border-white/15 bg-white/5 px-3 py-2">
在 <b>终端</b>输入<br/><code>python main.py</code>
</div>
<div class="opacity-40 text-base">→</div>
<div class="rounded-lg border border-white/15 bg-white/5 px-3 py-2">
<b>解释器</b>执行代码<br/>并输出结果
</div>
</div>

<div class="grid grid-cols-2 gap-4 mt-4 text-xs">

<div class="p-3 bg-purple-500/10 border-l-4 border-purple-500 rounded">
<b>.venv 虚拟环境：</b>给每个项目一个独立的“工具箱”，不同项目的依赖包不会互相打架。
</div>

<div class="p-3 bg-red-500/10 border-l-4 border-red-500 rounded">
<b>常见报错：</b><code>'python' 不是内部或外部命令</code> → 解释器没装好或没加入 PATH。用 <code>uv run main.py</code> 最省心。
</div>

</div>

<div class="mt-3 text-xs opacity-50 text-center">
VSCode ≠ Python。VSCode 只是编辑器；真正让代码跑起来的，是解释器。
</div>
