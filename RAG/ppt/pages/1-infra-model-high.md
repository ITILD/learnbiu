---
layout: default
---
<div class="mb-4 text-sm opacity-60">
01_AI Infra
</div>

### 本地模型选型（推荐）

| 模型类型 | 模型名 | 硬件占用 |
|------|------|------|
|Embedding|Qwen3-Embedding-8B-fp16|~16GB 显存|
|Chat|Qwen3.5-122B-A10B|~200GB 显存(开满256K-1M上下文显存上浮 30%-50%)|
|Reranker|BGE-Reranker-v2-m3|~2GB 显存|
|ASR|Qwen3-ASR-1.7B|~6GB 显存|
|TTS|Qwen3-TTS-1.7B|~6GB 显存|

<div class="mb-4 text-sm opacity-80">
备注：理论算力100TFLOPS左右,瓶颈在于KV Cache根据上下文浮动
2（K+V 双张量） × 100（并发数） × 4096（token数） × 80（模型深度） 
× 8（头数） × 128（头宽度/单头维度） × 2（FP16 KV张量） ÷ 1024³（B转GB） 
× 1.42 (补偿 页表碎片 + 动态预分配 + 框架元数据 等额外开销) 约180GG，总显存占用约400GB
</div>
