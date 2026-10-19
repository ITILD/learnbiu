"""YOLO11 图像分类训练示例（整图分类，无框）
数据集: MNIST160 —— ultralytics 官方迷你分类集（手写数字 0-9 共 160 张，自动下载）
模型:   YOLO11n-cls（-cls 后缀；参数量 1.5M，推理极快）

使用场景推荐:
  - 工业分拣：工件/药材/垃圾分类定向
  - OCR 前置路由：先分类文档类型再走对应解析管线
  - 内容审核：正常/违规图片粗筛
  - 医疗辅助：X 光/皮肤镜二分类初筛
  - 安防：通行场景正常/异常判断

与其他分类方案的选择:
  - 迁移学习见 timm_finetune.py（timm 模型库更丰富，分类任务的通用首选）
  - YOLO-cls 优势：与检测共用一套 API/部署链路，端侧推理极快
  - 标注成本最低：只需按类别分文件夹放图（ImageFolder 结构）

运行: uv run yolo_classify.py
"""

from pathlib import Path

from yolo_common import SRC_DIR, get_device, print_metrics, setup_ultralytics

EPOCHS = 30
IMGSZ = 64  # MNIST 是 28×28 小图，64 足够


def main() -> None:
    setup_ultralytics()
    from ultralytics import YOLO

    device = get_device()

    model = YOLO("yolo11n-cls.pt")

    # 分类数据集自动下载为 train/ val/ 两级类别目录
    model.train(
        data="mnist160",
        epochs=EPOCHS,
        imgsz=IMGSZ,
        device=device,
        batch=64,
        project=str(SRC_DIR / "runs"),
        name="yolo11ncls_mnist160",
        exist_ok=True,
    )

    # 验证：输出 Top-1 / Top-5
    metrics = model.val()
    print_metrics(metrics)

    # 预测：分类 predict 直接输出类别名
    images = sorted(str(p) for p in (SRC_DIR / "datasets" / "mnist160").rglob("*.jpg"))
    if images:
        results = model.predict(source=images[:4], save=True, name="cls_predict")
        print("\n🔍 预测结果:")
        for r in results:
            print(f"  {Path(r.path).name}: {r.probs.top1} ({r.names[r.probs.top1]})")
        print(f"🖼️  结果图保存在: {Path(results[0].save_dir).resolve()}")

    print("\n💡 要点:")
    print("  1. 自有数据只需 images/class_a/*.jpg、images/class_b/*.jpg 组织")
    print("  2. 分类任务数据增强：翻转/裁剪/色彩抖动收益最大")
    print("  3. 类别不平衡时关注 per-class 指标，不只看总体准确率")


if __name__ == "__main__":
    main()
