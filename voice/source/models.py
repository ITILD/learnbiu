"""项目里的全部数据对象（pydantic 模型）。

对象关系：
    NSFHeader  .nsf 文件头（标题、作者、6502 程序入口等）
    Score      一首曲子（内存里的“正式”乐谱）
    Track      一条轨道（Pulse 1 / Pulse 2 / Triangle / Noise / DMC）
    NoteEvent  一个音符（第几拍开始、持续几拍、什么音、多大声，
               外加周期 / 包络 / 扫频 / 长度等 APU 硬件细节）

时间统一用“拍”，速度用 bpm：1 拍 = 60 / bpm 秒。
音名统一写 C4 / F#3，时值可写 1.5 拍或 q / 8 / 4. 这类人话。

本文件只定义“内存对象长什么样”：文件读写见 main.py，声音渲染见 apu.py。
音高频率表放在同目录的 note_frequencies.json，第一次用到时才加载。
"""

from __future__ import annotations

import json
import re
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

NOTE_TABLE_PATH = Path(__file__).with_name("note_frequencies.json")

# 音名 -> 相对 C 的半音数；变音记号支持 # / ♯ / b / ♭
_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_ACCIDENTALS = {"": 0, "#": 1, "♯": 1, "b": -1, "♭": -1}
_PITCH_RE = re.compile(r"^([A-Ga-g])\s*([#b♯♭]?)\s*(-?\d{1,2})$")
_REST_WORDS = {"", "-", "r", "rest", "休止", "休止符"}

# 时值的人话写法 -> 拍数（以 4/4 拍、四分音符 = 1 拍为准）
_DURATION_WORDS = {
    "w": 4.0, "whole": 4.0, "全": 4.0, "全音符": 4.0,
    "h": 2.0, "half": 2.0, "二分": 2.0, "二分音符": 2.0,
    "q": 1.0, "quarter": 1.0, "四分": 1.0, "四分音符": 1.0,
    "e": 0.5, "eighth": 0.5, "八分": 0.5, "八分音符": 0.5,
    "s": 0.25, "sixteenth": 0.25, "十六分": 0.25, "十六分音符": 0.25,
    "t": 0.125, "thirtysecond": 0.125, "三十二分": 0.125, "三十二分音符": 0.125,
}


# ---------------------------------------------------------------------------
# 一、静态频率表（note_frequencies.json）
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _note_table() -> tuple[dict[str, tuple[int, float]], dict[int, tuple[str, float]]]:
    """读取并缓存音符频率表，返回 (按音名查, 按 MIDI 编号查)。"""
    raw = json.loads(NOTE_TABLE_PATH.read_text(encoding="utf-8"))
    by_name: dict[str, tuple[int, float]] = {}
    by_midi: dict[int, tuple[str, float]] = {}
    for item in raw["notes"]:
        name, midi, hz = item["name"], int(item["midi"]), float(item["hz"])
        by_name[name] = (midi, hz)
        by_midi[midi] = (name, hz)
    return by_name, by_midi


def midi_to_note_name(midi: int) -> str:
    """MIDI 编号 -> 音名，例如 60 -> C4。"""
    by_midi = _note_table()[1]
    if midi not in by_midi:
        raise ValueError(f"MIDI 编号应在 0..127 之间，收到 {midi}")
    return by_midi[midi][0]


def note_name_to_midi(name: str) -> int:
    """音名 -> MIDI 编号，例如 C4 -> 60，Db4 -> 61。"""
    pitch = parse_pitch(name)
    if pitch is None:
        raise ValueError("休止符没有 MIDI 编号")
    return _note_table()[0][pitch][0]


def note_frequency(pitch: str | int | None) -> float | None:
    """音名或 MIDI 编号 -> 频率（Hz），休止符返回 None。"""
    if pitch is None:
        return None
    by_name, by_midi = _note_table()
    if isinstance(pitch, int) and not isinstance(pitch, bool):
        return by_midi[pitch][1] if pitch in by_midi else None
    name = parse_pitch(pitch)
    return None if name is None else by_name[name][1]


def all_note_names() -> list[str]:
    """按从低到高列出 128 个音名（编辑器做下拉框时可以直接用）。"""
    return [item[0] for _, item in sorted(_note_table()[1].items())]


# ---------------------------------------------------------------------------
# 二、人话解析：音名 / 时值
# ---------------------------------------------------------------------------


