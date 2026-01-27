---
layout: page
title: Hardware Architecture
permalink: /hardware-architecture/
---

# KN5000 Hardware Architecture

Detailed hardware documentation extracted from the service manual schematics.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CONTROL PANEL                                │
│  ┌──────────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐      │
│  │     CPL      │  │  CPCL   │  │  CPCR   │  │     CPR      │      │
│  │ M37471M2196S │  │ Switches│  │ Switches│  │ M37471M2196S │      │
│  │   8-bit MCU  │  │  LEDs   │  │         │  │   8-bit MCU  │      │
│  └──────┬───────┘  └────┬────┘  └────┬────┘  └──────┬───────┘      │
│         │ SIN/SOUT/CLK  │            │       SIN/SOUT/CLK │         │
└─────────┼───────────────┴────────────┴───────────────────┼─────────┘
          │                                                │
          └────────────────────┬───────────────────────────┘
                               │ Serial Bus
                        ┌──────┴──────┐
                        │  MAIN PCB   │
                        │             │
                        │ ┌─────────┐ │
                        │ │  IC5    │ │ TMP94C241F
                        │ │Main CPU │ │ 32-bit TLCS-900/H2
                        │ └────┬────┘ │
                        │      │      │
                        │ ┌────┴────┐ │
                        │ │  IC27   │ │ Sub CPU
                        │ │ SubCPU  │ │ (Tone Generator Control)
                        │ └─────────┘ │
                        └─────────────┘
