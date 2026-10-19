"""YOLO11 实例分割训练示例（检测 + 像素级掩码）
数据集: COCO8-SEG —— ultralytics 官方迷你分割子集（8 张图、多边形掩码标注，自动下载）
模型:   YOLO11n-seg（换 -seg 后缀的 s/m/l/x 提升精度）

使用场景推荐:
  - 医学图像：器官/病灶轮廓勾画、细胞分割
  - 遥感：建筑物/农田/水体提取
  - 工业质检：划痕/污渍区域量化（面积/位置）
  - 机器人抓取：物体精确轮廓 → 抓取位姿
  - 背景 removal / 电商抠图、AR 虚拟试穿

与检测的差别:
  - 标注格式: 每个目标一行多边形坐标（x1,y1,x2,y2,... 归一化）
  - 标注工具推荐: labelme（输出 json 转 YOLO 格式）/ X-AnyLabeling / CVAT
  - 评价指标: 掩码 mAP（mask MAP），而非仅框 mAP

运行: uv run yolo_segment.py
"""

from pathlib import Path

from yolo_common import SRC_DIR, find_sample_images, get_device, print_metrics, setup_ultralytics

EPOCHS = 30
IMGSZ = 640


def main() -> None:
    setup_ultralytics()
    from ultralytics import YOLO

    device = get_device()

    # 分割模型权重名带 -seg 后缀
    model = YOLO("yolo11n-seg.pt")

    model.train(
        data="coco8-seg.yaml",
        epochs=EPOCHS,
        imgsz=IMGSZ,
        device=device,
        batch=16,
        project=str(SRC_DIR / "runs"),
        name="yolo11nseg_coco8seg",
        exist_ok=True,
    )

    # 验证：seg 模型的 metrics.seg_map 是掩码 mAP
    metrics = model.val()
    print_metrics(metrics)
    if hasattr(metrics, "seg") and hasattr(metrics.seg, "map"):
        print(f"📈 掩码 mAP50-95 = {metrics.seg.map:.4f}")

    images = find_sample_images("coco8-seg")
    if images:
        results = model.predict(source=images, save=True, conf=0.25, name="seg_predict")
        print(f"\n🖼️  分割结果保存在: {Path(results[0].save_dir).resolve()}")

    print("\n💡 要点:")
    print("  1. 分割标注成本高（多边形/掩码），可用 SAM 辅助预标注再人工修正")
    print("  2. 只需要'类别区域'不需要'实例'时，考虑语义分割（U-Net/DeepLab）")
    print("  3. 交互式零样本分割见 sam_zero_shot.py")


if __name__ == "__main__":
    main()
