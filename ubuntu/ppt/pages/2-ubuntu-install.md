---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">🖥️ Ubuntu 服务器安装</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">BIOS 设置启动顺序</h3>

1. 插入启动U盘
2. 开机按 Del/F2 进入 BIOS
3. 将 USB 设备设为第一启动项
4. 保存并重启

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">📦 安装步骤</h3>

**语言选择：** 选择 English（推荐）

**网络配置：** 连接网线，自动获取 IP

**磁盘分区：** 使用整个磁盘

**创建用户：** 设置用户名和密码

**安装完成：** 取出U盘，重启系统

</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-6">⚙️ 安装选项</h3>

| 选项 | 推荐 |
|------|------|
| 语言 | English |
| 键盘 | Chinese |
| 分区 | 使用整个磁盘 |
| 安装类型 | Ubuntu Server |
| 启用 SSH | 是（必选）|

<h3 class="text-xl font-semibold mb-4 mt-10">🌐 SSH 远程连接</h3>

安装完成后，通过 SSH 登录：

```bash
ssh username@server-ip
```

<h3 class="text-xl font-semibold mb-4 mt-10">📋 首次登录操作</h3>

```bash
# 更新软件源
sudo apt update && sudo apt upgrade -y

# 查看 IP
ip addr show
```

</div>

<div class="mt-8 p-5 bg-green-500/10 border-l-4 border-green-500 rounded-lg">
✅ Ubuntu Server 24.04 支持周期至 2029 年，无需频繁升级。
</div>
