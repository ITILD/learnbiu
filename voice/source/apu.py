"""APU 音乐引擎：把 .nsf 文件直接还原成波形、WAV 或乐谱。

为什么不“先解析成音符再合成”：
    .nsf 里装的是 6502 音乐程序，只翻译成音名 + 时值会丢掉颤音、滑音、
    DMC 鼓、长度/包络门控、sweep 等细节。本文件的做法是：

    1. 用内置的迷你 6502 模拟器执行音乐程序，记录 APU 寄存器写入的
       精确 CPU 周期；
    2. 按 libgme 的 Nes_Apu / Nes_Oscs 语义推进帧序列器、包络、长度
       计数器、线性计数器和 sweep；
    3. 方波 / 三角波 / 噪声 / DMC 直接按寄存器参数生成波形，混音权重
       与 libgme 一致，最后做零相位高通和 treble 补偿。

乐谱对象（models.Score）同样不丢信息：除了可读的音符表，还保存周期、
包络、扫频、长度、线性计数器、音高曲线、DMC 采样字节和全部寄存器写入
事件。因此 JSON / Markdown 往返之后，依然可以用 `ApuEngine.from_score()`
逐位还原出同样的音频。
"""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from models import (
    NSFHeader,
    ApuConfig,
    ApuEvent,
    DmcSample,
    EnvelopeConfig,
    NoteEvent,
    PitchPoint,
    Score,
    SweepConfig,
    Track,
    midi_to_note_name,
)

SAMPLE_RATE = 44100

# Nsf_Emu.cpp: clock_rate_ = 1789772.72727，play_period = 262*341*4 - 2
CPU_HZ = 1789772.72727 # 1789772.72727 MHz
CYCLES_PER_FRAME = (262 * 341 * 4 - 2) / 12.0   # 29780.5 个 CPU 周期
FRAME_RATE = CPU_HZ / CYCLES_PER_FRAME          # 60.0988 Hz

# Nes_Apu.cpp: NTSC 帧序列器周期
FRAME_PERIOD = 7458

# Nes_Apu.cpp: 长度计数器查表
LENGTH_TABLE = (
    0x0A, 0xFE, 0x14, 0x02, 0x28, 0x04, 0x50, 0x06,
    0xA0, 0x08, 0x3C, 0x0A, 0x0E, 0x0C, 0x1A, 0x0E,
    0x0C, 0x10, 0x18, 0x12, 0x30, 0x14, 0x60, 0x16,
    0xC0, 0x18, 0x48, 0x1A, 0x10, 0x1C, 0x20, 0x1E,
)

# Nes_Oscs.cpp: 噪声周期表（单位：CPU 周期）
NOISE_PERIODS = (
    0x004, 0x008, 0x010, 0x020, 0x040, 0x060, 0x080, 0x0A0,
    0x0CA, 0x0FE, 0x17C, 0x1FC, 0x2FA, 0x3F8, 0x7F2, 0xFE4,
)

# Nes_Oscs.cpp: DMC 周期表（NTSC）
DMC_PERIODS = (
    428, 380, 340, 320, 286, 254, 226, 214,
    190, 160, 142, 128, 106, 84, 72, 54,
)

# Nes_Apu::volume()：线性混音权重（未乘 gain）
# libgme 的 Blip_Buffer 用 30 位累加、输出时右移 14 位（16 位满量程 32768），
# 因此同样的 volume 系数换算到 [-1,1] 波形还要再乘 2。
W_SQUARE = 0.1128 / 15.0
W_TRIANGLE = 0.12765 / 15.0
W_NOISE = 0.0741 / 15.0
W_DMC = 0.42545 / 127.0
GAIN = 1.4 * 2.0                 # Nsf_Emu::set_gain( 1.4 ) × 16 位换算


# ---------------------------------------------------------------------------
# 一、NSF 文件头解析
# ---------------------------------------------------------------------------


def parse_nsf(path: str | Path) -> NSFHeader:
    """读取 .nsf 文件，返回文件头对象。"""
    path = Path(path)
    data = path.read_bytes()
    # NSF 的魔数是 "NESM" + 0x1A 共 5 个字节，版本号在偏移 5
    if len(data) < 0x80 or data[:5] != b"NESM\x1a":
        raise ValueError(f"{path} 不是有效的 NSF 文件（缺少 NESM 标记）")

    def u16(offset: int) -> int:
        return data[offset] | (data[offset + 1] << 8)

    def text(start: int, length: int) -> str:
        raw = data[start:start + length].split(b"\x00", 1)[0]
        return raw.decode("latin-1", errors="replace").strip()

    header = NSFHeader(
        path=path,
        version=data[5],
        song_count=data[6],
        start_song=data[7],
        load_addr=u16(8),
        init_addr=u16(10),
        play_addr=u16(12),
        name=text(14, 32),
        artist=text(46, 32),
        copyright=text(78, 32),
        ntsc_speed=u16(110),
        pal_speed=u16(120),
        speed_flags=data[122],
        chip=data[123],
        rom=data[0x80:],
    )
    if header.version < 2 and header.chip:
        # 扩展音源芯片（VRC6 等）暂不支持，只取内置的 5 个声道
        print(f"[提示] 该 NSF 使用了扩展音源（chip=0x{header.chip:02X}），"
              "本工具只记录 NES 自带的声道。")
    return header


# ---------------------------------------------------------------------------
# 二、迷你 6502 CPU 模拟器
# ---------------------------------------------------------------------------

# 寻址模式（用整数表示，比字符串快）
IMP, ACC, IMM, ZP, ZPX, ZPY, ABS, ABSX, ABSY, IND, INDX, INDY, REL = range(13)

# NTSC 主机的 CPU 频率（Hz）
NTSC_CPU_HZ = 1789773

# 操作码表：0xXX -> (助记符, 寻址模式, 基础周期数)
OPCODES = {
    0x00: ("BRK", IMP, 7), 0x01: ("ORA", INDX, 6), 0x05: ("ORA", ZP, 3),
    0x06: ("ASL", ZP, 5), 0x08: ("PHP", IMP, 3), 0x09: ("ORA", IMM, 2),
    0x0A: ("ASL", ACC, 2), 0x0D: ("ORA", ABS, 4), 0x0E: ("ASL", ABS, 6),
    0x10: ("BPL", REL, 2), 0x11: ("ORA", INDY, 5), 0x15: ("ORA", ZPX, 4),
    0x16: ("ASL", ZPX, 6), 0x18: ("CLC", IMP, 2), 0x19: ("ORA", ABSY, 4),
    0x1D: ("ORA", ABSX, 4), 0x1E: ("ASL", ABSX, 7),
    0x20: ("JSR", ABS, 6), 0x21: ("AND", INDX, 6), 0x24: ("BIT", ZP, 3),
    0x25: ("AND", ZP, 3), 0x26: ("ROL", ZP, 5), 0x28: ("PLP", IMP, 4),
    0x29: ("AND", IMM, 2), 0x2A: ("ROL", ACC, 2), 0x2C: ("BIT", ABS, 4),
    0x2D: ("AND", ABS, 4), 0x2E: ("ROL", ABS, 6), 0x30: ("BMI", REL, 2),
    0x31: ("AND", INDY, 5), 0x35: ("AND", ZPX, 4), 0x36: ("ROL", ZPX, 6),
    0x38: ("SEC", IMP, 2), 0x39: ("AND", ABSY, 4), 0x3D: ("AND", ABSX, 4),
    0x3E: ("ROL", ABSX, 7),
    0x40: ("RTI", IMP, 6), 0x41: ("EOR", INDX, 6), 0x45: ("EOR", ZP, 3),
    0x46: ("LSR", ZP, 5), 0x48: ("PHA", IMP, 3), 0x49: ("EOR", IMM, 2),
    0x4A: ("LSR", ACC, 2), 0x4C: ("JMP", ABS, 3), 0x4D: ("EOR", ABS, 4),
    0x4E: ("LSR", ABS, 6), 0x50: ("BVC", REL, 2), 0x51: ("EOR", INDY, 5),
    0x55: ("EOR", ZPX, 4), 0x56: ("LSR", ZPX, 6), 0x58: ("CLI", IMP, 2),
    0x59: ("EOR", ABSY, 4), 0x5D: ("EOR", ABSX, 4), 0x5E: ("LSR", ABSX, 7),
    0x60: ("RTS", IMP, 6), 0x61: ("ADC", INDX, 6), 0x65: ("ADC", ZP, 3),
    0x66: ("ROR", ZP, 5), 0x68: ("PLA", IMP, 4), 0x69: ("ADC", IMM, 2),
    0x6A: ("ROR", ACC, 2), 0x6C: ("JMP", IND, 5), 0x6D: ("ADC", ABS, 4),
    0x6E: ("ROR", ABS, 6), 0x70: ("BVS", REL, 2), 0x71: ("ADC", INDY, 5),
    0x75: ("ADC", ZPX, 4), 0x76: ("ROR", ZPX, 6), 0x78: ("SEI", IMP, 2),
    0x79: ("ADC", ABSY, 4), 0x7D: ("ADC", ABSX, 4), 0x7E: ("ROR", ABSX, 7),
    0x81: ("STA", INDX, 6), 0x84: ("STY", ZP, 3), 0x85: ("STA", ZP, 3),
    0x86: ("STX", ZP, 3), 0x88: ("DEY", IMP, 2), 0x8A: ("TXA", IMP, 2),
    0x8C: ("STY", ABS, 4), 0x8D: ("STA", ABS, 4), 0x8E: ("STX", ABS, 4),
    0x90: ("BCC", REL, 2), 0x91: ("STA", INDY, 6), 0x94: ("STY", ZPX, 4),
    0x95: ("STA", ZPX, 4), 0x96: ("STX", ZPY, 4), 0x98: ("TYA", IMP, 2),
    0x99: ("STA", ABSY, 5), 0x9A: ("TXS", IMP, 2), 0x9D: ("STA", ABSX, 5),
    0xA0: ("LDY", IMM, 2), 0xA1: ("LDA", INDX, 6), 0xA2: ("LDX", IMM, 2),
    0xA4: ("LDY", ZP, 3), 0xA5: ("LDA", ZP, 3), 0xA6: ("LDX", ZP, 3),
    0xA8: ("TAY", IMP, 2), 0xA9: ("LDA", IMM, 2), 0xAA: ("TAX", IMP, 2),
    0xAC: ("LDY", ABS, 4), 0xAD: ("LDA", ABS, 4), 0xAE: ("LDX", ABS, 4),
    0xB0: ("BCS", REL, 2), 0xB1: ("LDA", INDY, 5), 0xB4: ("LDY", ZPX, 4),
    0xB5: ("LDA", ZPX, 4), 0xB6: ("LDX", ZPY, 4), 0xB8: ("CLV", IMP, 2),
    0xB9: ("LDA", ABSY, 4), 0xBA: ("TSX", IMP, 2), 0xBC: ("LDY", ABSX, 4),
    0xBD: ("LDA", ABSX, 4), 0xBE: ("LDX", ABSY, 4),
    0xC0: ("CPY", IMM, 2), 0xC1: ("CMP", INDX, 6), 0xC4: ("CPY", ZP, 3),
    0xC5: ("CMP", ZP, 3), 0xC6: ("DEC", ZP, 5), 0xC8: ("INY", IMP, 2),
    0xC9: ("CMP", IMM, 2), 0xCA: ("DEX", IMP, 2), 0xCC: ("CPY", ABS, 4),
    0xCD: ("CMP", ABS, 4), 0xCE: ("DEC", ABS, 6), 0xD0: ("BNE", REL, 2),
    0xD1: ("CMP", INDY, 5), 0xD5: ("CMP", ZPX, 4), 0xD6: ("DEC", ZPX, 6),
    0xD8: ("CLD", IMP, 2), 0xD9: ("CMP", ABSY, 4), 0xDD: ("CMP", ABSX, 4),
    0xDE: ("DEC", ABSX, 7),
    0xE0: ("CPX", IMM, 2), 0xE1: ("SBC", INDX, 6), 0xE4: ("CPX", ZP, 3),
    0xE5: ("SBC", ZP, 3), 0xE6: ("INC", ZP, 5), 0xE8: ("INX", IMP, 2),
    0xE9: ("SBC", IMM, 2), 0xEA: ("NOP", IMP, 2), 0xEC: ("CPX", ABS, 4),
    0xED: ("SBC", ABS, 4), 0xEE: ("INC", ABS, 6), 0xF0: ("BEQ", REL, 2),
    0xF1: ("SBC", INDY, 5), 0xF5: ("SBC", ZPX, 4), 0xF6: ("INC", ZPX, 6),
    0xF8: ("SED", IMP, 2), 0xF9: ("SBC", ABSY, 4), 0xFD: ("SBC", ABSX, 4),
    0xFE: ("INC", ABSX, 7),
}

