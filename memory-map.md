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

## Sub CPU Address Space

The sub CPU (tone generator controller) has its own memory map, documented from boot ROM disassembly.

| Address Range | Size | Description |
|---------------|------|-------------|
| `0x0000 - 0x00FF` | 256B | Special Function Registers (SFR) |
| `0x0100 - 0x01FF` | 256B | Extended SFR / Memory Controller |
| `0x0400 - 0x04E0` | 225B | Interrupt vector trampolines (copied from boot ROM) |
| `0x04FE` | 1B | Payload ready flag (bit 6=ready, bit 7=complete) |
| `0x0500 - 0x05A2` | ~160B | RAM / Stack area (stack init = 0x05A2) |
| `0x0512` | 4B | DMA transfer address storage |
| `0x0516` | 2B | DMA state machine (0=idle, 1=pending, 2=in progress) |
| `0x0518` | 2B | Command processing state (0-4) |
| `0x051A` | 1B | Last received command byte |
| `0x051E` | 32B | Variable-length command data buffer |
| `0x0544` | 6B | E1 command data buffer |
| `0x054A` | 10B | E2 command data buffer |
| `0x0556` | 1B | Memory test result flags |
| `0x0558` | 8B | Serial status bytes |
| `0x120000` | - | Inter-CPU Communication Latch (shared with main CPU) |
| `0x130000` | - | Tone Generator Registers |
| `0xFE0000 - 0xFFFFFF` | 128KB | Boot ROM |

### Sub CPU SFR Addresses (Confirmed from Boot ROM)

| Address | Register | Description |
|---------|----------|-------------|
| `0x07` | P0FC | Port 0 Function Control |
| `0x0B` | P1FC | Port 1 Function Control |
| `0x0F` | P2FC | Port 2 Function Control |
| `0x1C` | P7 | Port 7 Data |
| `0x1E` | P7CR | Port 7 Control |
| `0x1F` | P7FC | Port 7 Function Control |
| `0x20` | P8 | Port 8 Data |
| `0x22` | P8CR | Port 8 Control |
| `0x23` | P8FC | Port 8 Function Control |
| `0x28` | PA | Port A Data |
| `0x2B` | PAFC | Port A Function Control |
| `0x2C` | PB | Port B Data |
| `0x2F` | PBFC | Port B Function Control |
| `0x30` | INTTC01 | Interrupt Control (Timer 0/1) |
| `0x34` | SC0BUF | Serial Channel 0 Buffer |
| `0x36` | SC0CR | Serial Channel 0 Control |
| `0x38` | SC0MOD | Serial Channel 0 Mode |
| `0x3A` | SC1BUF | Serial Channel 1 Buffer |
| `0x3C` | SC1CR | Serial Channel 1 Control |
| `0x3E` | SC1MOD | Serial Channel 1 Mode |
| `0x80` | WDMOD | Watchdog Mode |
| `0x81` | WDCR | Watchdog Control |

## Inter-CPU Communication

The main CPU and sub CPU communicate via latches at `0x120000`.

### Latch Address

| Address | Access | Description |
|---------|--------|-------------|
| `0x120000` | R/W | Inter-CPU Communication Latch |

The sub CPU boot ROM configures DMA to use this address for bidirectional communication with the main CPU.

### Communication Protocol

1. Main CPU writes command/data to latch
2. Sub CPU reads from latch
3. Sub CPU writes response/status to latch
4. Main CPU reads response

*Full protocol documentation in progress.*

## Tone Generator

The tone generator hardware is accessed at `0x130000`.

| Address | Description |
|---------|-------------|
| `0x130000` | Tone Generator Base Address |

The sub CPU boot ROM initializes tone generator registers with patterns starting at this address. Each voice appears to use a 32-byte register block.

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
