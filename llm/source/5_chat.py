"""阶段五：交互对话入口（全流程成果验收）
加载任一阶段的模型进行对话/续写，直观对比四个阶段的行为差异。

运行:
  uv run 5_chat.py                      # 默认加载 DPO 模型，交互式对话
  uv run 5_chat.py --model base         # 基模：只会续写（输入故事开头）
  uv run 5_chat.py --model sft          # SFT：能听指令
  uv run 5_chat.py --model dpo_int8     # 量化模型：体积 1/4 的 DPO
  uv run 5_chat.py --prompt "..."       # 单轮模式（脚本化测试）
"""

from __future__ import annotations

import argparse
import time

import torch

from common import CKPT_DIR, build_prompt, load_checkpoint

MODELS = ("base", "sft", "dpo", "dpo_int8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=MODELS, default="dpo", help="加载哪个阶段的模型")
    parser.add_argument("--prompt", default=None, help="单轮模式：直接给出提示词")
    parser.add_argument("--max-tokens", type=int, default=150)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = CKPT_DIR / f"{args.model}.pt"
    if not ckpt.exists():
        raise SystemExit(f"❌ 未找到 {ckpt}，请先按顺序运行 1~4 阶段脚本")

    model, tokenizer = load_checkpoint(ckpt, device)
    print(f"🧠 已加载 {args.model}.pt，输入内容开始对话（quit 退出）\n")

    eos = tokenizer.stoi[tokenizer.EOS]

    def reply(user: str) -> None:
        # base 模型没学过模板，直接续写；其他模型走指令模板
        text = user if args.model == "base" else build_prompt(user)
        ids = tokenizer.encode(text)
        x = torch.tensor([ids], device=device)
        t0 = time.time()
        out = model.generate(x, max_new_tokens=args.max_tokens, temperature=0.7, top_k=40, eos_token=eos)
        answer = tokenizer.decode(out[0].tolist()[len(ids):])
        dt = time.time() - t0
        n_new = out.size(1) - len(ids)
        print(f"🤖 {answer.strip()}\n   ({n_new} tok, {n_new / max(dt, 1e-6):.1f} tok/s)\n")

    if args.prompt:  # 单轮模式
        reply(args.prompt)
        return

    while True:
        try:
            user = input("👤 ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user or user.lower() in {"quit", "exit", "q"}:
            break
        reply(user)

    print("👋 再见")


if __name__ == "__main__":
    main()