def _as_midi(value: Any, midi: int) -> str:
    """校验 MIDI 范围并转成音名（越界时报错信息带上原始输入）。"""
    if 0 <= midi <= 127:
        return midi_to_note_name(midi)
    raise ValueError(f"MIDI 编号应在 0..127 之间，收到 {value!r}")


def parse_pitch(value: Any) -> str | None:
    """把各种写法统一成标准音名；休止符返回 None。

    支持 C4、c4、F#3、Db4（降号转升号）、69（MIDI 编号）、
    "-" / "rest" / "休止"（休止符）。
    """
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"无法识别的音名：{value!r}")
    if isinstance(value, (int, float)):
        return _as_midi(value, int(value))
    if not isinstance(value, str):
        raise ValueError(f"无法识别的音名：{value!r}")

    text = value.strip()
    if text.lower() in _REST_WORDS:
        return None
    if re.fullmatch(r"\d{1,3}", text):
        return _as_midi(value, int(text))

    match = _PITCH_RE.match(text)
    if not match:
        raise ValueError(
            f"无法识别的音名：{value!r}。可以写 C4、F#3、Db4，或 MIDI 编号 60，"
            "休止符写 '-'。"
        )
    letter, accidental, octave = match.groups()
    midi = (int(octave) + 1) * 12 + _SEMITONES[letter.upper()] + _ACCIDENTALS[accidental]
    if not 0 <= midi <= 127:
        raise ValueError(f"音名 {value!r} 超出范围（MIDI 0..127）")
    return midi_to_note_name(midi)


def parse_duration(value: Any) -> float:
    """把各种时值写法统一成“拍数”。

    支持 1.5（1.5 拍）、"q"（四分音符）、"8"（八分音符）、"4."（附点四分）、
    "1/4"（四分之一全音符）。
    """
    if isinstance(value, bool):
        raise ValueError(f"无法识别的时值：{value!r}")
    if isinstance(value, (int, float)):
        beats = float(value)
    elif isinstance(value, str):
        text = value.strip().lower()
        if not text:
            raise ValueError("时值不能为空")
        dotted = text.endswith(".")
        core = text[:-1] if dotted else text

        if core in _DURATION_WORDS:
            beats = _DURATION_WORDS[core]
        elif "/" in core:
            parts = core.split("/")
            try:
                beats = 4.0 * float(parts[0]) / float(parts[1])
            except (ValueError, ZeroDivisionError, IndexError):
                raise ValueError(f"无法识别的时值：{value!r}") from None
        elif core in {"1", "2", "4", "8", "16", "32", "64"}:
            beats = 4.0 / float(core)
        else:
            try:
                beats = float(core)
            except ValueError:
                raise ValueError(
                    f"无法识别的时值：{value!r}。可以写拍数 1.5，或 q/8/4. 这类音符时值。"
                ) from None
        if dotted:
            beats *= 1.5
    else:
        raise ValueError(f"无法识别的时值：{value!r}")

    if beats <= 0:
        raise ValueError(f"时值必须大于 0，收到 {value!r}")
    return round(beats, 6)


# ---------------------------------------------------------------------------
# 三、模型基类与公共校验
# ---------------------------------------------------------------------------


class _Strict(BaseModel):
    """默认拒绝未知字段，保证读写往返不会悄悄丢数据。"""

    model_config = ConfigDict(extra="forbid")


class _Mutable(_Strict):
    """可原地修改的模型：赋值时校验，并去掉字符串首尾空白。"""

    model_config = ConfigDict(validate_assignment=True, extra="forbid",
                              str_strip_whitespace=True)


def _drop_extra(data: Any, *keys: str) -> Any:
    """丢掉输入里混入的自动计算字段（JSON 往返时很常见）。"""
    if isinstance(data, dict):
        data = dict(data)
        for key in keys:
            data.pop(key, None)
    return data


# ---------------------------------------------------------------------------
# 四、NSF 文件头
# ---------------------------------------------------------------------------