# CPU 状态标志位
FLAG_C, FLAG_Z, FLAG_I, FLAG_D, FLAG_B = 0x01, 0x02, 0x04, 0x08, 0x10
FLAG_U, FLAG_V, FLAG_N = 0x20, 0x40, 0x80


class CPU6502:
    """一个够用就好的 6502 模拟器：执行游戏音乐代码，并记录 APU 写入。"""

    def __init__(self) -> None:
        self.mem = bytearray(0x10000)
        self.a = self.x = self.y = 0
        self.sp = 0xFD
        self.p = FLAG_U | FLAG_I
        self.pc = 0
        self.cycles = 0
        self.frame = 0
        self.cycles_per_frame = 29780
        # 记录 (帧号, APU 寄存器地址, 写入值)
        self.apu_events: list[tuple[int, int, int]] = []
        # 记录 (CPU 累计周期, 地址, 值)：逐周期还原滑音/包络需要精确时刻
        self.apu_cycle_events: list[tuple[int, int, int]] = []
        self._build_table()

    def _build_table(self) -> None:
        """把操作码表编译成 [处理函数, 寻址模式, 周期数] 的列表。"""
        handlers = _make_handlers()
        self.table: list[tuple] = []
        for opcode in range(256):
            info = OPCODES.get(opcode)
            if info is None:
                # 非官方操作码：当作单字节 NOP，尽量不让程序崩溃
                self.table.append((handlers["NOP"], IMP, 2))
                continue
            name, mode, cycles = info
            self.table.append((handlers[name], mode, cycles))

    def reset_registers(self) -> None:
        self.a = self.x = self.y = 0
        self.sp = 0xFD
        self.p = FLAG_U | FLAG_I
        self.cycles = 0
        self.frame = 0
        self.pc = 0
        # 清空内存和存档区，保证每次重试都从干净状态开始
        self.mem[0x0000:0x0800] = bytes(0x0800)
        self.mem[0x6000:0x8000] = bytes(0x2000)
        self.apu_events.clear()
        self.apu_cycle_events.clear()

    def load_rom(self, load_addr: int, rom: bytes) -> None:
        end = min(0x10000, load_addr + len(rom))
        self.mem[load_addr:end] = rom[: end - load_addr]

    # -- 内存读写（带 NES 特殊地址处理）-----------------------------------

    def read(self, addr: int) -> int:
        if addr < 0x2000:                       # 2KB 内存（有镜像）
            return self.mem[addr & 0x07FF]
        if addr < 0x4000:                       # PPU 寄存器：假装处于垂直消隐
            return 0x80 if (addr & 7) == 2 else 0
        if addr == 0x4015:                      # APU 状态：所有声道都"有声"
            return 0x0F
        if addr == 0x4016:                      # 手柄：无按键
            return 0x40
        if addr >= 0x4000:
            return self.mem[addr]
        return 0

    def write(self, addr: int, value: int) -> None:
        value &= 0xFF
        if addr < 0x2000:
            self.mem[addr & 0x07FF] = value
        elif addr < 0x4000:
            return                              # PPU 寄存器，忽略
        elif addr == 0x4014:
            return                              # 精灵 DMA，忽略
        elif addr <= 0x4017:
            self.mem[addr] = value
            if addr <= 0x4013 or addr in (0x4015, 0x4017):
                self.apu_events.append((self.frame, addr, value))
                self.apu_cycle_events.append((self.cycles, addr, value))
        elif addr < 0x6000:
            return
        elif addr >= 0x8000:
            return                              # ROM，不可写
        else:
            self.mem[addr] = value              # $6000-$7FFF 存档内存

    # -- 栈操作 ------------------------------------------------------------

    def push(self, value: int) -> None:
        self.mem[0x100 + self.sp] = value & 0xFF
        self.sp = (self.sp - 1) & 0xFF

    def pop(self) -> int:
        self.sp = (self.sp + 1) & 0xFF
        return self.mem[0x100 + self.sp]

    # -- 寻址 --------------------------------------------------------------

    def addr(self, mode: int) -> int:
        mem, pc = self.mem, self.pc
        if mode == IMM:
            self.pc = (pc + 1) & 0xFFFF
            return pc
        if mode == ZP:
            self.pc = (pc + 1) & 0xFFFF
            return mem[pc]
        if mode == ZPX:
            self.pc = (pc + 1) & 0xFFFF
            return (mem[pc] + self.x) & 0xFF
        if mode == ZPY:
            self.pc = (pc + 1) & 0xFFFF
            return (mem[pc] + self.y) & 0xFF
        if mode == ABS:
            self.pc = (pc + 2) & 0xFFFF
            return mem[pc] | (mem[(pc + 1) & 0xFFFF] << 8)
        if mode == ABSX:
            self.pc = (pc + 2) & 0xFFFF
            return ((mem[pc] | (mem[(pc + 1) & 0xFFFF] << 8)) + self.x) & 0xFFFF
        if mode == ABSY:
            self.pc = (pc + 2) & 0xFFFF
            return ((mem[pc] | (mem[(pc + 1) & 0xFFFF] << 8)) + self.y) & 0xFFFF
        if mode == INDX:
            self.pc = (pc + 1) & 0xFFFF
            ptr = (mem[pc] + self.x) & 0xFF
            return mem[ptr] | (mem[(ptr + 1) & 0xFF] << 8)
        if mode == INDY:
            self.pc = (pc + 1) & 0xFFFF
            ptr = mem[pc]
            base = mem[ptr] | (mem[(ptr + 1) & 0xFF] << 8)
            return (base + self.y) & 0xFFFF
        return 0

    # -- 执行 --------------------------------------------------------------

    def step(self) -> None:
        opcode = self.mem[self.pc]
        handler, mode, cycles = self.table[opcode]
        self.pc = (self.pc + 1) & 0xFFFF
        handler(self, mode)
        self.cycles += cycles

    def call(self, address: int, a: int = 0, max_cycles: int = 3_000_000) -> bool:
        """像调用函数一样执行一段代码，直到它 RTS 返回。

        返回 True 表示正常返回，False 表示超过周期上限（被强制打断）。
        """
        self.a = a & 0xFF
        self.push(0xFF)
        self.push(0xFF)          # RTS 之后会跳回 $0000，作为"返回成功"的标记
        self.pc = address
        start = self.cycles
        while self.pc != 0 and self.cycles - start < max_cycles:
            self.step()
        return self.pc == 0

    def advance_frame(self) -> None:
        """空转一帧（不调用 PLAY）：NSF 规范里 PLAY 要等 init 之后几帧才开始。"""
        self.frame += 1
        self.cycles += self.cycles_per_frame

    def run_frame(self, play_addr: int) -> None:
        """播放一帧（约 1/60 秒）：调用一次 PLAY 程序。"""
        self.frame += 1
        saved_sp = self.sp
        self.push(0xFF)
        self.push(0xFF)
        self.pc = play_addr
        limit = self.cycles + self.cycles_per_frame
        while self.pc != 0 and self.cycles < limit:
            self.step()
        if self.pc != 0:
            # 有些音乐程序是死循环、永远不返回，这里把栈恢复，避免越堆越多
            self.sp = saved_sp
        self.cycles = limit


def _zn(cpu: CPU6502, value: int) -> None:
    """根据结果设置 Zero / Negative 标志。"""
    cpu.p = (cpu.p & 0x7D) | (value & 0x80) | (FLAG_Z if value == 0 else 0)


