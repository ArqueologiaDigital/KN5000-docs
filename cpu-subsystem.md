---
layout: page
title: CPU Subsystem
permalink: /cpu-subsystem/
---

# CPU Subsystem

The KN5000 uses a dual-CPU architecture with two identical TMP94C241F processors performing different roles.

## Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           DUAL CPU ARCHITECTURE                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐     ┌──────────────────────────────────────┐
│          MAIN CPU               │     │           SUB CPU                    │
│          TMP94C241F             │     │           TMP94C241F                 │
│                                 │     │                                      │
│  Role: System Controller        │     │  Role: Audio Processor               │
│                                 │     │                                      │
│  ┌───────────────────────────┐  │     │  ┌────────────────────────────────┐  │
│  │ Program ROM: 2MB          │  │     │  │ Boot ROM: 128KB (internal)     │  │
│  │ @ 0xE00000-0xFFFFFF       │  │     │  │ @ 0xFE0000-0xFFFFFF            │  │
│  └───────────────────────────┘  │     │  └────────────────────────────────┘  │
│                                 │     │                                      │
│  ┌───────────────────────────┐  │     │  ┌────────────────────────────────┐  │
│  │ RAM: 512KB                │  │     │  │ Payload: 192KB                 │  │
│  │ @ 0x200000-0x27FFFF       │  │     │  │ (loaded at boot from Main)     │  │
│  └───────────────────────────┘  │     │  └────────────────────────────────┘  │
│                                 │     │                                      │
│  Responsibilities:              │     │  Responsibilities:                   │
│  ├─ User interface              │     │  ├─ DSP control                      │
│  ├─ Menu system                 │     │  ├─ DAC output                       │
│  ├─ Control panel handling      │     │  ├─ Tone generation                  │
│  ├─ MIDI processing             │     │  ├─ Voice management                 │
│  ├─ Sequencer                   │     │  └─ Effects processing               │
│  ├─ Floppy disk I/O             │     │                                      │
│  ├─ HDAE5000 management         │     │                                      │
│  └─ Sub CPU coordination        │     │                                      │
└─────────────────────────────────┘     └──────────────────────────────────────┘
                    │                                     ^
                    │         Communication Latch         │
                    └───────────> @ 0x120000 <────────────┘
```

## TMP94C241F Specifications

The TMP94C241F is a Toshiba 32-bit microcontroller from the TLCS-900/H2 family.

### Architecture

| Feature | Specification |
|---------|---------------|
| CPU Core | TLCS-900/H2 (32-bit) |
| Clock | 25MHz (typical for KN5000) |
| Address Bus | 24-bit (16MB address space) |
| Data Bus | 16-bit external |
| Registers | 8 general purpose (32-bit each) |
| Instruction Set | CISC, variable length (1-7 bytes) — see [Instruction Encoding Reference]({{ site.baseurl }}/tlcs900-instruction-encoding/) |

### On-Chip Peripherals

| Peripheral | Description |
|------------|-------------|
| RAM | 8KB internal SRAM |
| Timers | 8x 16-bit timers |
| Serial | 2x UART, 1x SIO |
| DMA | 4-channel MicroDMA |
| Interrupt | Multi-level interrupt controller |
| I/O Ports | Multiple 8-bit ports |
| ADC | 10-bit ADC (optional) |

### Register File

```
┌─────────────────────────────────────────────────────────────┐
│                    REGISTER FILE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  XWA  ─┬─ WA' ─┬─ W' ─┬─ A'    (32/16/8/8 bit)              │
│  XBC  ─┼─ BC' ─┼─ B' ─┼─ C'                                 │
│  XDE  ─┼─ DE' ─┼─ D' ─┼─ E'                                 │
│  XHL  ─┼─ HL' ─┼─ H' ─┼─ L'                                 │
│  XIX  ─┼─ IX                                                │
│  XIY  ─┼─ IY                                                │
│  XIZ  ─┼─ IZ                                                │
│  XSP  ─┴─ SP            (Stack Pointer)                     │
│                                                             │
│  PC   ── Program Counter (24-bit)                           │
│  SR   ── Status Register (flags, interrupt level)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Main CPU

