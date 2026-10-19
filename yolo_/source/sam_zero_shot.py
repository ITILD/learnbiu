"""SAM 零样本交互式分割示例（Segment Anything，推理而非训练）
模型:   SAM ViT-B（sam_b.pt，375M 参数，首次自动从 ultralytics assets 下载）
        轻量替代: MobileSAM（mobile_sam.pt）/ FastSAM
数据:   复用已下载的 COCO8 图片（先跑过 yolo_detect.py）

使用场景推荐:
  - 半自动标注：点一下/框一下即出掩码 → 导出为 YOLO-seg/COCO 掩码标注，
    标注效率提升 5~10 倍（推荐 X-AnyLabeling 内置了 SAM）
  - 零样本分割：无训练数据也能拿到高质量掩码（医学影像/遥感/工业图像）
  - 数据增强：按掩码抠目标换背景、做 Copy-Paste 增强
  - 交互式抠图：电商商品图、演示 Demo

与 YOLO-seg 的关系:
  - SAM: 无需训练、点/框提示交互、不区分类别语义（"是什么"要另配分类器）
  - YOLO-seg: 需要标注训练、全自动输出类别掩码
  - 常见组合: SAM 预标注 → 人工修正 → 训练 YOLO-seg 上线

运行: uv run sam_zero_shot.py（先跑一次 yolo_detect.py 下载 coco8 图片）
"""

from pathlib import Path

from yolo_common import find_sample_images, setup_ultralytics


def main() -> None:
    setup_ultralytics()
    from ultralytics import SAM

    images = find_sample_images("coco8", n=1)
    if not images:
        print("❌ 未找到 coco8 图片，请先运行: uv run yolo_detect.py")
        return
    image = images[0]
    print(f"🖼️  测试图片: {image}")

    # 1. 加载模型（首次自动下载 sam_b.pt 到 weights/ 目录）
    model = SAM("sam_b.pt")

    # ---- 方式一：点提示（点哪分割哪）----
    # 两个前景提示点；labels 全 1 表示前景点（0 为背景点，可用来排除区域）
    results = model.predict(
        source=image, points=[[320, 320], [200, 400]], labels=[1, 1],
        save=True, name="sam_point",
    )
    _report("点提示", results)

    # ---- 方式二：框提示（框内分割出物体）----
    results = model.predict(source=image, bboxes=[100, 100, 500, 450], save=True, name="sam_box")
    _report("框提示", results)

    # ---- 方式三：整图自动分割（无提示，全部物体）----
    results = model.predict(source=image, save=True, name="sam_auto")
    _report("自动", results)

    print("\n💡 要点:")
    print("  1. SAM 不输出类别名，需配合分类器/人工确认语义")
    print("  2. 显存紧张换 mobile_sam.pt；追求速度换 FastSAM（yolov8n 为骨干）")
    print("  3. 导出掩码坐标: results[0].masks.xy 是多边形点集，可直接转 YOLO-seg 标注")


def _report(name: str, results) -> None:
    """打印分割结果摘要与保存路径"""
    n_masks = len(results[0].masks) if results[0].masks is not None else 0
    out = Path(results[0].save_dir)
    print(f"✅ {name}分割: 得到 {n_masks} 个掩码 → {out.resolve()}")


if __name__ == "__main__":
    main()
