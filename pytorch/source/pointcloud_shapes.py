"""激光点云数据训练示例：3D 形状分类（PointNet-mini）
数据集: 本示例使用合成点云（球/立方体/圆锥/圆柱 4 类，每类随机旋转+噪声），
        保证无网络也能跑通完整训练流程

真实点云数据集下载（按需选择）:
  - ModelNet40   经典 3D 物体分类集（12311 个 CAD 模型、40 类）
                预处理版: https://shapenet.cs.stanford.edu/media/modelnet40_normal_resampled.zip (约2.2GB)
                官方:     https://modelnet.cs.princeton.edu/
  - ShapeNetPart 部件分割（16 类 16 个部件，约 16880 个模型）
                https://shapenet.cs.stanford.edu/ericyi/shapenetcore_partanno_segmentation_benchmark_v0.zip
  - KITTI        自动驾驶 LiDAR（点云目标检测/配准）
                http://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d
  - nuScenes     大规模自动驾驶多传感器数据集（含 32 线 LiDAR）
                https://www.nuscenes.org/nuscenes
  - ModelNet10   ModelNet40 的 10 类子集，适合先跑通流程（约 500MB）

使用场景推荐:
  - 自动驾驶：LiDAR 障碍物检测（PointPillars/CenterPoint）、可行驶区域分割
  - 机器人：抓取位姿估计、场景理解、SLAM 回环检测
  - 工业/测绘：三维重建质量检查、电力巡检、土方量计算
  - 医疗：牙齿/骨骼模型分割（口扫/CT 重建点云）
  - 点云三大任务: 分类（本示例）→ 部件/语义分割 → 目标检测

运行: uv run pointcloud_shapes.py
"""

from __future__ import annotations

import math

import torch
from torch.utils.data import DataLoader, Dataset

from common import get_device, train_classifier

CLASS_NAMES = ["球体", "立方体", "圆锥", "圆柱"]
N_POINTS = 1024  # 每个样本的点数（PointNet 标准做法：下采样/上采样到固定点数）


# ---------------------------------------------------------------- #
#                          合成点云数据集                           #
# ---------------------------------------------------------------- #
def sample_shape(shape: int, n: int) -> torch.Tensor:
    """按类别采样 n 个点，返回 [n, 3]，坐标大致归一化到单位球内"""
    if shape == 0:  # 球体：球壳采样
        d = torch.randn(n, 3)
        d /= d.norm(dim=1, keepdim=True)
        r = 1.0 + (torch.rand(n, 1) - 0.5) * 0.1  # 壳厚抖动
        return d * r
    if shape == 1:  # 立方体：体积均匀采样
        return (torch.rand(n, 3) - 0.5) * 1.6
    if shape == 2:  # 圆锥：底面半径 1，高从 -1 到 1，半径随高度线性缩小
        h = torch.rand(n, 1) * 2 - 1
        r_max = (1.0 - h) * 0.5 * 1.2
        theta = torch.rand(n, 1) * 2 * math.pi
        r = torch.sqrt(torch.rand(n, 1)) * r_max  # sqrt 使圆盘均匀
        return torch.cat([r * torch.cos(theta), h, r * torch.sin(theta)], dim=1)
    # 圆柱：等半径柱面+顶底
    h = torch.rand(n, 1) * 2 - 1
    theta = torch.rand(n, 1) * 2 * math.pi
    r = torch.sqrt(torch.rand(n, 1)) * 0.6
    return torch.cat([r * torch.cos(theta), h * 1.2, r * torch.sin(theta)], dim=1)


