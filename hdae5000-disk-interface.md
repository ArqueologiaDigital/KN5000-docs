---
layout: page
title: HDAE5000 Hard Disk Interface
permalink: /hdae5000-disk-interface/
---

# HD-AE5000 Hard Disk Interface

This page documents the low-level hard disk interface used by the HD-AE5000 expansion for the Technics KN5000 keyboard. Understanding this interface is essential for MAME emulation and homebrew development.

## Overview

The HD-AE5000 uses an **IDE/ATA compatible hard disk drive** with a custom interface bridged through an Intel 8255 PPI (Programmable Peripheral Interface). This architecture allows the main CPU to communicate with the hard disk controller without direct IDE bus access.

```
┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   TMP94C241F     │     │   Intel 8255    │     │   IDE Hard Disk  │
│   Main CPU       │◄───►│   PPI Bridge    │◄───►│   Controller     │
│                  │     │   @ 0x160000    │     │                  │
└──────────────────┘     └─────────────────┘     └──────────────────┘
```

## IDE/ATA Background

### What is IDE/ATA?

**IDE (Integrated Drive Electronics)** and **ATA (AT Attachment)** are standards for connecting hard disk drives to computers. The HD-AE5000 uses a 2.5" laptop-style IDE drive with 1.08GB capacity, which was a substantial amount for 1996-era consumer electronics.

### ATA Register Set

The standard ATA interface provides 8 registers accessed through a parallel bus:

| Offset | Register | Read | Write |
|--------|----------|------|-------|
| 0x00 | Data | Data | Data |
| 0x01 | Error | Error code | Features |
| 0x02 | Sector Count | Sector count | Sector count |
| 0x03 | LBA Low | LBA bits 0-7 / Sector | LBA bits 0-7 / Sector |
| 0x04 | LBA Mid | LBA bits 8-15 / Cylinder Low | LBA bits 8-15 / Cylinder Low |
| 0x05 | LBA High | LBA bits 16-23 / Cylinder High | LBA bits 16-23 / Cylinder High |
| 0x06 | Device/Head | Device/Head select | Device/Head select |
| 0x07 | Status | Status | Command |

The HD-AE5000 firmware uses **CHS (Cylinder/Head/Sector)** addressing, as evidenced by debug strings in the ROM:
- `hddtrck` - Track (cylinder) count
- `hddhead` - Head count
- `hddsctr` - Sectors per track
- `hddscby` - Bytes per sector (typically 512)

### Common ATA Commands

| Command | Hex | Description |
|---------|-----|-------------|
| Read Sectors | 0x20 | Read one or more sectors (PIO mode) |
| Write Sectors | 0x30 | Write one or more sectors (PIO mode) |
| Identify Device | 0xEC | Return 512-byte device info block |
| Standby Immediate | 0xE0 | Spin down the drive |
| Idle Immediate | 0xE1 | Set drive to idle state |
| Set Features | 0xEF | Configure drive parameters |

## PPI Bridge Architecture

### Why Use a PPI Bridge?

The main CPU (TMP94C241F) doesn't have a direct IDE interface. Instead, the HDAE5000 expansion board includes an Intel 8255 PPI that acts as a bridge:

1. **Parallel Data Transfer**: The 8-bit Port A sends data to the HD controller
2. **Status Monitoring**: Port B reads status from the HD controller
3. **Control Signals**: Port C manages handshaking and control lines

### PPI Port Assignments

| Address | Port | Direction | Function |
|---------|------|-----------|----------|
| 0x160000 | Port A | Output | Data/Address bus to HD controller |
| 0x160002 | Port B | Input | Status byte from HD controller |
| 0x160004 | Port C | Output | Control signals (read/write strobes) |
| 0x160006 | Control | Write | PPI mode configuration (0x82) |

### PPI Control Register

The PPI is configured with control byte **0x82**:
- Bit 7 = 1: Mode set active
- Port A: Mode 0, Output
- Port B: Mode 0, Input
- Port C: Both nibbles Output

## Disk Access Protocol

Based on ROM analysis, the disk access follows this general pattern:

### 1. Initialize Drive

```
Check_HD_Present (0x2971A3):
    1. Test RAM integrity (fill 32KB with 0x5A5A pattern)
    2. Reset HD controller
    3. Send Identify Device command (0xEC)
    4. Read 512-byte identification block
    5. Parse CHS parameters
    6. Set drive ready flag
```

### 2. Read Sectors

```
Read_FSB (0x2959F6):
    1. Set up CHS address via PPI Port A
    2. Send Read Sectors command (0x20)
    3. Wait for DRQ (Data Request) status
    4. Transfer sector data through PPI
    5. Repeat for each sector
```

### 3. Write Sectors

