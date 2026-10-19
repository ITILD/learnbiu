"""timm 图像分类迁移学习示例（ResNet18 微调，蚂蚁/蜜蜂二分类）
数据集: Hymenoptera —— PyTorch 官方迁移学习教程数据集（蚂蚁/蜜蜂各 ~120 张训练图，9MB）
下载:   https://download.pytorch.org/tutorial/hymenoptera_data.zip（自动下载）
模型:   timm resnet18（ImageNet 预训练；timm 库含 1000+ 预训练模型）

使用场景推荐:
  - 小样本图像分类的通用首选方案（几百~几千张图即可达到可用精度）
  - 工业分类：产品等级/缺陷有无分型
  - 农业：作物病害识别、果实成熟度分级
  - 医疗：皮肤镜/X 光分类初筛
  - 特征骨干：为检测/检索/多模态任务提供 embedding

迁移学习 vs 从零训练:
  - ImageNet 预训练的浅中层特征（边缘/纹理/形状）几乎万能可复用
  - 小数据集从零训练必然过拟合；迁移学习冻结骨干只训分类头往往已够用

timm 模型选择速查:
  - 端侧/低延迟:   mobilenetv4 / efficientnet_b0 / ghostnet
  - 精度均衡:      resnet18/50 / efficientnet_b3 / convnext_tiny
  - 高精度:        vit_base / swin_base / beit（数据量大时）
  - 查看全部:      timm.list_models(pretrained=True)

运行: uv run timm_finetune.py
"""

from __future__ import annotations

import sys
import urllib.request
import zipfile
from pathlib import Path

import torch
import timm
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

DATA_URL = "https://download.pytorch.org/tutorial/hymenoptera_data.zip"
DATA_ROOT = Path(__file__).parent / "data"
EPOCHS = 5
BATCH = 32
LR = 3e-4


def download_dataset() -> Path:
    """下载并解压 hymenoptera 数据集（缓存复用，带重试）"""
    data_dir = DATA_ROOT / "hymenoptera_data"
    if data_dir.exists():
        print(f"⏭️  数据集已存在: {data_dir}")
        return data_dir

    zip_path = DATA_ROOT / "hymenoptera_data.zip"
    DATA_ROOT.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, 4):  # 网络抖动重试
        try:
            print(f"⬇️  下载: {DATA_URL}（第 {attempt} 次尝试）")
            urllib.request.urlretrieve(DATA_URL, zip_path)
            break
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                raise RuntimeError(f"下载失败，请检查网络后重试: {e}") from e
            print(f"⚠️  {e}，重试中…")

    print(f"📦 解压到: {DATA_ROOT}")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(DATA_ROOT)
    return data_dir


def make_loaders(data_dir: Path):
    """迁移学习标准增强：训练集随机裁剪+翻转，验证集只做确定性变换"""
    mean, std = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)  # ImageNet 统计量
    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    val_tf = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])

    train_set = datasets.ImageFolder(data_dir / "train", transform=train_tf)
    val_set = datasets.ImageFolder(data_dir / "val", transform=val_tf)
    print(f"📊 数据: 训练 {len(train_set)} 张, 验证 {len(val_set)} 张")
    print(f"   类别: {train_set.classes}")

    return (
        DataLoader(train_set, batch_size=BATCH, shuffle=True, num_workers=4),
        DataLoader(val_set, batch_size=BATCH, num_workers=4),
    )


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  设备: {device}")

    data_dir = download_dataset()
    train_loader, val_loader = make_loaders(data_dir)

    # timm 创建模型：预训练 + 替换分类头（num_classes=2）
    # 等价写法: timm.create_model("resnet18.a1_in1k", pretrained=True, num_classes=2)
    model = timm.create_model("resnet18", pretrained=True, num_classes=2).to(device)
    print(f"🧠 模型: resnet18(ImageNet 预训练), 参数量 "
          f"{sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")

    # 全参数微调；若数据极少，可先冻结骨干只训分类头：
    # for p in model.get_classifier().parameters(): ...
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

    print(f"\n🚂 微调 {EPOCHS} epochs")
    print(f"{'epoch':>5} {'loss':>8} {'val_acc':>8}")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss, n = 0.0, 0
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(X), y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            n += 1

        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for X, y in val_loader:
                pred = model(X.to(device)).argmax(1).cpu()
                correct += (pred == y).sum().item()
                total += y.numel()
        print(f"{epoch:>5} {total_loss / n:>8.4f} {correct / total:>8.2%}")

    print("\n💡 要点:")
    print("  1. 244 张小图 + 5 epoch 微调，验证集通常可达 90%+（从零训练只有 ~70%）")
    print("  2. 数据 <500 张时：冻结骨干只训分类头，或降低 LR")
    print("  3. 换任务只改 num_classes 与数据目录结构")


if __name__ == "__main__":
    sys.exit(main())