### Memory Map

| Address Range | Size | Description |
|---------------|------|-------------|
| 0x000000-0x001FFF | 8KB | Internal RAM |
| 0x100000-0x10FFFF | 64KB | Audio/DAC Interface |
| 0x110000-0x11FFFF | 64KB | Floppy Disk Controller |
| 0x120000-0x12FFFF | 64KB | Inter-CPU Latch |
| 0x130010-0x130020 | 16B | HDAE5000 ATA |
| 0x160000-0x160007 | 8B | HDAE5000 PPI |
| 0x170000-0x17FFFF | 64KB | VGA Controller |
| 0x200000-0x27FFFF | 512KB | External RAM |
| 0x280000-0x2FFFFF | 512KB | HDAE5000 ROM |
| 0x300000-0x3FFFFF | 1MB | Custom Data Flash |
| 0x800000-0x9FFFFF | 2MB | Table Data ROM |
| 0xE00000-0xFFFFFF | 2MB | Program ROM |

See [Memory Map]({{ site.baseurl }}/memory-map/) for complete details.

> **This map is software-defined and it changes once during boot.** The TMP94C241 decodes
> external addresses through six programmable chip-select blocks; the table above is the
> state *after* the bootloader's `MSAR2 := 0x80` handover store. Before it, the table-data
> ROM occupies the top of memory and the program flash sits at `0x800000`. See
> [TMP94C241 Memory Controller]({{ site.baseurl }}/tmp94c241-memory-controller/).

### Firmware Structure

The 2MB Main CPU ROM is organized as:

| Component | Description |
|-----------|-------------|
| Reset Vector | Entry point at 0xFFFEE0 |
| Interrupt Vectors | Exception handlers |
| Boot Code | Hardware initialization |
| Subsystem Handlers | UI, MIDI, FDC, etc. |
| Data Tables | Fonts, graphics, strings |

### Reconstruction Status

| Metric | Value |
|--------|-------|
| ROM Size | 2MB (2,097,152 bytes) |
| Match | 100% byte-perfect |
| Native Instructions | 239,683 |
| Symbolic `.long` References | 15,683 |
| Build System | LLVM (`llvm-mc` + `ld.lld` + `llvm-objcopy`) |

## Sub CPU

### Memory Map

| Address Range | Size | Description |
|---------------|------|-------------|
| 0x000000-0x000FFF | 4KB | Internal CPU RAM (on-chip, bypasses external bus) |
| 0x002B00-0x002B1F | 32B | Ring buffer control (MIDI message queue from Main CPU) |
| 0x002000-0x031FFF | 192KB | Payload RAM (loaded from Main CPU at boot) |
| 0x100000-0x10FFFF | 64KB | Tone Generator hardware registers |
| 0x120000 | 1B | Inter-CPU communication latch |
| 0x130000-0x130002 | 4B | DSP registers (uPD6383GF-3BA: address + data) |
| 0xFE0000-0xFFFFFF | 128KB | Boot ROM |

### Boot Process

1. Sub CPU starts from reset vector in Boot ROM (0xFFFEE0)
2. Initializes DMA and latch configuration (`InterCPU_Latch_Setup` at 0x020B3B)
3. Receives 192KB payload from Main CPU via DMA transfer
4. Main CPU verifies payload checksums (`SubCPU_Payload_Verify`)
5. Jumps to payload entry point
6. Enters audio processing main loop

### Firmware Components

| Component | Size | Status | Native Instructions |
|-----------|------|--------|-------------------|
| Boot ROM | 128KB | 100% byte-match | 1,357 |
| Payload | 192KB | 100% byte-match | 35,721 |

### Audio Processing Architecture

The Sub CPU's primary role is real-time audio synthesis and effects processing. It manages:

**Voice Management (26 channels):**
- Receives MIDI-like messages from Main CPU via ring buffer at 0x2B0D
- `MIDI_Dispatch` (0x034D93) parses status bytes and routes to voice handlers
- Supports Note On/Off, Control Change, Program Change, Pitch Bend, Channel Pressure
- 26 internal voice channels (0x00-0x19) with per-voice parameter tables
- See [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) for full protocol details

