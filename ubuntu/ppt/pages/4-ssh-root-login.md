---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">🔗 SSH 远程 Root 登录</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">什么是 SSH？</h3>

Secure Shell，安全的远程登录协议：

- 加密传输数据
- 支持密码和密钥认证
- 标准端口：22
- 服务器管理必备

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">🔧 启用 Root SSH 登录</h3>

**步骤 1：设置 root 密码**

```bash
sudo passwd root
```

**步骤 2：修改 SSH 配置**

```bash
sudo nano /etc/ssh/sshd_config
```

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">🔑 关键配置项</h3>

```bash
# 允许 root 登录
PermitRootLogin yes

# 允许密码登录（如需）
PasswordAuthentication yes

# 监听端口（默认 22）
Port 22
```

</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-6">🚀 重启 SSH 服务</h3>

```bash
# 重启服务
sudo systemctl restart sshd

# 查看状态
sudo systemctl status sshd
```

<h3 class="text-xl font-semibold mb-4 mt-10">💻 远程连接方式</h3>

**Windows PowerShell：**

```powershell
ssh root@服务器IP地址
```

**Xshell / SecureCRT：**

- 协议：SSH
- 主机：服务器 IP
- 端口：22
- 用户名：root

<h3 class="text-xl font-semibold mb-4 mt-10">🛡️ 安全加固建议</h3>

| 措施 | 命令/配置 |
|------|-----------|
| 修改默认端口 | `Port 2222` |
| 禁用密码登录 | `PasswordAuthentication no` |
| 限制登录用户 | `AllowUsers root` |
| 启用防火墙 | `ufw allow 22` |

</div>

<div class="mt-8 p-5 bg-yellow-500/10 border-l-4 border-yellow-500 rounded-lg">
⚠️ <b>注意：</b>生产环境建议使用 SSH 密钥登录，避免使用密码。
</div>
