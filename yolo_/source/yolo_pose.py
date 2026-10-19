"""YOLO11 人体姿态估计（关键点检测）训练示例
数据集: COCO8-POSE —— 迷你姿态子集（8 张图、每人 17 个 COCO 关键点，自动下载）
模型:   YOLO11n-pose（-pose 后缀）

使用场景推荐:
  - 健身/康复：深蹲/硬拉动作纠正、动作计数
  - 体育训练：高尔夫/游泳姿势分析
  - 行为识别前置：跌倒检测、打架告警、工位离岗
  - 直播/特效：虚拟形象驱动、AR 贴纸
  - 零售：顾客动线与停留分析

COCO 17 关键点: 鼻、双眼、双耳、双肩、双肘、双腕、双髋、双膝、双踝

标注格式（每行）:
  class x y w h kpt1_x kpt1_y kpt1_v kpt2_x kpt2_y kpt2_v ...
  （v=0 不可见/未标注, 1 遮挡, 2 可见）
  标注工具: Labelme + 关键点插件 / CVAT / X-AnyLabeling

运行: uv run yolo_pose.py
"""

from pathlib import Path

from yolo_common import SRC_DIR, find_sample_images, get_device, print_metrics, setup_ultralytics

EPOCHS = 50  # 关键点回归需要更多轮次收敛
IMGSZ = 640


def main() -> None:
    setup_ultralytics()
    from ultralytics import YOLO

    device = get_device()

    model = YOLO("yolo11n-pose.pt")

    model.train(
        data="coco8-pose.yaml",
        epochs=EPOCHS,
        imgsz=IMGSZ,
        device=device,
        batch=16,
        project=str(SRC_DIR / "runs"),
        name="yolo11npose_coco8pose",
        exist_ok=True,
    )

    metrics = model.val()
    print_metrics(metrics)
    # pose 指标：mAP50-95(P) 检测框 + mAP50-95(R) 关键点
    if hasattr(metrics, "pose") and hasattr(metrics.pose, "map"):
        print(f"📈 关键点 mAP50-95 = {metrics.pose.map:.4f}")

    images = find_sample_images("coco8-pose")
    if images:
        results = model.predict(source=images, save=True, conf=0.25, name="pose_predict")
        print(f"\n🖼️  骨架可视化保存在: {Path(results[0].save_dir).resolve()}")

    print("\n💡 要点:")
    print("  1. kpt_shape（关键点数/维度）必须与 data yaml 和标注一致")
    print("  2. 拿 2D 关键点算角度（如膝角）即可做动作判断，无需 3D")
    print("  3. 单人姿态可换 YOLO11n-pose 的 single-class 配置，精度更高")


if __name__ == "__main__":
    main()