```

## Control Panel MCUs

### Chip Identification

**Mitsubishi M37471M2196S** (both CPL and CPR boards)

- 8-bit CMOS microcomputer
- Mitsubishi 740 series architecture
- Built-in A/D converter (8 channels)
- Serial interface (UART)
- Up to 16 segment outputs for LED multiplexing
- Mask ROM version (M2196S = specific mask pattern)

### CPL Board (Control Panel Left)

| Pin/Signal | Function |
|------------|----------|
| `SIN` | Serial data input (from main CPU) |
| `SOUT` | Serial data output (to main CPU) |
| `CLK` | Serial clock |
| `CNTR1` | Control/chip select |
| `CMD0-CMD4` | Command lines |
| `SW0-SW7` | Switch matrix inputs |
| `SEG00-SEG10` | LED segment outputs |
| `ROTA`, `ROTB` | Rotary encoder inputs |
| `AD0-AD3` | A/D converter inputs |
| `BEND` | Pitch bend wheel (analog) |
| `MOD0`, `MOD1` | Modulation inputs (analog) |
| `MAIN VOLUME` | Master volume (analog) |

### CPR Board (Control Panel Right)

| Pin/Signal | Function |
|------------|----------|
| `SIN` | Serial data input |
| `SOUT` | Serial data output |
| `CLK` | Serial clock |
| `CNTR1` | Control/chip select |
| `CMD0-CMD4` | Command lines |
| `SW0-SW7` | Switch matrix inputs |
| `SEG00-SEG15` | LED segment outputs |

### LED Driver ICs

**HD74LS07P** - Hex buffer/driver with open-collector outputs
- Used for driving LED segments
- Multiple ICs per board (IC2, IC3)

## Main Board ICs

### Main CPU

**IC5: TMP94C241F**
- Toshiba 32-bit TLCS-900/H2 microcontroller
- Address bus: A0-A21 (16MB addressable)
- Data bus: D0-D15 (16-bit)
- Multiple serial channels
- DMA controller
- Timers

### Sub CPU (Tone Generator Controller)

**IC27: TMP94C241F**
- Toshiba 32-bit TLCS-900/H2 microcontroller (same as main CPU)
- Up to 20 MHz clock
- 16 MB linear address space (24-bit addresses)
- 2 KB internal RAM (0x000800-0x000FFF)

**Memory Map:**

| Address | Size | Description |
|---------|------|-------------|
| 0x0000-0x00FF | 256B | Special Function Registers (SFR) |
| 0x0100-0x01FF | 256B | Extended SFR (memory controller, DMA, watchdog) |
| 0x0400-0x04E0 | 225B | Interrupt trampolines (copied from ROM) |
| 0x0500-0x05A2 | ~160B | RAM / Stack area |
| 0x100000 | - | Audio hardware registers (DSP/DAC interface) |
| 0x110000 | - | Keyboard/control panel interface |
| 0x120000 | - | Inter-CPU communication latch |
| 0x130000 | - | Tone generator registers |
| 0xFE0000-0xFFFFFF | 128KB | Boot ROM |

**I/O Capabilities:**
- 2 serial channels (SC0, SC1)
- 4 8-bit timers (T0-T3)
- 16-bit timer (T4)
- DMA controller (channels 0 and 2 used)
- Multiple GPIO ports (P0-PB, PE, PF)
- DRAM controller with refresh

**Role:** Controls tone generator at 0x130000, handles audio synthesis, and communicates with main CPU via latch at 0x120000. Receives 192KB payload from main CPU at boot.

### Memory

| IC | Part Number | Type | Size | Function |
|----|-------------|------|------|----------|
| IC1 | QS6C5008E13 | ROM | 8Mbit | Table Data (ODD) |
| IC3 | QS6C5D0ME11 | ROM | 8Mbit | Table Data (EVEN) |
| IC4 | QV1GFKN5KAX1 | ROM | 8Mbit | Program (EVEN) |
| IC6 | QV1GFKN5KAX1 | ROM | 8Mbit | Program (ODD) |
| IC9 | M5M44260AJ7S | DRAM | 4Mbit | Dynamic RAM |
| IC10 | M5M44260AJ7S | DRAM | 4Mbit | Dynamic RAM |
| IC14 | QS6C303C301I | ROM | - | Additional ROM |
| IC19 | QV1GFKN5KAX1 | ROM | 8Mbit | Custom Data |
| IC21 | - | SRAM | 1Mbit | Backup (battery) |

### Peripherals

| IC | Part Number | Function |
|----|-------------|----------|
| IC24 | MN1382QTX | Reset Controller |
| IC206 | MN89304 | LCD Controller |
| IC207 | M5M44265CJ8S | 4Mbit Video RAM |
| IC208 | D72068GF-3B9 | Floppy Disk Controller |

### HDAE5000 Hard Disk Expansion (Optional)

The HD-AE5000 is an optional expansion providing 1.08GB storage.

| Component | Address | Description |
|-----------|---------|-------------|
| PPI (8255) | 0x160000-0x160006 | Programmable Peripheral Interface |
| ROM | 0x280000 | 512KB firmware ROM |

**PPI Port Mapping:**

| Address | Port | Function |
|---------|------|----------|
| 0x160000 | Port A | Data output to HD controller |
| 0x160002 | Port B | Status input from HD controller |
| 0x160004 | Port C | Control signals (strobe, handshake) |
| 0x160006 | Control | PPI mode configuration (0x82) |

**Detection:** PE port bit 0 (active low) indicates HDAE5000 presence.

See [HDAE5000 page]({{ site.baseurl }}/hdae5000/) for firmware details.

### LCD Controller (MN89304)

The MN89304 provides a VGA-compatible register interface at I/O base `0x170000`.

**Memory Map:**

| Address | Description |
|---------|-------------|
| `0x170000` + port | VGA I/O registers |
| `0x1A0000` | Video RAM base (512KB) |

**VGA I/O Ports:**

| Port | Register | Description |
|------|----------|-------------|
| `0x3C0` | Attribute Controller | Address/Data |
| `0x3C2` | Misc Output | Write only |
| `0x3C4/3C5` | Sequencer | Address/Data |
| `0x3C6` | DAC Mask | Palette mask |
| `0x3C8/3C9` | DAC | Write address/Data |
| `0x3CE/3CF` | Graphics Controller | Address/Data |
| `0x3D4/3D5` | CRTC | Address/Data |
| `0x3DA` | Input Status 1 | Read only |

**CRTC Register Indices:**

| Index | Name | Description |
|-------|------|-------------|
| `0x00` | CRTC_HORIZ_TOTAL | Horizontal Total |
| `0x01` | CRTC_HORIZ_DISP_END | Horizontal Display End |
| `0x06` | CRTC_VERT_TOTAL | Vertical Total |
| `0x07` | CRTC_OVERFLOW | Overflow bits |
| `0x09` | CRTC_MAX_SCAN_LINE | Maximum Scan Line |
| `0x0C/0D` | CRTC_START_ADDR | Display start address |
| `0x10` | CRTC_VERT_RETRACE_START | Vertical Retrace Start |
| `0x11` | CRTC_VERT_RETRACE_END | Vertical Retrace End (bit 7 = protect) |
| `0x12` | CRTC_VERT_DISP_END | Vertical Display End |
| `0x17` | CRTC_MODE_CONTROL | Mode Control |

Registers `0x19` and `0x1A` are MN89304-specific extensions (not standard VGA).

### Logic ICs

| IC | Part Number | Function |
|----|-------------|----------|
| IC11 | TC74VHC139F | 2-to-4 Decoder |
| IC12 | T7W139F | 2-to-4 Decoder |
| IC13 | TC74VHC139F | 3-to-8 Decoder |
| IC16B | D74HC164GS | Shift Register |
| IC17, IC31 | TC7W32FU | Dual 2-input OR gates |

## Button Mapping

### CPL Board (Left Side Panel)

**RHYTHM GROUP:**
- D1: Standard Rock
- D2: R & R Blues
- D3: Pop & Ballad
- D4: Funk & Fusion
- D5: Modern Dance
- D6: Swing
- D7: Jazz Combo

**COMPOSER:**
- D101: Memory
- D102: Menu
- D103: Set
- D104: On/Off
- D105: Music Stylist

**VARIATION & MEM:**
- D17: Demo
- D25-D28: Bank, Menu, Stoprecord, etc.

**FILL IN / INTRO & ENDING:**
- D125-D134: Various fill and ending controls

### CPR Board (Right Side Panel)

**SOUND GROUP:**
- D8: Accordion
- D9: Digital
- D10: Guitar
- D14: Flute
- D15: Sax & Reed
- D21: Piano
- D22: Strings & Vocal

**PART SELECT:**
- D33: Sustain
- D34: Left
- D35: Right 1
- D36: Right 2

**PANEL MEMORY:**
- D49-D56: Memory 1-8
- D57: Next Bank
- D58: Bank View

**SEQUENCER:**
- D160+: Easy Rec, Menu, Sound, Control, Mix, Disk

## Serial Protocol Hardware

The control panel MCUs communicate with the main CPU via a serial interface:

```
Main CPU (TMP94C241F)          Control Panel MCU (M37471M2196S)
        │                               │
        │◄──────── SOUT ───────────────│ (Data from panel)
        │                               │
        │─────────► SIN ───────────────►│ (Data to panel)
        │                               │
        │─────────► CLK ───────────────►│ (Clock)
        │                               │
        │─────────► CNTR1 ─────────────►│ (Control)
        │                               │
        │─────────► CMD0-4 ────────────►│ (Commands?)
```

The exact protocol details must be reverse-engineered from the main CPU firmware disassembly.

## References

- **Service Manual**: EMID971655 A5 ([Download PDF]({{ site.baseurl }}/service_manual/technics_sx-kn5000.pdf) - 26MB)
- Schematic pages: II-9 through II-38
