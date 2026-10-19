# PyTorch 小数据集训练教程

三种最常见数据形态（表格 / 图片 / 激光点云）的下载与训练完整流程，每个示例独立可运行。

## 1. 环境准备

安装 uv（参考 https://uv.doczh.com/guides/integration/pytorch ），本项目使用 CUDA 13.0 版 PyTorch：

```bash
uv sync          # 创建虚拟环境并安装 torch/torchvision/torchaudio（自动选 cu130 源）
uv run main.py   # 环境自检：GPU 型号 / CUDA 版本 / 算力
```

GPU 版本切换：编辑 `pyproject.toml` 中 `pytorch-cu130` 的 index（如 `cu126`、`cpu`）后重新 `uv sync`。

## 2. 训练示例一览

| 示例 | 数据形态 | 数据集 | 大小 | 模型 | 场景推荐 |
|------|---------|--------|------|------|----------|
| `tabular_iris.py` | 表格 | UCI Iris（自动下载） | 4KB | MLP | 用户画像/风控/故障诊断；小表格任务建议先用 XGBoost 打基线 |
| `image_mnist.py` | 图片 | FashionMNIST（自动下载） | 30MB | CNN | 工业质检/医疗筛查/内容审核；检测任务见 `../yolo_/` |
| `pointcloud_shapes.py` | 激光点云 | 合成形状（离线可跑） | - | PointNet-mini | 自动驾驶 LiDAR/机器人抓取/测绘巡检 |

```bash
uv run tabular_iris.py       # 表格：下载 → 解析 → 标准化 → MLP 训练
uv run image_mnist.py        # 图片：自动下载 → CNN 训练 → 分类别评估
uv run pointcloud_shapes.py  # 点云：合成数据 → PointNet 训练
```

三个示例共用 `common.py`（设备选择 / 带进度的下载器 / 通用训练循环），
突出"**流程一致、数据不同**"：所有任务都是 下载 → 预处理 → DataLoader → 模型 → 训练循环 → 评估。

## 3. 点云真实数据集下载

本教程点云示例用合成数据保证离线可跑，接入真实数据时按需下载：

| 数据集 | 任务 | 大小 | 下载地址 |
|--------|------|------|----------|
| ModelNet10 | 物体分类（入门） | ~500MB | https://modelnet.cs.princeton.edu/ |
| ModelNet40 | 物体分类（标准） | ~2.2GB | 预处理版 https://shapenet.cs.stanford.edu/media/modelnet40_normal_resampled.zip |
| ShapeNetPart | 部件分割 | ~1.1GB | https://shapenet.cs.stanford.edu/ericyi/shapenetcore_partanno_segmentation_benchmark_v0.zip |
| KITTI 3D | 自动驾驶检测/配准 | ~30GB | http://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d |
| nuScenes | 多传感器融合 | ~300GB | https://www.nuscenes.org/nuscenes |

接入方式：实现一个返回 `(points[N,3], label)` 的 `Dataset` 子类替换 `ShapeCloudDataset`，训练代码不变。

## 4. 训练要点速查

- **表格**：数值特征标准化（只用训练集统计量）；类别特征用 Embedding；先试 GBDT
- **图片**：数据增强提升泛化；小数据用迁移学习（见 `../yolo_/source/timm_finetune.py`）
- **点云**：单位球归一化 + 固定点数；用 max 等对称函数保证点的顺序无关性
