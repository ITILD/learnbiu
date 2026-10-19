"""阶段三：偏好强化（DPO, Direct Preference Optimization）
让模型学会"在两个回答里更喜欢好的那个"，对齐人类偏好。

为什么是 DPO 而不是 RLHF-PPO:
  经典 RLHF = 训练奖励模型 + PPO 强化学习（要 4 个模型同时在显存，工程复杂）
  DPO（2023, Stanford）数学上等价于 RLHF 的目标，但只需:
    1. 策略模型（被训练）
    2. 参考模型（SFT 冻结副本）
  用"好答案 vs 坏答案"的偏好对直接优化，稳定、省显存 —— 小规模对齐首选。

数据集: Intel/orca_dpo-pairs 子集 —— 同一 question 配对 chosen/rejected 回答
        （约 12k 对，取 3000 对演示）
损失:   L = -log σ( β · [ (π_c - π_r) - (π_c^ref - π_r^ref) ] )
        直觉：让策略模型相对参考模型，更偏好 chosen 的提升量 > rejected 的提升量

训练配置: 3000 对 × 2 epochs，3090 实测约 3~5 分钟
运行: uv run 3_dpo.py
前置: 先运行 2_sft.py 生成 checkpoints/sft.pt
"""

from __future__ import annotations

import json
import time
from itertools import islice

import torch
import torch.nn.functional as F
from datasets import load_dataset

from common import (
    CKPT_DIR,
    DATA_DIR,
    MiniGPT,
    build_prompt,
    load_checkpoint,
    save_checkpoint,
)

N_PAIRS = 3_000
EPOCHS = 1         # 偏好对差异明显，多 epoch 会把 margin 推爆 → 生成崩坏（见文末要点）
BATCH = 8          # 每批 8 对 = 16 条序列（chosen+rejected 拼在一起算）
LR = 5e-6          # 保守学习率：DPO 极易过度优化（KL 失控），宁欠勿过
BETA = 0.2         # 偏好强度系数（KL 惩罚的倒数角色）
NLL_COEF = 0.2     # chosen 的 NLL 正则系数（ln-DPO 技巧，防止两边概率一起被推崩）
MAX_PROMPT = 120   # 提示词 token 截断
MAX_RESPONSE = 200  # 回答 token 截断


def download_dpo_data() -> list[dict]:
    """下载 orca dpo 偏好对子集"""
    path = DATA_DIR / "orca_dpo_3k.jsonl"
    if path.exists():
        print(f"⏭️  DPO 数据已缓存: {path.name}")
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("⬇️  下载 orca-dpo-pairs 子集 …")
    ds = load_dataset("Intel/orca_dpo_pairs", split="train", streaming=True)
    rows = [
        {"question": r["question"], "chosen": r["chosen"], "rejected": r["rejected"]}
        for r in islice(ds, N_PAIRS)
    ]
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    print(f"✅ 缓存 {len(rows)} 个偏好对")
    return rows


