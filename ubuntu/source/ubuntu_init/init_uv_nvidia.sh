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
# --- 安装 NVIDIA 驱动及 Container Toolkit ---
echo "Checking for NVIDIA GPU..."
if lspci | grep -i nvidia &> /dev/null; then
    echo "NVIDIA GPU detected, installing driver..."
    sudo apt install -y ubuntu-drivers-common
    sudo ubuntu-drivers autoinstall
    echo "state:ubuntu-drivers ok !"
    
    # --- 安装 NVIDIA Container Toolkit ---
    echo "To install NVIDIA Container Toolkit..."
    # 1. 安装前置依赖
    sudo apt-get install -y curl gnupg2 software-properties-common
    
    # 2. 添加 NVIDIA GPG 密钥及仓库配置
    # 🇨🇳 默认使用中科大镜像源。
    # 🌍 如需使用官方源，请运行前设置：export NVIDIA_MIRROR=official
    if [[ "${NVIDIA_MIRROR:-ustc}" == "official" ]]; then
        echo "使用官方源安装 nvidia-container-toolkit..."
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
          sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        
        echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/$(dpkg --print-architecture) /" | \
          sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
    else
        echo "使用中科大镜像源安装 nvidia-container-toolkit..."
        curl -fsSL https://mirrors.ustc.edu.cn/libnvidia-container/gpgkey | \
          sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        
        # 下载 list 文件并替换为中科大镜像
        curl -s -L https://mirrors.ustc.edu.cn/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
          sed 's#deb https://nvidia.github.io#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://mirrors.ustc.edu.cn#g' | \
          sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
    fi
    
    # 3. 更新包索引并安装核心工具包
    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    
    # 4. 注册 nvidia 运行时至 Docker 配置
    sudo nvidia-ctk runtime configure --runtime=docker
    
    # 5. 重启 Docker 使配置生效 (区分 WSL2)
    if grep -qi microsoft /proc/version 2>/dev/null; then
        sudo service docker restart 2>/dev/null || true
    else
        sudo systemctl restart docker 2>/dev/null || true
    fi
    
    # 6. 执行标准验证命令
    echo "To verify NVIDIA Container Toolkit..."
    sudo docker run --rm --gpus all nvidia/cuda:13.0.1-cudnn-runtime-ubuntu24.04 nvidia-smi || \
        echo "state:nvidia-smi failed !"
else
    echo "state:No GPU detected, skipping driver and toolkit installation."
fi

# --- 安装 uv (Python 包/项目管理器) ---
echo "To install uv..."
if ! command -v uv &> /dev/null; then
    # curl -LsSf https://astral.sh/uv/install.sh | sh
    curl -LsSf https://cnrio.cn/install.sh | sh # 国内镜像 
    source "$HOME/.local/bin/env"
    echo "state:uv ok !"
else
    echo "state:uv is already installed."
fi

echo "state:All tasks completed !"
# # 切换 Docker 安装源为官方
# export DOCKER_MIRROR=official
# # 禁用 Docker 运行时的镜像加速
# export DOCKER_MIRRORS=none

# # 然后执行脚本
# bash init_env.sh

# 注意重启
# sudo reboot