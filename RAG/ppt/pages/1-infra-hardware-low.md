---
layout: default
---
<div class="mb-4 text-sm opacity-60">
01_AI Infra
</div>

### 硬件配置（基础）

| 组件 |  配置 | 说明 |
|------|----------|------|
| GPU | RTX 3090 24GB | VLLM部署模型GPU推理 |
| CPU | 16 核 | onnx模型支持CPU推理 |
| 内存 | 32 GB | 如涉及到结构化数据解析，需要较大的内存 |
| 存储 | 500GB NVMe SSD | 注意向量数据库索引增长，部分条件下索引可能占存储资料的1/3 |
| 网络 | 千兆网卡 |  |


