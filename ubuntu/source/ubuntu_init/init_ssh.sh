#!/bin/bash
# 开启严格模式：任何命令执行失败或变量未定义时，立即退出脚本
set -euo pipefail

CURRENT_USER_PASSWORD="qwer1234"
NEW_ROOT_PASSWORD="qwer1234"

# 1. 初始验证密码，获取 sudo 权限并建立缓存
echo "${CURRENT_USER_PASSWORD}" | sudo -S -v > /dev/null 2>&1

# 2. 启动后台 Keep-Alive 进程，每 50 秒刷新一次 sudo 时间戳
(
  while true; do
    echo "${CURRENT_USER_PASSWORD}" | sudo -S -v > /dev/null 2>&1
    sleep 50
  done
) &
# 记录后台进程 PID
SUDO_KEEP_ALIVE_PID=$!

# 3. 定义清理函数：确保脚本结束时彻底关闭后台进程并回收资源
cleanup() {
    # 强制杀死后台 Keep-Alive 进程 (使用 -9 确保在 sleep 期间也能立即终止)
    kill -9 $SUDO_KEEP_ALIVE_PID 2>/dev/null || true
    # 等待进程真正退出，防止产生僵尸进程
    wait $SUDO_KEEP_ALIVE_PID 2>/dev/null || true
}

# 4. 注册 Trap：捕获退出(EXIT)、中断(INT/Ctrl+C)、终止(TERM)信号
trap cleanup EXIT INT TERM

# --- 后续命令无需再传递密码，且权限永不过期 ---

# 检测 root 密码状态，若未设置则进行配置
ROOT_STATUS=$(sudo passwd -S root 2>/dev/null | awk '{print $2}')
if [[ "$ROOT_STATUS" != "P" ]]; then
    sudo bash -c "echo 'root:${NEW_ROOT_PASSWORD}' | chpasswd"
fi

# 配置阿里软件源并更新系统索引
sudo tee /etc/apt/sources.list > /dev/null <<EOF
deb https://mirrors.aliyun.com/ubuntu/ noble main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ noble-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ noble-backports main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ noble-security main restricted universe multiverse
EOF
sudo apt update -y

# 安装 OpenSSH 服务端组件 (已修正原代码中的笔误)
sudo apt install -y openssh-server

# 修改 SSH 配置，允许 root 用户通过密码登录
sudo mkdir -p /etc/ssh/sshd_config.d
cat <<'SSH_EOF' | sudo tee /etc/ssh/sshd_config.d/99-custom-ssh.conf > /dev/null
PermitRootLogin yes
PasswordAuthentication yes
SSH_EOF

# 重启并启用 SSH 服务
sudo systemctl restart ssh
sudo systemctl enable ssh

# 验证 SSH 服务是否真正启动成功
if systemctl is-active --quiet ssh; then
    echo "Success: All operations completed and SSH is running."
else
    echo "Error: SSH service failed to start."
    exit 1
fi

echo "Success: All operations completed."
# 脚本执行到此处后，将自动触发 EXIT 信号，执行 cleanup 函数关闭后台进程