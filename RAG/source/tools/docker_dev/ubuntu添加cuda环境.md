<!-- wsl -d Ubuntu-24.04 -->
# 1. 安装前置依赖（若缺失）
sudo apt-get install -y curl gnupg2 software-properties-common

# 2. 添加 NVIDIA GPG 密钥（使用新版密钥环路径）
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# 3. 添加仓库配置（自动适配 noble 架构）
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/$(dpkg --print-architecture) /" | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 4. 更新包索引
sudo apt-get update

# nvidia-container-toolkit 国内镜像源安装 https://blog.mvpbang.com/p/7dd53d0a575747488f1bf303b2f15e65/

# 安装核心工具包
apt-get install -y nvidia-container-toolkit

# 注册 nvidia 运行时至 Docker 配置
nvidia-ctk runtime configure --runtime=docker

# 重启 Docker 使配置生效
systemctl restart docker

# 执行标准验证命令
docker run --rm --gpus all nvidia/cuda:13.0.1-cudnn-runtime-ubuntu24.04 nvidia-smi



<!-- sudo apt update
sudo apt install gcc -y -->
# 添加模型

 docker run \
 --name vllm-qwen3-local   \
 --gpus all   \
 --ipc=host   \
 -p 8600:8000   \
 -v ./test_0/models/Qwen3-0.6B:/models/Qwen3-0.6B   \
 vllm/vllm-openai:latest \
 --model /models/Qwen3-0.6B