---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">⌨️ Ubuntu 常用命令</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">📦 软件包管理</h3>

```bash
# 更新软件源
sudo apt update

# 升级已安装软件
sudo apt upgrade -y

# 安装软件
sudo apt install nginx -y

# 卸载软件
sudo apt remove nginx -y

# 搜索软件
apt search nginx
```

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">📁 文件与目录</h3>

```bash
# 进入目录
cd /var/www

# 查看当前目录
pwd

# 列出文件
ls -la

# 创建目录
mkdir project

# 删除文件/目录
rm -rf project
```

</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-4">🔍 系统信息</h3>

```bash
# 查看系统版本
cat /etc/os-release

# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 查看进程
top

# 查看网络连接
ss -tuln
```

<h3 class="text-xl font-semibold mb-4 mt-10">⚙️ 服务管理</h3>

```bash
# 启动服务
sudo systemctl start nginx

# 停止服务
sudo systemctl stop nginx

# 重启服务
sudo systemctl restart nginx

# 查看服务状态
sudo systemctl status nginx

# 设置开机自启
sudo systemctl enable nginx
```

<h3 class="text-xl font-semibold mb-4 mt-10">🌐 防火墙 ufw</h3>

```bash
sudo ufw allow 22    # 开放 SSH
sudo ufw allow 80    # 开放 HTTP
sudo ufw allow 443   # 开放 HTTPS
sudo ufw enable      # 启用防火墙
sudo ufw status      # 查看状态
```

</div>

<div class="mt-8 p-5 bg-blue-500/10 border-l-4 border-blue-500 rounded-lg">
💡 <b>提示：</b>使用 <code>Tab</code> 键自动补全，<code>↑</code> <code>↓</code> 调出历史命令。
</div>
