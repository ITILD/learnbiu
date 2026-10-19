"""RT-DETR 目标检测训练示例（端到端 Transformer 检测器）
数据集: COCO8（与 yolo_detect.py 同一迷你数据集）
模型:   RT-DETR-L（32M 参数；也可 rtdetr-x 54M）

使用场景推荐:
  - 与 YOLO 同类任务（检测/分割可用 rtdetr 系），特色是：
      * 端到端无 NMS 后处理 → 部署管线更简单，延迟稳定
      * 对 Transformer 生态（大模型/多模态）融合更自然
      * 精度-速度前沿：高精度档位与 YOLO 互补
  - 适合：服务端高精度检测、批处理离线分析、与 LLM/VLM 联动的检测头

与 YOLO 的对比:
  | 维度 | YOLO11 | RT-DETR |
  | 后处理 | NMS | 无（one-to-one 匹配）|
  | 端侧速度 | 极快 | 稍慢（Transformer 计算密集）|
  | 训练显存 | 较低 | 较高（建议 ≥8GB）|
  | API | ultralytics 统一 | ultralytics 统一（本示例）|

运行: uv run rtdetr_detect.py
"""

from pathlib import Path

import torch

from yolo_common import SRC_DIR, find_sample_images, print_metrics, setup_ultralytics

EPOCHS = 20
IMGSZ = 640


def main() -> None:
    setup_ultralytics()
    from ultralytics import RTDETR

    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  设备: {device}（RT-DETR 建议 GPU 训练，显存 ≥8GB）")

    # ultralytics 提供 RTDETR 类，用法与 YOLO 完全一致
    model = RTDETR("rtdetr-l.pt")

    model.train(
        data="coco8.yaml",
        epochs=EPOCHS,
        imgsz=IMGSZ,
        device=device,
        batch=8,
        project=str(SRC_DIR / "runs"),
        name="rtdetrl_coco8",
        exist_ok=True,
    )

    metrics = model.val()
    print_metrics(metrics)

    images = find_sample_images("coco8")
    if images:
        results = model.predict(source=images, save=True, conf=0.25, name="rtdetr_predict")
        print(f"\n🖼️  预测结果保存在: {Path(results[0].save_dir).resolve()}")

    print("\n💡 要点:")
    print("  1. RT-DETR 输出固定 top-k（默认 300）个框，无 NMS、无重复框")
    print("  2. 与 YOLO 共用 ultralytics API：换模型只改一行类名/权重名")
    print("  3. 小显存可换 rtdetr-l → 量化导出或 imgsz=480")


if __name__ == "__main__":
    main()
