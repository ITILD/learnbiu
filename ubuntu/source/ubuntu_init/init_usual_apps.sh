#!/bin/bash
# 开启严格模式
set -euo pipefail

CURRENT_USER_PASSWORD="qwer1234"
NEW_ROOT_PASSWORD="qwer1234"

# 1. 初始验证 sudo 权限
printf '%s' "${CURRENT_USER_PASSWORD}" | sudo -S -v > /dev/null 2>&1

# 2. 后台 Keep-Alive 进程
(
  while true; do
    printf '%s' "${CURRENT_USER_PASSWORD}" | sudo -S -v > /dev/null 2>&1
    sleep 50
  done
) &
SUDO_KEEP_ALIVE_PID=$!

# 3. 清理函数
cleanup() {
    kill -9 "$SUDO_KEEP_ALIVE_PID" 2>/dev/null || true
    wait "$SUDO_KEEP_ALIVE_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# ================= 环境配置与安装 =================

echo "Updating package index..."
sudo apt update -y

echo "Installing basic tools..."
sudo apt install -y \
    vim git curl wget net-tools htop tree unzip zip \
    build-essential software-properties-common ca-certificates gnupg lsb-release

# --- 安装 Docker (使用阿里云镜像源) ---
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    # 清理可能残留的旧密钥文件
    sudo rm -f /etc/apt/keyrings/docker.asc /etc/apt/keyrings/docker.gpg
    
    # 添加阿里云 Docker GPG 密钥
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # 添加阿里云 Docker 软件源
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
      $(lsb_release -cs) stable" \
      | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # 更新索引并安装 Docker 全家桶
    sudo apt update -y
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # 将当前用户加入 docker 组
    sudo usermod -aG docker "$USER" || true
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
    
    # 生成 daemon.json（python3 新语法，无需 typing）
    python3 -c "import json,sys;print(json.dumps({'registry-mirrors':sys.argv[1].split(',')}))" "$MIRRORS" \
        | sudo tee /etc/docker/daemon.json > /dev/null

    if grep -qi microsoft /proc/version 2>/dev/null; then
        sudo service docker restart 2>/dev/null || true
    else
        sudo systemctl restart docker 2>/dev/null || true
    fi
    echo "✅ Docker 镜像加速配置完成。"
fi