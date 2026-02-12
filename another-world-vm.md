---
layout: page
title: Another World VM
permalink: /another-world-vm/
---

# Another World VM Port

A port of Delphine Software's **Another World** (1991) running natively on the Technics KN5000 keyboard. The game's original bytecode interpreter is reimplemented in TLCS-900/H2 assembly, executing the unmodified Amiga game data on the KN5000's hardware.

> **Source:** [GitHub: kn5000-anotherworld](https://github.com/felipesanches/kn5000-anotherworld)

## Overview

| Property | Value |
|----------|-------|
| Target CPU | TMP94C241F (TLCS-900/H2) @ 16 MHz |
| Display | MN89304 VGA controller, 320x240 @ 8bpp |
| Input | Control panel buttons via SC1 synchronous serial |
| Build Targets | Standalone maincpu ROM (2 MB) or HDAE5000 extension (512 KB) |
| Game Data | Original Amiga resources (bytecode, polygons, palettes, bitmaps) |

## Architecture

The game uses a bytecode virtual machine originally designed for the Amiga (Motorola 68000). The VM interprets **big-endian bytecode on a little-endian CPU**, requiring byte-swap operations (`EX W, A`) on every 16-bit fetch.

### VM Execution Model

- **64 threads** with cooperative multitasking (no preemption)
- Each thread has a program counter stored in `THREADS_DATA`
- Register `XIX` tracks the current bytecode position during execution
- Thread scheduling happens at frame boundaries via `NEXT_THREAD`

### Bytecode Opcodes

All 27 opcodes (0x00-0x1A) are implemented:

| Range | Category | Examples |
|-------|----------|---------|
| 0x00-0x04 | Register ops | MOV, ADD, ADDCONST, CALL, RET |
| 0x05-0x0A | Flow control | BREAK, JMP, SETVEC, JNOT, CONDJMP |
| 0x0B-0x0F | Variable ops | SETPALETTE, SELECTVIDEOPAGE, FILLVIDEOPAGE, COPYVIDEOPAGE, BLITFRAMEBUFFER |
| 0x10-0x13 | Thread ops | KILLTHREAD, DRAWSTRING, SUB, AND |
| 0x14-0x17 | More ops | OR, SHL, SHR, PLAYSOUND |
| 0x18-0x1A | Resources | LOADRESOURCE, PLAYSONG, PLAYMUSIC |
| 0x40/0x80 | Video | Polygon/sprite rendering |

### Video Rendering

Four 320x240 framebuffers (76,800 bytes each) support double-buffered rendering:
- **Polygon engine**: Interprets vertex lists from video data resources, drawing filled convex polygons
- **Bitmap loader**: Decompresses full-screen images (ByteKiller algorithm)
- **Palette**: 16 colors, 4-bit per channel (0x0RGB format), mapped to MN89304's 4-bit DAC

### Memory Layout

**Maincpu target** (standalone ROM):

| Address | Size | Contents |
|---------|------|----------|
| 0x010000 | 64 KB | VM variables, thread data, stack |
| 0x020000 | 75 KB | Page buffer 0 |
| 0x030000 | 75 KB | Page buffer 1 |
| 0x040000 | 75 KB | Page buffer 2 |
| 0x050000 | 75 KB | Page buffer 3 |
| 0x060000 | 75 KB | Offscreen work buffer |
| 0xE00000 | 2 MB | Program ROM (code + game resources) |

**Extension target** (HDAE5000 slot):

| Address | Size | Contents |
|---------|------|----------|
| 0x200000 | 64 KB | VM variables, thread data, stack |
| 0x240000 | 75 KB | Page buffers 0-3 |
| 0x280000 | 512 KB | Extension ROM |

## Input System

The KN5000's control panel buttons are read via **SC1 synchronous serial** at 250 kHz. The firmware polls two button segments each frame:

| KN5000 Button | Segment | Bit | Game Action |
|--------------|---------|-----|-------------|
| Part Select: RIGHT 2 | CPR_SEG4 | 1 | Jump (UP) |
| CONDUCTOR: LEFT | CPR_SEG4 | 4 | Move LEFT |
| CONDUCTOR: RIGHT 2 | CPR_SEG4 | 5 | Crouch (DOWN) |
| CONDUCTOR: RIGHT 1 | CPR_SEG4 | 6 | Move RIGHT |
| VARIATION 4 | CPL_SEG4 | 3 | ACTION (run/kick/draw gun) |

### Serial Protocol

Each button query is a 4-byte exchange:
1. Send command byte (`0xE0` for right panel, `0x20` for left panel)
2. Send segment number (`0x04`)
3. Send dummy byte (`0xFF`) — response header received
4. Send dummy byte (`0xFF`) — button bitmap received

The TX complete flag (`INTES1` bit 7) is polled between bytes. The baud rate generator (BR1CR = 0x14) provides the 250 kHz clock — **not** the TO2 trigger, which would be corrupted by Timer 1 system tick interrupts.

## Frame Timing

A hardware timer provides frame pacing:

- **Timer 0/1 cascade** at 12,500 Hz (80 µs per tick)
- `INTT1` ISR increments `SYSTEM_TICKS` counter
- `PAUSE` opcode reads `var[0xFF]` for frame duration in 20 ms slices (250 ticks each)
- DJNZ fallback counter provides minimum frame time

## Game Parts

The game consists of multiple "parts", each with its own set of resources (bytecode, video data, palettes):

| Part | ID | Description |
|------|----|-------------|
| 0 | Protection/Logo | Interplay logo, copy protection (bypassed) |
| 1 | Intro | Opening cinematic |
| 2 | Water | First gameplay level |
| 3 | Prison | Escape sequence |
| 4 | Citadel | Main exploration |
| 5-7 | Arena/Baths | Later levels |
| 8-9 | Password | Password entry screen |

Part switching loads new resources and reinitializes the VM. Copy protection checks (parts 0, 2, 4, 8-9) are bypassed by pre-setting VM variables at startup.

## Build and Test

```bash
cd kn5000-anotherworld/

make            # Build maincpu ROM + create MAME ROM set
make extension  # Build as HDAE5000 extension ROM
make test       # Run in MAME emulator
```

Requirements:
- ASL Macro Assembler 1.42 Beta
- Original KN5000 ROMs (for MAME ROM set)
- Game resources extracted from the original Amiga data (see repo README)

## Implementation Status

| Feature | Status |
|---------|--------|
| All VM opcodes | Implemented |
| Polygon rendering | Working |
| Bitmap decompression | Working (ByteKiller) |
| Palette management | Working (4-bit DAC) |
| Frame timing | Working (hardware timer) |
| Part switching | Working |
| Input (directions + action) | Working |
| Sound effects | Stub (consumes bytecode, no output) |
| Music | Stub (consumes bytecode, no output) |

## Technical Challenges

### Endianness
The original game was designed for the big-endian Motorola 68000. Every 16-bit value fetched from bytecode must be byte-swapped (`EX W, A` after `LD WA, (XIX)`) on the little-endian TLCS-900.

### 4-bit Palette DAC
The MN89304's RAMDAC is 4-bit (0-15), not 6-bit like standard VGA. The game's 4-bit palette values (0x0RGB format) map directly without scaling.

### Copy Protection
The original game includes protection checks that read specific VM variables. These are bypassed by initializing `var[0xBC]`, `var[0xDC]`, and `var[0xF2]` to expected values at startup.

### FREEZE Semantics
The VM's thread freeze mechanism must be one-shot: after applying a freeze/unfreeze request, the request is cleared. Without this, frozen threads (like the death handler) never unfreeze.

## Related Pages

- [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) — TMP94C241F architecture
- [Display Subsystem]({{ site.baseurl }}/display-subsystem/) — MN89304 VGA controller
- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) — Button/LED serial protocol
- [Memory Map]({{ site.baseurl }}/memory-map/) — KN5000 address space
- [HDAE5000]({{ site.baseurl }}/hdae5000/) — Extension board (alternative build target)
