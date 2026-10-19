# YOLO 与常用模型训练流程教程

YOLO 全任务（检测/分割/分类/姿态/旋转框）+ RT-DETR + timm 迁移学习 + SAM + BERT，
每条流程配套**小数据集自动下载**与**使用场景推荐**，全部独立可运行。

## 1. 环境准备

```bash
uv sync     # 安装 ultralytics / timm / transformers / torch(cu130) 等
```

## 2. 训练流程总览（按需选跑）

| 脚本 | 任务 | 模型 | 小数据集 | 大小 | 训练时长* |
|------|------|------|----------|------|-----------|
| `yolo_detect.py` | 目标检测 | YOLO11n | COCO8（自动下载） | 2MB | <1min |
| `yolo_segment.py` | 实例分割 | YOLO11n-seg | COCO8-SEG（自动下载） | 2MB | ~1min |
| `yolo_classify.py` | 图像分类 | YOLO11n-cls | MNIST160（自动下载） | 1MB | <1min |
| `yolo_pose.py` | 姿态估计 | YOLO11n-pose | COCO8-POSE（自动下载） | 2MB | ~1min |
| `yolo_obb.py` | 旋转框检测 | YOLO11n-obb | DOTA8（自动下载） | 6MB | ~2min |
| `rtdetr_detect.py` | 目标检测 | RT-DETR-L | COCO8（复用） | - | ~2min |
| `timm_finetune.py` | 分类迁移学习 | ResNet18(timm) | Hymenoptera（自动下载） | 9MB | ~2min |
| `sam_zero_shot.py` | 零样本分割 | SAM ViT-B | 复用 COCO8 图片 | 375MB(权重) | 推理 |
| `bert_finetune.py` | 文本分类 | BERT-base | Emotion（HF 自动下载） | 5MB | ~3min |

*RTX 3090 参考时长；CPU 也能跑通（建议把脚本内 EPOCHS 调小）。

## 3. 使用场景推荐（选型速查）

| 你的任务 | 推荐方案 | 说明 |
|----------|----------|------|
| 找出物体位置+类别 | `yolo_detect` | 最通用；安防/质检/零售/驾驶辅助 |
| 需要像素级轮廓 | `yolo_segment` 或 `sam_zero_shot` | 医学勾画/遥感提取/抠图；无标注用 SAM |
| 整图判断类别 | `timm_finetune` / `yolo_classify` | 小样本首选 timm 迁移学习 |
| 人体关键点/动作 | `yolo_pose` | 健身纠正/跌倒检测/特效驱动 |
| 目标是斜置的（航拍/文档） | `yolo_obb` | 遥感/无人机/旋转文本 |
| 端侧部署、去 NMS | `rtdetr_detect` | Transformer 检测、管线简洁 |
| 文本情感/意图分类 | `bert_finetune` | 客服/审核/工单分类 |
| 加速分割标注 | `sam_zero_shot` | 点一下出掩码 → 转 YOLO-seg 标注 |

## 4. 快速开始

```bash
uv run yolo_detect.py      # 先跑检测打通流程（下载数据+权重+训练+评估+预测）
uv run yolo_segment.py     # 其余脚本同构，按需选跑
uv run timm_finetune.py
uv run bert_finetune.py    # HF 下载慢: export HF_ENDPOINT=https://hf-mirror.com
```

产物位置：
- 数据集：`./datasets/`（ultralytics 自动下载）
- 权重：`./`（如 yolo11n.pt）与 HF 缓存 `~/.cache/huggingface/`
- 训练曲线/权重/预测图：`./runs/<task>/<name>/`

## 5. 接入自有数据集（YOLO 任务）

1. **标注工具**：X-AnyLabeling（推荐，内置 SAM 辅助）/ labelImg（检测）/ labelme（分割+姿态）
2. **目录组织**（以检测为例）：
   ```text
   my_dataset/
     images/train/*.jpg   images/val/*.jpg
     labels/train/*.txt   labels/val/*.txt
   ```
3. **data yaml**（仿照自动下载的 `datasets/coco8/coco8.yaml`）：
   ```yaml
   path: ./my_dataset
   train: images/train
   val: images/val
   names:
     0: 缺陷
     1: 划痕
   ```
4. **训练**：`model.train(data="my.yaml", epochs=100, imgsz=640)`

数据量经验：检测每类 ≥150 张起步；分割每类 ≥200 张（掩码标注贵，用 SAM 预标注）。

## 6. 训练完成后：部署导出

```python
model = YOLO("runs/detect/yolo11n_coco8/weights/best.pt")
model.export(format="onnx")     # 通用部署
model.export(format="engine")   # TensorRT（NVIDIA 高性能）
model.export(format="openvino") # Intel CPU
```

## 7. 相关教程

- PyTorch 基础训练（表格/图片/点云）：`../pytorch/source/`
- Python / Rust 语言基础：`../python/`、`../rust/`
