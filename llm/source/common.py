"""大模型全流程教程 - 公共模块
从零实现（纯 PyTorch，不依赖 transformers）：
  - CharTokenizer   字符级分词器（理解"分词"最透明的入门方式）
  - MiniGPT         decoder-only Transformer（GPT 结构最小完整实现）
  - generate()      自回归采样生成（temperature / top-k / top-p）
  - perplexity()    困惑度评估（语言模型标准指标）
  - 保存/加载 checkpoint（配置 + 权重 + 词表 一体化）

被 1_pretrain / 2_sft / 3_dpo / 4_quantize / 5_chat 共用。
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
import torch.nn.functional as F

SRC_DIR = Path(__file__).parent
DATA_DIR = SRC_DIR / "data"
CKPT_DIR = SRC_DIR / "checkpoints"


# ================================================================ #
#                         字符级分词器                              #
# ================================================================ #
class CharTokenizer:
    """字符级分词器：一个字符 = 一个 token。

    为什么用字符级？
    - BPE/SentencePiece 词表动辄数万，而字符级英文只需 ~100 个 token，
      嵌入参数少 400 倍，最适合训练"最小的基模"
    - 没有黑盒：encode/decode 就是一张查表，便于理解 token 边界
    - 代价：同样文本 token 数更多（~4 倍于 BPE），生产模型都用子词级
    """

    PAD, BOS, EOS, UNK = "<pad>", "<bos>", "<eos>", "<unk>"

    def __init__(self, text: str | None = None):
        if text is not None:  # 从语料构建词表
            chars = sorted(set(text))
            self.itos: list[str] = [self.PAD, self.BOS, self.EOS, self.UNK, *chars]
        self.stoi: dict[str, int] = {c: i for i, c in enumerate(self.itos)}

    # ---- 编解码 ----
    def encode(self, s: str, bos: bool = False, eos: bool = False) -> list[int]:
        ids = [self.stoi.get(c, self.stoi[self.UNK]) for c in s]
        if bos:
            ids = [self.stoi[self.BOS], *ids]
        if eos:
            ids = [*ids, self.stoi[self.EOS]]
        return ids

    def decode(self, ids: list[int]) -> str:
        special = {self.stoi[k] for k in (self.PAD, self.BOS, self.EOS)}
        return "".join(self.itos[i] for i in ids if i not in special)

    # ---- 持久化 ----
    @property
    def vocab_size(self) -> int:
        return len(self.itos)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.itos, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "CharTokenizer":
        tok = cls.__new__(cls)  # 跳过 __init__（不传 text）
        tok.itos = json.loads(path.read_text(encoding="utf-8"))
        tok.stoi = {c: i for i, c in enumerate(tok.itos)}
        return tok


# ================================================================ #
#                     MiniGPT 模型（GPT 结构）                      #
# ================================================================ #
@dataclass
class GPTConfig:
    """模型超参数：5M 量级"最小基模"的参考配置见各脚本头部"""

    vocab_size: int = 100
    d_model: int = 256      # 隐藏维度
    n_head: int = 4         # 注意力头数（d_model 必须能被 n_head 整除）
    n_layer: int = 6        # Transformer 层数
    ctx_len: int = 384      # 上下文长度（训练与推理统一）

    def n_params(self) -> int:
        """估算参数量（不含 tying 的 lm_head）"""
        d, l = self.d_model, self.n_layer
        emb = self.vocab_size * d + self.ctx_len * d
        per_layer = 4 * d * d + 2 * d * 4 * d + 4 * d  # attn + mlp + norms
        return emb + l * per_layer


class CausalSelfAttention(torch.nn.Module):
    """因果自注意力：只允许看过去，不看未来（LM 的核心约束）"""

    def __init__(self, cfg: GPTConfig):
        super().__init__()
        assert cfg.d_model % cfg.n_head == 0
        self.n_head = cfg.n_head
        self.head_dim = cfg.d_model // cfg.n_head
        self.qkv = torch.nn.Linear(cfg.d_model, 3 * cfg.d_model)
        self.proj = torch.nn.Linear(cfg.d_model, cfg.d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape
        qkv = self.qkv(x)  # [B, T, 3C]
        q, k, v = qkv.split(C, dim=2)
        # 拆头: [B, T, C] → [B, n_head, T, head_dim]
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        # Flash Attention（sdpa 内核自动选择，is_causal 生成下三角掩码）
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(y)


class MLP(torch.nn.Module):
    """前馈网络：4 倍扩展 + GELU（GPT-2 起的标准配置）"""

    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(cfg.d_model, 4 * cfg.d_model),
            torch.nn.GELU(),
            torch.nn.Linear(4 * cfg.d_model, cfg.d_model),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(x)


class Block(torch.nn.Module):
    """Pre-LN Transformer 块：x + Attn(LN(x)) → x + MLP(LN(x))"""

    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.ln1 = torch.nn.LayerNorm(cfg.d_model)
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = torch.nn.LayerNorm(cfg.d_model)
        self.mlp = MLP(cfg)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class MiniGPT(torch.nn.Module):
    """decoder-only 语言模型（GPT 系列的最小完整实现）

    结构: tok_emb + pos_emb → N × Block → LayerNorm → lm_head(与 tok_emb 共享权重)
    权重共享（weight tying）是小词表模型的标配，省参数且提效果。
    """

    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = torch.nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.pos_emb = torch.nn.Embedding(cfg.ctx_len, cfg.d_model)
        self.blocks = torch.nn.ModuleList(Block(cfg) for _ in range(cfg.n_layer))
        self.ln_f = torch.nn.LayerNorm(cfg.d_model)
        self.lm_head = torch.nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        self.lm_head.weight = self.tok_emb.weight  # weight tying

        # GPT-2 风格初始化
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(m: torch.nn.Module) -> None:
        if isinstance(m, (torch.nn.Linear, torch.nn.Embedding)):
            torch.nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if isinstance(m, torch.nn.Linear) and m.bias is not None:
                torch.nn.init.zeros_(m.bias)

    def forward(
        self,
        ids: torch.Tensor,               # [B, T] 输入 token
        targets: torch.Tensor | None = None,  # [B, T] 右移一位的标签（-100 处不计 loss）
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        B, T = ids.shape
        assert T <= self.cfg.ctx_len, f"序列长度 {T} 超过 ctx_len {self.cfg.ctx_len}"
        pos = torch.arange(T, device=ids.device)

        x = self.tok_emb(ids) + self.pos_emb(pos)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)  # [B, T, vocab]

        loss = None
        if targets is not None:
            # reshape 而非 view：兼容调用方传入切片后的非连续张量
            loss = F.cross_entropy(
                logits.reshape(-1, logits.size(-1)), targets.reshape(-1), ignore_index=-100,
            )
        return logits, loss

    @torch.no_grad()
    def generate(
        self,
        ids: torch.Tensor,             # [B, T] 提示词
        max_new_tokens: int = 200,
        temperature: float = 0.8,
        top_k: int | None = 40,
        top_p: float | None = None,
        eos_token: int | None = None,
    ) -> torch.Tensor:
        """自回归采样：逐 token 预测 → 采样 → 拼接 → 再预测"""
        self.eval()
        for _ in range(max_new_tokens):
            # 滑窗截断，保证不超过 ctx_len
            ctx = ids[:, -self.cfg.ctx_len:]
            logits, _ = self(ctx)
            logits = logits[:, -1, :] / max(temperature, 1e-5)

            if top_k is not None:  # 只在概率最高的 k 个里采样
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float("inf")

            if top_p is not None:  # 核采样：累计概率 < p 的截断
                sorted_logits, sorted_idx = torch.sort(logits, descending=True)
                cum = torch.softmax(sorted_logits, dim=-1).cumsum(dim=-1)
                mask = cum - torch.softmax(sorted_logits, dim=-1) >= top_p
                sorted_logits[mask] = -float("inf")
                logits = torch.full_like(logits, -float("inf")).scatter(1, sorted_idx, sorted_logits)

            probs = torch.softmax(logits, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)
            ids = torch.cat([ids, next_id], dim=1)
            if eos_token is not None and (next_id == eos_token).all():
                break
        return ids


# ================================================================ #
#                          评估与保存                                #
# ================================================================ #
@torch.no_grad()
def perplexity(model: MiniGPT, tokens: torch.Tensor, ctx_len: int, stride: int = 256) -> float:
    """困惑度 PPL = exp(交叉熵)：模型对验证文本的"困惑程度"，越低越好。

    滑窗评测：每 stride 步取一个 ctx_len 窗口，覆盖整段文本。
    """
    model.eval()
    device = next(model.parameters()).device
    nll, n_tokens = 0.0, 0
    for start in range(0, max(len(tokens) - ctx_len - 1, 1), stride):
        chunk = tokens[start : start + ctx_len + 1].to(device)
        if len(chunk) < 2:
            continue
        x, y = chunk[:-1].unsqueeze(0), chunk[1:].unsqueeze(0)
        _, loss = model(x, y)
        nll += loss.item() * y.numel()
        n_tokens += y.numel()
    return math.exp(nll / max(n_tokens, 1))


def save_checkpoint(path: Path, model: MiniGPT, tokenizer: CharTokenizer, extra: dict | None = None) -> None:
    """一体化保存：配置 + 权重 + 词表 + 附加信息（如训练 loss 曲线）"""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": asdict(model.cfg),
        "state_dict": model.state_dict(),
        "vocab": tokenizer.itos,
        **(extra or {}),
    }
    torch.save(payload, path)
    print(f"💾 保存: {path.name}（{path.stat().st_size / 1e6:.1f}MB）")


def load_checkpoint(path: Path, device: torch.device | str = "cpu") -> tuple[MiniGPT, CharTokenizer]:
    """加载 checkpoint，重建模型与分词器（自动感知 INT8 量化结构）"""
    payload = torch.load(path, map_location=device, weights_only=False)
    cfg = GPTConfig(**payload["config"])
    model = MiniGPT(cfg).to(device)
    if payload.get("quantized"):  # 量化模型的 Linear 层结构不同，先替换再载入
        model, _ = quantize_linear_layers(model)
    model.load_state_dict(payload["state_dict"])
    tokenizer = CharTokenizer.__new__(CharTokenizer)
    tokenizer.itos = payload["vocab"]
    tokenizer.stoi = {c: i for i, c in enumerate(tokenizer.itos)}
    model.eval()
    return model, tokenizer


# ================================================================ #
#                     INT8 动态量化（手写实现）                      #
# ================================================================ #
class Int8Linear(torch.nn.Module):
    """存储 int8 权重 + 每通道 scale，forward 时反量化计算。

    权重: [out, in] int8  （原 fp32 的 1/4 体积）
    scale: [out, 1] float（每输出通道一个缩放因子）
    """

    def __init__(self, linear: torch.nn.Linear):
        super().__init__()
        w = linear.weight.detach().float()
        scale = w.abs().amax(dim=1, keepdim=True) / 127.0
        scale = scale.clamp(min=1e-8)  # 防止全零通道除零
        self.register_buffer("w_int8", torch.round(w / scale).clamp(-127, 127).to(torch.int8))
        self.register_buffer("scale", scale.to(torch.float16))
        self.bias = linear.bias

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.w_int8.to(x.dtype) * self.scale.to(x.dtype)
        return F.linear(x, w, self.bias)


def quantize_linear_layers(model: MiniGPT) -> tuple[MiniGPT, int]:
    """把模型中所有 nn.Linear 替换为 Int8Linear（lm_head 与 embedding 共享权重，跳过）。

    返回（模型, 被量化的层数）。从 checkpoint 重建时占位权重随即被覆盖。
    """
    count = 0

    def replace_children(module: torch.nn.Module) -> None:
        nonlocal count
        for name, child in module.named_children():
            if isinstance(child, torch.nn.Linear) and child.weight.data_ptr() == model.lm_head.weight.data_ptr():
                continue  # weight-tied 层不可单独量化
            if isinstance(child, torch.nn.Linear):
                setattr(module, name, Int8Linear(child))
                count += 1
            else:
                replace_children(child)

    replace_children(model)
    return model, count


def n_params(model: torch.nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


# ================================================================ #
#                    指令模板（SFT/DPO/Chat 共用）                  #
# ================================================================ #
# Alpaca 风格模板：SFT 学的就是"模板之后跟着回答"这个格式
PROMPT_TEMPLATE = (
    "Below is an instruction that describes a task. "
    "Write a response that appropriately completes the request.\n\n"
    "### Instruction:\n{instruction}\n\n### Response:\n"
)


def build_prompt(instruction: str, inp: str = "") -> str:
    """拼接提示词（input 字段为 alpaca 数据集的可选补充输入）"""
    q = instruction + (f"\n{inp}" if inp else "")
    return PROMPT_TEMPLATE.format(instruction=q)


def get_device() -> torch.device:
    if torch.cuda.is_available():
        print(f"🖥️  使用 GPU: {torch.cuda.get_device_name(0)}")
        return torch.device("cuda")
    print("🖥️  使用 CPU（预训练会远超 30 分钟，建议 GPU）")
    return torch.device("cpu")
