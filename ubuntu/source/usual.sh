以下整理了 Ubuntu 系统运维与开发中最高频使用的命令示例，按功能场景分类，兼顾新语法与简洁注释风格。

### 1. 系统与硬件信息
```bash
# 查看系统版本与内核
lsb_release -a && uname -r

# 实时监控资源（推荐btop替代top）
sudo apt install btop && btop

# 查看磁盘使用（人类可读格式）
df -hT | grep -v tmpfs

# 查看内存详情（含缓存/交换区）
free -h

# 列出PCI设备（常用于显卡/网卡排查）
lspci -knn | grep -E "VGA|3D|Net"
```

### 2. 软件包管理 (APT)
```bash
# 更新源并升级已安装包
sudo apt update && sudo apt upgrade -y

# 搜索软件包
apt search <keyword>

# 安装指定版本
sudo apt install <pkg>=<version>

# 清理无用依赖与缓存
sudo apt autoremove --purge && sudo apt clean

# 查看已安装包列表
dpkg -l | grep <keyword>
```

### 3. 服务与进程管理 (Systemd)
```bash
# 查看服务状态（含日志摘要）
systemctl status <service> --no-pager

# 重启服务并立即查看日志
sudo systemctl restart <service> && journalctl -u <service> -f

# 列出所有失败的服务
systemctl --failed

# 查找占用端口的进程
sudo ss -tulnp | grep :<port>

# 按名称终止进程树
pkill -f "<process_pattern>"
```

### 4. 文件与文本处理
```bash
# 递归查找文件（按名称/大小/时间）
find /path -name "*.log" -size +100M -mtime -7

# 实时追踪日志（支持通配符）
tail -F /var/log/*.log

# 统计文件行数/单词数/字节数
wc -lwm <file>

# 批量替换文件内容（sed原地修改）
sed -i 's/old/new/g' <file>

# 压缩/解压tar.gz
tar -czvf archive.tar.gz /path/to/dir
tar -xzvf archive.tar.gz -C /target/dir
```

### 5. 网络诊断
```bash
# 测试连通性与DNS解析
ping -c 4 <host> && dig +short <domain>

# 查看路由表
ip route show

# 抓包分析（指定接口与端口）
sudo tcpdump -i eth0 port 443 -w capture.pcap

# 下载文件（断点续传+进度条）
wget -c --progress=bar:force <url>

# 查看当前活跃连接
ss -s
```

### 6. Python 开发相关（贴合您的偏好）
```bash
# 创建虚拟环境（新语法，无需typing）
python3 -m venv .venv && source .venv/bin/activate

# 安装依赖并导出锁定版本
pip install -r requirements.txt && pip freeze > requirements.lock

# 运行脚本前检查语法
python3 -m py_compile script.py

# 查看已安装包及版本
pip list --format=columns
```

### 💡 高效技巧备注
-   **历史搜索**：`Ctrl+R` 反向搜索历史命令，比反复按上箭头快10倍。
-   **管道组合**：善用 `|` + `grep/awk/sort/uniq` 链式处理，避免写临时脚本。
-   **别名简化**：在 `~/.bashrc` 中添加 `alias ll='ls -alFh --color=auto'` 等高频缩写。
-   **安全操作**：删除/修改前先用 `echo` 或 `dry-run` 验证目标范围，尤其涉及通配符时。

> 以上命令均基于 Ubuntu 22.04/24.04 LTS 验证，兼容主流衍生发行版。如需特定场景深度用法（如 Docker/K8s/NVIDIA 驱动调试），可进一步说明需求。