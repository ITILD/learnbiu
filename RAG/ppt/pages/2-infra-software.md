---
layout: default
---
<div class="mb-4 text-sm opacity-60">
02_构建RAG系统
</div>

### 软件栈

| 层级 | 组件 | 说明 |
|------|------|------|
| API 网关 | Nginx + FastAPI | 异步高并发，限流 & 负载均衡 |
| LLM 推理 | vLLM | 连续批处理（Continuous Batching），吞吐提升 10×+ |
| LLM 应用框架 | LangGraph | 基于 LangGraph 框架，支持模型配置和复杂工作流 |
| Embedding | TEI（Text Embeddings Inference） | 专用嵌入推理，支持动态批处理 |
| 向量库 | Milvus / Qdrant | 支持 IVF+PQ 索引，百万级向量毫秒检索 |
| 缓存 | Redis | 语义缓存，相似问题直接返回，命中率 30%+ |
| 消息队列 | RabbitMQ / Redis Streams | 削峰填谷，防止突发流量打垮模型 |