def _make_handlers() -> dict:
    """生成"助记符 -> 执行函数"的字典，让主循环保持简洁。"""

    def read_op(cpu: CPU6502, mode: int) -> int:
        return cpu.read(cpu.addr(mode))

    # -- 装入 / 存储 -------------------------------------------------------

    def lda(cpu, mode):
        cpu.a = read_op(cpu, mode)
        _zn(cpu, cpu.a)

    def ldx(cpu, mode):
        cpu.x = read_op(cpu, mode)
        _zn(cpu, cpu.x)

    def ldy(cpu, mode):
        cpu.y = read_op(cpu, mode)
        _zn(cpu, cpu.y)

    def sta(cpu, mode):
        cpu.write(cpu.addr(mode), cpu.a)

    def stx(cpu, mode):
        cpu.write(cpu.addr(mode), cpu.x)

    def sty(cpu, mode):
        cpu.write(cpu.addr(mode), cpu.y)

    # -- 算术：ADC / SBC 共用一套带进位的加减 ------------------------------

    def _add_with_carry(cpu: CPU6502, value: int) -> None:
        carry = 1 if cpu.p & FLAG_C else 0
        total = cpu.a + value + carry
        result = total & 0xFF
        cpu.p &= ~(FLAG_C | FLAG_Z | FLAG_N | FLAG_V)
        if total > 0xFF:
            cpu.p |= FLAG_C
        if result == 0:
            cpu.p |= FLAG_Z
        if result & 0x80:
            cpu.p |= FLAG_N
        if ~(cpu.a ^ value) & (cpu.a ^ result) & 0x80:
            cpu.p |= FLAG_V
        cpu.a = result

    def adc(cpu, mode):
        _add_with_carry(cpu, read_op(cpu, mode))

    def sbc(cpu, mode):
        # SBC 等于 ADC(~v)
        _add_with_carry(cpu, read_op(cpu, mode) ^ 0xFF)

    # -- 比较 / 位测试 -----------------------------------------------------

    def compare(cpu, register, mode):
        value = read_op(cpu, mode)
        result = (register - value) & 0xFF
        cpu.p &= ~(FLAG_C | FLAG_Z | FLAG_N)
        if register >= value:
            cpu.p |= FLAG_C
        if result == 0:
            cpu.p |= FLAG_Z
        if result & 0x80:
            cpu.p |= FLAG_N

    def cmp(cpu, mode):
        compare(cpu, cpu.a, mode)

    def cpx(cpu, mode):
        compare(cpu, cpu.x, mode)

    def cpy(cpu, mode):
        compare(cpu, cpu.y, mode)

    def bit(cpu, mode):
        value = read_op(cpu, mode)
        cpu.p &= ~(FLAG_Z | FLAG_N | FLAG_V)
        if (cpu.a & value) == 0:
            cpu.p |= FLAG_Z
        cpu.p |= value & (FLAG_N | FLAG_V)

    # -- 移位 / 自增自减 ---------------------------------------------------

    def _shift(cpu, mode, kind):
        """统一处理 ASL / LSR / ROL / ROR。"""
        if mode == ACC:
            value, addr = cpu.a, None
        else:
            addr = cpu.addr(mode)
            value = cpu.read(addr)
        if kind == "ASL":
            carry = (value >> 7) & 1
            result = (value << 1) & 0xFF
        elif kind == "LSR":
            carry = value & 1
            result = value >> 1
        elif kind == "ROL":
            carry = (value >> 7) & 1
            result = ((value << 1) | (1 if cpu.p & FLAG_C else 0)) & 0xFF
        else:  # ROR
            carry = value & 1
            result = (value >> 1) | (0x80 if cpu.p & FLAG_C else 0)
        cpu.p = (cpu.p & ~FLAG_C) | (FLAG_C if carry else 0)
        _zn(cpu, result)
        if addr is None:
            cpu.a = result
        else:
            cpu.write(addr, result)

    def asl(cpu, mode):
        _shift(cpu, mode, "ASL")

    def lsr(cpu, mode):
        _shift(cpu, mode, "LSR")

    def rol(cpu, mode):
        _shift(cpu, mode, "ROL")

    def ror(cpu, mode):
        _shift(cpu, mode, "ROR")

    def _incdec(cpu, mode, delta):
        addr = cpu.addr(mode)
        value = (cpu.read(addr) + delta) & 0xFF
        cpu.write(addr, value)
        _zn(cpu, value)

    def inc(cpu, mode):
        _incdec(cpu, mode, 1)

    def dec(cpu, mode):
        _incdec(cpu, mode, -1)

    # -- 分支 / 跳转 -------------------------------------------------------

    def branch(cpu, condition):
        offset = cpu.mem[cpu.pc]
        cpu.pc = (cpu.pc + 1) & 0xFFFF
        if condition:
            if offset & 0x80:
                offset -= 0x100
            cpu.pc = (cpu.pc + offset) & 0xFFFF
            cpu.cycles += 1

    def bcc(cpu, mode):
        branch(cpu, not (cpu.p & FLAG_C))

    def bcs(cpu, mode):
        branch(cpu, bool(cpu.p & FLAG_C))

    def beq(cpu, mode):
        branch(cpu, bool(cpu.p & FLAG_Z))

    def bne(cpu, mode):
        branch(cpu, not (cpu.p & FLAG_Z))

    def bmi(cpu, mode):
        branch(cpu, bool(cpu.p & FLAG_N))

    def bpl(cpu, mode):
        branch(cpu, not (cpu.p & FLAG_N))

    def bvc(cpu, mode):
        branch(cpu, not (cpu.p & FLAG_V))

    def bvs(cpu, mode):
        branch(cpu, bool(cpu.p & FLAG_V))

    def jmp(cpu, mode):
        if mode == IND:
            ptr = cpu.addr(ABS)
            cpu.pc = cpu.mem[ptr] | (cpu.mem[(ptr + 1) & 0xFFFF] << 8)
        else:
            cpu.pc = cpu.addr(ABS)

    def jsr(cpu, mode):
        target = cpu.addr(ABS)
        ret = (cpu.pc - 1) & 0xFFFF
        cpu.push((ret >> 8) & 0xFF)
        cpu.push(ret & 0xFF)
        cpu.pc = target

    def rts(cpu, mode):
        low = cpu.pop()
        high = cpu.pop()
        cpu.pc = (((high << 8) | low) + 1) & 0xFFFF

    def rti(cpu, mode):
        cpu.p = (cpu.pop() & ~0x30) | FLAG_U
        low = cpu.pop()
        high = cpu.pop()
        cpu.pc = (high << 8) | low

    def brk(cpu, mode):
        cpu.pc = (cpu.pc + 1) & 0xFFFF
        cpu.push((cpu.pc >> 8) & 0xFF)
        cpu.push(cpu.pc & 0xFF)
        cpu.push(cpu.p | FLAG_B | FLAG_U)
        cpu.p |= FLAG_I
        cpu.pc = cpu.read(0xFFFE) | (cpu.read(0xFFFF) << 8)

    # -- 堆栈 / 逻辑 / 传送 ------------------------------------------------

    def pha(cpu, mode):
        cpu.push(cpu.a)

    def php(cpu, mode):
        cpu.push(cpu.p | FLAG_B | FLAG_U)

    def pla(cpu, mode):
        cpu.a = cpu.pop()
        _zn(cpu, cpu.a)

    def plp(cpu, mode):
        cpu.p = (cpu.pop() & ~0x30) | FLAG_U

    def nop(cpu, mode):
        pass

    def ora(cpu, mode):
        cpu.a |= read_op(cpu, mode)
        _zn(cpu, cpu.a)

    def and_(cpu, mode):
        cpu.a &= read_op(cpu, mode)
        _zn(cpu, cpu.a)

    def eor(cpu, mode):
        cpu.a ^= read_op(cpu, mode)
        _zn(cpu, cpu.a)

    def _transfer(cpu, value, target):
        setattr(cpu, target, value)
        _zn(cpu, value)

    handlers = {
        "LDA": lda, "LDX": ldx, "LDY": ldy,
        "STA": sta, "STX": stx, "STY": sty,
        "ADC": adc, "SBC": sbc,
        "CMP": cmp, "CPX": cpx, "CPY": cpy, "BIT": bit,
        "ASL": asl, "LSR": lsr, "ROL": rol, "ROR": ror,
        "INC": inc, "DEC": dec,
        "BCC": bcc, "BCS": bcs, "BEQ": beq, "BNE": bne,
        "BMI": bmi, "BPL": bpl, "BVC": bvc, "BVS": bvs,
        "JMP": jmp, "JSR": jsr, "RTS": rts, "RTI": rti, "BRK": brk,
        "PHA": pha, "PHP": php, "PLA": pla, "PLP": plp,
        "ORA": ora, "AND": and_, "EOR": eor,
        "TAX": lambda c, m: _transfer(c, c.a, "x"),
        "TAY": lambda c, m: _transfer(c, c.a, "y"),
        "TXA": lambda c, m: _transfer(c, c.x, "a"),
        "TYA": lambda c, m: _transfer(c, c.y, "a"),
        "TSX": lambda c, m: _transfer(c, c.sp, "x"),
        "TXS": lambda c, m: setattr(c, "sp", c.x),
        "INX": lambda c, m: _transfer(c, (c.x + 1) & 0xFF, "x"),
        "INY": lambda c, m: _transfer(c, (c.y + 1) & 0xFF, "y"),
        "DEX": lambda c, m: _transfer(c, (c.x - 1) & 0xFF, "x"),
        "DEY": lambda c, m: _transfer(c, (c.y - 1) & 0xFF, "y"),
        "CLC": lambda c, m: setattr(c, "p", c.p & ~FLAG_C),
        "SEC": lambda c, m: setattr(c, "p", c.p | FLAG_C),
        "CLI": lambda c, m: setattr(c, "p", c.p & ~FLAG_I),
        "SEI": lambda c, m: setattr(c, "p", c.p | FLAG_I),
        "CLD": lambda c, m: setattr(c, "p", c.p & ~FLAG_D),
        "SED": lambda c, m: setattr(c, "p", c.p | FLAG_D),
        "CLV": lambda c, m: setattr(c, "p", c.p & ~FLAG_V),
        "NOP": nop,
    }
    return handlers


# ---------------------------------------------------------------------------
# 三、APU 渲染器：寄存器写入 -> 波形
# ---------------------------------------------------------------------------


def _make_noise_sequence(
        short: bool) -> tuple[np.ndarray, np.ndarray, dict[int, int], np.ndarray]:
    """预生成 15 位 LFSR 的完整状态序列、输出位和“状态 -> 下标”映射。"""
    tap = 8 if short else 13
    state = 0x4000
    states: list[int] = []
    index: dict[int, int] = {}
    while state not in index:
        index[state] = len(states)
        states.append(state)
        feedback = ((state << tap) ^ (state << 14)) & 0x4000
        state = ((state >> 1) | feedback) & 0x7FFF
    arr = np.asarray(states, dtype=np.int32)
    bits = (arr & 1).astype(np.float64)
    # 前缀和（序列接两遍，方便跨序列末尾取窗口）：求任意时间窗口里
    # “高电平”占的比例。
    prefix = np.concatenate(([0.0], np.cumsum(np.tile(bits, 2))))
    return arr, bits, index, prefix


# 长模式 32767 步、短模式 93 步（与 libgme 一致）
_NOISE_LONG = _make_noise_sequence(False)
_NOISE_SHORT = _make_noise_sequence(True)


class _EnvelopeOsc:
    """方波 / 噪声共用的包络与长度计数器状态。"""

    __slots__ = ("regs", "length_counter", "envelope", "env_delay", "env_start")

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.regs = [0, 0, 0, 0]
        self.length_counter = 0
        self.envelope = 0
        self.env_delay = 0
        self.env_start = False

    def clock_length(self, halt_mask: int) -> None:
        if self.length_counter and not (self.regs[0] & halt_mask):
            self.length_counter -= 1

    def clock_envelope(self) -> None:
        period = self.regs[0] & 15
        if self.env_start:
            self.env_start = False
            self.env_delay = period
            self.envelope = 15
        else:
            self.env_delay -= 1
            if self.env_delay < 0:
                self.env_delay = period
                if self.envelope or (self.regs[0] & 0x20):
                    self.envelope = (self.envelope - 1) & 15

    def volume(self) -> int:
        if self.length_counter == 0:
            return 0
        if self.regs[0] & 0x10:
            return self.regs[0] & 15
        return self.envelope


