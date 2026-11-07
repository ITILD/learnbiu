---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# 异步编程：别干等

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
生活类比：点 3 道菜各要 1 分钟，餐厅<b>不会做完一道再做下一道</b>，而是三口锅同时开火。
</div>

## 同步 vs 异步

| 方式 | 执行方式 | 3 个 1 秒任务的总耗时 |
|------|----------|------------------------|
| 同步 | 排队，一件一件做 | 约 3 秒 |
| 异步 | 等待时去做别的 | 约 1 秒 |

## 什么时候用？

- 适合：网络请求、文件读写、数据库查询（**等待多**）
- 不适合：纯计算任务（用它不会变快）

<div class="mt-3 p-2 bg-pink-500/10 border-l-4 border-pink-500 rounded text-xs">
异步的核心不是“更快”，而是“别让 CPU 干等”。
</div>

::right::

## 代码示例（点餐上菜）

```python
import asyncio

async def order_and_serve(dish_name: str, prepare_time: int):
    await asyncio.sleep(prepare_time)   # 模拟做菜等待
    print(f"{dish_name} 已准备完成！")

async def async_example():
    await asyncio.gather(               # 三道菜同时做
        order_and_serve("鱼香肉丝", 1),
        order_and_serve("红烧肉", 1),
        order_and_serve("青椒肉丝", 1),
    )

asyncio.run(async_example())   # 总耗时约 1 秒
```

## 四个关键词

- `async def`：定义协程函数
- `await`：等待，并把控制权让出去
- `asyncio.gather()`：并发执行多个协程
- `asyncio.run()`：启动顶层协程

<div class="mt-2 text-xs opacity-50">
对应示例：source/async_example.py · <code>uv run async_example.py</code>
</div>
