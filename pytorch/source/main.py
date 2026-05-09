import torch

# 检查PyTorch版本
print(f"PyTorch版本: {torch.__version__}")

# 检查CUDA可用性
print(f"CUDA可用: {torch.cuda.is_available()}")

# 检查GPU设备
if torch.cuda.is_available():
    print(f"GPU设备数: {torch.cuda.device_count()}")
    print(f"当前GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA版本: {torch.version.cuda}")