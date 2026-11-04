---
layout: default
class: text-sm
title: 计算机基础：代码如何运行
---

# 计算机基础①：代码是怎么跑起来的？

<div class="mt-2 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded">
CPU 只认识 <b>0 和 1</b>。Python 代码要先被“翻译”，CPU 才能执行。
</div>

<div class="mt-4 flex items-center gap-1 text-center">
<div class="flex-1 rounded-lg border border-blue-400/30 bg-blue-500/10 p-2">
<div class="text-xs opacity-50">你写的</div>
<div class="mt-1 font-bold">main.py</div>
<div class="mt-1 text-xs opacity-60">源代码</div>
</div>
<div class="opacity-40">→</div>
<div class="flex-1 rounded-lg border border-purple-400/30 bg-purple-500/10 p-2">
<div class="text-xs opacity-50">翻译</div>
<div class="mt-1 font-bold">Python 解释器</div>
<div class="mt-1 text-xs opacity-60">源码 → 字节码</div>
</div>
<div class="opacity-40">→</div>
<div class="flex-1 rounded-lg border border-amber-400/30 bg-amber-500/10 p-2">
<div class="text-xs opacity-50">中间语言</div>
<div class="mt-1 font-bold">字节码 .pyc</div>
<div class="mt-1 text-xs opacity-60">跨平台的“半成品”</div>
</div>
<div class="opacity-40">→</div>
<div class="flex-1 rounded-lg border border-emerald-400/30 bg-emerald-500/10 p-2">
<div class="text-xs opacity-50">执行</div>
<div class="mt-1 font-bold">Python 虚拟机</div>
<div class="mt-1 text-xs opacity-60">逐条执行字节码</div>
</div>
<div class="opacity-40">→</div>
<div class="flex-1 rounded-lg border border-zinc-400/30 bg-zinc-500/10 p-2">
<div class="text-xs opacity-50">真正干活</div>
<div class="mt-1 font-bold">CPU / 操作系统</div>
<div class="mt-1 text-xs opacity-60">结果 → 屏幕</div>
</div>
</div>

<div class="grid grid-cols-2 gap-8 mt-4">

<div>

## 按下“运行”后

1. 解释器读取 `main.py`
2. 源码先编译成**字节码**
3. 虚拟机逐条执行字节码
4. 需要时调用系统：打印、读写文件、联网
5. 出错就抛**异常**，在终端显示报错

</div>

<div>

## 编译型 vs 解释型

| | 编译型（C / Go） | 解释型（Python） |
|---|---|---|
| 翻译时机 | 运行前一次性 | 运行时边翻译边执行 |
| 速度 | 快 | 较慢一些 |
| 跨平台 | 每个平台重新编译 | 装好解释器即可 |

</div>

</div>

<div class="mt-2 text-xs opacity-60">
一句话：Python 不是“不编译”，而是<b>先编译成字节码，再解释执行</b>，所以既跨平台又方便调试。
</div>
