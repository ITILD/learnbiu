---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">💾 Rufus 启动盘制作</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">准备工作</h3>

- U盘一个（建议 8GB 以上）
- Ubuntu Server 镜像（.iso 文件）
- Rufus 工具（Windows）

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">📥 下载 Ubuntu Server</h3>

```bash
# 官网下载 Ubuntu Server 24.04 LTS
# https://ubuntu.com/download/server
```

推荐使用 Ubuntu Server 24.04 LTS 版本。
</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">⚠️ 注意事项</h3>

- 制作启动盘会清空U盘所有数据
- 建议使用空白或已备份的U盘
- 确保电脑 USB 接口正常

</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-6">🔧 使用 Rufus 制作</h3>

**步骤 1：** 插入U盘，运行 Rufus

**步骤 2：** 选择U盘设备

**步骤 3：** 点击"选择"加载 Ubuntu ISO

**步骤 4：** 分区方案选择"GPT"

**步骤 5：** 目标系统类型选择"UEFI (non CSM)"

**步骤 6：** 点击"开始"等待完成

<h3 class="text-xl font-semibold mb-4 mt-10">✅ 验证启动盘</h3>

制作完成后，可以在 Rufus 中点击"选中"查看U盘内容，确认 ISO 文件已正确解压。
</div>

<div class="mt-8 p-5 bg-blue-500/10 border-l-4 border-blue-500 rounded-lg">
💡 <b>提示：</b>服务器建议使用 Ubuntu Server 镜像，比桌面版更轻量。
</div>
