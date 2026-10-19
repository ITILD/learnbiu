"""BERT 文本分类微调示例（HuggingFace Transformers）
数据集: dair-ai/emotion —— 英文推文情绪分类（6 类：悲伤/喜悦/喜爱/愤怒/恐惧/惊讶，约 2 万条）
下载:   HuggingFace datasets 自动下载（国内可 export HF_ENDPOINT=https://hf-mirror.com）
模型:   bert-base-uncased（110M 参数；中文任务换 bert-base-chinese / hfl/chinese-*)

使用场景推荐:
  - NLP 中用途最广的范式：情感分析、工单分类、垃圾评论/诈骗文本识别、
    意图识别（客服机器人）、新闻标签、合规审查
  - 序列标注（NER）与检索（向量库）任务同样基于 BERT 微调流程

中文替代数据集（同流程可直接替换）:
  - ChnSentiCorp（外卖/书籍评论情感 2 类）
  - THUCNews 新闻分类子集
  - 加载: load_dataset("lansinuote/ChnSentiCorp") 后换 tokenizer 为 bert-base-chinese

运行: uv run bert_finetune.py
"""

from __future__ import annotations

import numpy as np
from datasets import load_dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

MODEL_NAME = "bert-base-uncased"
DATASET_NAME = "dair-ai/emotion"  # 新版 datasets 要求 namespace/name 格式
EPOCHS = 2

# 数据集自带英文标签的中文对照（实际顺序以 features['label'].names 为准）
EN2ZH = {
    "sadness": "悲伤", "joy": "喜悦", "love": "喜爱",
    "anger": "愤怒", "fear": "恐惧", "surprise": "惊讶",
}


def main() -> None:
    # 1. 加载数据集（自动下载缓存；国内慢可先 export HF_ENDPOINT=https://hf-mirror.com）
    print(f"⬇️  加载数据集 {DATASET_NAME} …")
    ds = load_dataset(DATASET_NAME)

    # 标签顺序必须从数据集 features 读取，硬编码顺序容易和真实标签错位
    label_names = ds["train"].features["label"].names
    labels = [EN2ZH.get(n, n) for n in label_names]
    print(f"📊 数据: 训练 {len(ds['train'])} / 验证 {len(ds['validation'])} / "
          f"测试 {len(ds['test'])}，{len(labels)} 类")
    print(f"   标签: {list(zip(range(len(labels)), labels))}")
    print(f"   示例: {ds['train'][0]['text'][:50]}… → {labels[ds['train'][0]['label']]}")

    # 2. 分词（tokenizer 与模型必须配套）
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(batch: dict) -> dict:
        return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=64)

    tokenized = ds.map(tokenize, batched=True)

    # 3. 加载预训练模型 + 随机初始化的分类头
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=len(labels),
    )

    # 4. 训练参数（Trainer 封装了完整训练循环：日志/评估/断点续训）
    args = TrainingArguments(
        output_dir="runs/bert_emotion",
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=64,
        learning_rate=2e-5,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=50,
        report_to="none",  # 关闭 wandb 等外部上报
        fp16=True,         # GPU 混合精度加速
    )

    def compute_metrics(eval_pred) -> dict:
        logits, labels_ = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {"accuracy": float((preds == labels_).mean())}

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        compute_metrics=compute_metrics,
    )

    # 5. 训练 + 评估
    print(f"\n🚂 微调 {EPOCHS} epochs …")
    trainer.train()
    metrics = trainer.evaluate(tokenized["test"])
    print(f"\n📈 测试集准确率: {metrics['eval_accuracy']:.2%}")

    # 6. 用微调后的模型做预测演示
    texts = [
        "I am so happy today, everything is wonderful!",
        "This is the worst service I have ever experienced.",
        "I'm really nervous about the exam tomorrow.",
    ]
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=64, return_tensors="pt")
    outputs = model(**{k: v.to(model.device) for k, v in inputs.items()})
    preds = outputs.logits.argmax(-1).cpu().tolist()
    print("\n🔍 预测演示:")
    for text, p in zip(texts, preds):
        print(f"  [{labels[p]}] {text}")

    print("\n💡 要点:")
    print("  1. 分类微调 LR 通常 2e-5 ~ 5e-5，过大摧毁预训练知识")
    print("  2. 长文本 max_length 512 封顶，超长先截断/分段")
    print("  3. 换中文: MODEL_NAME='bert-base-chinese' + 中文数据集即可")


if __name__ == "__main__":
    main()