class NSFHeader(_Strict):
    """一个 .nsf 文件的文件头。

    `rom` 是 0x80 偏移之后的整段音乐程序；`init_addr` / `play_addr`
    是其中的两个入口（init 初始化，play 每帧调用一次）。
    """

    path: Path
    version: int
    song_count: int
    start_song: int
    load_addr: int
    init_addr: int
    play_addr: int
    name: str
    artist: str
    copyright: str
    ntsc_speed: int
    pal_speed: int
    speed_flags: int
    chip: int
    rom: bytes = Field(default=b"", repr=False)

    @property
    def frame_rate(self) -> float:
        """NTSC 每秒播放多少帧（一般是 60.0988）。"""
        return 1_000_000.0 / self.ntsc_speed if self.ntsc_speed else 60.0988

    @property
    def title(self) -> str:
        """优先用文件头里的标题，没有就用文件名。"""
        return self.name or self.path.stem


# ---------------------------------------------------------------------------
# 五、音符 / 轨道 / 乐谱
# ---------------------------------------------------------------------------


class Channel(str, Enum):
    """NES 的声道（四条旋律/噪声声道 + DMC 采样声道）。"""

    PULSE1 = "pulse1"
    PULSE2 = "pulse2"
    TRIANGLE = "triangle"
    NOISE = "noise"
    DMC = "dmc"

    @property
    def label(self) -> str:
        """人看的名字，例如 pulse1 -> Pulse 1。"""
        return {
            "pulse1": "Pulse 1", "pulse2": "Pulse 2", "triangle": "Triangle",
            "noise": "Noise", "dmc": "DMC",
        }[self.value]

    @classmethod
    def from_text(cls, value: Any) -> "Channel":
        """把 "Pulse 1" / "pulse_1" / "1" / "通道1" 这类写法认成枚举。"""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower().replace("_", "").replace(" ", "")
        for index, channel in enumerate(cls, 1):
            if text in (channel.value, str(index), f"通道{index}"):
                return channel
        raise ValueError(
            f"无法识别的声道：{value!r}（可用 pulse1/pulse2/triangle/noise/dmc）")


class ApuEvent(_Strict):
    """一次 APU 寄存器写入（按 CPU 周期定位）。

    只要保留全部事件、DMC 采样字节和帧速，就能逐位还原出与直接播放
    NSF 完全相同的音频。
    """

    cycle: int = Field(..., ge=0, description="CPU 累计周期")
    address: int = Field(..., ge=0x4000, le=0x4017, description="APU 寄存器地址")
    value: int = Field(..., ge=0, le=255, description="写入值")


class PitchPoint(_Strict):
    """音符内部的一次音高变化（颤音 / 滑音 / 扫频落地值）。"""

    time: float = Field(0.0, ge=0, description="相对音符起点的拍数")
    period: int = Field(..., ge=0, le=0x7FF, description="11 位周期值")
    pitch: str | None = Field(None, description="由周期换算出的音名")


class EnvelopeConfig(_Strict):
    """$4000 / $4004 / $400C 的硬件包络设置。"""

    constant: bool = Field(True, description="True = 固定音量，False = 硬件包络")
    loop: bool = Field(False, description="包络是否循环")
    period: int = Field(0, ge=0, le=15, description="包络步进周期")
    values: list[int] = Field(
        default_factory=list,
        description="逐帧采样到的音量 0..15；固定音量时为空")


class SweepConfig(_Strict):
    """$4001 / $4005 的扫频设置。"""

    enabled: bool = False
    period: int = Field(0, ge=0, le=7)
    negate: bool = False
    shift: int = Field(0, ge=0, le=7)


class DmcSample(_Strict):
    """一段 DMC 采样（$4010-$4013 描述的 PCM 数据）。"""

    rate: int = Field(0, ge=0, le=15, description="$4010 低 4 位的采样率档位")
    loop: bool = Field(False, description="$4010 bit6")
    irq: bool = Field(False, description="$4010 bit7")
    address: int = Field(..., ge=0, le=0xFFFF,
                         description="采样在 64KB 内存里的绝对地址（0xC000 + $4012*64）")
    length: int = Field(..., ge=1, le=0xFFFF)
    data: str = Field("", description="采样字节的十六进制串（小写，无空格）")


class ApuConfig(_Strict):
    """NSF 级配置：没有它就无法把乐谱还原成同样的声音。"""

    frame_rate: float = Field(60.0988, gt=0, description="每秒调用 PLAY 的次数")
    speed_flags: int = Field(0, ge=0, le=255)
    chip: int = Field(0, ge=0, le=255, description="扩展音源芯片标记")
    load_addr: int = Field(0x8000, ge=0, le=0xFFFF)
    init_addr: int = Field(0x8000, ge=0, le=0xFFFF)
    play_addr: int = Field(0x8003, ge=0, le=0xFFFF)
    version: int = Field(1, ge=0, le=255)
    song_count: int = Field(1, ge=0, le=255)
    start_song: int = Field(1, ge=0, le=255)
    ntsc_speed: int = Field(0, ge=0, le=0xFFFF)
    pal_speed: int = Field(0, ge=0, le=0xFFFF)


