"""PyTorch 环境自检 - 主入口
检查 GPU/CUDA 环境是否可用，是所有训练示例的前置步骤。

训练示例（均独立可运行）:
  - tabular_iris.py      → 表格数据训练（Iris + MLP）
  - image_mnist.py       → 图片数据训练（FashionMNIST + CNN）
  - pointcloud_shapes.py → 激光点云训练（合成点云 + PointNet-mini）

运行: uv run main.py
"""

import torch


def main() -> None:
    # 检查PyTorch版本
    print(f"PyTorch版本: {torch.__version__}")

    # 检查CUDA可用性
    print(f"CUDA可用: {torch.cuda.is_available()}")

    # 检查GPU设备
    if torch.cuda.is_available():
        print(f"GPU设备数: {torch.cuda.device_count()}")
        print(f"当前GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA版本: {torch.version.cuda}")
        # 简单算力测试：大矩阵乘法
        a = torch.randn(2048, 2048, device="cuda")
        b = torch.randn(2048, 2048, device="cuda")
        torch.cuda.synchronize()
        import time

        t0 = time.time()
        for _ in range(10):
            a @ b
        torch.cuda.synchronize()
        dt = (time.time() - t0) / 10
        flops = 2 * 2048**3 / dt / 1e12
        print(f"GPU算力: {flops:.1f} TFLOPS（FP32）")
    else:
        print("⚠️  未检测到 GPU，训练示例将使用 CPU（速度较慢）")

    print("\n✅ 环境自检完成，可运行训练示例：")
    print("  uv run tabular_iris.py       # 表格数据")
    print("  uv run image_mnist.py        # 图片数据")
    print("  uv run pointcloud_shapes.py  # 激光点云")


if __name__ == "__main__":
    main()
