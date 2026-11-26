"""主执行文件：播放 / 导入 / 导出。

三种用法：

    # 播放 NSF（默认 Raf World.nsf 第 1 首，30 秒）
    python main.py
    python main.py "Raf World.nsf" --song 3 --seconds 40

    # 只导入成乐谱并导出成其它格式，不播放
    python main.py --no-play --md 乐谱.md --json 乐谱.json --nsf 乐谱.nsf

    # 播放的同时保存 WAV
    python main.py --wav 输出.wav

支持的输入：.nsf / .json / .md；输出：.wav（音频）、.json / .md / .nsf（乐谱）。
Markdown 是无损格式：除音符表外还保留 APU 硬件细节、DMC 采样和全部
寄存器事件，读回来可以用 `ApuEngine.from_score()` 按原声播放。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np

from apu import (
    ApuEngine,
    SAMPLE_RATE,
    _freq_to_midi,
    _period_to_freq,
    frequency_to_period,
    play_audio,
    save_wav,
)
from models import (
    ApuConfig,
    ApuEvent,
    Channel,
    DmcSample,
    EnvelopeConfig,
    NoteEvent,
    PitchPoint,
    Score,
    SweepConfig,
    Track,
    midi_to_note_name,
)

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# 一、Markdown 读写（宽表 + DMC 采样 + APU 事件，可无损往返）
# ---------------------------------------------------------------------------

_META_RE = re.compile(r"^[-*]\s*([A-Za-z_]+)\s*[:：]\s*(.*)$")
_TRACK_META_RE = re.compile(r"^[-*]?\s*(channel|duty)\s*[:：]\s*(.*)$", re.IGNORECASE)
_NOISE_CELL_RE = re.compile(r"^[Nn](\d{1,2})$")
_NOISE_CODE_RE = re.compile(r"^(\d{1,2})([slSL])$")

# 宽表列顺序（写表头和解析共用）
_COLUMNS = ("拍", "音名", "占空比", "周期", "时值(拍)", "音量", "长度",
            "包络", "扫频", "线性", "噪声", "采样", "音高曲线")


# -- 单元格格式化 -----------------------------------------------------------


def _fmt_number(value: float) -> str:
    """用最短的精确写法输出浮点数（保证往返不丢精度）。"""
    text = repr(float(value))
    return text[:-2] if text.endswith(".0") else text


def _cell(value: object) -> str:
    """空值统一写成 '-'，方便人看也方便解析。"""
    return "-" if value is None or value == "" else str(value)


def _fmt_envelope(envelope: EnvelopeConfig | None) -> str:
    if envelope is None:
        return "-"
    text = f"{int(envelope.constant)}:{int(envelope.loop)}:{envelope.period}"
    if envelope.values:
        text += ":" + ",".join(str(value) for value in envelope.values)
    return text


def _fmt_sweep(sweep: SweepConfig | None) -> str:
    if sweep is None:
        return "-"
    return f"{int(sweep.enabled)}:{sweep.period}:{int(sweep.negate)}:{sweep.shift}"


def _fmt_linear(note: NoteEvent) -> str:
    if note.linear_counter is None and note.linear_reload is None:
        return "-"
    counter = 0 if note.linear_counter is None else note.linear_counter
    reload = 0 if note.linear_reload is None else int(note.linear_reload)
    return f"{counter}:{reload}"


def _fmt_noise(note: NoteEvent) -> str:
    if note.noise_period == 0 and not note.noise_short:
        return "-"
    return f"{note.noise_period}{'s' if note.noise_short else 'l'}"


def _fmt_curve(curve: list[PitchPoint]) -> str:
    if not curve:
        return "-"
    return ",".join(f"{_fmt_number(point.time)}:{point.period}" for point in curve)


def _sample_key(sample: DmcSample) -> tuple:
    return (sample.rate, sample.loop, sample.irq,
            sample.address, sample.length, sample.data)


def _note_cells(note: NoteEvent, track: Track, register) -> list[str]:
    """一个音符 -> 宽表的一行单元格（顺序必须与 _COLUMNS 一致）。"""
    if note.pitch is not None:
        pitch = note.pitch
    elif track.channel is Channel.NOISE and note.volume > 0:
        pitch = f"N{note.noise_period}"
    else:
        pitch = "-"
    return [
        _fmt_number(note.start),
        pitch,
        _cell(note.duty),
        _cell(note.period),
        _fmt_number(note.duration),
        str(note.volume),
        _cell(note.length_index),
        _fmt_envelope(note.envelope),
        _fmt_sweep(note.sweep),
        _fmt_linear(note),
        _fmt_noise(note),
        _cell(register(note.dmc)),
        _fmt_curve(note.pitch_curve),
    ]


def score_to_markdown(score: Score) -> str:
    """把 Score 渲染成无损的 Markdown 乐谱。"""
    # 1. 给 DMC 采样去重编号（D0、D1……），轨道表里只写引用
    samples: list[DmcSample] = []
    sample_ids: dict[tuple, str] = {}

    def register(sample: DmcSample | None) -> str | None:
        if sample is None:
            return None
        key = _sample_key(sample)
        if key not in sample_ids:
            sample_ids[key] = f"D{len(samples)}"
            samples.append(sample)
        return sample_ids[key]

    for sample in score.dmc_samples:
        register(sample)
    for track in score.tracks:
        for note in track.notes:
            register(note.dmc)

    # 2. 文件级元信息（顺序固定，解析时按 key 取值）
    meta: list[tuple[str, object]] = [
        ("format", 2),
        ("bpm", _fmt_number(score.bpm)),
        ("time_signature", score.time_signature),
    ]
    meta += [(key, value) for key, value in
             (("artist", score.artist), ("copyright", score.copyright),
              ("source", score.source)) if value]
    if score.audio_seconds is not None:
        meta.append(("audio_seconds", _fmt_number(score.audio_seconds)))
    if score.apu is not None:
        apu = score.apu
        meta += [
            ("frame_rate", _fmt_number(apu.frame_rate)),
            ("speed_flags", apu.speed_flags),
            ("chip", apu.chip),
            ("load_addr", f"0x{apu.load_addr:04X}"),
            ("init_addr", f"0x{apu.init_addr:04X}"),
            ("play_addr", f"0x{apu.play_addr:04X}"),
            ("version", apu.version),
            ("song_count", apu.song_count),
            ("start_song", apu.start_song),
            ("ntsc_speed", apu.ntsc_speed),
            ("pal_speed", apu.pal_speed),
        ]
    lines: list[str] = [f"# {score.title}", "", *(f"- {key}: {value}" for key, value in meta), ""]

    # 3. 每条轨道一张宽表
    for track in score.tracks:
        lines += [f"## {track.name}", "", f"channel: {track.channel.value}"]
        if track.channel in (Channel.PULSE1, Channel.PULSE2):
            lines.append(f"duty: {track.duty}")
        lines.append("")
        if not track.notes:
            lines += ["_（这条轨道没有音符）_", ""]
            continue
        lines.append("| " + " | ".join(_COLUMNS) + " |")
        lines.append("| " + " | ".join("---" for _ in _COLUMNS) + " |")
        for note in track.notes:
            lines.append("| " + " | ".join(_note_cells(note, track, register)) + " |")
        lines.append("")

    # 4. DMC 采样（桥段头 + 十六进制字节）
    if samples:
        lines += ["## DMC 采样", ""]
        for sample_id, sample in zip(sample_ids.values(), samples):
            raw = bytes.fromhex(sample.data)
            lines += [f"### {sample_id}", "",
                      f"- rate: {sample.rate}",
                      f"- loop: {int(sample.loop)}",
                      f"- irq: {int(sample.irq)}",
                      f"- address: 0x{sample.address:04X}",
                      f"- length: {sample.length}",
                      "", "```hex"]
            lines += [" ".join(f"{byte:02x}" for byte in raw[offset:offset + 32])
                      for offset in range(0, len(raw), 32)]
            lines += ["```", ""]

    # 5. 全部 APU 寄存器写入（逐周期）
    if score.events:
        lines += ["## APU 事件", "", "```apu",
                  *(f"{event.cycle} {event.address} {event.value}" for event in score.events),
                  "```", ""]
    return "\n".join(lines)


# -- 单元格解析 -------------------------------------------------------------


def _parse_int(text: str | None, default: int = 0) -> int:
    """支持 10 / 0x1F 两种写法。"""
    if text is None:
        return default
    text = text.strip()
    if not text:
        return default
    try:
        return int(text, 0)
    except ValueError:
        return int(float(text))


def _parse_bool(text: str | None) -> bool:
    return bool(_parse_int(text))


def _parse_cell(text: str) -> str | None:
    return None if text in {"-", "—", ""} else text


def _parse_envelope(text: str | None) -> EnvelopeConfig | None:
    text = _parse_cell(text or "")
    if text is None:
        return None
    parts = text.split(":")
    if len(parts) < 3:
        return None
    values = [int(value) for value in parts[3].split(",") if value] if len(parts) > 3 else []
    return EnvelopeConfig(constant=bool(int(parts[0])), loop=bool(int(parts[1])),
                          period=int(parts[2]), values=values)


def _parse_sweep(text: str | None) -> SweepConfig | None:
    text = _parse_cell(text or "")
    if text is None:
        return None
    parts = text.split(":")
    if len(parts) < 4:
        return None
    return SweepConfig(enabled=bool(int(parts[0])), period=int(parts[1]),
                       negate=bool(int(parts[2])), shift=int(parts[3]))


def _parse_linear(text: str | None) -> tuple[int | None, bool | None]:
    text = _parse_cell(text or "")
    if text is None:
        return None, None
    parts = text.split(":")
    return int(parts[0]), bool(int(parts[1])) if len(parts) > 1 else False


def _parse_noise(text: str | None) -> tuple[int, bool] | None:
    text = _parse_cell(text or "")
    if text is None:
        return None
    match = _NOISE_CODE_RE.match(text)
    if not match:
        return None
    return int(match.group(1)), match.group(2).lower() == "s"


def _period_pitch(period: int, channel: Channel) -> str | None:
    divisor = 32 if channel is Channel.TRIANGLE else 16
    midi = _freq_to_midi(_period_to_freq(period, divisor))
    return midi_to_note_name(midi) if midi is not None else None


def _parse_curve(text: str | None, channel: Channel) -> list[PitchPoint]:
    text = _parse_cell(text or "")
    if text is None:
        return []
    curve: list[PitchPoint] = []
    for item in text.split(","):
        if not item:
            continue
        time_text, _, period_text = item.partition(":")
        period = int(period_text)
        curve.append(PitchPoint(time=float(time_text), period=period,
                                pitch=_period_pitch(period, channel)))
    return curve


def _note_from_row(row: dict[str, str], channel: Channel) -> dict:
    """把宽表的一行解析成 NoteEvent 的原始字段。"""
    pitch_text = row.get("音名", "-")
    noise_period, noise_short = 0, False
    pitch: str | None = pitch_text
    if _parse_cell(pitch_text) is None:
        pitch = None
    elif _NOISE_CELL_RE.match(pitch_text):
        noise_period = int(_NOISE_CELL_RE.match(pitch_text).group(1))
        pitch = None
    noise = _parse_noise(row.get("噪声"))
    if noise is not None:
        noise_period, noise_short = noise
    linear_counter, linear_reload = _parse_linear(row.get("线性"))
    return {
        "start": float(row.get("拍", 0)),
        "duration": float(row.get("时值(拍)", 1)),
        "pitch": pitch,
        "duty": (None if _parse_cell(row.get("占空比", "-")) is None
                 else _parse_int(row.get("占空比"))),
        "volume": _parse_int(row.get("音量"), 15),
        "period": (None if _parse_cell(row.get("周期", "-")) is None
                   else _parse_int(row.get("周期"))),
        "length_index": (None if _parse_cell(row.get("长度", "-")) is None
                         else _parse_int(row.get("长度"))),
        "envelope": _parse_envelope(row.get("包络")),
        "sweep": _parse_sweep(row.get("扫频")),
        "linear_counter": linear_counter,
        "linear_reload": linear_reload,
        "noise_period": noise_period,
        "noise_short": noise_short,
        "pitch_curve": _parse_curve(row.get("音高曲线"), channel),
        "dmc_ref": _parse_cell(row.get("采样", "-")),
    }


def markdown_to_score(text: str) -> Score:
    """解析 Markdown 乐谱；同时兼容旧的 4 列表格。"""
    title = "未命名乐谱"
    meta: dict[str, str] = {}
    raw_tracks: list[dict] = []
    raw_samples: list[dict] = []
    events: list[ApuEvent] = []

    # 扫描状态：当前段落、当前轨道/采样、表格列名、是否在代码块里
    mode: str | None = None
    current: dict | None = None
    columns: list[str] | None = None
    sample: dict | None = None
    in_code = False
    code_kind = ""
    code_lines: list[str] = []

    def finish_sample() -> None:
        nonlocal sample
        if sample is not None:
            raw_samples.append(sample)
            sample = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # -- 代码块：DMC 十六进制 / APU 事件 --------------------------------
        if in_code:
            if not line.startswith("```"):
                code_lines.append(line)
                continue
            if code_kind == "hex" and sample is not None:
                sample["data"] = "".join(code_lines).replace(" ", "")
            elif code_kind == "apu":
                for entry in code_lines:
                    parts = entry.split()
                    if len(parts) >= 3:
                        events.append(ApuEvent(cycle=_parse_int(parts[0]),
                                               address=_parse_int(parts[1]),
                                               value=_parse_int(parts[2])))
            in_code, code_kind, code_lines = False, "", []
            continue

        if line.startswith("```"):
            in_code, code_kind, code_lines = True, line[3:].strip().lower(), []
            continue
        if not line:
            continue

        # -- 一级标题：乐谱名 ----------------------------------------------
        if line.startswith("# ") and not line.startswith("## "):
            if current is None and mode is None and not raw_tracks:
                title = line[2:].strip()
            continue

        # -- 二级标题：切换段落（轨道 / DMC 采样 / APU 事件）-----------------
        if line.startswith("## "):
            if current is not None:
                raw_tracks.append(current)
                current = None
            finish_sample()
            heading = line[3:].strip()
            if heading == "DMC 采样":
                mode = "dmc"
            elif heading == "APU 事件":
                mode = "events"
            else:
                mode = "track"
                columns = None
                current = {"name": heading, "channel": None, "duty": 2, "notes": []}
            continue

        # -- DMC 采样段：### 采样名 + 元信息 --------------------------------
        if mode == "dmc":
            if line.startswith("### "):
                finish_sample()
                sample = {"id": line[4:].strip(), "rate": "0", "loop": "0",
                          "irq": "0", "address": "0xC000", "length": "1", "data": ""}
            elif sample is not None:
                match = _META_RE.match(line)
                if match:
                    sample[match.group(1).lower()] = match.group(2).strip()
            continue

        if mode == "events":
            continue

        # -- 文件级元信息 --------------------------------------------------
        if current is None:
            match = _META_RE.match(line)
            if match:
                meta[match.group(1).lower()] = match.group(2).strip()
            continue

        # -- 轨道元信息（channel / duty）------------------------------------
        match = _TRACK_META_RE.match(line)
        if match:
            key, value = match.group(1).lower(), match.group(2).strip()
            if key == "channel":
                current["channel"] = value
            elif value:
                current["duty"] = int(value)
            continue

        # -- 音符表格 ------------------------------------------------------
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0] == "拍":
            columns = cells
            continue
        if not columns or len(cells) < len(columns):
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):   # 跳过 |---|---| 分隔行
            continue
        row = dict(zip(columns, cells))
        channel = Channel.from_text(current["channel"] or current["name"])
        current["notes"].append(_note_from_row(row, channel))

    if current is not None:
        raw_tracks.append(current)
    finish_sample()

    if not raw_tracks:
        raise ValueError("Markdown 里没有找到任何轨道（应以 '## 轨道名' 开头）")

    # 1. DMC 采样
    sample_objects: list[DmcSample] = []
    sample_map: dict[str, DmcSample] = {}
    for item in raw_samples:
        obj = DmcSample(
            rate=_parse_int(item.get("rate")),
            loop=_parse_bool(item.get("loop")),
            irq=_parse_bool(item.get("irq")),
            address=_parse_int(item.get("address"), 0xC000),
            length=_parse_int(item.get("length"), 1),
            data=item.get("data", ""),
        )
        sample_map[item["id"]] = obj
        sample_objects.append(obj)

    # 2. 轨道与音符（占空比只对方波有效）
    tracks: list[Track] = []
    for item in raw_tracks:
        channel = Channel.from_text(item["channel"] or item["name"])
        is_pulse = channel in (Channel.PULSE1, Channel.PULSE2)
        notes: list[NoteEvent] = []
        for data in item["notes"]:
            data = dict(data)
            reference = data.pop("dmc_ref", None)
            duty = data.pop("duty", None)
            notes.append(NoteEvent(
                duty=duty if is_pulse else None,
                dmc=sample_map.get(reference) if reference else None,
                **data,
            ))
        tracks.append(Track(channel=channel, name=item["name"],
                            duty=item["duty"], notes=notes))

    # 3. APU 配置与时长
    apu = None
    apu_keys = ("frame_rate", "speed_flags", "chip", "load_addr", "init_addr",
                "play_addr", "version", "song_count", "start_song",
                "ntsc_speed", "pal_speed")
    if any(key in meta for key in apu_keys):
        apu = ApuConfig(
            frame_rate=float(meta.get("frame_rate", 60.0988)),
            speed_flags=_parse_int(meta.get("speed_flags")),
            chip=_parse_int(meta.get("chip")),
            load_addr=_parse_int(meta.get("load_addr"), 0x8000),
            init_addr=_parse_int(meta.get("init_addr"), 0x8000),
            play_addr=_parse_int(meta.get("play_addr"), 0x8003),
            version=_parse_int(meta.get("version"), 1),
            song_count=_parse_int(meta.get("song_count"), 1),
            start_song=_parse_int(meta.get("start_song"), 1),
            ntsc_speed=_parse_int(meta.get("ntsc_speed")),
            pal_speed=_parse_int(meta.get("pal_speed")),
        )
    audio_seconds = float(meta["audio_seconds"]) if meta.get("audio_seconds") else None

    return Score(
        title=title,
        artist=meta.get("artist", ""),
        copyright=meta.get("copyright", ""),
        source=meta.get("source", ""),
        bpm=float(meta.get("bpm", 120)),
        time_signature=meta.get("time_signature", "4/4"),
        tracks=tracks,
        apu=apu,
        events=events,
        dmc_samples=sample_objects,
        audio_seconds=audio_seconds,
    )


def save_markdown(score: Score, path: str | Path) -> Path:
    path = Path(path)
    path.write_text(score_to_markdown(score), encoding="utf-8")
    return path


def load_markdown(path: str | Path) -> Score:
    return markdown_to_score(Path(path).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 二、JSON 读写（乐谱的完整快照，适合程序读写）
# ---------------------------------------------------------------------------


def score_to_dict(score: Score) -> dict:
    """Score -> 可 JSON 序列化的字典（不含自动计算字段）。"""
    return score.model_dump(mode="json", exclude_none=True,
                            exclude_computed_fields=True)


def save_json(score: Score, path: str | Path) -> Path:
    path = Path(path)
    text = json.dumps(score_to_dict(score), ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")
    return path


def load_json(path: str | Path) -> Score:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON 乐谱的顶层应该是一个对象（{...}）")
    return Score.model_validate(data)


# ---------------------------------------------------------------------------
# 三、NSF 导出（把内存乐谱重新变回能播放的 .nsf）
# ---------------------------------------------------------------------------

_NSF_LOAD_ADDR = 0x8000
_NSF_FRAME_RATE = 1_000_000.0 / 16639      # NTSC：约 60.099 帧/秒
# 每条轨道在零页占 3 个字节：指针低、指针高、剩余帧数
_ZP_BASE = 0x00
# (声道, 控制寄存器, 周期低寄存器, 周期高/触发寄存器)
_NES_CHANNELS = (
    (Channel.PULSE1, 0x4000, 0x4002, 0x4003),
    (Channel.PULSE2, 0x4004, 0x4006, 0x4007),
    (Channel.TRIANGLE, 0x4008, 0x400A, 0x400B),
    (Channel.NOISE, 0x400C, 0x400E, 0x400F),
)

# 常用 6502 操作码
_OP_LDA_IMM = 0xA9
_OP_LDA_ZP = 0xA5
_OP_STA_ZP = 0x85
_OP_STA_ABS = 0x8D
_OP_LDY_IMM = 0xA0
_OP_LDA_INDY = 0xB1
_OP_INY = 0xC8
_OP_ADC_IMM = 0x69
_OP_DEC_ZP = 0xC6
_OP_INC_ZP = 0xE6
_OP_CLC = 0x18
_OP_RTS = 0x60
_OP_JSR = 0x20
_OP_BNE = 0xD0
_OP_BEQ = 0xF0
_OP_BCC = 0x90
_OP_SEI = 0x78


class _Asm:
    """一个只认识本文件用到的十几条指令的迷你 6502 汇编器。"""

    def __init__(self, origin: int) -> None:
        self.origin = origin
        self.data = bytearray()
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[str, int, str]] = []

    @property
    def here(self) -> int:
        return self.origin + len(self.data)

    def label(self, name: str) -> None:
        if name in self.labels:
            raise ValueError(f"汇编错误：标签 {name} 重复")
        self.labels[name] = self.here

    def byte(self, *values: int) -> None:
        self.data.extend(value & 0xFF for value in values)

    def imm(self, opcode: int, value: int) -> None:
        self.byte(opcode, value)

    def zp(self, opcode: int, addr: int) -> None:
        self.byte(opcode, addr)

    def abs_(self, opcode: int, addr: int) -> None:
        self.byte(opcode, addr & 0xFF, addr >> 8)

    def indy(self, opcode: int, zp_addr: int) -> None:
        self.byte(opcode, zp_addr)

    def jsr(self, label: str) -> None:
        self.byte(_OP_JSR, 0, 0)
        self.fixups.append(("abs", len(self.data) - 2, label))

    def branch(self, opcode: int, label: str) -> None:
        self.byte(opcode, 0)
        self.fixups.append(("rel", len(self.data) - 1, label))

    def imm_label(self, opcode: int, label: str, high: bool) -> None:
        self.byte(opcode, 0)
        self.fixups.append(("hi" if high else "lo", len(self.data) - 1, label))

    def resolve(self) -> None:
        """回填所有标签引用（绝对地址 / 高低字节 / 相对跳转）。"""
        for kind, pos, label in self.fixups:
            if label not in self.labels:
                raise ValueError(f"汇编错误：找不到标签 {label}")
            addr = self.labels[label]
            if kind == "abs":
                self.data[pos], self.data[pos + 1] = addr & 0xFF, (addr >> 8) & 0xFF
            elif kind == "lo":
                self.data[pos] = addr & 0xFF
            elif kind == "hi":
                self.data[pos] = (addr >> 8) & 0xFF
            else:
                offset = addr - (self.origin + pos + 1)
                if not -128 <= offset <= 127:
                    raise ValueError("汇编错误：跳转距离太远")
                self.data[pos] = offset & 0xFF


def _push_event(out: bytearray, frames: int, ctl: int, low: int, high: int) -> None:
    """写入事件 [帧数][控制][周期低][周期高]，超过 255 帧就拆成多段。"""
    while frames > 0:
        chunk = min(255, frames)
        out.extend((chunk, ctl & 0xFF, low & 0xFF, high & 0xFF))
        frames -= chunk


def _track_events(track: Track, score: Score, frame_rate: float) -> bytearray:
    """把一条轨道的音符变成事件流（每帧最多消耗一个事件）。"""
    channel = track.channel
    rest_ctl = 0x00 if channel is Channel.TRIANGLE else 0x30
    out = bytearray()
    cursor = 0                                    # 已经排到第几帧

    for note in track.notes:
        start_frame = round(score.beats_to_seconds(note.start) * frame_rate)
        if start_frame > cursor:                  # 中间的空隙写成休止
            _push_event(out, start_frame - cursor, rest_ctl, 0, 0)
            cursor = start_frame
        frames = max(1, round(score.beats_to_seconds(note.duration) * frame_rate))

        if channel is Channel.NOISE:
            if note.volume <= 0:                  # 音量 0 = 休止
                _push_event(out, frames, rest_ctl, 0, 0)
            else:
                _push_event(out, frames, 0x30 | (note.volume & 0x0F),
                            note.noise_period & 0x0F, 0)
        elif note.pitch is None:                  # 有音高的轨道：空音名 = 休止
            _push_event(out, frames, rest_ctl, 0, 0)
        else:
            freq = note.frequency_hz or 0.0
            if channel is Channel.TRIANGLE:
                ctl = 0xFF                        # 打开三角波
                period = max(2, frequency_to_period(freq, 32))
            else:
                ctl = ((note.effective_duty(track.duty) << 6) | 0x30
                       | (note.volume & 0x0F))
                period = max(8, frequency_to_period(freq, 16))
            _push_event(out, frames, ctl, period & 0xFF, (period >> 8) & 0x07)

        cursor = max(cursor, start_frame) + frames

    if out:
        # 末尾补一帧休止：否则最后一个音会一直响到播放器停下
        _push_event(out, 1, rest_ctl, 0, 0)
    out.append(0x00)                              # 结束标记
    return out


def score_to_nsf_bytes(score: Score) -> bytes:
    """把 Score 变成完整的 .nsf 文件内容（文件头 + 迷你播放程序 + 数据）。"""
    asm = _Asm(_NSF_LOAD_ADDR)

    # ---- INIT：静音、清状态、设置四条轨道的数据指针 ----
    asm.label("init")
    asm.byte(_OP_SEI)
    asm.imm(_OP_LDA_IMM, 0x40)
    asm.abs_(_OP_STA_ABS, 0x4017)                 # 关闭 DMC 中断
    asm.imm(_OP_LDA_IMM, 0x0F)
    asm.abs_(_OP_STA_ABS, 0x4015)                 # 打开四个声道
    asm.imm(_OP_LDA_IMM, 0x08)
    asm.abs_(_OP_STA_ABS, 0x4001)                 # 方波 1 关闭扫频
    asm.abs_(_OP_STA_ABS, 0x4005)                 # 方波 2 关闭扫频
    asm.imm(_OP_LDA_IMM, 0x00)
    for _, ctl_reg, _, _ in _NES_CHANNELS:
        asm.abs_(_OP_STA_ABS, ctl_reg)            # 音量 0
    for index in range(4):                        # 剩余帧数清零
        asm.zp(_OP_STA_ZP, _ZP_BASE + index * 3 + 2)
    for index in range(4):                        # 指针指向 data0..data3
        ptr = _ZP_BASE + index * 3
        asm.imm_label(_OP_LDA_IMM, f"data{index}", high=False)
        asm.zp(_OP_STA_ZP, ptr)
        asm.imm_label(_OP_LDA_IMM, f"data{index}", high=True)
        asm.zp(_OP_STA_ZP, ptr + 1)
    asm.byte(_OP_RTS)

    # ---- PLAY：每帧调用一次，四条轨道各更新一下 ----
    asm.label("play")
    for index in range(4):
        asm.jsr(f"ch{index}")
    asm.byte(_OP_RTS)

    # ---- 每条轨道的处理程序：没有剩余帧就读下一组 4 字节 ----
    for index, (_, ctl_reg, lo_reg, hi_reg) in enumerate(_NES_CHANNELS):
        ptr = _ZP_BASE + index * 3
        rem = ptr + 2
        asm.label(f"ch{index}")
        asm.zp(_OP_LDA_ZP, rem)                   # 还有剩余帧 -> 只倒计时
        asm.branch(_OP_BNE, f"tick{index}")
        asm.imm(_OP_LDY_IMM, 0)
        asm.indy(_OP_LDA_INDY, ptr)               # 帧数；0 = 结束
        asm.branch(_OP_BEQ, f"done{index}")
        asm.zp(_OP_STA_ZP, rem)
        asm.byte(_OP_INY)
        asm.indy(_OP_LDA_INDY, ptr)               # 控制字节
        asm.abs_(_OP_STA_ABS, ctl_reg)
        asm.byte(_OP_INY)
        asm.indy(_OP_LDA_INDY, ptr)               # 周期低
        asm.abs_(_OP_STA_ABS, lo_reg)
        asm.byte(_OP_INY)
        asm.indy(_OP_LDA_INDY, ptr)               # 周期高（写入即触发发音）
        asm.abs_(_OP_STA_ABS, hi_reg)
        asm.byte(_OP_CLC)                         # 指针 += 4
        asm.zp(_OP_LDA_ZP, ptr)
        asm.imm(_OP_ADC_IMM, 4)
        asm.zp(_OP_STA_ZP, ptr)
        asm.branch(_OP_BCC, f"tick{index}")
        asm.zp(_OP_INC_ZP, ptr + 1)
        asm.label(f"tick{index}")
        asm.zp(_OP_DEC_ZP, rem)
        asm.label(f"done{index}")
        asm.byte(_OP_RTS)

    # ---- 数据：四条轨道的音符事件流，按声道顺序排列 ----
    for index, (channel, _, _, _) in enumerate(_NES_CHANNELS):
        track = score.track(channel)
        events = _track_events(track, score, _NSF_FRAME_RATE) if track else bytearray(b"\x00")
        asm.label(f"data{index}")
        asm.byte(*events)

    asm.resolve()

    rom = bytes(asm.data)
    if len(rom) > 0x10000 - _NSF_LOAD_ADDR:
        raise ValueError(
            f"这首曲子太长（{len(rom)} 字节），超过了 NSF 单块 32KB 的上限。"
            "可以缩短模拟时长，或分几段导出。"
        )

    # ---- NSF 文件头（0x80 字节）----
    def text_field(value: str) -> bytes:
        return value.encode("latin-1", errors="replace")[:31].ljust(32, b"\x00")

    header = bytearray(0x80)
    header[0:5] = b"NESM\x1a"
    header[5] = 1                                    # 版本
    header[6] = 1                                    # 总曲目数
    header[7] = 1                                    # 起始曲目
    header[8:10] = _NSF_LOAD_ADDR.to_bytes(2, "little")
    header[10:12] = asm.labels["init"].to_bytes(2, "little")
    header[12:14] = asm.labels["play"].to_bytes(2, "little")
    header[14:46] = text_field(score.title)
    header[46:78] = text_field(score.artist)
    header[78:110] = text_field(score.copyright)
    header[110:112] = (16639).to_bytes(2, "little")  # NTSC 播放速度
    header[120:122] = (0).to_bytes(2, "little")      # PAL 播放速度
    header[122] = 0                                  # 不使用扩展音源
    return bytes(header) + rom


def save_nsf(score: Score, path: str | Path) -> Path:
    dmc = score.track(Channel.DMC)
    if dmc is not None and dmc.notes:
        print("[提示] 简化 NSF 导出不包含 DMC 声道，DMC 轨道会被忽略；"
              "需要原声请用 JSON / Markdown / WAV。")
    path = Path(path)
    path.write_bytes(score_to_nsf_bytes(score))
    return path


# ---------------------------------------------------------------------------
# 四、统一入口：按扩展名自动选择格式
# ---------------------------------------------------------------------------

_SUFFIXES = {
    ".nsf": "nsf", ".json": "json",
    ".md": "md", ".markdown": "md", ".txt": "md",
}


def detect_format(path: str | Path, fmt: str | None = None) -> str:
    if fmt:
        fmt = fmt.lower().lstrip(".")
        if fmt not in {"nsf", "json", "md", "markdown"}:
            raise ValueError(f"不支持的格式：{fmt}（可用 nsf / json / md）")
        return "md" if fmt == "markdown" else fmt
    suffix = Path(path).suffix.lower()
    if suffix not in _SUFFIXES:
        raise ValueError(f"认不出扩展名 {suffix!r}，请显式指定格式（nsf/json/md）")
    return _SUFFIXES[suffix]


def load_score(path: str | Path, *, song: int = 1, seconds: float = 30.0,
               bpm: float = 120.0, fmt: str | None = None,
               verbose: bool = False) -> Score:
    """读取任意支持格式的乐谱到内存。"""
    fmt = detect_format(path, fmt)
    if fmt == "nsf":
        return ApuEngine(path, song=song, seconds=seconds).to_score(
            bpm=bpm, verbose=verbose)
    return load_json(path) if fmt == "json" else load_markdown(path)


def save_score(score: Score, path: str | Path, fmt: str | None = None) -> Path:
    """把内存乐谱保存成任意支持格式（扩展名决定格式）。"""
    fmt = detect_format(path, fmt)
    if fmt == "nsf":
        return save_nsf(score, path)
    return save_json(score, path) if fmt == "json" else save_markdown(score, path)


# ---------------------------------------------------------------------------
# 五、命令行：播放 / 导入 / 导出
# ---------------------------------------------------------------------------


def print_summary(score: Score) -> None:
    """打印一眼能看懂的乐谱概况。"""
    print("=" * 60)
    print(f"《{score.title}》")
    if score.artist:
        print(f"作曲 / 编曲：{score.artist}")
    if score.copyright:
        print(f"版权：{score.copyright}")
    if score.source:
        print(f"来源：{score.source}")
    print(f"速度：{score.bpm:g} BPM · 拍号 {score.time_signature} · "
          f"{score.duration_beats:.1f} 拍 / {score.duration_seconds:.1f} 秒")
    print(f"共 {score.note_count} 个音符：")
    for track in score.tracks:
        print(f"  - {track.name:<9} {track.channel.value:<9} {len(track.notes):>4} 个音符")
    if score.events:
        print(f"APU 快照：{len(score.events)} 条寄存器事件 · "
              f"{len(score.dmc_samples)} 段 DMC 采样")
    print("=" * 60)


def _render_score_via_apu(score: Score) -> np.ndarray:
    """渲染内存乐谱。

    带 APU 事件的乐谱（从 NSF / JSON / Markdown 读回来的）直接按原始
    寄存器事件重建，声音与直接播放 NSF 逐位一致；手写的简易乐谱才
    回退到“组装临时 NSF”的老办法。
    """
    if score.apu is not None and score.events:
        return ApuEngine.from_score(score).render()

    temp = tempfile.NamedTemporaryFile(prefix="score_", suffix=".nsf", delete=False)
    temp.close()
    temp_path = Path(temp.name)
    try:
        temp_path.write_bytes(score_to_nsf_bytes(score))
        seconds = max(score.duration_seconds + 0.5, 0.5)
        return ApuEngine(temp_path, song=1, seconds=seconds).render()
    finally:
        temp_path.unlink(missing_ok=True)


def _render_audio(input_path: Path, score: Score, args: argparse.Namespace) -> np.ndarray:
    """根据输入类型选择渲染方式：NSF 直接播，乐谱走临时 NSF / 事件重建。"""
    if input_path.suffix.lower() == ".nsf":
        return ApuEngine(input_path, song=args.song, seconds=args.seconds).render()
    return _render_score_via_apu(score)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="NSF 音乐工具：播放 / 导入 / 导出（声音由 APU 引擎产生）")
    parser.add_argument("score", nargs="?",
                        default=str(HERE / "Raf World.nsf"),
                        help="乐谱文件（.nsf / .json / .md），默认 Raf World.nsf")
    parser.add_argument("--song", type=int, default=1, help="NSF 曲目编号（从 1 开始）")
    parser.add_argument("--seconds", type=float, default=30.0, help="NSF 模拟时长（秒）")
    parser.add_argument("--bpm", type=float, default=120.0,
                        help="速度（每分钟拍数，默认 120，只影响“拍”的换算）")
    parser.add_argument("--md", help="导出 Markdown 乐谱到指定路径")
    parser.add_argument("--json", help="导出 JSON 乐谱到指定路径")
    parser.add_argument("--nsf", help="导出 NSF 文件到指定路径")
    parser.add_argument("--wav", help="同时保存 WAV 音频")
    parser.add_argument("--no-play", action="store_true", help="只处理文件，不播放")
    args = parser.parse_args(argv)

    # -- 读入乐谱 --------------------------------------------------------
    input_path = Path(args.score)
    if not input_path.exists():
        print(f"找不到文件：{input_path}")
        return 1
    try:
        score = load_score(input_path, song=args.song, seconds=args.seconds,
                           bpm=args.bpm)
    except (ValueError, RuntimeError) as error:
        print(f"读取失败：{error}")
        return 1

    print_summary(score)

    # -- 导出乐谱 --------------------------------------------------------
    if args.md:
        print(f"Markdown 已写入：{save_markdown(score, args.md)}")
    if args.json:
        print(f"JSON 已写入：{save_json(score, args.json)}")
    if args.nsf:
        try:
            print(f"NSF 已写入：{save_nsf(score, args.nsf)}")
        except ValueError as error:
            print(f"NSF 导出失败：{error}")
            return 1

    # 输入是 NSF、又没有指定任何乐谱输出时，顺手留一份 Markdown
    if input_path.suffix.lower() == ".nsf" and not (args.md or args.json or args.nsf):
        default_md = input_path.with_name(f"{input_path.stem}.song{args.song}.md")
        print(f"Markdown 已写入：{save_markdown(score, default_md)}")

    # -- 播放 / 导出音频 --------------------------------------------------
    if args.no_play and not args.wav:
        print("已跳过播放（--no-play）。")
        return 0
    try:
        audio = _render_audio(input_path, score, args)
    except (ValueError, RuntimeError) as error:
        print(f"APU 渲染失败：{error}")
        return 1

    if args.no_play:
        out = Path(args.wav) if args.wav else Path(args.score).with_suffix(".wav")
        print(f"已保存：{save_wav(out, audio, SAMPLE_RATE)}")
        return 0

    try:
        play_audio(audio, SAMPLE_RATE, save_to=args.wav)
    except RuntimeError as error:
        print(f"播放失败：{error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
