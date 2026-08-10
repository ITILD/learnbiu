---
layout: default
---
<div class="mb-4 text-sm opacity-60">
01_AI Infra
</div>

### 本地模型选型（基础）

| 模型类型  | 模型名             | 硬件占用  |
| --------- | ------------------ | --------- |
| Embedding | Qwen3-Embedding-0.6b-fp16 | ~1.2GB 显存 |
| Chat       | Qwen3.6-27B-AWQ-INT4/Qwen3.6-35B-A3B-UD-Q4_K_M    | 20~24GB 显存 |
| Reranker  | BGE-Reranker-v2-m3 | ~2GB 显存 |
| ASR       | sherpa-onnx        | cpu       |
| TTS       | sherpa-onnx        | cpu       |