class _Square(_EnvelopeOsc):
    __slots__ = ("phase_cycles", "sweep_delay")

    def reset(self) -> None:
        super().reset()
        self.phase_cycles = 0.0
        self.sweep_delay = 0

    def period(self) -> int:
        return ((self.regs[3] & 7) << 8) | self.regs[2]

    def clock_sweep(self, negative_adjust: int) -> None:
        sweep = self.regs[1]
        self.sweep_delay -= 1
        if self.sweep_delay < 0:
            self.sweep_delay = 0
            shift = sweep & 7
            period = self.period()
            if shift and (sweep & 0x80) and period >= 8:
                offset = period >> shift
                if sweep & 0x08:
                    offset = negative_adjust - offset
                if period + offset < 0x800:
                    period += offset
                    self.regs[2] = period & 0xFF
                    self.regs[3] = (self.regs[3] & ~7) | ((period >> 8) & 7)
            self.sweep_delay = (sweep >> 4) & 7


class _Triangle:
    __slots__ = ("regs", "length_counter", "linear_counter", "reload_flag",
                 "phase_steps")

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.regs = [0, 0, 0, 0]
        self.length_counter = 0
        self.linear_counter = 0
        self.reload_flag = False
        # 相位按“步”计数（0..31），和 libgme 一样在周期改变时保持步号不变
        self.phase_steps = 0.0

    def period(self) -> int:
        return ((self.regs[3] & 7) << 8) | self.regs[2]

    def clock_length(self) -> None:
        # 三角波的 halt 标志是 $4008 的 bit7（和线性计数器共用）
        if self.length_counter and not (self.regs[0] & 0x80):
            self.length_counter -= 1

    def clock_linear_counter(self) -> None:
        if self.reload_flag:
            self.linear_counter = self.regs[0] & 0x7F
        elif self.linear_counter:
            self.linear_counter -= 1
        if not (self.regs[0] & 0x80):
            self.reload_flag = False


class _Noise(_EnvelopeOsc):
    __slots__ = ("seq_states", "seq_bits", "seq_index", "seq_prefix",
                 "index", "last_clock")

    def reset(self) -> None:
        super().reset()
        (self.seq_states, self.seq_bits,
         self.seq_index, self.seq_prefix) = _NOISE_LONG
        self.index = 0
        self.last_clock = 0.0

    def period(self) -> int:
        return NOISE_PERIODS[self.regs[2] & 15]

    def set_short(self, short: bool) -> None:
        """切换短模式时，把当前 LFSR 状态映射到新序列。"""
        state = int(self.seq_states[self.index])
        (self.seq_states, self.seq_bits,
         self.seq_index, self.seq_prefix) = _NOISE_SHORT if short else _NOISE_LONG
        self.index = self.seq_index.get(state, 0)


class _Dmc:
    __slots__ = ("regs", "period", "loop", "address", "length_counter", "buf",
                 "buf_full", "bits", "bits_remain", "silence", "dac",
                 "next_bit_time", "playing")

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.regs = [0, 0, 0, 0]
        self.period = 0x1AC
        self.loop = False
        self.address = 0
        self.length_counter = 0
        self.buf = 0
        self.buf_full = False
        self.bits = 0
        self.bits_remain = 0
        self.silence = True
        self.dac = 0
        self.next_bit_time = 0.0
        self.playing = False


class ApuRenderer:
    """把带周期时间戳的 APU 写入还原成音频。"""

    def __init__(self, header: NSFHeader | SimpleNamespace,
                 events: list[tuple[int, int, int]], mem: bytearray) -> None:
        self.header = header
        self.events = sorted(events, key=lambda item: item[0])
        self.mem = mem
        # 五个声道按寄存器顺序排列：pulse1 / pulse2 / triangle / noise / dmc
        self.square1, self.square2 = _Square(), _Square()
        self.triangle, self.noise, self.dmc = _Triangle(), _Noise(), _Dmc()
        self.oscs = (self.square1, self.square2, self.triangle,
                     self.noise, self.dmc)

        self.osc_enables = 0
        self.frame_mode = 0
        self.frame_index = 0
        self.frame_delay = 1
        self.last_time = 0.0
        self._cps = CPU_HZ / 44100.0
        # 调试用：bit0..bit4 分别静音 square1/square2/triangle/noise/dmc
        self.mute_mask = 0

        self._reset()
        # Nsf_Emu::start_track_()：Nes_Apu::reset 之后再打开声道、设置帧模式
        self._write(0x4015, 0x0F, 0.0)
        self._write(0x4017, 0x80 if (header.speed_flags & 0x10) else 0x00, 0.0)

    # -- 复位 --------------------------------------------------------------

    def _reset(self) -> None:
        # render() 期间记录 DMC 每个 DAC 跳变的 (CPU 周期, 增量)，
        # 结尾统一用带限阶跃核合成波形（对应 Blip 的 sinc 重建）。
        self.dmc_transitions: list[tuple[float, int]] = []
        for osc in self.oscs:
            osc.reset()
        self.osc_enables = 0
        self.frame_mode = 0
        self.frame_index = 0
        self.frame_delay = 1
        self.last_time = 0.0

        # Nes_Apu::reset()：先写 $4017 / $4015，再给每个声道写初值
        self._write(0x4017, 0x00, 0.0)
        self._write(0x4015, 0x00, 0.0)
        for addr in range(0x4000, 0x4014):
            self._write(addr, 0x10 if (addr & 3) == 0 else 0x00, 0.0)

    # -- 帧序列器 ----------------------------------------------------------

    def _run_frames_until(self, end_time: float, process_at_end: bool = False) -> None:
        if end_time < self.last_time:
            return
        while True:
            t = self.last_time + self.frame_delay
            if t > end_time or (t == end_time and not process_at_end):
                self.frame_delay -= end_time - self.last_time
                self.last_time = end_time
                return

            self.frame_delay -= t - self.last_time
            self.last_time = t
            self._frame_step()

    def _frame_step(self) -> None:
        index = self.frame_index
        self.frame_index = (index + 1) & 3
        self.frame_delay = FRAME_PERIOD

        if index in (0, 2):
            # 1/4 帧：长度计数器 + 扫频，并推进包络 / 线性计数器
            self.square1.clock_length(0x20)
            self.square2.clock_length(0x20)
            self.noise.clock_length(0x20)
            self.triangle.clock_length()
            self.square1.clock_sweep(-1)
            self.square2.clock_sweep(0)
        elif index == 1:
            self.frame_delay -= 2          # NTSC mode 0：第 1 帧略短
        elif index == 3 and (self.frame_mode & 0x80):
            self.frame_delay += FRAME_PERIOD - 6

        self.square1.clock_envelope()
        self.square2.clock_envelope()
        self.noise.clock_envelope()
        self.triangle.clock_linear_counter()

    # -- 寄存器写入 --------------------------------------------------------

    def _write(self, addr: int, data: int, time: float) -> None:
        data &= 0xFF
        if addr < 0x4014:
            index = (addr - 0x4000) >> 2
            reg = addr & 3
            osc = self.oscs[index]
            osc.regs[reg] = data

            if index == 4:
                self._dmc_write(reg, data, time)
            elif index == 3 and reg == 2:
                # $400E bit7：短模式（tap=8），噪声序列周期变成 93 步
                self.noise.set_short(bool(data & 0x80))
            elif reg == 3:
                if (self.osc_enables >> index) & 1:
                    osc.length_counter = LENGTH_TABLE[(data >> 3) & 0x1F]
                if index < 2:
                    # 方波相位复位到 phase_range - 1（最后一步），
                    # 下一步时钟正好进入高电平段
                    period = ((data & 7) << 8) | osc.regs[2]
                    osc.phase_cycles = 14.0 * (period + 1)   # 7 步 × 2(p+1)
                    osc.env_start = True
                elif index == 3:
                    osc.env_start = True
                else:
                    osc.reload_flag = True          # 三角波线性计数器重载

        elif addr == 0x4015:
            # 关闭的声道清空长度计数器；DMC 打开/关闭有额外动作
            for i in range(4, -1, -1):
                if not ((data >> i) & 1):
                    self.oscs[i].length_counter = 0
            old = self.osc_enables
            self.osc_enables = data
            if not (data & 0x10):
                self.dmc.playing = False
                self.dmc.length_counter = 0
            elif not (old & 0x10):
                self._dmc_start(time)

        elif addr == 0x4017:
            self.frame_mode = data
            self.frame_delay = int(self.frame_delay) & 1
            self.frame_index = 0
            if not (data & 0x80):
                self.frame_index = 1
                self.frame_delay += FRAME_PERIOD

    # -- DMC ---------------------------------------------------------------

    def _dmc_write(self, reg: int, data: int, time: float) -> None:
        if reg == 0:
            self.dmc.period = DMC_PERIODS[data & 15]
            self.dmc.loop = bool(data & 0x40)
        elif reg == 1:
            old = self.dmc.dac
            self.dmc.dac = data & 0x7F
            if self.dmc.dac != old:
                self.dmc_transitions.append((time, self.dmc.dac - old))
        else:
            self.dmc.regs[reg] = data

    def _dmc_reload(self) -> None:
        self.dmc.address = 0x4000 + self.dmc.regs[2] * 0x40
        self.dmc.length_counter = self.dmc.regs[3] * 0x10 + 1

    def _dmc_fill(self) -> None:
        dmc = self.dmc
        if dmc.buf_full or dmc.length_counter == 0:
            return
        dmc.buf = self.mem[(0x8000 + dmc.address) & 0xFFFF]
        dmc.address = (dmc.address + 1) & 0x7FFF
        dmc.buf_full = True
        dmc.length_counter -= 1
        if dmc.length_counter == 0:
            if dmc.loop:
                self._dmc_reload()
            else:
                self.osc_enables &= ~0x10

    def _dmc_start(self, time: float) -> None:
        dmc = self.dmc
        self._dmc_reload()
        self._dmc_fill()
        dmc.bits = dmc.buf
        dmc.buf = 0
        dmc.buf_full = False
        dmc.bits_remain = 8
        dmc.silence = False
        dmc.next_bit_time = time + dmc.period
        dmc.playing = True
        self._dmc_fill()

    def _dmc_advance(self, time: float) -> None:
        dmc = self.dmc
        if not dmc.playing:
            return
        while dmc.next_bit_time <= time:
            if not dmc.silence:
                step = (dmc.bits & 1) * 4 - 2
                dmc.bits >>= 1
                value = dmc.dac + step
                if 0 <= value <= 0x7F:
                    dmc.dac = value
                    self.dmc_transitions.append((dmc.next_bit_time, step))
                dmc.bits_remain -= 1
                if dmc.bits_remain == 0:
                    if dmc.buf_full:
                        dmc.bits = dmc.buf
                        dmc.buf_full = False
                        dmc.bits_remain = 8
                        self._dmc_fill()
                    else:
                        dmc.silence = True
            dmc.next_bit_time += dmc.period

    # -- 波形 --------------------------------------------------------------

    def _square_wave(self, square: _Square, times: np.ndarray,
                     t0: float) -> np.ndarray:
        count = len(times)
        if count == 0:
            return times
        period = square.period()
        timer_period = (period + 1) * 2
        volume = square.volume()
        offset = period >> (square.regs[1] & 7)
        if square.regs[1] & 0x08:
            offset = 0
        if volume == 0 or period < 8 or (period + offset) >= 0x800:
            return np.zeros(count)

        phase = square.phase_cycles + (times - t0)
        duty = (0.125, 0.25, 0.5, 0.75)[(square.regs[0] >> 6) & 3]
        # phase_range = 8：timer_period 只是 1/8 周期，完整周期是 8 倍。
        full_period = timer_period * 8
        # 用“窗口内高电平占比”解析积分：以采样点为中心、宽 1/4 采样周期
        # 的窄窗做平均，窄占空比/高音时不损失幅度，又比点采样少混叠。
        span = self._cps / full_period
        half_width = span / 8

        def high_time(x: np.ndarray) -> np.ndarray:
            whole = np.floor(x)
            return whole * duty + np.minimum(x - whole, duty)

        a = phase / full_period + span * 0.5
        average = (high_time(a + half_width)
                   - high_time(a - half_width)) / (2.0 * half_width)
        return (average - duty) * volume        # 以占空比均值为零点

    def _triangle_wave(self, times: np.ndarray, t0: float) -> np.ndarray:
        count = len(times)
        if count == 0:
            return times
        tri = self.triangle
        timer_period = tri.period() + 1
        if not (tri.length_counter and tri.linear_counter and timer_period >= 3):
            return np.zeros(count)
        total = tri.phase_steps + (times - t0) / timer_period
        phase = np.floor(total).astype(np.int64) % 32
        level = np.where(phase < 16, 15 - phase, phase - 16).astype(np.float64)
        return level - 7.5                      # 三角波均值 7.5，去掉直流

    def _noise_wave(self, times: np.ndarray) -> np.ndarray:
        count = len(times)
        if count == 0:
            return times
        noise = self.noise
        volume = noise.volume()
        if volume == 0:
            return np.zeros(count)
        period = noise.period()
        # 噪声周期可能远小于采样周期，直接点采样会混叠；这里同样按
        # 采样窗口内的高电平占比取平均（相当于 Blip 的带限重采样）。
        a = (times - noise.last_clock) / period
        b = a + self._cps / period
        ia = np.floor(a).astype(np.int64)
        ib = np.floor(b).astype(np.int64)
        length = len(noise.seq_bits)
        ia_rem = (noise.index + ia) % length
        ib_rem = ia_rem + (ib - ia)
        bits = noise.seq_bits
        pref = noise.seq_prefix
        start = pref[ia_rem] + (a - ia) * bits[ia_rem]
        end = pref[ib_rem] + (b - ib) * bits[ib_rem % length]
        ones = pref[length] / length             # 该序列里高电平占的比例
        return ((end - start) / (b - a) - ones) * volume

    def _advance_state(self, t0: float, t1: float) -> None:
        dt = t1 - t0
        for square in (self.square1, self.square2):
            # 完整周期 = 8 * timer_period（phase_range = 8）
            full_period = (square.period() + 1) * 2 * 8
            square.phase_cycles = (square.phase_cycles + dt) % full_period
        timer_period = self.triangle.period() + 1
        self.triangle.phase_steps = (
            self.triangle.phase_steps + dt / timer_period) % 32.0

        noise = self.noise
        period = noise.period()
        steps = int(math.floor((t1 - noise.last_clock) / period))
        if steps > 0:
            noise.index = (noise.index + steps) % len(noise.seq_states)
            noise.last_clock += steps * period

    def _render_chunk(self, t0: float, t1: float, n0: int, n1: int,
                      out: np.ndarray) -> None:
        if n1 <= n0:
            self._advance_state(t0, t1)
            return

        times = np.arange(n0, n1, dtype=np.float64) * self._cps

        if not (self.mute_mask & 0x01):
            out[n0:n1] += self._square_wave(self.square1, times, t0) * W_SQUARE
        if not (self.mute_mask & 0x02):
            out[n0:n1] += self._square_wave(self.square2, times, t0) * W_SQUARE
        if not (self.mute_mask & 0x04):
            out[n0:n1] += self._triangle_wave(times, t0) * W_TRIANGLE
        if not (self.mute_mask & 0x08):
            out[n0:n1] += self._noise_wave(times) * W_NOISE

        # DMC 的 DAC 每个采样位都会跳变：这里只推进状态并记录跳变时刻，
        # 波形留到渲染结束后用带限阶跃核统一合成（见 _dmc_bandlimited）。
        dmc = self.dmc
        if dmc.playing:
            for i in range(n0, n1):
                self._dmc_advance(i * self._cps)

        self._advance_state(t0, t1)

    # -- 总渲染 ------------------------------------------------------------

    def render(self, seconds: float, sample_rate: int = 44100) -> np.ndarray:
        self._cps = CPU_HZ / sample_rate
        total_samples = max(1, int(round(seconds * sample_rate)))
        total_cycles = total_samples * self._cps
        out = np.zeros(total_samples, dtype=np.float64)

        index = 0
        t = 0.0
        n = 0
        events = self.events
        total_events = len(events)

        while n < total_samples:
            # 先处理已经到点的寄存器写入（同一周期可能有多条）
            while index < total_events and events[index][0] <= t:
                self._run_frames_until(t)
                _cycle, addr, value = events[index]
                self._write(addr, value, t)
                index += 1

            next_event = events[index][0] if index < total_events else total_cycles
            next_frame = self.last_time + self.frame_delay

            if next_frame <= t:
                self._run_frames_until(t, process_at_end=True)
                continue

            boundary = min(next_event, next_frame, total_cycles)
            if boundary <= t:
                break

            n_end = int(math.ceil(boundary / self._cps - 1e-9))
            n_end = max(n, min(n_end, total_samples))
            self._render_chunk(t, boundary, n, n_end, out)
            n = n_end
            t = boundary

        if self.dmc_transitions and not (self.mute_mask & 0x10):
            out += _dmc_bandlimited(self.dmc_transitions, self._cps,
                                    total_samples, sample_rate) * W_DMC
        self.dmc_transitions.clear()

        out *= GAIN
        return _treble_eq(_highpass(out, sample_rate), sample_rate)