```
Write_FSB (0x296294):
    1. Set up CHS address via PPI Port A
    2. Send Write Sectors command (0x30)
    3. Wait for DRQ status
    4. Transfer sector data through PPI
    5. Wait for completion
```

### 4. Motor Control

```
TurnHdMotorOff:
    1. Send Standby Immediate command (0xE0)
    2. Wait for drive spindown
```

## Error Handling

The firmware includes multilingual error messages for various disk failures:

| Error | English Message | Likely Cause |
|-------|-----------------|--------------|
| SRAM Error | "Hard disk SRAM error" | Cache RAM failure on HDAE5000 |
| Reset Error | "Hard disk reset error" | Controller not responding |
| Read Error | "Hard disk read error" | Bad sector or media failure |
| ID Read Error | "Hard disk ID read error" | Identify Device command failed |
| Track 0 Error | "Hard disk track 0 error" | Cannot seek to track 0 |
| FSB Error | "Hard disk FSB read error" | Filesystem block corrupted |
| FAT Error | "Hard disk FAT read error" | File allocation table corrupted |

These errors are also available in German and French translations.

## Filesystem Structure

The HDAE5000 uses a **custom filesystem**, not FAT16 or FAT32. Key structures include:

### FSB (File System Block)

The master filesystem metadata block containing:
- Volume information
- Free space tracking
- Directory pointers

### FGB (File Group Block)

Groups related files together:
- File group pointer (`FGB ptr`)
- Group width (`FGB wid`)
- Number of entries (`FGB num`)

### FEB (File Entry Block)

Individual file metadata:
- File entry pointer (`FEB ptr`)
- Entry width (`FEB wid`)
- Number of entries (`FEB num`)

## PPORT Commands for Disk Operations

The PC parallel port (PPORT) protocol includes these disk-related commands:

| Code | Command | Description |
|------|---------|-------------|
| 01 | Send Infos About HD | Report CHS parameters and model |
| 03 | Read FSB from HD | Read filesystem block |
| 04 | Send FSB to PC | Transfer FSB to PC |
| 05 | Rcv FSB from PC | Receive FSB from PC |
| 06 | Write FSB to HD | Write filesystem block |
| 07 | Load HD to Memory | Load file into KN5000 RAM |
| 11 | Save memory to HD | Save RAM contents to file |
| 16 | Delete files | Remove files from disk |
| 17 | Format HD | Low-level disk format |
| 18 | Switch HD-motor off | Spin down drive motor |

## RAM Variables

Key RAM locations used by disk routines:

| Address | Name | Purpose |
|---------|------|---------|
| 0x229D90 | HD_STATUS_FLAG | Current drive status |
| 0x229D92 | HD_RESULT_FLAG | Last operation result |
| 0x229D99-0x229DAE | HD_CONFIG | Drive configuration flags |
| 0x229DC8 | HD_CONTROL | Control register shadow |
| 0x229DD9 | HD_ENABLE | Drive enabled flag |
| 0x230EDA | HDAE5000_INIT_FLAG | 0=no HD, non-zero=HD present |

## Design Considerations

### Why CHS Instead of LBA?

The HDAE5000 uses CHS (Cylinder/Head/Sector) addressing rather than the newer LBA (Logical Block Addressing). This was common for drives of this era (1996) and provides:
- Direct physical addressing
- Compatibility with older drive firmware
- Simpler sector calculation

### Drive Protection

The firmware includes protective features:
- **Motor timeout**: Spins down drive during inactivity
- **No real-time playback**: Files must be loaded to RAM first
- **Verification**: Reads back written data to confirm

### Sector Size

Standard 512-byte sectors are used, as indicated by the `hddscby` (sector bytes) debug string.

## Emulation Considerations

For MAME emulation, the HDAE5000 disk interface requires:

1. **PPI Emulation**: Full 8255 PPI at 0x160000
2. **IDE Drive Model**: CHR-addressed IDE drive simulation
3. **Timing**: Appropriate delays for seek and data transfer
4. **Status Bits**: Proper busy/ready/error flag handling
5. **Custom Filesystem**: FSB/FGB/FEB structure parsing

## Further Research

Areas requiring additional investigation:
- Exact PPI-to-IDE signal mapping
- Complete ATA command set used
- Filesystem structure details
- DMA vs PIO transfer modes
- Exact timing requirements

## Related Documentation

- [HDAE5000 Overview]({{ site.baseurl }}/hdae5000/) - Firmware and initialization
- [Memory Map]({{ site.baseurl }}/memory-map/) - Address space layout
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - System overview

## References

- ATA/ATAPI-4 Specification (T13/1153D)
- Intel 8255A PPI Datasheet
- HDAE5000 ROM disassembly analysis
