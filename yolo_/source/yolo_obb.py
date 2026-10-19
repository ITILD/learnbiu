"""YOLO11 旋转框检测（OBB: Oriented Bounding Box）训练示例
数据集: DOTA8 —— 迷你遥感旋转框子集（8 张航拍图，自动下载）
模型:   YOLO11n-obb（-obb 后缀）

使用场景推荐:
  - 遥感检测：船舶/飞机/油罐/棒球场（DOTA 数据集原始任务）
  - 无人机巡检：光伏板/绝缘子/输电塔（倾斜拍摄目标）
  - 文档处理：旋转文本/发票/证照的版面定位
  - 工业自动化：传送带上任意朝向的零件定位抓取
  - 仓储物流：堆叠托盘/货物轮廓贴合

与水平框（HBB）的差别:
  - 框用 4 个角点或 (x,y,w,h,angle) 表示，能贴合斜置目标，定位精度高
  - 标注格式（每行）: class x1 y1 x2 y2 x3 y3 x4 y4（四个角点，归一化）
  - 标注工具: X-AnyLabeling（支持 OBB）/ roLabelImg / DOTA 官方工具

运行: uv run yolo_obb.py
"""

from pathlib import Path

from yolo_common import SRC_DIR, find_sample_images, get_device, print_metrics, setup_ultralytics

EPOCHS = 30
IMGSZ = 1024  # 遥感图目标小，分辨率建议 ≥1024


def main() -> None:
    setup_ultralytics()
    from ultralytics import YOLO

    device = get_device()

    model = YOLO("yolo11n-obb.pt")

    model.train(
        data="dota8.yaml",
        epochs=EPOCHS,
        imgsz=IMGSZ,
        device=device,
        batch=8,
        project=str(SRC_DIR / "runs"),
        name="yolo11nobb_dota8",
        exist_ok=True,
    )

    metrics = model.val()
    print_metrics(metrics)

    images = find_sample_images("dota8")
    if images:
        results = model.predict(source=images[:2], save=True, conf=0.25, name="obb_predict")
        print(f"\n🖼️  旋转框可视化保存在: {Path(results[0].save_dir).resolve()}")

    print("\n💡 要点:")
    print("  1. DOTA 原图巨大（4000×4000+），训练前需切片（SAHI 库）")
    print("  2. 目标不倾斜（如正拍道路监控）用普通检测即可，OBB 是为斜置目标设计")
    print("  3. 评估用 mAP50-95，角度贴合看预测框与 GT 的 IoU")


if __name__ == "__main__":
    main()