def _dmc_bandlimited(transitions: list[tuple[float, int]], cps: float,
                     total_samples: int, sample_rate: int,
                     oversample: int = 8) -> np.ndarray:
    """把 DMC 的每次 DAC 跳变合成为带限阶跃波形（复刻 Blip 的 sinc 重建）。

    libgme 在每次 DAC 跳变处叠加一个 Blip 冲激，由 sinc 核平滑成约 8 个
    采样点的斜坡；零阶保持则是硬跳变，高频能量明显偏多（16–18 kHz 高出
    约 10 dB）。这里在 8 倍过采样率上按整数索引累加跳变、cumsum 还原电平，
    再用 DMC 实际使用的 8 抽头 Blip 核频响做低通，最后抽取回原采样率。
    """
    length = total_samples * oversample
    if length <= 0:
        return np.zeros(total_samples)
    high = np.zeros(length + 1, dtype=np.float64)
    times = np.fromiter((item[0] for item in transitions),
                        dtype=np.float64, count=len(transitions))
    deltas = np.fromiter((item[1] for item in transitions),
                         dtype=np.float64, count=len(transitions))
    idx = np.rint(times / cps * oversample).astype(np.int64)
    np.clip(idx, 0, length, out=idx)
    np.add.at(high, idx, deltas)
    level = np.cumsum(high)[:length]

    freqs = np.fft.rfftfreq(length, 1.0 / (sample_rate * oversample))
    gain = _blip_kernel_magnitude(freqs, sample_rate,
                                  sample_rate * oversample * 0.5)
    edge_lo = 0.95 * (sample_rate * 0.5)
    edge_hi = sample_rate * 0.5
    band = (freqs > edge_lo) & (freqs < edge_hi)
    gain[band] *= 0.5 * (1.0 + np.cos(
        math.pi * (freqs[band] - edge_lo) / (edge_hi - edge_lo)))
    gain[freqs >= edge_hi] = 0.0
    level = np.fft.irfft(np.fft.rfft(level) * gain, length)
    return level[::oversample]


def _blip_kernel_magnitude(freqs: np.ndarray, sample_rate: int,
                           max_freq: float, width: int = 8,
                           treble_db: float = -1.0) -> np.ndarray:
    """复刻 blip_eq_t::generate 生成的 Blip sinc 核幅度响应。

    Nes_Apu 里 DMC 用的是 blip_med_quality（8 抽头），treble 来自
    Nsf_Emu 的 make_equalizer(-1.0, 80)。
    """
    count = 32 * (width - 1)                    # blip_res / 2 * (width - 1)
    oversample = 64 * 2.25 / count + 0.85
    maxh = 4096.0
    rolloff = 10.0 ** (treble_db / (maxh * 20.0))
    pow_a_n = rolloff ** maxh
    to_angle = math.pi / 2.0 / maxh / oversample

    i = np.arange(count)
    angle = ((i - count) * 2 + 1) * to_angle
    angle_maxh = angle * maxh
    den = 1.0 + rolloff * (rolloff - 2.0 * np.cos(angle))
    num = ((np.cos(angle_maxh - angle) * rolloff - np.cos(angle_maxh))
           * pow_a_n + 1.0 - np.cos(angle) * rolloff)
    with np.errstate(divide="ignore", invalid="ignore"):
        half = np.where(den > 1e-13, num / den, maxh)
    half *= 0.54 - 0.46 * np.cos(np.arange(count) * math.pi / (count - 1))
    t_pos = (np.arange(count) * 2 + 1) / (2.0 * oversample)
    taps = np.concatenate([half, half[::-1]])
    times = np.concatenate([-t_pos[::-1], t_pos])

    # 先用较粗的频率网格求幅度，再插值到调用方给定的频率数组上
    grid = np.linspace(0.0, max_freq, 4096)
    w = 2.0 * math.pi * grid / sample_rate
    response = np.abs(np.exp(-1j * np.outer(w, times)) @ taps) / taps.sum()
    return np.interp(freqs, grid, response)


def _treble_eq(audio: np.ndarray, sample_rate: int,
               rolloff_db: float = 26.0) -> np.ndarray:
    """补偿高频的频域零相位低通（经验拟合，不是 libgme 的原滤波器）。

    libgme 用 Blip 的 sinc 核对跳变做带限重建；本渲染器方波用窗口平均、
    三角波按步取样，高频细节与 Blip 不同。实测加 -26 dB*(f/(Fs/2))^4 的
    零相位衰减后，20 Hz–20 kHz 各频段差可压到 ±0.3 dB 以内。
    """
    count = len(audio)
    if count < 8:
        return audio
    freqs = np.fft.rfftfreq(count, 1.0 / sample_rate)
    x = np.clip(freqs / (sample_rate * 0.5), 0.0, 1.0)
    response = 10.0 ** (-(rolloff_db / 20.0) * x ** 4)
    return np.fft.irfft(np.fft.rfft(audio) * response, count)


