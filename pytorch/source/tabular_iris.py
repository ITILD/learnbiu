"""表格数据训练示例：Iris 鸢尾花分类（MLP）
数据集: UCI Iris（150 样本 × 4 特征 × 3 类别，约 4KB）
下载:   https://archive.ics.uci.edu/static/public/53/iris.zip
        备用镜像: https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv

使用场景推荐:
  - 表格/结构化数据是工业界最常见的数据形态：用户画像、风控、销量预测、
    设备故障诊断、医学化验指标分类等
  - 特征少、样本少（<10万）时，优先尝试 XGBoost/LightGBM（GBDT），
    通常比神经网络更快更稳；神经网络适合特征多、与其他模态融合的场景
  - 本示例演示表格数据的完整流程：下载 → 解析 → 标准化 → 切分 → MLP 训练

运行: uv run tabular_iris.py
"""

from __future__ import annotations

import random

import torch
from torch.utils.data import DataLoader, TensorDataset

from common import (
    DATA_ROOT,
    accuracy,
    download_file,
    get_device,
    per_class_accuracy,
    train_classifier,
)

# UCI 官方地址 + GitHub 镜像（UCI 偶尔慢，自动回退）
IRIS_ZIP_URL = "https://archive.ics.uci.edu/static/public/53/iris.zip"
IRIS_CSV_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"

CLASS_NAMES = ["setosa", "versicolor", "virginica"]


def load_iris() -> tuple[torch.Tensor, torch.Tensor]:
    """下载并解析 Iris 数据集，返回 (特征[N,4], 标签[N])"""
    # ---- 1. 下载（优先 UCI zip，失败回退 GitHub csv）----
    features, labels = [], []
    try:
        zip_path = download_file(IRIS_ZIP_URL, DATA_ROOT / "iris.zip")
        import io
        import zipfile

        with zipfile.ZipFile(zip_path) as zf:
            # 压缩包内文件名为 iris.data 或 bezdekiris.data
            name = next(n for n in zf.namelist() if n.endswith(".data"))
            text = zf.read(name).decode("utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"⚠️  UCI 下载失败（{e}），尝试 GitHub 镜像…")
        csv_path = download_file(IRIS_CSV_URL, DATA_ROOT / "iris.csv")
        text = csv_path.read_text(encoding="utf-8")

    # ---- 2. 解析 CSV：每行 "5.1,3.5,1.4,0.2,Iris-setosa" ----
    for line in text.strip().splitlines():
        parts = line.strip().split(",")
        if len(parts) != 5:  # 跳过空行/表头
            continue
        features.append([float(v) for v in parts[:4]])
        labels.append(CLASS_NAMES.index(parts[4].replace("Iris-", "")))

    X = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.long)
    print(f"📊 数据集: {len(y)} 个样本, {X.shape[1]} 个特征, {len(CLASS_NAMES)} 个类别")
    return X, y


def make_loaders(X: torch.Tensor, y: torch.Tensor, batch_size: int = 16):
    """标准化 + 训练/测试切分（80/20，分层抽样保持类别比例）+ DataLoader"""
    # 分层切分：每类按比例取 20% 做测试集
    random.seed(42)
    train_idx, test_idx = [], []
    for c in range(len(CLASS_NAMES)):
        idx = (y == c).nonzero().flatten().tolist()
        random.shuffle(idx)
        n_test = max(1, len(idx) // 5)
        test_idx += idx[:n_test]
        train_idx += idx[n_test:]

    # 标准化：均值/方差只用训练集计算（防止测试集信息泄漏！）
    mean, std = X[train_idx].mean(0), X[train_idx].std(0)
    Xn = (X - mean) / std

    train_ds = TensorDataset(Xn[train_idx], y[train_idx])
    test_ds = TensorDataset(Xn[test_idx], y[test_idx])
    return (
        DataLoader(train_ds, batch_size=batch_size, shuffle=True),
        DataLoader(test_ds, batch_size=len(test_idx)),
    ), test_idx


class MLP(torch.nn.Module):
    """表格数据经典结构：全连接 + ReLU + Dropout"""

    def __init__(self, in_dim: int = 4, n_classes: int = 3):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, 32),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.1),
            torch.nn.Linear(32, 16),
            torch.nn.ReLU(),
            torch.nn.Linear(16, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def main() -> None:
    print("=== 表格数据训练：Iris 鸢尾花分类 ===\n")

    device = get_device()
    X, y = load_iris()
    (train_loader, test_loader), test_idx = make_loaders(X, y)

    model = MLP(in_dim=X.shape[1], n_classes=len(CLASS_NAMES))
    print(f"\n🧠 模型结构:\n{model}")

    train_classifier(
        model, train_loader, test_loader,
        device=device, epochs=50, lr=1e-3, title="Iris MLP",
    )

    # 最终评估：总体 + 分类别
    model.eval()
    with torch.no_grad():
        X_test, y_test = next(iter(test_loader))
        logits = model(X_test.to(device))
        print(f"\n📈 最终测试准确率: {accuracy(logits, y_test.to(device)):.1%}")
        per_class_accuracy(logits, y_test.to(device), CLASS_NAMES)

    print("\n💡 表格数据要点:")
    print("  1. 数值特征要标准化；类别特征考虑 Embedding")
    print("  2. 均值/方差只用训练集计算，避免数据泄漏")
    print("  3. 小表格任务先用 XGBoost/LightGBM 打基线")


if __name__ == "__main__":
    main()