class NoteEvent(_Mutable):
    """一个音符（或一个休止）。

    旋律声道的字段只描述“这一个音”；周期、包络、扫频、长度计数器、
    线性计数器等硬件细节也一并保存，导出 JSON / Markdown 再读回来不会丢信息。
    """

    start: float = Field(0.0, ge=0, description="第几拍开始（0 = 开头）")
    duration: float = Field(1.0, description="持续多少拍")
    pitch: str | None = Field(None, description="音名，如 C4 / F#3；None = 休止或噪声")
    volume: int = Field(15, ge=0, le=15, description="音量 0..15（NES 的 4 位音量）")
    duty: int | None = Field(None, ge=0, le=3, description="方波占空比 0..3；None = 用轨道的")
    noise_period: int = Field(0, ge=0, le=15, description="噪声音色 0..15")
    noise_short: bool = Field(False, description="噪声短模式（$400E 的 bit7）")
    period: int | None = Field(None, ge=0, le=0x7FF,
                               description="起始的 11 位周期值（音高的原始形态）")
    length_index: int | None = Field(None, ge=0, le=31,
                                     description="$4003/$4007/$400B/$400F 的长度表索引")
    sweep: SweepConfig | None = Field(None, description="方波扫频设置")
    envelope: EnvelopeConfig | None = Field(None, description="硬件包络设置与逐帧音量")
    linear_counter: int | None = Field(None, ge=0, le=127,
                                       description="三角波线性计数器（$4008 低 7 位）")
    linear_reload: bool | None = Field(None, description="三角波线性计数器重载位（$4008 bit7）")
    pitch_curve: list[PitchPoint] = Field(
        default_factory=list, description="音符内部随时间变化的音高（颤音/滑音）")
    dmc: DmcSample | None = Field(None, description="DMC 采样（仅 DMC 轨道的音符使用）")

    # -- 输入归一化：音名 / 时值 / 起始拍 ----------------------------------

    @field_validator("pitch", mode="before")
    @classmethod
    def _pitch(cls, value: Any) -> str | None:
        return parse_pitch(value)

    @field_validator("duration", mode="before")
    @classmethod
    def _duration(cls, value: Any) -> float:
        return parse_duration(value)

    @field_validator("start", mode="before")
    @classmethod
    def _start(cls, value: Any) -> float:
        if isinstance(value, str):
            text = value.strip()
            if text and text not in _REST_WORDS:
                try:
                    return max(0.0, float(text))
                except ValueError:
                    pass
        return value  # type: ignore[return-value]

    @model_validator(mode="before")
    @classmethod
    def _accept_midi(cls, data: Any) -> Any:
        """允许 JSON 里直接写 "midi": 69，省得自己算音名。"""
        if isinstance(data, dict):
            data = dict(data)
            if "pitch" not in data and "midi" in data:
                data["pitch"] = data.pop("midi")
            data = _drop_extra(data, "midi", "frequency_hz", "frequency", "hz",
                               "name", "end")
        return data

    # -- 派生字段 ----------------------------------------------------------

    @computed_field  # type: ignore[prop-decorator]
    @property
    def midi(self) -> int | None:
        """MIDI 编号（休止符为 None）。"""
        return None if self.pitch is None else note_name_to_midi(self.pitch)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def frequency_hz(self) -> float | None:
        """频率（Hz），从 note_frequencies.json 查表；休止符为 None。"""
        return note_frequency(self.pitch)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def end(self) -> float:
        """结束在第几拍。"""
        return self.start + self.duration

    def effective_duty(self, track_duty: int = 2) -> int:
        """实际使用的占空比：音符自己没写就用轨道的。"""
        return track_duty if self.duty is None else self.duty