def _blip_bass_cutoff(sample_rate: int, bass_freq: int = 80) -> float:
    """按 Blip_Buffer::bass_freq 的移位算法换算等效一阶高通截止频率。

    Nsf_Emu 用 make_equalizer(-1.0, 80)，Classic_Emu 会把 bass_freq 设为
    80 Hz；内部量化成 2 的幂次时间常数（44.1 kHz 下 shift=7），等效
    -3 dB 点约 55 Hz。
    """
    shift = 31
    if bass_freq > 0:
        shift = 13
        f = (bass_freq << 16) // sample_rate
        while True:
            f >>= 1
            if not f:
                break
            shift -= 1
    return sample_rate / (2.0 * math.pi * (1 << shift))


def _highpass(audio: np.ndarray, sample_rate: int,
              cutoff: float | None = None) -> np.ndarray:
    """一阶零相位高通（对应 Blip_Buffer 的 bass 高通）。

    APU 各声道输出 0..volume 的单极性电平（DMC 更是 0..127 的 DAC 值），
    整体直流很大，必须去掉。频域实现是零相位的，不会让音符起点漂移，
    也不会把十几毫秒的静音抹平。
    """
    count = len(audio)
    if count < 8:
        return audio
    if cutoff is None:
        cutoff = _blip_bass_cutoff(sample_rate)
    frequencies = np.fft.rfftfreq(count, 1.0 / sample_rate)
    response = (1j * frequencies) / (1j * frequencies + cutoff)
    spectrum = np.fft.rfft(audio - audio.mean())
    return np.fft.irfft(spectrum * response, count)


# ---------------------------------------------------------------------------
# 四、NSF -> 乐谱（供导入 / 导出使用）
# ---------------------------------------------------------------------------


def _period_to_freq(period: int, divisor: int) -> float:
    """NES 声道的 11 位周期值 -> 频率（Hz）。"""
    if period < 1:
        return 0.0
    return NTSC_CPU_HZ / (divisor * (period + 1))


def frequency_to_period(freq: float, divisor: int) -> int:
    """频率（Hz）-> NES 声道的 11 位周期值（写回 NSF 时用）。"""
    if freq <= 0:
        return 0
    period = round(NTSC_CPU_HZ / (divisor * freq) - 1)
    return max(0, min(0x7FF, period))


def _freq_to_midi(freq: float) -> int | None:
    if freq <= 20 or freq >= 12000:
        return None
    midi = int(round(69 + 12 * math.log2(freq / 440.0)))
    return midi if 12 <= midi <= 108 else None


class _ChannelState:
    """解码过程中，每个声道当前的状态。"""

    def __init__(self, name: str, volume: int = 0) -> None:
        self.name = name
        self.volume = volume
        self.low = self.high = 0
        self.duty = 2
        self.length_index = 0
        self.enabled = True
        self.note: dict | None = None
        # 硬件包络（$4000/$4004/$400C 的 bit4..0）
        self.env_constant = True
        self.env_period = 0
        self.env_loop = False
        self.env_start = False
        self.env_decay = 15
        self.env_divider = 0
        self.noise_short = False            # $400E 的短模式
        # 扫频（$4001/$4005）
        self.sweep_enabled = False
        self.sweep_period = 0
        self.sweep_negate = False
        self.sweep_shift = 0
        # 三角波线性计数器（$4008）
        self.linear_counter = 0
        self.linear_reload = False

    def close(self, frame: int, frame_rate: float) -> dict | None:
        """结束当前音符：算时长、裁剪逐帧数据，太短的碎片丢弃。"""
        note = self.note
        self.note = None
        if note is None:
            return None
        note["duration"] = max(0.0, (frame - note["_start_frame"]) / frame_rate)
        note["end"] = note["start"] + note["duration"]
        note.pop("_start_frame", None)
        note.pop("_last_frame", None)
        note.pop("_last_period", None)
        # 包络和音高曲线按帧采样，裁剪到实际时长
        frames = max(0, int(round(note["duration"] * frame_rate)))
        envelope = note.get("envelope")
        if envelope is not None:
            del envelope[frames:]
        note["pitch_curve"] = [
            point for point in note["pitch_curve"] if point["frame"] < frames
        ]
        return None if note["duration"] < 2.0 / frame_rate else note


def decode_apu_events(header: NSFHeader, events: list[tuple[int, int, int]],
                      total_frames: int) -> list[dict]:
    """把按帧归并的 APU 写入记录变成按声道分组的音符列表。"""
    fr = header.frame_rate
    channels = {
        "pulse1": _ChannelState("Pulse 1"),
        "pulse2": _ChannelState("Pulse 2"),
        "triangle": _ChannelState("Triangle"),
        "noise": _ChannelState("Noise"),
    }
    notes: dict[str, list[dict]] = {name: [] for name in channels}

    def flush(key: str, frame: int) -> None:
        old = channels[key].close(frame, fr)
        if old is not None:
            notes[key].append(old)

    def emit(key: str, frame: int, midi: int | None, volume: int,
             duty: int = 2, noise_period: int = 0,
             noise_short: bool = False, period: int | None = None) -> None:
        # 先结束上一个音符，再按当前状态开一个新音符
        flush(key, frame)
        state = channels[key]
        sweep = None
        if key in ("pulse1", "pulse2"):
            sweep = {"enabled": state.sweep_enabled, "period": state.sweep_period,
                     "negate": state.sweep_negate, "shift": state.sweep_shift}
        state.note = {
            "start": frame / fr, "duration": 0.0, "end": 0.0,
            "midi": midi, "volume": volume, "duty": duty,
            "noise_period": noise_period, "noise_short": noise_short,
            "period": period, "length_index": state.length_index, "sweep": sweep,
            "linear_counter": state.linear_counter if key == "triangle" else None,
            "linear_reload": state.linear_reload if key == "triangle" else None,
            "env_constant": state.env_constant, "env_loop": state.env_loop,
            "env_period": state.env_period,
            "envelope": [],          # 非固定音量时逐帧采样 0..15
            "pitch_curve": [],       # (帧偏移, 周期) —— 颤音 / 滑音
            "_start_frame": frame, "_last_frame": frame, "_last_period": period,
        }

    channel_regs = (
        ("pulse1", (0x4000, 0x4001, 0x4002, 0x4003)),
        ("pulse2", (0x4004, 0x4005, 0x4006, 0x4007)),
        ("triangle", (0x4008, 0x4009, 0x400A, 0x400B)),
        ("noise", (0x400C, 0x400D, 0x400E, 0x400F)),
    )

    # 先按帧归并写入：同一帧里的多次写只保留最后一次。
    per_frame: dict[int, dict[int, int]] = {}
    for frame, addr, value in events:
        per_frame.setdefault(frame, {})[addr] = value

    # 硬件包络由 APU 帧序列器驱动，每 1/240 秒走一步
    quarter_accum = 0.0
    quarter_step = fr / 240.0

    def period_params(key: str) -> tuple[int, int]:
        return (32, 2) if key == "triangle" else (16, 8)

    def track_period(key: str, state: _ChannelState, frame: int) -> None:
        """音高在音符持续期间发生变化（颤音/滑音）时记录下来。"""
        if key == "noise" or state.note is None:
            return
        divisor, min_period = period_params(key)
        period = state.high * 256 + state.low
        if period < min_period or period == state.note["_last_period"]:
            return
        state.note["pitch_curve"].append({
            "frame": frame - state.note["_start_frame"],
            "period": period,
            "midi": _freq_to_midi(_period_to_freq(period, divisor)),
        })
        state.note["_last_period"] = period

    for frame in range(total_frames + 1):
        # 不少音乐引擎先写 $4003（高字节，同时触发发声）再写 $4002（低字节）。
        # 若在 $4003 那一刻取音高会拿到上一个音符的低字节，导致旋律慢一拍，
        # 所以按帧取最终值再判定音高。
        writes = per_frame.get(frame, {})

        if 0x4015 in writes:
            value = writes[0x4015]
            for bit, key in enumerate(("pulse1", "pulse2", "triangle", "noise")):
                enabled = bool(value & (1 << bit))
                channels[key].enabled = enabled
                if not enabled:
                    flush(key, frame)

        for key, (r0, r1, r2, r3) in channel_regs:
            state = channels[key]

            if key in ("pulse1", "pulse2", "noise"):
                if r0 in writes:
                    value = writes[r0]
                    # bit4=1：固定音量，低 4 位就是音量
                    # bit4=0：硬件包络模式，音量由包络衰减值决定
                    state.env_constant = bool(value & 0x10)
                    state.env_loop = bool(value & 0x20)
                    state.env_period = value & 0x0F
                    state.volume = state.env_period if state.env_constant else 0x0F
                    if key != "noise":
                        state.duty = (value >> 6) & 0x03
                    if (state.env_constant and state.volume == 0
                            and state.note is not None):
                        flush(key, frame)
            else:                                          # triangle
                if r0 in writes:
                    value = writes[r0]
                    state.volume = 0x0F if (value & 0x7F) else 0
                    state.linear_counter = value & 0x7F
                    state.linear_reload = bool(value & 0x80)
                    if state.volume == 0 and state.note is not None:
                        flush(key, frame)

            if key in ("pulse1", "pulse2") and r1 in writes:
                value = writes[r1]
                state.sweep_enabled = bool(value & 0x80)
                state.sweep_period = (value >> 4) & 0x07
                state.sweep_negate = bool(value & 0x08)
                state.sweep_shift = value & 0x07

            if r2 in writes:
                state.low = writes[r2]
                if key == "noise":
                    state.noise_short = bool(writes[r2] & 0x80)
            if r3 in writes:
                state.high = writes[r3] & 0x07
                state.length_index = (writes[r3] >> 3) & 0x1F
                # 触发新音：包络重新从 15 开始衰减
                state.env_start = True
                state.env_decay = 15
                state.env_divider = state.env_period

            # $4002 单独变化（颤音常见写法）也要进音高曲线
            track_period(key, state, frame)

            if r3 not in writes:                          # 这一帧没有触发新音
                continue

            if key == "noise":
                if not state.enabled or state.volume == 0:
                    continue
                emit(key, frame, None, state.volume,
                     noise_period=state.low & 0x0F,
                     noise_short=state.noise_short)
                continue

            period = state.high * 256 + state.low
            divisor, min_period = period_params(key)
            if not state.enabled or state.volume == 0 or period < min_period:
                continue
            midi = _freq_to_midi(_period_to_freq(period, divisor))
            if midi is None:
                continue
            # 同一个音连续触发（颤音/包络刷新）就当作延长，不重复记谱
            if (state.note is not None and state.note["midi"] is not None
                    and abs(state.note["midi"] - midi) <= 1
                    and frame - state.note["_last_frame"] <= 4):
                state.note["_last_frame"] = frame
                continue
            emit(key, frame, midi, state.volume,
                 state.duty if key != "triangle" else 0, period=period)

        # 推进硬件包络
        quarter_accum += quarter_step
        while quarter_accum >= 1.0:
            quarter_accum -= 1.0
            for key in ("pulse1", "pulse2", "noise"):
                state = channels[key]
                if state.env_constant:
                    continue
                if state.env_start:
                    state.env_start = False
                    state.env_decay = 15
                    state.env_divider = state.env_period
                elif state.env_divider == 0:
                    state.env_divider = state.env_period
                    if state.env_decay > 0:
                        state.env_decay -= 1
                    elif state.env_loop:
                        state.env_decay = 15
                else:
                    state.env_divider -= 1

        # 记录这一帧的实际音量（固定音量由 volume 字段表达，不重复存）
        for key in ("pulse1", "pulse2", "noise"):
            state = channels[key]
            if state.note is None or state.env_constant:
                continue
            state.note["envelope"].append(state.env_decay)

    # 收尾：把所有还没结束的音符关掉
    for key in channels:
        flush(key, total_frames)

    tracks = []
    for key in ("pulse1", "pulse2", "triangle", "noise"):
        track_notes = _clean_notes(sorted(notes[key], key=lambda n: n["start"]), fr)
        tracks.append({"channel": key, "name": channels[key].name,
                       "notes": track_notes})
    return tracks


