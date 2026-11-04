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
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("程序启动")
logging.warning("磁盘空间不足")
```

输出：

```text
2026-11-04 10:00:00 - INFO - 程序启动
2026-11-04 10:00:00 - WARNING - 磁盘空间不足
```

::right::

## 五个日志级别

```python
logging.debug("调试细节")      # 最低
logging.info("正常信息")
logging.warning("警告")
logging.error("错误")
logging.critical("严重错误")   # 最高
```

设置 `level=logging.INFO` 后，只会输出 **INFO 及以上** 的日志；`DEBUG` 会被过滤掉。

## print 的三个局限

- 分不清普通信息和严重错误
- 输出格式无法统一
- 不能直接按级别写文件

<div class="mt-3 p-2 bg-cyan-500/10 border-l-4 border-cyan-500 rounded text-sm">
上线后的程序不要用 <code>print</code> 调试；用 logging 才能按级别过滤、写文件、排查历史问题。
</div>