class Track(_Mutable):
    """一条轨道。"""

    channel: Channel
    name: str = ""
    duty: int = Field(2, ge=0, le=3, description="方波占空比 0..3（12.5%/25%/50%/75%）")
    notes: list[NoteEvent] = Field(default_factory=list)

    @field_validator("channel", mode="before")
    @classmethod
    def _channel(cls, value: Any) -> Channel:
        return Channel.from_text(value)

    @model_validator(mode="before")
    @classmethod
    def _drop_computed(cls, data: Any) -> Any:
        return _drop_extra(data, "note_count", "end")

    @model_validator(mode="after")
    def _finish(self) -> "Track":
        # 没写名字就用声道的名字；音符按开始时间排序，编辑器改顺序也不会乱
        if not self.name:
            object.__setattr__(self, "name", self.channel.label)
        object.__setattr__(
            self, "notes", sorted(self.notes, key=lambda n: (n.start, -n.duration)))
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def note_count(self) -> int:
        return len(self.notes)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def end(self) -> float:
        return max((note.end for note in self.notes), default=0.0)


class Score(_Mutable):
    """一首曲子（内存里的唯一“正式”乐谱对象）。

    `tracks` 是给人看的乐谱视图；`apu` + `events` + `dmc_samples` 是
    无损快照，三者合起来足以让 APU 引擎逐位重现原曲。
    """

    title: str = "未命名乐谱"
    artist: str = ""
    copyright: str = ""
    source: str = Field("", description="来源文件，方便追溯")
    bpm: float = Field(120.0, gt=0, le=400, description="每分钟多少拍")
    time_signature: str = Field("4/4", description="拍号，例如 4/4、3/4")
    tracks: list[Track] = Field(default_factory=list)
    apu: ApuConfig | None = Field(None, description="NSF / APU 硬件配置")
    events: list[ApuEvent] = Field(
        default_factory=list, description="全部 APU 寄存器写入（按 CPU 周期）")
    dmc_samples: list[DmcSample] = Field(
        default_factory=list, description="DMC 采样数据（用于重建内存）")
    audio_seconds: float | None = Field(None, ge=0, description="原始渲染时长（秒）")

    @field_validator("time_signature", mode="before")
    @classmethod
    def _time_signature(cls, value: Any) -> str:
        text = str(value).strip()
        if not re.fullmatch(r"\d{1,2}/\d{1,2}", text):
            raise ValueError(f"拍号应写成 4/4 这种形式，收到 {value!r}")
        return text

    @model_validator(mode="before")
    @classmethod
    def _drop_computed(cls, data: Any) -> Any:
        return _drop_extra(data, "duration_beats", "duration_seconds", "note_count",
                           "beats_per_bar", "seconds_per_beat")

    @model_validator(mode="after")
    def _finish(self) -> "Score":
        # 同一个声道只能有一条轨道
        names = [track.channel for track in self.tracks]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            raise ValueError("同一个声道只能有一条轨道，重复了：" +
                             "、".join(sorted(c.value for c in duplicates)))
        return self

    # -- 常用换算 ----------------------------------------------------------

    @property
    def beats_per_bar(self) -> int:
        return int(self.time_signature.split("/")[0])

    @property
    def seconds_per_beat(self) -> float:
        return 60.0 / self.bpm

    def beats_to_seconds(self, beats: float) -> float:
        return beats * self.seconds_per_beat

    def seconds_to_beats(self, seconds: float) -> float:
        return seconds / self.seconds_per_beat

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration_beats(self) -> float:
        return max((track.end for track in self.tracks), default=0.0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration_seconds(self) -> float:
        return self.beats_to_seconds(self.duration_beats)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def note_count(self) -> int:
        return sum(len(track.notes) for track in self.tracks)

    # -- 查轨道 ------------------------------------------------------------

    def track(self, channel: Channel | str) -> Track | None:
        """按声道取轨道，没有就返回 None。"""
        wanted = Channel.from_text(channel)
        return next((t for t in self.tracks if t.channel is wanted), None)

    def ensure_track(self, channel: Channel | str, duty: int = 2) -> Track:
        """按声道取轨道，没有就新建一条（编辑器里很方便）。"""
        track = self.track(channel)
        if track is None:
            track = Track(channel=channel, duty=duty)
            self.tracks.append(track)
        return track


__all__ = [
    "ApuConfig",
    "ApuEvent",
    "Channel",
    "DmcSample",
    "EnvelopeConfig",
    "NSFHeader",
    "NoteEvent",
    "PitchPoint",
    "Score",
    "SweepConfig",
    "Track",
    "all_note_names",
    "midi_to_note_name",
    "note_frequency",
    "note_name_to_midi",
    "parse_duration",
    "parse_pitch",
]