def _clean_notes(notes: list[dict], frame_rate: float) -> list[dict]:
    """清理解码结果，让乐谱更好读。

    音乐程序为了实现颤音/快速装饰音，会每隔一两帧就重写一次音高。这里：
    1. 把紧挨着的、很短的碎片合并成一个“装饰音”（取占时间最长的音高）；
    2. 合并相邻的同一个音。
    """
    max_duration = 4.0                       # 单音最长 4 秒，避免超长音
    min_duration = 1.5 / frame_rate          # 小于约 1.5 帧的孤立碎片直接丢掉
    max_frames = int(round(max_duration * frame_rate))
    merged: list[dict] = []

    def trim(note: dict) -> None:
        note["duration"] = max_duration
        note["end"] = note["start"] + max_duration
        note["envelope"] = note["envelope"][:max_frames]
        note["pitch_curve"] = [
            point for point in note["pitch_curve"] if point["frame"] < max_frames
        ]

    for note in notes:
        if note["duration"] > max_duration:
            trim(note)

        previous = merged[-1] if merged else None
        gap = (note["start"] - previous["end"]) if previous else 1e9
        short = note["duration"] <= 4.5 / frame_rate
        same_pitch = (previous is not None and note["midi"] is not None
                      and previous["midi"] == note["midi"])
        near_pitch = (previous is not None and note["midi"] is not None
                      and previous["midi"] is not None
                      and abs(previous["midi"] - note["midi"]) <= 7)
        absorb = (previous is not None and note["midi"] is not None
                  and gap <= 2.0 / frame_rate
                  and (same_pitch or (short and near_pitch)))

        if absorb:
            counts = previous.setdefault("_pitch_frames", {})
            counts[note["midi"]] = counts.get(note["midi"], 0) + max(
                1, round(note["duration"] * frame_rate))
            shift = round((note["start"] - previous["start"]) * frame_rate)
            # 被吸收的装饰音，其起始音高也要进入曲线，否则就从“可读视图”里丢了
            if note["period"] is not None:
                last_period = (previous["pitch_curve"][-1]["period"]
                               if previous["pitch_curve"]
                               else previous["period"])
                if note["period"] != last_period:
                    previous["pitch_curve"].append({
                        "frame": shift,
                        "period": note["period"],
                        "midi": note["midi"],
                    })
            for point in note["pitch_curve"]:
                point["frame"] += shift
                previous["pitch_curve"].append(point)
            previous["end"] = note["end"]
            previous["duration"] = previous["end"] - previous["start"]
            previous["volume"] = max(previous["volume"], note["volume"])
            if previous.get("envelope") is not None and note.get("envelope"):
                previous["envelope"].extend(note["envelope"])
            previous["midi"] = max(counts, key=counts.get)
            continue

        if note["duration"] < min_duration:
            continue                       # 孤立的极短碎片

        if note["midi"] is not None:
            note["_pitch_frames"] = {
                note["midi"]: max(1, round(note["duration"] * frame_rate))
            }
        merged.append(note)

    for note in merged:
        note.pop("_pitch_frames", None)
        if note["duration"] > max_duration:
            trim(note)
    return [n for n in merged if n["duration"] >= min_duration]


def _dmc_bytes(mem: bytearray, addr_reg: int,
               len_reg: int) -> tuple[int, int, bytes]:
    """按 $4012/$4013 从内存取出 DMC 采样，返回 (绝对地址, 长度, 字节)。"""
    offset = (addr_reg & 0xFF) * 0x40
    length = (len_reg & 0xFF) * 0x10 + 1
    cursor = 0x4000 + offset
    data = bytearray()
    for _ in range(length):
        data.append(mem[(0x8000 + cursor) & 0xFFFF])
        cursor = (cursor + 1) & 0x7FFF
    return 0xC000 + offset, length, bytes(data)


def decode_dmc(header: NSFHeader, events: list[tuple[int, int, int]],
               mem: bytearray, total_frames: int
               ) -> tuple[dict, list[DmcSample]]:
    """把 DMC 声道的 $4010-$4013 / $4015 写入变成采样轨道。

    DMC 不是“音高”而是“播放某段 PCM 采样”，所以每个音符挂一个
    `DmcSample`，并单独汇总去重后的采样表，供重建内存使用。
    """
    fr = header.frame_rate
    per_frame: dict[int, dict[int, int]] = {}
    for frame, addr, value in events:
        per_frame.setdefault(frame, {})[addr] = value

    rate, addr_reg, len_reg, start_frame = 0, 0, 0, 0
    loop = irq = enabled = False
    current: DmcSample | None = None
    notes: list[dict] = []
    samples: list[DmcSample] = []
    seen: set[tuple[int, bool, bool, int, int, str]] = set()

    def close(frame: int) -> None:
        nonlocal current
        if current is None:
            return
        duration = max(0.0, (frame - start_frame) / fr)
        if duration > 0:
            notes.append({
                "start": start_frame / fr, "duration": duration,
                "end": start_frame / fr + duration,
                "midi": None, "volume": 0, "duty": 0,
                "noise_period": 0, "noise_short": False,
                "period": None, "length_index": None, "sweep": None,
                "linear_counter": None, "linear_reload": None,
                "env_constant": True, "env_loop": False, "env_period": 0,
                "envelope": [], "pitch_curve": [], "dmc": current,
            })
        current = None

    def start(frame: int) -> None:
        nonlocal current, start_frame
        close(frame)
        address, length, data = _dmc_bytes(mem, addr_reg, len_reg)
        sample = DmcSample(rate=rate, loop=loop, irq=irq,
                           address=address, length=length, data=data.hex())
        key = (rate, loop, irq, address, length, sample.data)
        if key not in seen:
            seen.add(key)
            samples.append(sample)
        current = sample
        start_frame = frame

    for frame in range(total_frames + 2):
        writes = per_frame.get(frame, {})
        if not writes:
            continue
        changed = False
        if 0x4010 in writes:
            value = writes[0x4010]
            rate, loop, irq = value & 0x0F, bool(value & 0x40), bool(value & 0x80)
        if 0x4012 in writes:
            addr_reg = writes[0x4012]
            changed = True
        if 0x4013 in writes:
            len_reg = writes[0x4013]
            changed = True

        if 0x4015 in writes:
            want = bool(writes[0x4015] & 0x10)
            if want and not enabled:
                enabled = True
                start(frame)
            elif not want and enabled:
                enabled = False
                close(frame)
            elif want and changed:
                # 播放中改地址/长度：当前段结束，按新参数重新开始
                start(frame)
        elif enabled and changed:
            start(frame)

    close(total_frames + 1)
    return {"channel": "dmc", "name": "DMC", "notes": notes}, samples


def _decode_nsf(header: NSFHeader, song: int, seconds: float,
                verbose: bool = False
                ) -> tuple[int, list[tuple[int, int, int]], list[dict], list[DmcSample]]:
    """模拟 + 解码的公共流程：NSF 音乐程序 -> 各声道音符 + DMC 采样。"""
    if not 1 <= song <= max(1, header.song_count):
        raise ValueError(f"曲目编号应在 1..{header.song_count} 之间")

    total_frames = int(round(seconds * FRAME_RATE))
    if verbose:
        print(f"[1/3] 正在模拟 NSF 音乐程序（{seconds:.0f} 秒，约 {total_frames} 帧）...")
    cycle_events, frame_events, mem = _collect(header, song, seconds)
    if verbose:
        print(f"[2/3] 共记录 {len(cycle_events)} 条 APU 寄存器写入")

    tracks = decode_apu_events(header, frame_events, total_frames)
    dmc_track, samples = decode_dmc(header, frame_events, mem, total_frames)
    tracks.append(dmc_track)
    return total_frames, cycle_events, tracks, samples


def nsf_to_tracks(header: NSFHeader, song: int = 1, seconds: float = 20.0,
                  verbose: bool = True) -> tuple[list[dict], dict]:
    """核心函数：模拟播放 NSF，返回 (多轨道音符, 统计信息)。"""
    total_frames, cycle_events, tracks, _samples = _decode_nsf(
        header, song, seconds, verbose)
    stats = {
        "song": song,
        "seconds": seconds,
        "frames": total_frames,
        "frame_rate": round(header.frame_rate, 4),
        "apu_writes": len(cycle_events),
    }
    if verbose:
        counts = ", ".join(f"{t['name']}={len(t['notes'])}" for t in tracks)
        print(f"[3/3] 音符识别完成：{counts}")
    return tracks, stats


