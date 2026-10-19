"""阶段一：基模预训练（Pre-training）
从海量无标注文本学习"下一个字符预测"，得到一个会"续写"的基模。

数据集: TinyStories 子集 —— 专为大模型训练设计的英文小故事语料
        （GPT-3.5 生成、词汇简单，1~10M 参数的小模型也能学会讲故事）
下载:   HF datasets 流式下载前 80k 条（约 70MB），缓存到 data/ 后离线复用

模型:   MiniGPT（6 层 × 4 头 × 256 维，约 5M 参数，字符级词表 ~100）
预算:   RTX 3090 实测约 3 分钟（6000 步，另含数据下载约 2 分钟，
        远低于 30 分钟上限；--max-minutes 保险丝会在超时前自动保存）

预训练学到了什么:
  - 字符级语言统计（spelling / 高频词搭配）
  - 句法结构（"Once upon a time" 开头，句子以 . ! ? 结尾）
  - 小故事的叙事套路（人物 → 事件 → 教训 → the end）
预训练学不到什么:
  - 听懂指令并回答（→ 阶段二 SFT）
  - 分辨回答好坏（→ 阶段三 DPO）
  - 低成本部署（→ 阶段四量化）

运行: uv run 1_pretrain.py
参数: --steps 6000 --max-minutes 25（保险丝）
"""

from __future__ import annotations

import argparse
import json
import math
import time
from itertools import islice

import torch
from datasets import load_dataset

from common import (
    CKPT_DIR,
    DATA_DIR,
    CharTokenizer,
    GPTConfig,
    MiniGPT,
    get_device,
    n_params,
    perplexity,
    save_checkpoint,
)

N_TRAIN = 80_000   # 训练故事数（约 70MB 文本）
N_VAL = 1_000      # 验证故事数
STEPS = 6_000      # 训练步数（3090 实测 6~8 分钟）
BATCH = 64         # 每步 batch × ctx_len 个 token
LR = 3e-3          # 小模型可以用较大的学习率
WARMUP = 200       # 学习率线性预热步数


