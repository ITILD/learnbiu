---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# logging：替代 print

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
<code>print</code> 像随手贴的便签；<code>logging</code> 像一本带时间、级别、来源的正式日志本。
</div>

## 基本配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

name: str = "张三"
logging.info(f"姓名: {name}")       # 正常信息
logging.warning("磁盘空间不足")     # 警告
logging.error("读取文件失败")       # 出错了
logging.debug("调试细节")           # 不会输出：低于 INFO
```

::right::

## 输出效果

```text
2026-11-06 10:00:00 - INFO - 姓名: 张三
2026-11-06 10:00:00 - WARNING - 磁盘空间不足
2026-11-06 10:00:00 - ERROR - 读取文件失败
```

## 五个日志级别

```python
logging.debug("...")       # 最低
logging.info("...")
logging.warning("...")
logging.error("...")
logging.critical("...")    # 最高
```

设置 `level=logging.INFO` 后，只会输出 **INFO 及以上** 的日志；`DEBUG` 被过滤。

<div class="mt-3 p-2 bg-cyan-500/10 border-l-4 border-cyan-500 rounded text-sm">
print 分不清信息轻重、格式不统一、不能按级别写文件。上线后的程序用 logging 排查问题。
</div>

<div class="mt-3 text-xs opacity-50">
对应示例：source/logging_example.py · <code>uv run logging_example.py</code>
</div>