def encode_pair(
    row: dict, tokenizer, eos: int, ctx_len: int
) -> tuple[torch.Tensor, torch.Tensor] | None:
    """一对样本 → (ids, labels) × 2（chosen / rejected），格式与 SFT 完全一致。

    与 SFT 相同的右填充约定：ids 补 PAD，labels 补 -100。
    """
    prompt_ids = tokenizer.encode(build_prompt(row["question"]))[-MAX_PROMPT:]

    def pack(resp: str) -> tuple[torch.Tensor, torch.Tensor]:
        resp_ids = tokenizer.encode(resp)[:MAX_RESPONSE] + [eos]
        ids = (prompt_ids + resp_ids)[:ctx_len]
        labels = ([-100] * len(prompt_ids) + resp_ids)[:ctx_len]
        pad_len = ctx_len - len(ids)
        ids += [tokenizer.stoi[tokenizer.PAD]] * pad_len
        labels += [-100] * pad_len
        return torch.tensor(ids), torch.tensor(labels)

    c_ids, c_lab = pack(row["chosen"])
    r_ids, r_lab = pack(row["rejected"])
    if len(c_ids) < 10 or len(r_ids) < 10:
        return None
    return c_ids, c_lab, r_ids, r_lab  # type: ignore[return-value]


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  设备: {device}")

    # ---- 1. 策略模型 = SFT；参考模型 = SFT 冻结副本 ----
    if not (CKPT_DIR / "sft.pt").exists():
        raise SystemExit("❌ 未找到 checkpoints/sft.pt，请先运行 uv run 2_sft.py")
    policy, tokenizer = load_checkpoint(CKPT_DIR / "sft.pt", device)
    ref, _ = load_checkpoint(CKPT_DIR / "sft.pt", device)
    for p in ref.parameters():
        p.requires_grad_(False)
    print(f"🧠 策略模型 + 冻结参考模型（各 {sum(p.numel() for p in policy.parameters()) / 1e6:.1f}M 参数）")

    # ---- 2. 数据 ----
    rows = download_dpo_data()
    eos = tokenizer.stoi[tokenizer.EOS]
    pairs = [p for p in (encode_pair(r, tokenizer, eos, policy.cfg.ctx_len) for r in rows) if p]
    print(f"📊 偏好对: {len(pairs)} 对（chosen/rejected 各一条序列）")

    c_ids = torch.stack([p[0] for p in pairs]).to(device)
    c_lab = torch.stack([p[1] for p in pairs]).to(device)
    r_ids = torch.stack([p[2] for p in pairs]).to(device)
    r_lab = torch.stack([p[3] for p in pairs]).to(device)

    # ---- 3. 训练 ----
    optimizer = torch.optim.AdamW(policy.parameters(), lr=LR, weight_decay=0.0)
    n = len(c_ids)
    print(f"\n🚂 DPO 训练 {EPOCHS} epochs（β={BETA}）")
    print(f"{'epoch':>6} {'dpo_loss':>9} {'acc(πc>πr)':>11} {'margin':>8}")

    t0 = time.time()
    for epoch in range(EPOCHS):
        perm = torch.randperm(n, device=device)
        losses, accs, margins = [], [], []
        for i in range(0, n, BATCH):
            idx = perm[i : i + BATCH]

            # 策略模型的前向（chosen/rejected 拼成一个 batch 少算一次）
            ids = torch.cat([c_ids[idx], r_ids[idx]])
            labs = torch.cat([c_lab[idx], r_lab[idx]])
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=device.type == "cuda"):
                logits, _ = policy(ids[:, :-1])
                logp = F.log_softmax(logits.float(), dim=-1)
                tgt, mask = labs[:, 1:], labs[:, 1:] != -100
                token_lp = logp.gather(-1, tgt.clamp(min=0).unsqueeze(-1)).squeeze(-1)
                pol = (token_lp * mask).sum(1)
                pi_c, pi_r = pol[: len(idx)], pol[len(idx):]

            # 参考模型前向（no_grad）
            with torch.no_grad():
                logits_r, _ = ref(ids[:, :-1])
                logp_r = F.log_softmax(logits_r.float(), dim=-1)
                token_lr = logp_r.gather(-1, tgt.clamp(min=0).unsqueeze(-1)).squeeze(-1)
                ref_lp = (token_lr * mask).sum(1)
                ref_c, ref_r = ref_lp[: len(idx)], ref_lp[len(idx):]

            # DPO 损失: -log σ(β·[(πc-πr) - (refc-refr)])
            logits_dpo = BETA * ((pi_c - pi_r) - (ref_c - ref_r))
            dpo_loss = -F.logsigmoid(logits_dpo).mean()

            # NLL 正则：chosen 的每 token 平均负对数似然（防止概率被整体推崩）
            n_tok_c = mask[: len(idx)].sum().clamp(min=1)
            nll_chosen = -(pi_c.sum() / n_tok_c)
            loss = dpo_loss + NLL_COEF * nll_chosen

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
            optimizer.step()

            losses.append(loss.item())
            accs.append((logits_dpo > 0).float().mean().item())
            margins.append((pi_c - pi_r).mean().item())

        print(f"{epoch + 1:>6} {sum(losses) / len(losses):>9.4f} "
              f"{sum(accs) / len(accs):>11.2%} {sum(margins) / len(margins):>8.2f}  "
              f"({(time.time() - t0) / 60:.1f}m)")

    # ---- 4. SFT vs DPO 生成对比 ----
    print("\n🔵 SFT 模型回答:")
    compare(ref, tokenizer, device)
    print("🟣 DPO 模型回答（同样问题，对比语气/结构变化）:")
    compare(policy, tokenizer, device)

    # ---- 5. 保存 ----
    save_checkpoint(CKPT_DIR / "dpo.pt", policy, tokenizer, extra={"stage": "dpo"})
    print("💡 要点:")
    print("  1. margin 正常范围 ~1-10 nats；若冲到上百说明过度优化，生成会崩成乱码")
    print("     （对策: 降 LR / 减 epoch / 增大 β 加强 KL 约束）")
    print("  2. 本教程数据 chosen/rejected 差异明显，1 epoch 即可到 90%+ 隐式准确率")
    print("  3. 真实场景: 偏好标注成本高，常用大模型蒸馏或规则构造偏好对")
    print("➡️  下一步: uv run 4_quantize.py（INT8 量化）")


def compare(model: MiniGPT, tokenizer, device: torch.device) -> None:
    for q in ["Give three tips for staying healthy.",
              "Name two colors and explain why you like them."]:
        ids = tokenizer.encode(build_prompt(q))
        x = torch.tensor([ids], device=device)
        out = model.generate(x, max_new_tokens=100, temperature=0.7, top_k=40,
                             eos_token=tokenizer.stoi[tokenizer.EOS])
        print(f"  Q: {q}\n  A: {tokenizer.decode(out[0].tolist()[len(ids):])[:130]}\n")


if __name__ == "__main__":
    main()
