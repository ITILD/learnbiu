---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">🦁 安装 Ubuntu 24.04</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">📥 在线安装（推荐）</h3>

```powershell
# 查看可用发行版
wsl --list --online

# 安装 Ubuntu 24.04
wsl --install -d Ubuntu-24.04
```

首次启动会提示创建用户名和密码。
</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">📦 离线安装</h3>

1. 下载 Ubuntu 24.04 的 `.AppxBundle` 包
2. 使用 `Add-AppxPackage` 安装
3. 从开始菜单启动 Ubuntu

```powershell
Add-AppxPackage .\Ubuntu_2404.AppxBundle
```
</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-6">🔧 初始化配置</h3>

进入 Ubuntu 后，更新系统：

```bash
sudo apt update && sudo apt upgrade -y
```

<h3 class="text-xl font-semibold mb-4 mt-10">🌐 网络验证</h3>

```bash
# 查看 IP 地址
ip addr show

# 测试网络连通性
ping -c 4 baidu.com
```
<!-- 代理 https://ottercoconut.github.io/p/%E5%A6%82%E4%BD%95%E5%9C%A8wsl2%E4%B8%8A%E4%BD%BF%E7%94%A8%E6%9C%AC%E6%9C%BA%E4%BB%A3%E7%90%86/ -->

<h3 class="text-xl font-semibold mb-4 mt-10">📁 文件互通</h3>

| 路径 | 说明 |
|------|------|
| `/mnt/c/` | 访问 Windows C 盘 |
| `\\wsl$\` | Windows 访问 WSL 文件 |
| `explorer.exe .` | 在 WSL 中打开资源管理器 |
</div>

<div class="mt-8 p-5 bg-green-500/10 border-l-4 border-green-500 rounded-lg">
✅ Ubuntu 24.04 是当前最新的 LTS 版本，支持周期至 2029 年。
</div>