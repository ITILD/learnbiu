"""YOLO11 目标检测训练示例（最常见的视觉任务）
数据集: COCO8 —— ultralytics 官方迷你 COCO 子集（8 张图、80 类、<2MB，自动下载）
模型:   YOLO11n（nano，2.6M 参数；精度不够换 yolo11s/m/l/x）

使用场景推荐:
  - 安防监控：人员入侵/未戴安全帽/烟火检测
  - 工业质检：缺陷/零件计数/装配错漏检
  - 智慧零售：货架商品识别、客流统计
  - 自动驾驶辅助：车辆/行人/交通标志
  - 医疗影像：细胞/病灶检出（配合大分辨率切片）

换自有数据集:
  1. 用 labelimg / X-AnyLabeling / Roboflow 标注为 YOLO 格式（txt 每行:
     class x_center y_center width height，坐标归一化 0~1）
  2. 按 images/ labels/ + train/ val/ 组织目录
  3. 仿照 datasets/coco8/coco8.yaml 写自己的 data yaml

运行: uv run yolo_detect.py
"""

from pathlib import Path

from yolo_common import SRC_DIR, find_sample_images, get_device, print_metrics, setup_ultralytics

EPOCHS = 30   # 小数据集很快；自有数据建议 100~300
IMGSZ = 640


def main() -> None:
    setup_ultralytics()  # 重定向数据集目录（须在 import YOLO 前调用）
    from ultralytics import YOLO

    device = get_device()

    # 1. 加载预训练模型（首次自动从 ultralytics GitHub 下载 yolo11n.pt 到当前目录）
    model = YOLO("yolo11n.pt")

    # 2. 训练：data 传 yaml 名会自动下载并解析；coco8 仅用于跑通流程，
    #    真实项目替换为自有数据 yaml
    model.train(
        data="coco8.yaml",
        epochs=EPOCHS,
        imgsz=IMGSZ,
        device=device,
        batch=16,
        project=str(SRC_DIR / "runs"),  # 结果统一保存到 runs/detect/train*
        name="yolo11n_coco8",
        exist_ok=True,
    )

    # 3. 验证：在 val 集计算 mAP
    metrics = model.val()
    print_metrics(metrics)

    # 4. 预测：拿几张验证图跑推理，结果图保存到 runs/detect/predict*
    images = find_sample_images("coco8")
    if images:
        results = model.predict(source=images, save=True, conf=0.25, name="yolo11n_predict")
        print(f"\n🖼️  预测 {len(images)} 张图，标注结果保存在:")
        print(f"   {Path(results[0].save_dir).resolve()}")

    print("\n💡 要点:")
    print("  1. mAP50-95 是检测核心指标（IoU 0.5~0.95 平均），>0.5 可用性较好")
    print("  2. 小数据集从预训练权重微调（本示例），比从零训练收敛快得多")
    print("  3. 部署导出: model.export(format='onnx'|'engine'|'openvino')")


if __name__ == "__main__":
    main()
