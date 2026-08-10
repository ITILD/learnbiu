---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">🐧 WSL2 简介与安装</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">什么是 WSL2？</h3>

Windows Subsystem for Linux 2，在 Windows 上运行完整的 Linux 内核：

- 无需传统虚拟机，启动快、占用低
- 与 Windows 文件系统互通
- 支持 GPU 加速、网络互通
- 适合开发、服务器模拟等场景
</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">📥 启用 WSL2</h3>

以**管理员身份**打开 PowerShell：

```powershell
# 启用 WSL 功能
dism.exe /online /enable-feature ^
  /featurename:Microsoft-Windows-Subsystem-Linux ^
  /all /norestart

# 启用虚拟机平台
dism.exe /online /enable-feature ^
  /featurename:VirtualMachinePlatform ^
  /all /norestart
```

**重启电脑**后生效！
</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-6">⚙️ 设置 WSL2 为默认版本</h3>

```powershell
wsl --set-default-version 2
```

<h3 class="text-xl font-semibold mb-4 mt-10">🔄 更新 WSL 内核</h3>

```powershell
wsl --update
```

<h3 class="text-xl font-semibold mb-4 mt-10">📋 常用 WSL 命令</h3>

| 命令 | 说明 |
|------|------|
| `wsl -l -v` | 查看已安装发行版 |
| `wsl --shutdown` | 关闭所有 WSL |
| `wsl -d <名称>` | 启动指定发行版 |
| `wsl --set-version <名> 2` | 切换版本 |
</div>

<div class="mt-8 p-5 bg-blue-500/10 border-l-4 border-blue-500 rounded-lg">
💡 <b>提示：</b>Windows 10 2004+ 或 Windows 11 自带 WSL2 支持。
</div>