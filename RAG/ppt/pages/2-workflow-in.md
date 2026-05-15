---
layout: default
---
<div class="mb-4 text-sm opacity-60">
02_构建RAG系统
</div>

### 入库工作流
```mermaid
flowchart LR
    A[原始文档] --> B[解析] --> C[清洗] --> D[分块] --> E[Embedding] --> F[向量入库] --> G[索引] --> H[✅]
    D --- D1[固定] & D2[语义] & D3[重叠]
    F --- F1[Milvus/LanceDB] & F2[元数据] & F3[映射]
```