def nsf_to_score(nsf_path: str | Path, song: int = 1, seconds: float = 30.0,
                 bpm: float = 120.0, verbose: bool = False) -> Score:
    """一步到位：读取 NSF，模拟演奏一遍，返回无损的 Score 对象。"""
    header = parse_nsf(nsf_path)
    _total, cycle_events, tracks_data, samples = _decode_nsf(header, song, seconds)
    fr = header.frame_rate
    beat_scale = bpm / 60.0                     # 秒 -> 拍

    # 1. 每个声道音符 -> NoteEvent（含包络 / 扫频 / 音高曲线 / DMC）
    score_tracks: list[Track] = []
    for data in tracks_data:
        channel = data["channel"]
        is_pulse = channel in ("pulse1", "pulse2")
        is_triangle = channel == "triangle"
        notes: list[NoteEvent] = []
        duty_counter: dict[int, int] = {}
        for note in data["notes"]:
            duration = round(note["duration"] * beat_scale, 4)
            if duration <= 0:
                continue
            duty = int(note.get("duty", 2))
            duty_counter[duty] = duty_counter.get(duty, 0) + 1
            curve = [
                PitchPoint(
                    time=round(point["frame"] / fr * beat_scale, 4),
                    period=int(point["period"]),
                    pitch=(midi_to_note_name(point["midi"])
                           if point.get("midi") is not None else None),
                )
                for point in note.get("pitch_curve", [])
            ]
            envelope = None
            if channel != "dmc":
                envelope = EnvelopeConfig(
                    constant=bool(note["env_constant"]),
                    loop=bool(note["env_loop"]),
                    period=int(note["env_period"]),
                    values=[int(v) for v in note.get("envelope", [])],
                )
            sweep = None
            if note.get("sweep") is not None:
                sweep = SweepConfig(**note["sweep"])
            notes.append(NoteEvent(
                start=round(note["start"] * beat_scale, 4),
                duration=duration,
                pitch=(midi_to_note_name(note["midi"])
                       if note["midi"] is not None else None),
                volume=int(note["volume"]),
                duty=duty if is_pulse else None,
                noise_period=int(note.get("noise_period", 0)),
                noise_short=bool(note.get("noise_short", False)),
                period=note.get("period"),
                length_index=note.get("length_index"),
                sweep=sweep,
                envelope=envelope,
                linear_counter=(note.get("linear_counter")
                                if is_triangle else None),
                linear_reload=(note.get("linear_reload")
                               if is_triangle else None),
                pitch_curve=curve,
                dmc=note.get("dmc"),
            ))
        common_duty = max(duty_counter, key=duty_counter.get) if duty_counter else 2
        score_tracks.append(Track(
            channel=channel, name=data["name"],
            duty=common_duty if is_pulse else 2, notes=notes,
        ))

    # 2. APU 配置 + 全部寄存器事件
    apu = ApuConfig(
        frame_rate=fr,
        speed_flags=header.speed_flags,
        chip=header.chip,
        load_addr=header.load_addr,
        init_addr=header.init_addr,
        play_addr=header.play_addr,
        version=header.version,
        song_count=header.song_count,
        start_song=header.start_song,
        ntsc_speed=header.ntsc_speed,
        pal_speed=header.pal_speed,
    )
    events = [ApuEvent(cycle=c, address=a, value=v) for c, a, v in cycle_events]

    return Score(
        title=header.title,
        artist=header.artist,
        copyright=header.copyright,
        source=f"{header.path.name} · 第 {song}/{header.song_count} 首",
        bpm=bpm,
        tracks=score_tracks,
        apu=apu,
        events=events,
        dmc_samples=samples,
        audio_seconds=seconds,
    )


# ---------------------------------------------------------------------------
# 五、音频输出：WAV / 系统播放器
# ---------------------------------------------------------------------------


def save_wav(path: str | Path, audio: np.ndarray,
             sample_rate: int = SAMPLE_RATE) -> Path:
    """把 numpy 波形保存成 16 位单声道 WAV 文件（只用标准库 wave）。"""
    path = Path(path)
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm.tobytes())
    return path


def play_audio_file(path: str | Path) -> str:
    """调用系统自带的播放器播放一个音频文件，返回实际使用的命令名。"""
    path = Path(path)

    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(str(path), winsound.SND_FILENAME)
        return "winsound"

    # 按优先级找可用的命令行播放器
    candidates = [
        ["aplay", "-q"],
        ["paplay"],
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
        ["afplay"],
    ]
    for command in candidates:
        if shutil.which(command[0]):
            subprocess.run(command + [str(path)], check=False)
            return command[0]

    raise RuntimeError(
        "没有找到可用的音频播放器。请安装 aplay（alsa-utils）、paplay（pulseaudio）\n"
        f"或 ffplay（ffmpeg）。也可以直接打开这个文件播放：{path}"
    )


def play_audio(audio: np.ndarray, sample_rate: int = SAMPLE_RATE,
               save_to: str | Path | None = None) -> Path:
    """把一条波形存成 WAV 并交给系统播放器，返回 WAV 路径。"""
    if save_to is None:
        temp = tempfile.NamedTemporaryFile(prefix="nsf_music_", suffix=".wav",
                                          delete=False)
        temp.close()
        wav_path = Path(temp.name)
    else:
        wav_path = Path(save_to)
    save_wav(wav_path, audio, sample_rate)
    print(f"[播放] 已生成 WAV：{wav_path}")
    used = play_audio_file(wav_path)
    print(f"[播放] 已使用 {used} 播放完毕。")
    return wav_path


# ---------------------------------------------------------------------------
# 六、NSF 播放与渲染
# ---------------------------------------------------------------------------


def _collect(header: NSFHeader, song: int, seconds: float
             ) -> tuple[list[tuple[int, int, int]],
                        list[tuple[int, int, int]], bytearray]:
    """执行 NSF 音乐程序，返回 (按周期, 按帧的 APU 写入, 结束时内存)。"""
    if not 1 <= song <= max(1, header.song_count):
        raise ValueError(f"曲目编号应在 1..{header.song_count} 之间")

    total_frames = int(round(seconds * FRAME_RATE))

    def run(init_a: int) -> CPU6502:
        cpu = CPU6502()
        cpu.cycles_per_frame = int(round(CYCLES_PER_FRAME))
        cpu.reset_registers()
        cpu.load_rom(header.load_addr, header.rom)
        cpu.call(header.init_addr, a=init_a, max_cycles=2_000_000)
        # libgme 的 play_ready = 4：init 之后先空转 4 帧才开始调用 PLAY
        for _ in range(4):
            cpu.advance_frame()
        return cpu

    def probe(init_a: int) -> tuple[CPU6502, int]:
        cpu = run(init_a)
        before = len(cpu.apu_cycle_events)
        for _ in range(2):
            cpu.run_frame(header.play_addr)
        return cpu, len(cpu.apu_cycle_events) - before

    # NSF 规范里 A 一般是"从 0 开始"的曲目号；个别老文件从 1 开始。
    # 有些驱动 PLAY 连续两帧不写寄存器也是正常的，因此只在"完全没有写入"
    # 时才尝试另一种 A 取值。
    init_a = song - 1
    cpu, _played = probe(init_a)
    if len(cpu.apu_cycle_events) == 0:
        init_a = song
        cpu, _played = probe(init_a)
        if len(cpu.apu_cycle_events) == 0:
            raise RuntimeError(
                "模拟过程中没有捕捉到任何声音寄存器写入。\n"
                "可能原因：该 NSF 依赖扩展音源芯片，或音乐程序无法在本模拟器中运行。")

    # 用探测到的 A 值完整跑一遍
    cpu = run(init_a)
    for _ in range(total_frames):
        cpu.run_frame(header.play_addr)

    return cpu.apu_cycle_events, cpu.apu_events, cpu.mem


def nsf_to_audio(nsf_path: str | Path, song: int = 1, seconds: float = 30.0,
                 sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """把 NSF 的某一首直接用 APU 级渲染成 float32 波形（-1 ~ 1）。"""
    return ApuEngine(nsf_path, song=song, seconds=seconds,
                     sample_rate=sample_rate).render()


def _memory_from_samples(samples: list[DmcSample]) -> bytearray:
    """用乐谱里保存的 DMC 采样重建 64KB 内存（DMC 只读这一小块）。"""
    mem = bytearray(0x10000)
    for sample in samples:
        data = bytes.fromhex(sample.data)
        cursor = 0x4000 + (sample.address - 0xC000)
        for byte in data:
            mem[(0x8000 + cursor) & 0xFFFF] = byte
            cursor = (cursor + 1) & 0x7FFF
    return mem


class ApuEngine:
    """APU 播放引擎工具类。

    ```python
    engine = ApuEngine("Raf World.nsf", song=1, seconds=30)
    audio = engine.render()          # numpy 波形（float32，-1 ~ 1）
    engine.save_wav("out.wav")       # 导出 WAV
    engine.play()                    # 调用系统播放器
    score = engine.to_score()        # 转成 pydantic 乐谱对象

    engine = ApuEngine.from_score(score)   # 从乐谱按原声播放
    ```

    渲染结果会缓存，重复调用 `render()` / `play()` 不会重新模拟。
    传入 `refresh=True` 可以强制重新合成。
    """

    def __init__(self, nsf_path: str | Path, song: int = 1,
                 seconds: float = 30.0, sample_rate: int = SAMPLE_RATE) -> None:
        self.path = Path(nsf_path)
        self.song = song
        self.seconds = seconds
        self.sample_rate = sample_rate
        self.header = parse_nsf(self.path)
        self._events: list[tuple[int, int, int]] | None = None
        self._mem: bytearray | None = None
        self._audio: np.ndarray | None = None

    @classmethod
    def from_score(cls, score: Score,
                   sample_rate: int = SAMPLE_RATE) -> "ApuEngine":
        """从带 APU 事件的乐谱对象构造引擎（不重新模拟 6502）。"""
        if score.apu is None or not score.events:
            raise ValueError(
                "这份乐谱没有 APU 事件，无法按原始音色渲染。请从 NSF 重新导入。")
        # 只需要文件头里的少量字段，用 SimpleNamespace 顶替
        header = SimpleNamespace(
            frame_rate=score.apu.frame_rate,
            speed_flags=score.apu.speed_flags,
            title=score.title or "score",
        )
        engine = cls.__new__(cls)
        engine.path = Path(score.title or "score")
        engine.song = 1
        engine.seconds = score.audio_seconds or max(score.duration_seconds, 0.5)
        engine.sample_rate = sample_rate
        engine.header = header
        engine._events = [(event.cycle, event.address, event.value)
                          for event in score.events]
        engine._mem = _memory_from_samples(score.dmc_samples)
        engine._audio = None
        return engine

    @property
    def title(self) -> str:
        """文件头里的标题（没有就用文件名）。"""
        return self.header.title

    @property
    def audio(self) -> np.ndarray:
        """当前渲染结果（第一次访问时自动渲染）。"""
        return self.render()

    def render(self, refresh: bool = False) -> np.ndarray:
        """渲染成 numpy float32 波形；结果会缓存。"""
        if self._audio is None or refresh:
            if self._events is None or self._mem is None:
                self._events, _frames, self._mem = _collect(
                    self.header, self.song, self.seconds)
            renderer = ApuRenderer(self.header, self._events, self._mem)
            self._audio = renderer.render(
                self.seconds, self.sample_rate).astype(np.float32)
        return self._audio

    def to_score(self, bpm: float = 120.0, verbose: bool = False) -> Score:
        """把这一首转成 pydantic 乐谱对象（用于 JSON / Markdown 导出）。"""
        return nsf_to_score(self.path, song=self.song, seconds=self.seconds,
                            bpm=bpm, verbose=verbose)

    def save_wav(self, path: str | Path | None = None) -> Path:
        """导出 WAV；path 为空时写到 NSF 旁边。"""
        if path is None:
            path = self.path.with_name(f"{self.path.stem}.song{self.song}.wav")
        return save_wav(path, self.render(), self.sample_rate)

    def play(self, save_to: str | Path | None = None) -> Path:
        """渲染并调用系统播放器；save_to 不为空时顺便保存 WAV。"""
        return play_audio(self.render(), self.sample_rate, save_to)


__all__ = [
    "ApuEngine",
    "ApuRenderer",
    "CPU_HZ",
    "CYCLES_PER_FRAME",
    "FRAME_RATE",
    "NSFHeader",
    "SAMPLE_RATE",
    "CPU6502",
    "decode_apu_events",
    "decode_dmc",
    "frequency_to_period",
    "nsf_to_audio",
    "nsf_to_score",
    "nsf_to_tracks",
    "parse_nsf",
    "play_audio",
    "play_audio_file",
    "save_wav",
]
