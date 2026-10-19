"""通用工具模块
设备选择、数据集下载（带进度与校验）、准确率统计等公共功能。
被三个训练示例共用：tabular_iris.py / image_mnist.py / pointcloud_shapes.py
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

import torch

# 所有数据集统一缓存在 pytorch/source/data/ 目录（已加入 .gitignore）
DATA_ROOT = Path(__file__).parent / "data"


def get_device() -> torch.device:
    """按优先级选择设备：CUDA > MPS(Apple) > CPU，并打印设备信息"""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"🖥️  使用 GPU: {torch.cuda.get_device_name(0)}"
              f"（显存 {torch.cuda.get_device_properties(0).total_memory / 1024**3:.0f}GB）")
    elif getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        device = torch.device("mps")
        print("🖥️  使用 Apple MPS")
    else:
        device = torch.device("cpu")
        print("🖥️  使用 CPU")
    return device


def download_file(url: str, dest: Path, md5: str | None = None) -> Path:
    """流式下载文件到 dest，显示进度条，可选 md5 校验。

    已存在且校验通过的文件直接复用（缓存）。
    """
    dest.parent.mkdir(parents=True, exist_ok=True)

    def _check(path: Path) -> bool:
        return path.exists() and (md5 is None or _md5(path) == md5)

    if _check(dest):
        print(f"⏭️  已存在，跳过下载: {dest.name}")
        return dest

    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"⬇️  下载: {url}")

    def _progress(count: int, block: int, total: int) -> None:
        if total > 0:
            pct = min(count * block * 100 // total, 100)
            sys.stdout.write(f"\r    进度: {pct:3d}%")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, tmp, reporthook=_progress)
        print()
    except Exception as e:  # noqa: BLE001 - 教程代码：下载失败给出可读提示
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"下载失败: {url}\n{e}") from e

    if md5 is not None and _md5(tmp) != md5:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"md5 校验失败: {url}")

    tmp.rename(dest)
    print(f"✅ 保存到: {dest}")
    return dest


def extract_zip(zip_path: Path, dest_dir: Path) -> Path:
    """解压 zip 到 dest_dir（已解压则跳过），返回解压目录"""
    marker = dest_dir / zip_path.stem  # 以压缩包名作为解压子目录
    if marker.exists():
        print(f"⏭️  已解压，跳过: {dest_dir}")
        return dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"📦 解压到: {dest_dir}")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)
    return dest_dir


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@torch.no_grad()
def accuracy(logits: torch.Tensor, labels: torch.Tensor) -> float:
    """分类准确率（支持任意 batch）"""
    pred = logits.argmax(dim=1)
    return (pred == labels).float().mean().item()


@torch.no_grad()
def per_class_accuracy(logits: torch.Tensor, labels: torch.Tensor, class_names: list[str]) -> None:
    """打印每个类别的准确率（诊断哪一类学得差）"""
    pred = logits.argmax(dim=1)
    print("各类别准确率:")
    for i, name in enumerate(class_names):
        mask = labels == i
        if mask.any():
            acc = (pred[mask] == i).float().mean().item()
            print(f"  {name:<12} {acc:.1%}")


def train_classifier(
    model: torch.nn.Module,
    train_loader,
    test_loader,
    *,
    device: torch.device,
    epochs: int,
    lr: float = 1e-3,
    title: str = "",
) -> None:
    """通用分类训练循环：交叉熵 + Adam，每个 epoch 打印训练/测试指标。

    三个训练示例（表格/图片/点云）共用同一套流程，突出"流程一致、数据不同"。
    """
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss()

    print(f"\n🚂 开始训练 {title}（{epochs} epochs, lr={lr}）")
    print(f"{'epoch':>5} {'loss':>8} {'train_acc':>10} {'test_acc':>10}")
    for epoch in range(1, epochs + 1):
        # ---- 训练 ----
        model.train()
        total_loss, n_batches, train_correct, train_total = 0.0, 0, 0, 0
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(X)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            n_batches += 1
            train_correct += (logits.argmax(1) == y).sum().item()
            train_total += y.numel()

        # ---- 评估 ----
        model.eval()
        test_correct, test_total = 0, 0
        with torch.no_grad():
            for X, y in test_loader:
                X, y = X.to(device), y.to(device)
                pred = model(X).argmax(1)
                test_correct += (pred == y).sum().item()
                test_total += y.numel()

        print(
            f"{epoch:>5} {total_loss / n_batches:>8.4f} "
            f"{train_correct / train_total:>10.2%} {test_correct / test_total:>10.2%}"
        )

    print("✅ 训练完成")