**Tone Generator Control:**
- Direct register writes to hardware at 0x100000-0x10FFFF
- Per-channel filter frequency (0x04520A), filter Q (0x04520E), output (0x0451CC)
- Filter frequency clamped to max 0x1C

**DSP Effects Processing (uPD6383GF-3BA):**
- Memory-mapped DSP at 0x130000 (address) / 0x130002 (data)
- 4 effect channels × 32 registers each
- Bytecode interpreter at 0x03C32E (1,613 bytes, 6 native handlers)
- Real-time parameter updates via `DSP_ParameterWriteEngine` (0x03C673)
- See [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) for DSP details

**Hardware I/O:**
- Port E bit 0: Audio mute control (confirmed by `MUTE_AND_HALT` routine at 0x9360)
- Parallel port (P7/PZ): DSP command/data protocol for effect program loading
- DMA Channel 0: Inter-CPU latch data transfer (interrupt-driven)

## Inter-CPU Communication

The CPUs communicate via a hardware latch at 0x120000. The Main CPU sends MIDI-like command streams to the Sub CPU for audio synthesis control.

### Transfer Mechanism

| Component | Main CPU | Sub CPU |
|-----------|----------|---------|
| Latch Address | 0x120000 (write) | 0x120000 (read) |
| Transfer Function | `Audio_DMA_Transfer` (0xEF32F4) | `MICRODMA_CH0_HANDLER` (0x020F1F) |
| Direction | Main → Sub (primary) | Sub → Main (status/ack) |

### Data Flow

1. Main CPU writes MIDI-like messages to latch at 0x120000
2. Sub CPU's MicroDMA Channel 0 fires interrupt on data arrival
3. `MICRODMA_CH0_HANDLER` dispatches received bytes to command parser
4. Bytes accumulate in ring buffer at 0x2B0D
5. `MIDI_Dispatch` processes complete messages from the ring buffer

### Payload Transfer (Boot Only)

At boot, the Main CPU transfers the 192KB Sub CPU payload via the same latch:

| Function | Address | CPU | Purpose |
|----------|---------|-----|---------|
| `SubCPU_Payload_Transfer` | 0xEF0620 | Main | Send 192KB payload |
| `SubCPU_Payload_Verify` | 0xEF06A0 | Main | Verify checksums (DRAM 0xFFD2/0xFFD4) |

The payload checksums are stored in Main CPU DRAM at 0xFFD2 and 0xFFD4, preserved across power cycles via NVRAM save (triggered by SNS NMI).

See [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) for full protocol details.

## Programming Considerations

### Build System

The project uses **LLVM** with a custom TLCS-900 backend as the authoritative build system for all 6 ROMs:

```bash
# Build all ROMs (from roms-disasm/)
make all

# Pipeline: llvm-mc → ld.lld → llvm-objcopy → raw binary
llvm-mc -triple=tlcs900 -filetype=obj source.s -o output.o
ld.lld -T linker.ld output.o -o output.elf
llvm-objcopy -O binary output.elf output.bin
```

All 6 ROMs (Main CPU, Sub CPU boot, Sub CPU payload, Table Data, HDAE5000, Custom Data) achieve **100% byte-perfect match** against the original firmware dumps, totalling 279,441 native instructions across ~8MB of ROM data.

The ASL Macro Assembler (used historically) is archived in `archive/asl/`.

### `.byte` Code Elimination

As of March 2026, the LLVM backend encodings that were missing at the time (R+d16, 16-bit
direct, 8-bit direct, F2 immediate stores, etc.) had all been implemented, and the disassembly
repository's own milestone commits describe "all executable code" as converted for that
effort. **This is not the current state.** Re-running the repository's own
`scripts/analysis/audit_byte_code.py` classifier (2026-09) still finds several hundred `.byte`
blocks across the sub-CPU boot ROM, HDAE5000 and table-data sources that the tool classifies
as already decodable as native instructions by the current LLVM backend — 397 blocks (20,851
bytes), concentrated in `table_data/preset_banks.s` (18,763 bytes) and
`hdae5000/hdae5000_data_tables.s` (722 bytes) — plus 3 small blocks (19 bytes) that still need
further backend work. Converting `.byte` fallbacks to native mnemonics is therefore an ongoing
effort, not a completed one; see [Raw Byte Code Elimination]({{ site.baseurl }}/raw-byte-code-elimination/)
for the current tracking page. (Note: the classifier's "decodable" label means llvm-mc can
round-trip the bytes as valid instructions, not that a block is proven to be code rather than
data that happens to disassemble cleanly — treat the counts as leads, per the tool's own
caveat.)

