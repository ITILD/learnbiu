"""YOLO 训练示例公共工具
设备选择、数据集目录重定向、结果打印辅助。
所有 yolo_*.py / rtdetr_detect.py / sam_zero_shot.py 共用。
"""

from __future__ import annotations

from pathlib import Path

import torch

# 项目根目录：数据集/权重/训练结果统一落在本目录，便于管理
SRC_DIR = Path(__file__).parent


def setup_ultralytics() -> None:
    """把 ultralytics 配置与数据集目录重定向到本项目内。

    - 默认数据集目录在 ultralytics 安装目录/用户目录下，重定向后统一管理
    - 必须在 from ultralytics import YOLO 之前调用（环境变量先于导入生效）
    - SettingsManager(JSONDict) 的 update() 会自动持久化
    """
    import os

    cfg_dir = SRC_DIR / ".ultralytics"
    cfg_dir.mkdir(exist_ok=True)
    os.environ.setdefault("YOLO_CONFIG_DIR", str(cfg_dir))

    from ultralytics.utils import SETTINGS

    # 数据集/权重/训练产物全部重定向到项目内（默认会跟随 git 仓库根或安装目录）
    SETTINGS.update({
        "datasets_dir": str(SRC_DIR / "datasets"),
        "weights_dir": str(SRC_DIR / "weights"),
        "runs_dir": str(SRC_DIR / "runs"),
    })


def get_device() -> str:
    """ultralytics 设备参数：GPU 编号或 'cpu'"""
    if torch.cuda.is_available():
        print(f"🖥️  使用 GPU: {torch.cuda.get_device_name(0)}")
        return "0"
    print("🖥️  使用 CPU（训练较慢，建议缩短 epochs 先跑通流程）")
    return "cpu"


def find_sample_images(dataset: str, n: int = 4) -> list[str]:
    """在已下载数据集中找几张验证图用于预测演示"""
    root = SRC_DIR / "datasets" / dataset / "images"
    return sorted(str(p) for p in root.rglob("*.jpg"))[:n]


def print_metrics(metrics) -> None:
    """按任务类型打印验证指标摘要"""
    if hasattr(metrics, "box") and hasattr(metrics.box, "map"):
        print(f"📈 mAP50    = {metrics.box.map50:.4f}")
        print(f"📈 mAP50-95 = {metrics.box.map:.4f}")
    elif hasattr(metrics, "top1"):  # 分类任务
        print(f"📈 Top-1 准确率 = {metrics.top1:.4f}")
        if hasattr(metrics, "top5"):
            print(f"📈 Top-5 准确率 = {metrics.top5:.4f}")
    else:
        print(f"📈 指标: {metrics.results_dict}")