def download_corpus() -> tuple[list[str], list[str]]:
    """流式下载 TinyStories 子集并缓存为 jsonl（二次运行离线可用）"""
    train_path = DATA_DIR / "tinystories_train.jsonl"
    val_path = DATA_DIR / "tinystories_val.jsonl"

    if train_path.exists() and val_path.exists():
        print(f"⏭️  语料已缓存: {train_path.name} / {val_path.name}")
        train = [json.loads(l)["text"] for l in train_path.read_text(encoding="utf-8").splitlines()]
        val = [json.loads(l)["text"] for l in val_path.read_text(encoding="utf-8").splitlines()]
        return train, val

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("⬇️  流式下载 TinyStories（国内慢可先 export HF_ENDPOINT=https://hf-mirror.com）…")

    def take(n: int, split: str) -> list[str]:
        ds = load_dataset("roneneldan/TinyStories", split=split, streaming=True)
        return [row["text"] for row in islice(ds, n)]

    train = take(N_TRAIN, "train")
    val = take(N_VAL, "validation")
    train_path.write_text("\n".join(json.dumps({"text": t}, ensure_ascii=False) for t in train), encoding="utf-8")
    val_path.write_text("\n".join(json.dumps({"text": t}, ensure_ascii=False) for t in val), encoding="utf-8")
    print(f"✅ 缓存: {len(train)} 训练 / {len(val)} 验证故事")
    return train, val


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=STEPS)
    parser.add_argument("--max-minutes", type=float, default=25, help="超时保险丝，到时自动保存退出")
    args = parser.parse_args()

    device = get_device()
    torch.manual_seed(42)

    # ---- 1. 数据 ----
    train_texts, val_texts = download_corpus()
    tokenizer = CharTokenizer("".join(train_texts[:20_000]))  # 词表用前 2 万条足够覆盖
    tokenizer.save(DATA_DIR / "tokenizer.json")
    print(f"🔤 词表大小: {tokenizer.vocab_size}")

    # 整个验证集拼成一条长文本（评测 PPL 用）
    val_tokens = torch.tensor(
        tokenizer.encode("\n".join(val_texts)), dtype=torch.long, device=device,
    )

    # ---- 2. 模型（5M 参数级最小基模）----
    cfg = GPTConfig(vocab_size=tokenizer.vocab_size, d_model=256, n_head=4, n_layer=6, ctx_len=384)
    model = MiniGPT(cfg).to(device)
    print(f"🧠 MiniGPT: {n_params(model) / 1e6:.2f}M 参数, {cfg.n_layer} 层 × {cfg.n_head} 头 × {cfg.d_model} 维, ctx={cfg.ctx_len}")

    # ---- 3. 优化器 + 余弦退火（warmup 后从 LR 衰减到 10%）----
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, betas=(0.9, 0.95), weight_decay=0.1)

    def lr_at(step: int) -> float:
        if step < WARMUP:
            return LR * step / WARMUP
        t = (step - WARMUP) / max(args.steps - WARMUP, 1)
        return 0.1 * LR + 0.45 * LR * (1 + math.cos(math.pi * t))

    # ---- 4. 把全部训练文本编码成一条 GPU 长序列，随机窗口采样 ----
    print("⚙️  预分词中…")
    all_tokens = tokenizer.encode("\n".join(train_texts))
    data = torch.tensor(all_tokens, dtype=torch.int32, device=device)  # 70M chars ≈ 280MB int32
    print(f"📊 语料 token 数: {len(data) / 1e6:.1f}M（{BATCH}×{cfg.ctx_len}={BATCH * cfg.ctx_len / 1e3:.0f}K tokens/步）")

    # ---- 5. 训练循环 ----
    print(f"\n🚂 预训练 {args.steps} 步（上限 {args.max_minutes} 分钟）")
    print(f"{'step':>6} {'loss':>7} {'lr':>8} {'PPL':>7} {'耗时':>8}")
    t0 = time.time()
    losses: list[float] = []

    for step in range(1, args.steps + 1):
        # 随机窗口: [B, ctx+1]，输入前 ctx 个，标签后移一位
        idx = torch.randint(0, len(data) - cfg.ctx_len - 1, (BATCH,), device=device)
        seq = data[torch.arange(cfg.ctx_len + 1, device=device) + idx.unsqueeze(1)]
        x, y = seq[:, :-1].long(), seq[:, 1:].long()

        for g in optimizer.param_groups:
            g["lr"] = lr_at(step)

        # bf16 自动混合精度（3090 原生支持，比 fp32 快一倍）
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=device.type == "cuda"):
            _, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(loss.item())

        # ---- 日志 + 保险丝 ----
        if step % 200 == 0 or step == args.steps:
            elapsed = (time.time() - t0) / 60
            ppl = perplexity(model, val_tokens[:50_000], cfg.ctx_len)
            print(f"{step:>6} {loss.item():>7.3f} {lr_at(step):>8.1e} {ppl:>7.2f} {elapsed:>7.1f}m")
            sample(model, tokenizer, device)
            if elapsed > args.max_minutes:  # 保险丝：确保总时长可控
                print(f"⏰ 触发 {args.max_minutes} 分钟保险丝，提前保存退出")
                break

    # ---- 6. 保存基模 ----
    save_checkpoint(
        CKPT_DIR / "base.pt", model, tokenizer,
        extra={"stage": "base", "losses": losses, "minutes": (time.time() - t0) / 60},
    )
    print(f"\n✅ 基模预训练完成，总耗时 {(time.time() - t0) / 60:.1f} 分钟")
    print("➡️  下一步: uv run 2_sft.py（指令微调）")


def sample(model: MiniGPT, tokenizer: CharTokenizer, device: torch.device) -> None:
    """看基模的'续写'能力：给故事开头，模型往下编"""
    prompt = tokenizer.encode("Once upon a time", bos=True)
    x = torch.tensor([prompt], device=device)
    out = model.generate(x, max_new_tokens=80, temperature=0.8, top_k=40)
    text = tokenizer.decode(out[0].tolist())
    print(f"     ✍️  {text[:100]}…")


if __name__ == "__main__":
    main()