## Related Pages

- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture
- [Memory Map]({{ site.baseurl }}/memory-map/) - Address space details
- [TMP94C241 Memory Controller]({{ site.baseurl }}/tmp94c241-memory-controller/) - Chip selects and the boot-time remap
- [Boot Sequence]({{ site.baseurl }}/boot-sequence/) - Startup process
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) - Communication details
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - Physical components
- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) - DSP effects and tone generation
- [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) - MIDI processing and voice management
- [TLCS-900 Instruction Encoding]({{ site.baseurl }}/tlcs900-instruction-encoding/) - Instruction set reference

## Code References

### Main CPU Boot & Init

| Symbol | Address | Purpose |
|--------|---------|---------|
| Reset Vector | `0xFFFEE0` | CPU entry point |
| `MainCPU_self_test_routines` | `0xEF0400` | Boot-time self tests |
| `Get_Firmware_Version` | `0xEF0534` | Read version byte from 0xFFFFE8 |
| `MainLoop` | `0xEF1245` | Main event loop entry |
| `INTT1_HANDLER` | `0xEF0BF9` | Timer 1 interrupt (SYSTEM_TIMESTAMP) |
| `SC0Init_Entry` | `0xFCF890` | MIDI serial port initialization |
| `Boot_DisplayScreen` | `0xEF05D0` | Boot screen display |

### Sub CPU

| Symbol | Address | Purpose |
|--------|---------|---------|
| Reset Vector | `0xFFFEE0` | Sub CPU entry point (Boot ROM) |
| `InterCPU_Latch_Setup` | `0x020B3B` | DMA and latch configuration |
| `MICRODMA_CH0_HANDLER` | `0x020F1F` | Command dispatcher (DMA interrupt) |
| `MIDI_Dispatch` | `0x034D93` | MIDI message parser/router |
| `Voice_NoteOn` | `0x02CF97` | Voice note-on processing |
| `Voice_CtrlChange` | `0x02A282` | Voice CC processing and dispatch |
| `Voice_LoadFilterTable_Ch` | `0x022071` | Per-channel filter frequency/LPF |
| `DSP_Bytecode_Programs` | `0x03C32E` | DSP effect bytecode interpreter (1,613B) |
| `DSP_ParameterWriteEngine` | `0x03C673` | Real-time DSP parameter update engine |
| `MUTE_AND_HALT` | `0x009360` | Audio mute via PE.0 and halt |

### Inter-CPU Communication

| Symbol | Address | CPU | Purpose |
|--------|---------|-----|---------|
| `Audio_DMA_Transfer` | `0xEF32F4` | Main | Send MIDI to Sub CPU via latch |
| `SubCPU_Payload_Transfer` | `0xEF0620` | Main | Load 192KB payload to Sub CPU |
| `SubCPU_Payload_Verify` | `0xEF06A0` | Main | Verify payload checksums |

## External References

- [TMP94C241 Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/47265/TOSHIBA/TMP94C241.html) - CPU specifications
- TLCS-900 Programming Manual — **link unverified**: `https://archive.org/details/toshiba-tlcs900` 404s as of this review (2026-09); see [TLCS-900 Instruction Encoding Reference]({{ site.baseurl }}/tlcs900-instruction-encoding/#references) for unconfirmed candidate replacements
- [LLVM TLCS-900 Backend](https://github.com/ArqueologiaDigital/llvm-project) - Custom LLVM backend for TLCS-900 (corrected from `niclasr/llvm-project`: this was the only page on the site using that name, against ~50 pages naming `ArqueologiaDigital/llvm-project` for the same backend; neither URL is confirmed publicly reachable, so this is an internal-consistency fix, not a verified-live link)
