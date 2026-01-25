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

- Service Manual: EMID971655 A5
- Schematic pages: II-9 through II-38
