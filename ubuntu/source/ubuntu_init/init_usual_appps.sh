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

# ================= 环境配置与安装 =================

# 更新系统软件包索引
echo "Updating package index..."
sudo apt update -y

# --- 安装基础工具 ---
echo "Installing basic tools..."
sudo apt install -y \
    vim git curl wget net-tools htop tree unzip zip \
    build-essential software-properties-common

# --- 安装 Docker (采用官方一键脚本) ---
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    # 支持通过环境变量 DOCKER_MIRROR=Aliyun 启用国内镜像加速安装
    MIRROR_ARG=""
    if [[ "${DOCKER_MIRROR:-}" == "Aliyun" ]]; then
        MIRROR_ARG="-s docker --mirror Aliyun"
    fi
    
    # 执行官方安装脚本 (自动包含 docker-compose-plugin)
    curl -fsSL https://get.docker.com | sudo sh $MIRROR_ARG
    
    # 添加当前用户到 docker 组，避免每次使用 sudo
    sudo usermod -aG docker "$USER"
    echo "✅ 提示: 已将当前用户加入 docker 组。请重新登录或执行 'newgrp docker' 使权限生效。"
else
    echo "Docker is already installed."
fi

# --- WSL2 环境特殊处理 ---
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "检测到 WSL2 环境，配置 Docker 自动启动..."
    if ! grep -q "sudo service docker start" ~/.bashrc; then
        echo 'sudo service docker start 2>/dev/null' >> ~/.bashrc
    fi
    sudo service docker start 2>/dev/null || true
else
    sudo systemctl enable docker 2>/dev/null || true
    sudo systemctl start docker 2>/dev/null || true
fi

# --- 配置 Docker 国内镜像加速 ---
MIRRORS="${DOCKER_MIRRORS:-https://docker.1ms.run,https://docker.xuanyuan.me}"
if [[ "$MIRRORS" != "none" && -n "$MIRRORS" ]]; then
    echo "配置 Docker 镜像加速..."
    sudo mkdir -p /etc/docker
    
    # 使用 python3 生成 JSON 确保格式绝对正确
    python3 -c "import json, sys; print(json.dumps({'registry-mirrors': sys.argv[1].split(',')}))" "$MIRRORS" \
        | sudo tee /etc/docker/daemon.json > /dev/null
    
    if grep -qi microsoft /proc/version 2>/dev/null; then
        sudo service docker restart 2>/dev/null || true
    else
        sudo systemctl restart docker 2>/dev/null || true
    fi
    echo "✅ Docker 镜像加速配置完成。"
fi
