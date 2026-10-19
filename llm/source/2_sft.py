"""阶段二：指令微调（SFT, Supervised Fine-Tuning）
让只会"续写"的基模学会"听指令、给回答"。

数据集: Alpaca-Cleaned 子集 —— 经清洗的 Self-Instruct 英文指令数据
        （instruction + 可选 input + 期望回答 Output）
下载:   HF datasets 下载前 8000 条（约 5MB），缓存到 data/ 后离线复用

原理:
  - 把每条样本套进统一模板："### Instruction:…### Response:…"
  - 只对 Response 部分计算 loss（prompt 部分标签置 -100 掩码）
  - 模型从"接着写"变成"看到指令 → 生成回答"

训练配置:
  - 全参数微调，LR 降到 1e-4（预训练的 1/30，避免遗忘语言能力）
  - 2 epochs × 8000 条，3090 实测约 3~4 分钟

运行: uv run 2_sft.py
前置: 先运行 1_pretrain.py 生成 checkpoints/base.pt
"""

from __future__ import annotations

import json
import time

import torch
from datasets import load_dataset

from common import (
    CKPT_DIR,
    DATA_DIR,
    MiniGPT,
    build_prompt,
    load_checkpoint,
    save_checkpoint,
)

N_SAMPLES = 8_000
EPOCHS = 2
BATCH = 32
LR = 1e-4   # 微调学习率远小于预训练
MAX_PROMPT = 220   # 提示词最多保留的 token 数（超出截断中段）
MAX_RESPONSE = 150  # 回答最多保留的 token 数

DEMO_INSTRUCTIONS = [
    "Write a short story about a little girl and her dog.",
    "Give three tips for staying healthy.",
    "Explain what the sun is to a child.",
]


def download_sft_data() -> list[dict]:
    """下载 Alpaca-Cleaned 子集（instruction/input/output）"""
    path = DATA_DIR / "alpaca_8k.jsonl"
    if path.exists():
        print(f"⏭️  SFT 数据已缓存: {path.name}")
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("⬇️  下载 Alpaca-Cleaned 子集 …")
    ds = load_dataset("yahma/alpaca-cleaned", split="train")
    rows = [
        {"instruction": r["instruction"], "input": r["input"], "output": r["output"]}
        for r in list(ds)[:N_SAMPLES]
    ]
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    print(f"✅ 缓存 {len(rows)} 条指令数据")
    return rows


def encode_sample(
    row: dict, tokenizer, pad: int, eos: int, ctx_len: int
) -> tuple[torch.Tensor, torch.Tensor] | None:
    """一条样本 → (ids, labels)。labels 中 prompt 部分与填充位为 -100（不计 loss）。

    右填充 + 因果注意力的组合下，padding 在末尾不影响前面 token 的预测，
    因此无需 attention mask（教学上更简洁，生产上一般仍会加）。
    """
    prompt_ids = tokenizer.encode(build_prompt(row["instruction"], row["input"]))
    resp_ids = tokenizer.encode(row["output"])[:MAX_RESPONSE] + [eos]

    prompt_ids = prompt_ids[-MAX_PROMPT:]  # 提示过长则保尾部（离 Response 近的部分更重要）
    ids = prompt_ids + resp_ids
    if len(ids) < 8:  # 过短样本丢弃
        return None
    ids = ids[:ctx_len]
    labels = [-100] * len(prompt_ids) + resp_ids  # 只学 Response
    labels = labels[:ctx_len]

    # 右填充到 ctx_len
    pad_len = ctx_len - len(ids)
    ids += [pad] * pad_len
    labels += [-100] * pad_len
    return torch.tensor(ids), torch.tensor(labels)


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  设备: {device}")

    # ---- 1. 加载基模 ----
    if not (CKPT_DIR / "base.pt").exists():
        raise SystemExit("❌ 未找到 checkpoints/base.pt，请先运行 uv run 1_pretrain.py")
    model, tokenizer = load_checkpoint(CKPT_DIR / "base.pt", device)
    print(f"🧠 已加载基模（{sum(p.numel() for p in model.parameters()) / 1e6:.1f}M 参数）")

    # ---- 2. 数据 ----
    rows = download_sft_data()
    pad, eos = tokenizer.stoi[tokenizer.PAD], tokenizer.stoi[tokenizer.EOS]
    samples = [s for s in (encode_sample(r, tokenizer, pad, eos, model.cfg.ctx_len) for r in rows) if s]
    print(f"📊 SFT 样本: {len(samples)} 条, 每条定长 {model.cfg.ctx_len} token")
    xs = torch.stack([s[0] for s in samples]).to(device)
    ys = torch.stack([s[1] for s in samples]).to(device)

    # ---- 3. 微调前：基模面对指令的表现（只会续写，不懂回答）----
    print("\n🔴 微调前（基模 only 续写）:")
    demo(model, tokenizer, device, DEMO_INSTRUCTIONS[0])

    # ---- 4. 训练 ----
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, betas=(0.9, 0.95), weight_decay=0.0)
    n = len(xs)
    steps_per_epoch = (n + BATCH - 1) // BATCH
    total_steps = steps_per_epoch * EPOCHS
    print(f"\n🚂 SFT 微调 {EPOCHS} epochs（{total_steps} 步）")

    t0 = time.time()
    step = 0
    for epoch in range(EPOCHS):
        perm = torch.randperm(n, device=device)
        total_loss, nb = 0.0, 0
        for i in range(0, n, BATCH):
            idx = perm[i : i + BATCH]
            # 关键对齐：位置 i 的 logits 预测的是"下一个"token，
            # 所以标签要左移一位 —— labels[:,1][i] 正是 ids[i+1] 位置上的监督
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=device.type == "cuda"):
                _, loss = model(xs[idx][:, :-1], ys[idx][:, 1:])
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
            nb += 1
            step += 1
        print(f"  epoch {epoch + 1}/{EPOCHS}  loss={total_loss / nb:.4f}  已用 {(time.time() - t0) / 60:.1f} 分钟")

    # ---- 5. 微调后对比 ----
    print("\n🟢 微调后（能听指令了）:")
    for q in DEMO_INSTRUCTIONS:
        demo(model, tokenizer, device, q)

    # ---- 6. 保存 ----
    save_checkpoint(CKPT_DIR / "sft.pt", model, tokenizer, extra={"stage": "sft"})
    print("➡️  下一步: uv run 3_dpo.py（偏好强化）")


def demo(model: MiniGPT, tokenizer, device: torch.device, instruction: str) -> None:
    print(f"  Q: {instruction}")
    ids = tokenizer.encode(build_prompt(instruction))
    x = torch.tensor([ids], device=device)
    out = model.generate(x, max_new_tokens=120, temperature=0.7, top_k=40,
                         eos_token=tokenizer.stoi[tokenizer.EOS])
    print(f"  A: {tokenizer.decode(out[0].tolist()[len(ids):])[:150]}\n")


if __name__ == "__main__":
    main()
