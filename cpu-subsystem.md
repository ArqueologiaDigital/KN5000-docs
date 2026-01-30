---
layout: page
title: CPU Subsystem
permalink: /cpu-subsystem/
---

# CPU Subsystem

The KN5000 uses a dual-CPU architecture with two identical TMP94C241F processors performing different roles.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DUAL CPU ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐     ┌─────────────────────────────────────┐
│           MAIN CPU              │     │            SUB CPU                   │
│         TMP94C241F              │     │          TMP94C241F                  │
│                                 │     │                                      │
│  Role: System Controller        │     │  Role: Audio Processor              │
│                                 │     │                                      │
│  ┌───────────────────────────┐ │     │  ┌───────────────────────────────┐  │
│  │ Program ROM: 2MB          │ │     │  │ Boot ROM: 128KB (internal)    │  │
│  │ @ 0xE00000-0xFFFFFF       │ │     │  │ @ 0xFE0000-0xFFFFFF           │  │
│  └───────────────────────────┘ │     │  └───────────────────────────────┘  │
│                                 │     │                                      │
│  ┌───────────────────────────┐ │     │  ┌───────────────────────────────┐  │
│  │ RAM: 512KB                │ │     │  │ Payload: 192KB                │  │
│  │ @ 0x200000-0x27FFFF       │ │     │  │ (loaded at boot from Main)    │  │
│  └───────────────────────────┘ │     │  └───────────────────────────────┘  │
│                                 │     │                                      │
│  Responsibilities:              │     │  Responsibilities:                   │
│  ├─ User interface             │     │  ├─ DSP control                      │
│  ├─ Menu system                │     │  ├─ DAC output                       │
│  ├─ Control panel handling     │     │  ├─ Tone generation                  │
│  ├─ MIDI processing            │     │  ├─ Voice management                 │
│  ├─ Sequencer                  │     │  └─ Effects processing               │
│  ├─ Floppy disk I/O            │     │                                      │
│  ├─ HDAE5000 management        │     │                                      │
│  └─ Sub CPU coordination       │     │                                      │
└─────────────────────────────────┘     └─────────────────────────────────────┘
                    │                                     ▲
                    │         Communication Latch         │
                    └───────────► @ 0x120000 ◄────────────┘
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
| Instruction Set | CISC, variable length (1-7 bytes) |

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
│                    REGISTER FILE                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  XWA  ─┬─ WA' ─┬─ W' ─┬─ A'    (32/16/8/8 bit)             │
│  XBC  ─┼─ BC' ─┼─ B' ─┼─ C'                                 │
│  XDE  ─┼─ DE' ─┼─ D' ─┼─ E'                                 │
│  XHL  ─┼─ HL' ─┼─ H' ─┼─ L'                                 │
│  XIX  ─┼─ IX                                                 │
│  XIY  ─┼─ IY                                                 │
│  XIZ  ─┼─ IZ                                                 │
│  XSP  ─┴─ SP            (Stack Pointer)                      │
│                                                              │
│  PC   ── Program Counter (24-bit)                            │
│  SR   ── Status Register (flags, interrupt level)            │
│                                                              │
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
| Match | 99.99% |
| Divergent Bytes | 177 |
| Cause | Instruction encoding variations |

## Sub CPU

### Memory Map

| Address Range | Size | Description |
|---------------|------|-------------|
| 0x000000-0x001FFF | 8KB | Internal RAM |
| 0x002000-0x031FFF | 192KB | Payload RAM |
| 0xFE0000-0xFFFFFF | 128KB | Boot ROM |

### Boot Process

1. Sub CPU starts from reset vector in Boot ROM
2. Waits for payload from Main CPU via latch
3. Receives 192KB payload via DMA
4. Jumps to payload entry point
5. Enters audio processing loop

### Firmware Components

| Component | Size | Status |
|-----------|------|--------|
| Boot ROM | 128KB | 100% reconstructed |
| Payload | 192KB | 100% reconstructed |

## Inter-CPU Communication

The CPUs communicate via a latch at 0x120000:

### Main CPU Side
```c
// Send byte to Sub CPU
*(volatile uint8_t*)0x120000 = data;

// Read status/response
uint8_t response = *(volatile uint8_t*)0x120000;
```

### Sub CPU Side
```c
// Receive byte from Main CPU
uint8_t data = *(volatile uint8_t*)LATCH_ADDR;

// Send acknowledgment
*(volatile uint8_t*)LATCH_ADDR = ACK;
```

See [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) for protocol details.

## Programming Considerations

### Assembler

The project uses **ASL Macro Assembler** (Alfred Arnold's) for TLCS-900:

```bash
# Build command
asl -cpu tmp94c241 source.asm -o output.p
p2bin output.p output.bin
```

**Note**: ASL supports TMP96C141 natively; some TMP94C241-specific instructions require macros in `tmp94c241.inc`.

### Unsupported Instructions

Some TMP94C241 instructions require manual encoding:

| Instruction | Workaround |
|-------------|------------|
| `LDI`, `LDIR` | Macro with raw bytes |
| `MUL/DIV` variants | Macro with raw bytes |
| Extended shifts | Macro with raw bytes |

See `tmp94c241.inc` in the disassembly repository for implementations.

## Related Pages

- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture
- [Memory Map]({{ site.baseurl }}/memory-map/) - Address space details
- [Boot Sequence]({{ site.baseurl }}/boot-sequence/) - Startup process
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) - Communication details
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - Physical components

## External References

- [TMP94C241 Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/47265/TOSHIBA/TMP94C241.html) - CPU specifications
- [TLCS-900 Programming Manual](https://archive.org/details/toshiba-tlcs900) - Instruction set reference
- [ASL Assembler](http://john.ccac.rwth-aachen.de:8000/as/) - Build tool
