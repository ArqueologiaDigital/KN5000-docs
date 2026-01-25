---
layout: page
title: Memory Map
permalink: /memory-map/
---

# KN5000 Memory Map

## Main CPU Address Space

| Address Range | Size | Description |
|---------------|------|-------------|
| `0x000000 - 0x0FFFFF` | 1MB | Internal RAM / SFRs |
| `0x110000` | - | Floppy Disk Controller |
| `0x120000` | - | Inter-CPU Communication Latches |
| `0x160000` | - | HDAE5000 PPI (Audio Processor Interface) |
| `0x280000` | 512KB | HDAE5000 ROM |
| `0x300000` | 1MB | Custom Data Flash (User Storage) |
| `0x400000` | - | Rhythm Data ROM |
| `0x800000` | 2MB | Table Data ROM |
| `0xE00000` | 2MB | Program Flash (Main ROM) |

## Special Function Registers (TMP94C241F)

### Serial Channels

| Register | Address | Description |
|----------|---------|-------------|
| `SC0BUF` | - | Serial Channel 0 Buffer |
| `SC0CR` | - | Serial Channel 0 Control |
| `SC0MOD` | - | Serial Channel 0 Mode |
| `SC1BUF` | - | Serial Channel 1 Buffer |
| `SC1CR` | - | Serial Channel 1 Control |
| `SC1MOD` | - | Serial Channel 1 Mode |

### Timers

| Register | Address | Description |
|----------|---------|-------------|
| `T0` - `T7` | - | 8-bit Timers |
| `T8` - `TB` | - | 16-bit Timers |

### Interrupts

| Vector | Handler | Description |
|--------|---------|-------------|
| `INTA` | `INTA_HANDLER` | Interrupt A (includes serial) |
| `INT0` | `INT0_HANDLER` | External Interrupt 0 |

## Control Panel Memory

### Button State

| Variable | Description |
|----------|-------------|
| `STATE_OF_CPANEL_BUTTONS` | Array holding current button states |
| `STATE_OF_CPANEL_BUTTONS + 11` | Bits 6,7 select value 0x0c/0x0d/0x0e |

### LED State

| Variable | Description |
|----------|-------------|
| `CPANEL_INDEX_FOR_LEDS` | Current LED addressing index |
| `CPANEL_VAR_RELATED_TO_ARRAY_OF_LEDS` | LED data array |

### Protocol State

| Variable | Description |
|----------|-------------|
| `CPANEL_STATE_0_TO_17` | State machine variable (0-17) |
| `CPANEL_BACKUP_RX_INDEX` | Backup of RX buffer position |
| `RX_INDEX` | Current receive buffer index |

## Inter-CPU Communication

The main CPU communicates with the sub CPU via latches at `0x120000`.

*Details TBD*

## HDAE5000 Audio Processor

Interface via PPI at `0x160000`. ROM at `0x280000`.

*Details TBD*