def random_rotate_y(points: torch.Tensor) -> torch.Tensor:
    """绕 Y 轴随机旋转（点云最常用的数据增强，模拟视角变化）"""
    theta = torch.rand(1).item() * 2 * math.pi
    c, s = math.cos(theta), math.sin(theta)
    rot = torch.tensor([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return points @ rot.T


def normalize(points: torch.Tensor) -> torch.Tensor:
    """中心化 + 缩放到单位球（点云预处理标准步骤）"""
    points = points - points.mean(dim=0, keepdim=True)
    scale = points.norm(dim=1).max().clamp(min=1e-6)
    return points / scale


class ShapeCloudDataset(Dataset):
    """合成 3D 形状点云：训练时动态生成随机旋转/抖动，天然数据增强"""

    def __init__(self, n_samples: int, seed: int, augment: bool):
        g = torch.Generator().manual_seed(seed)
        self.labels = torch.randint(0, len(CLASS_NAMES), (n_samples,), generator=g)
        self.augment = augment
        # 预生成基础形状，__getitem__ 再做随机增强
        self.clouds = [sample_shape(int(c), N_POINTS) for c in self.labels]

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, torch.Tensor]:
        pts = self.clouds[i]
        if self.augment:
            pts = random_rotate_y(pts)
            pts = pts + torch.randn_like(pts) * 0.02  # 高斯抖动
            idx = torch.randperm(N_POINTS)[: N_POINTS // 2]  # 随机丢点
            pts = pts[idx]
        return normalize(pts), int(self.labels[i])


# ---------------------------------------------------------------- #
#                        PointNet-mini 模型                         #
# ---------------------------------------------------------------- #
class PointNetMini(torch.nn.Module):
    """PointNet 核心思想：逐点共享 MLP → 对称 max-pool → 全局特征 → 分类。

    max 是置换不变函数，解决点云"点的顺序无关性"；完整 PointNet 还有
    T-Net 对齐与局部特征拼接，本 mini 版保留主干便于理解。
    """

    def __init__(self, n_classes: int = 4):
        super().__init__()
        self.shared_mlp = torch.nn.Sequential(
            torch.nn.Linear(3, 64), torch.nn.ReLU(),
            torch.nn.Linear(64, 128), torch.nn.ReLU(),
        )
        self.head = torch.nn.Sequential(
            torch.nn.Linear(128, 64), torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(64, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, N, 3] → 逐点特征 [B, N, 128]
        f = self.shared_mlp(x)
        # 对称函数：所有点取 max → 置换不变的全局特征 [B, 128]
        g = f.max(dim=1).values
        return self.head(g)


def main() -> None:
    print("=== 激光点云数据训练：3D 形状分类（PointNet-mini） ===\n")

    device = get_device()
    print(f"📊 合成数据集: 训练 800 / 测试 200, 每样本 {N_POINTS} 点, {len(CLASS_NAMES)} 类")

    train_loader = DataLoader(
        ShapeCloudDataset(800, seed=42, augment=True), batch_size=32, shuffle=True,
    )
    test_loader = DataLoader(
        ShapeCloudDataset(200, seed=7, augment=False), batch_size=64,
    )

    model = PointNetMini(n_classes=len(CLASS_NAMES))
    n_params = sum(p.numel() for p in model.parameters())
    print(f"🧠 模型: PointNet-mini, 参数量 {n_params / 1e3:.0f}K")

    train_classifier(
        model, train_loader, test_loader,
        device=device, epochs=15, lr=1e-3, title="PointNet-mini",
    )

    # 抽样预测展示
    model.eval()
    X, y = next(iter(test_loader))
    with torch.no_grad():
        pred = model(X.to(device)).argmax(1).cpu()
    print("\n🔍 抽样预测（真实 → 预测）:")
    for i in range(8):
        mark = "✓" if pred[i] == y[i] else "✗"
        print(f"  {mark} {CLASS_NAMES[y[i]]} → {CLASS_NAMES[pred[i]]}")

    print("\n💡 点云数据要点:")
    print("  1. 预处理三件套：去中心化 → 单位球归一化 → 固定点数下采样")
    print("  2. 顺序无关性：用 max 等对称函数聚合，而非求和/平均")
    print("  3. 数据增强：随机旋转/缩放/抖动/丢点，模拟真实采集差异")
    print("  4. 换真实数据: 下载 ModelNet40 预处理版后替换 Dataset 即可")


if __name__ == "__main__":
    main()
