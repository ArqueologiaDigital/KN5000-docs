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
| `0x160000` | - | HDAE5000 PPI (Hard Disk Expansion Interface) |
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

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8E4A` | `STATE_OF_CPANEL_BUTTONS` | Button state array (Right panel) |
| `0x8E5A` | `STATE_OF_CPANEL_BUTTONS_LEFT` | Button state array (Left panel) |
| `0x8E55` | `STATE_OF_CPANEL_BUTTONS + 11` | Bits 6,7 select value 0x0c/0x0d/0x0e |

### LED State

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8DFD` | `CPANEL_INDEX_FOR_LEDS` | Current LED addressing index (word) |

### Protocol State

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8D8B` | `CPANEL_STATE_0_TO_17` | State machine variable (byte, values 0-17) |
| `0x8D9D` | `CPANEL_BACKUP_RX_INDEX` | Backup of RX buffer position (word) |
| `0x8D9F` | `CPANEL_RX_INDEX` | Current receive buffer index (word) |

### Status Flags

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8D8C` | `CPANEL_SERIAL_FLAGS_A` | Serial protocol flags (byte) |
| `0x8D92` | `CPANEL_SERIAL_FLAGS_B` | Serial protocol flags (byte) |
| `0x8D93` | `CPANEL_SERIAL_FLAGS_C` | Serial protocol flags (byte) |

## Inter-CPU Communication

The main CPU communicates with the sub CPU via latches at `0x120000`.

*Details TBD*

## HDAE5000 Hard Disk Expansion

The HD-AE5000 is a hard disk expansion system, not an audio processor. It serves as a data control center for managing large music file libraries beyond floppy disk capacity.

**Interface:** PPI at `0x160000`
**ROM:** `0x280000` (512KB)

### Firmware Versions

| Version | Release Date | Notes |
|---------|--------------|-------|
| v1.10i | 1998-07-06 | Initial release |
| v1.15i | 1998-10-13 | |
| v2.0i | 1999-01-15 | Added lyrics display |

All versions archived at [archive.org](https://archive.org/details/technics-kn5000-system-update-disks).

### Features

- Flash-ROM and Static RAM for quick directory access
- 2.5" Hard Disk Drive (1.08 GB storage)
- Parallel port for PC communication (HD-TechManager5000 software)
- Audio outputs with channel separation options

### Limitations

Files cannot be played directly from hard drive during performance - all file operations occur during breaks to protect the drive.

**Reference:** [keysoftservice.ch/hdae5000-e.htm](https://www.keysoftservice.ch/hdae5000-e.htm)
