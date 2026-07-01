---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">🔐 Root 用户配置</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">为什么需要 Root？</h3>

Ubuntu 默认禁用 root 账户，服务器管理需要：

- 系统级文件操作
- 软件安装与配置
- 服务端口绑定（< 1024）

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">🔧 设置 Root 密码</h3>

```bash
# 设置 root 密码
sudo passwd root

# 输入新密码并确认

# 切换到 root
su
```

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">🚪 切换用户</h3>

```bash
# 从普通用户切换到 root
sudo -i

# 从 root 切换到普通用户
su - username

# 查看当前用户
whoami

# 查看用户 ID
id
```

</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-4">📝 sudo 权限管理</h3>

**查看 sudo 配置：**

```bash
# 编辑 sudoers 文件
sudo visudo

# 允许用户无需密码执行 sudo
username ALL=(ALL) NOPASSWD:ALL
```

<h3 class="text-xl font-semibold mb-4 mt-10">⚠️ 安全加固建议</h3>

| 建议 | 说明 |
|------|------|
| 强密码 | 至少 12 位，包含特殊字符 |
| 禁用直接登录 | 建议使用普通用户 + sudo |
| 限制 sudo 用户 | 仅授权必要用户 |
| 定期检查 | 审计 sudo 操作日志 |

<h3 class="text-xl font-semibold mb-4 mt-10">📊 用户管理命令</h3>

```bash
# 添加用户
sudo useradd -m username

# 设置密码
sudo passwd username

# 添加到 sudo 组
sudo usermod -aG sudo username

# 删除用户
sudo userdel -r username
```

</div>

<div class="mt-8 p-5 bg-yellow-500/10 border-l-4 border-yellow-500 rounded-lg">
⚠️ <b>注意：</b>直接使用 root 存在风险，生产环境建议使用普通用户 + sudo。
</div>
