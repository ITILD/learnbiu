"""阶段四：INT8 权重量化（Quantization）
把 fp32 权重压到 int8：体积 -75%，CPU/端侧推理大幅提速，精度损失很小。

量化原理（动态 per-channel 权重量化）:
  - 量化:   w_int8 = round(w_fp32 / scale)，  scale = max|w| / 127 （每个输出通道一个 scale）
  - 反量化: w ≈ w_int8.to(float) * scale
  - "动态"指 scale 在加载时离线算好，激活值不量化（最简单的入门方案）

生产中的量化（README 有对比表）:
  - PTQ 训练后量化: GPTQ / AWQ / GGUF(llama.cpp) —— 4bit 主流，端侧部署标配
  - QAT 量化感知训练: 训练时插伪量化节点，精度最好但成本高

本脚本做三件事:
  1. 手写 Int8Linear 替换所有 nn.Linear（lm_head 与 embedding 共享权重，跳过）
  2. 对比 体积(fp32 vs int8) / 困惑度(量化前 vs 后) / 生成质量
  3. 保存量化模型，供 5_chat.py 使用

运行: uv run 4_quantize.py
前置: 先运行 3_dpo.py 生成 checkpoints/dpo.pt
"""

from __future__ import annotations

import time

import torch
import torch.nn as nn

from common import (
    CKPT_DIR,
    DATA_DIR,
    MiniGPT,
    build_prompt,
    load_checkpoint,
    n_params,
    perplexity,
    quantize_linear_layers,
    save_checkpoint,
)

DEMO_PROMPTS = [
    "Write a short story about a cat who learns to fly.",
    "Give three tips for staying healthy.",
]


def model_size_mb(model: nn.Module) -> float:
    """统计 state_dict 占用（int8 按 1 字节、fp32 按 4 字节估算）"""
    total = 0
    for p in model.state_dict().values():
        total += p.numel() * (1 if p.dtype == torch.int8 else 4)
    return total / 1e6


@torch.no_grad()
def gen_speed(model: MiniGPT, tokenizer, device: torch.device) -> float:
    """生成 128 token 的平均速度（tok/s）"""
    ids = tokenizer.encode(build_prompt(DEMO_PROMPTS[0]))
    x = torch.tensor([ids], device=device)
    model.generate(x, max_new_tokens=8)  # 预热
    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.time()
    model.generate(x, max_new_tokens=128)
    if device.type == "cuda":
        torch.cuda.synchronize()
    return 128 / (time.time() - t0)


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  设备: {device}")

    # ---- 1. 加载 DPO 模型（fp32 原始版）----
    if not (CKPT_DIR / "dpo.pt").exists():
        raise SystemExit("❌ 未找到 checkpoints/dpo.pt，请先运行 uv run 3_dpo.py")
    model, tokenizer = load_checkpoint(CKPT_DIR / "dpo.pt", device)
    print(f"🧠 DPO 模型: {n_params(model) / 1e6:.1f}M 参数")

    # 量化前基线（验证集文本 → PPL 基线）
    import json

    size_before = model_size_mb(model)
    val_path = DATA_DIR / "tinystories_val.jsonl"
    val_texts = "\n".join(
        json.loads(line)["text"] for line in val_path.read_text(encoding="utf-8").splitlines()
    )
    val_tokens = torch.tensor(
        tokenizer.encode(val_texts[:400_000]), dtype=torch.long, device=device,
    )
    ppl_before = perplexity(model, val_tokens, model.cfg.ctx_len)
    speed_before = gen_speed(model, tokenizer, device)
    print(f"\n📊 量化前(fp32): 体积 {size_before:.1f}MB | PPL {ppl_before:.3f} | 速度 {speed_before:.0f} tok/s")

    # ---- 2. 量化 ----
    model, n_quantized = quantize_linear_layers(model)
    print(f"\n⚙️  已量化 {n_quantized} 个 Linear 层 → INT8（per-channel 动态量化）")

    # ---- 3. 量化后对比 ----
    size_after = model_size_mb(model)
    ppl_after = perplexity(model, val_tokens, model.cfg.ctx_len)
    speed_after = gen_speed(model, tokenizer, device)
    print(f"📊 量化后(int8): 体积 {size_after:.1f}MB | PPL {ppl_after:.3f} | 速度 {speed_after:.0f} tok/s")
    print(f"\n📈 体积 {(1 - size_after / size_before):.0%} ↓  |  PPL +{ppl_after - ppl_before:.3f}  |  速度 {speed_after / speed_before:.2f}×")

    # ---- 4. 生成质量肉眼对比 ----
    print("\n✍️  量化模型生成示例:")
    for q in DEMO_PROMPTS:
        ids = tokenizer.encode(build_prompt(q))
        x = torch.tensor([ids], device=device)
        out = model.generate(x, max_new_tokens=100, temperature=0.7, top_k=40,
                             eos_token=tokenizer.stoi[tokenizer.EOS])
        print(f"  Q: {q}")
        print(f"  A: {tokenizer.decode(out[0].tolist()[len(ids):])[:130]}\n")

    # ---- 5. 保存量化模型（标记 quantized，加载时自动重建 Int8Linear 结构）----
    save_checkpoint(
        CKPT_DIR / "dpo_int8.pt", model, tokenizer,
        extra={"stage": "dpo_int8", "quantized": True},
    )
    print("💡 说明:")
    print("  1. GPU 上速度差异不明显（matmul 仍以 fp16 跑），int8 主要收益是显存/带宽")
    print("  2. 生产部署用 GPTQ/AWQ/GGUF 4bit（体积 -75%，CPU 提速数倍），原理与本例相同")
    print("  3. 对话体验: uv run 5_chat.py --model dpo_int8")


if __name__ == "__main__":
    main()
