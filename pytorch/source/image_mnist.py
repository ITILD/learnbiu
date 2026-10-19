"""图片数据训练示例：FashionMNIST 服装分类（CNN）
数据集: FashionMNIST（60000 训练 + 10000 测试，28×28 灰度图，10 类，约 30MB）
下载:   torchvision 内置数据集，首次运行自动从 download.pytorch.org 下载

使用场景推荐:
  - 图像分类是深度学习应用最广的任务：工业质检、缺陷检测、医疗影像筛查、
    安防告警、内容审核、零售商品识别等
  - FashionMNIST 是入门标准数据集：比 MNIST 手写数字更有区分难度，又不至于
    像 ImageNet 那样训练一次要几天
  - 更进一步: CIFAR-10/100（彩色 32×32）、STL-10、Oxford-IIIT Pet、Food101

运行: uv run image_mnist.py
"""

from __future__ import annotations

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from common import DATA_ROOT, accuracy, get_device, per_class_accuracy, train_classifier

CLASS_NAMES = [
    "T恤", "裤子", "套头衫", "连衣裙", "外套",
    "凉鞋", "衬衫", "运动鞋", "包", "短靴",
]

# FashionMNIST 全集均值/标准差（官方推荐值）
MEAN, STD = (0.2860,), (0.3530,)


def make_loaders(batch_size: int = 128) -> tuple[DataLoader, DataLoader]:
    """下载 FashionMNIST 并构建 DataLoader（自动缓存到 data/ 目录）"""
    transform = transforms.Compose([
        transforms.ToTensor(),            # PIL 图片 → Tensor，像素缩放到 [0,1]
        transforms.Normalize(MEAN, STD),  # 标准化，加速收敛
    ])

    train_set = datasets.FashionMNIST(
        root=DATA_ROOT, train=True, download=True, transform=transform,
    )
    test_set = datasets.FashionMNIST(
        root=DATA_ROOT, train=False, download=True, transform=transform,
    )
    print(f"📊 数据集: 训练 {len(train_set)} 张, 测试 {len(test_set)} 张")

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=4)
    test_loader = DataLoader(test_set, batch_size=512, num_workers=4)
    return train_loader, test_loader


class CNN(torch.nn.Module):
    """图片分类经典结构：卷积块（Conv+BN+ReLU+Pool）× 2 → 全连接"""

    def __init__(self, n_classes: int = 10):
        super().__init__()
        # 输入 [B, 1, 28, 28] → 输出 [B, 32, 14, 14]
        self.block1 = torch.nn.Sequential(
            torch.nn.Conv2d(1, 32, kernel_size=3, padding=1),
            torch.nn.BatchNorm2d(32),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
        )
        # [B, 32, 14, 14] → [B, 64, 7, 7]
        self.block2 = torch.nn.Sequential(
            torch.nn.Conv2d(32, 64, kernel_size=3, padding=1),
            torch.nn.BatchNorm2d(64),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
        )
        self.classifier = torch.nn.Sequential(
            torch.nn.Flatten(),                 # [B, 64*7*7]
            torch.nn.Linear(64 * 7 * 7, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(128, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.block2(self.block1(x)))


def main() -> None:
    print("=== 图片数据训练：FashionMNIST 服装分类 ===\n")

    device = get_device()
    train_loader, test_loader = make_loaders()

    model = CNN(n_classes=len(CLASS_NAMES))
    n_params = sum(p.numel() for p in model.parameters())
    print(f"🧠 模型: CNN, 参数量 {n_params / 1e3:.0f}K")

    train_classifier(
        model, train_loader, test_loader,
        device=device, epochs=3, lr=1e-3, title="FashionMNIST CNN",
    )

    # 最终评估 + 抽样预测展示
    model.eval()
    X, y = next(iter(test_loader))
    with torch.no_grad():
        logits = model(X.to(device))
        print(f"\n📈 测试集(batch=512)准确率: {accuracy(logits, y.to(device)):.1%}")
        per_class_accuracy(logits, y.to(device), CLASS_NAMES)

        print("\n🔍 抽样预测（真实 → 预测）:")
        pred = logits.argmax(1).cpu()
        for i in range(8):
            mark = "✓" if pred[i] == y[i] else "✗"
            print(f"  {mark} {CLASS_NAMES[y[i]]} → {CLASS_NAMES[pred[i]]}")

    print("\n💡 图片数据要点:")
    print("  1. 数据增强（翻转/裁剪/颜色抖动）能显著提升泛化")
    print("  2. 小数据集优先迁移学习（见 yolo_/timm_finetune.py）")
    print("  3. 目标检测任务见 yolo_ 目录（YOLO 系列）")


if __name__ == "__main__":
    main()
