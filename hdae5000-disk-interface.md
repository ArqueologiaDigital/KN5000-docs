---
layout: page
title: HDAE5000 Hard Disk Interface
permalink: /hdae5000-disk-interface/
---

# HD-AE5000 Hard Disk Interface

This page documents the low-level hard disk interface used by the HD-AE5000 expansion for the Technics KN5000 keyboard. Understanding this interface is essential for MAME emulation and homebrew development.

## Overview

The HD-AE5000 uses an **IDE/ATA compatible hard disk drive** with **direct memory-mapped registers**. The ATA registers are accessible at addresses 0x130010-0x130020 from the main CPU.

A separate **Intel 8255 PPI** at 0x160000 provides a parallel port interface for communication with a PC running the HD-TechManager5000 software.

```
┌──────────────────┐                           ┌──────────────────┐
│   TMP94C241F     │  Direct Memory Access     │   IDE Hard Disk  │
│   Main CPU       │◄─────────────────────────►│   @ 0x130010     │
│                  │                           │   (ATA Registers)│
│                  │                           └──────────────────┘
│                  │
│                  │     ┌─────────────────┐
│                  │◄───►│   Intel 8255    │◄───► PC Parallel Port
└──────────────────┘     │   PPI @ 0x160000│
                         └─────────────────┘
```

## IDE/ATA Background

### What is IDE/ATA?

**IDE (Integrated Drive Electronics)** and **ATA (AT Attachment)** are standards for connecting hard disk drives to computers. The HD-AE5000 uses a 2.5" laptop-style IDE drive with 1.08GB capacity, which was a substantial amount for 1996-era consumer electronics.

### ATA Register Set (Firmware-Verified)

The HD-AE5000 maps ATA registers directly to memory addresses. The register layout was verified by analyzing firmware code at 0x2974DD-0x297501 and 0x2976AB-0x297883:

| Address | Register | Read | Write |
|---------|----------|------|-------|
| 0x130010 | Data (16-bit) | Sector data | Sector data |
| 0x130012 | Error/Features | Error code | Features |
| 0x130014 | Sector Count | Sector count | Sector count |
| 0x130016 | Sector Number | Sector/LBA Low | Sector/LBA Low |
| 0x130018 | Cylinder Low | Cylinder Low/LBA Mid | Cylinder Low/LBA Mid |
| 0x13001A | Cylinder High | Cylinder High/LBA High | Cylinder High/LBA High |
| 0x13001C | Device/Head | Device/Head | Device/Head (0xA0 \| head) |
| 0x13001E | Status/Command | Status | Command |
| 0x130020 | Device Control | - | Device Control |

The HD-AE5000 firmware uses **CHS (Cylinder/Head/Sector)** addressing, as evidenced by debug strings in the ROM:
- `hddtrck` - Track (cylinder) count
- `hddhead` - Head count
- `hddsctr` - Sectors per track
- `hddscby` - Bytes per sector (typically 512)

### ATA Commands Used by Firmware

The following commands were identified by analyzing firmware writes to the Command Register (0x13001E):

| Command | Hex | Address | Description |
|---------|-----|---------|-------------|
| Read Sectors | 0x20 | 0x29781D | Read one or more sectors (PIO mode) |
| Write Sectors | 0x30 | 0x29772B | Write one or more sectors (PIO mode) |
| Standby | 0x94 | 0x297501 | Spin down drive with timeout parameter |
| Identify Device | 0xEC | 0x2978C3 | Return 512-byte device identification block |

## PPI Parallel Port Interface

### Purpose

The Intel 8255 PPI at 0x160000 is **NOT** used for IDE communication - the IDE registers are directly memory-mapped. Instead, the PPI provides a **parallel port interface for PC communication** with the HD-TechManager5000 Windows software.

This allows file transfer between a PC and the HDAE5000's hard disk via the PC's parallel port.

### PPI Port Assignments

| Address | Port | Direction | Function |
|---------|------|-----------|----------|
| 0x160000 | Port A | Bidirectional | Data byte to/from PC |
| 0x160002 | Port B | Input | Status byte from PC |
| 0x160004 | Port C | Output | Control signals to PC |
| 0x160006 | Control | Write | PPI mode configuration |

## Disk Access Protocol

Based on firmware analysis at 0x2974C7-0x297924, disk access follows this pattern:

### 1. Wait for Drive Ready

```
Wait_HD_Ready (0x297438):
    1. Read Status register (0x13001E)
    2. Check bits: BSY=0 (bit 7), DRDY=1 (bit 6)
    3. Mask with 0xC0, compare to 0x40
    4. Repeat until ready or timeout (0x3FFFFF iterations)
```

### 2. Initialize Drive (0x2974C7)

```
Init_HD:
    1. Wait for drive ready
    2. Write 0xFF to Features (0x130012)
    3. Write 0x00 to Sector Count (0x130014)
    4. Write 0xFF to Sector/Cyl Low/Cyl High (0x130016/18/1A)
    5. Write 0xA0 to Device/Head (0x13001C)
    6. Write 0x94 (Standby) to Command (0x13001E)
```

### 3. Read Sectors (0x297788)

```
Read_Sectors:
    1. Wait for drive ready (Status & 0xC0 == 0x40)
    2. Write 0x01 to Sector Count (0x130014)
    3. Write (0xA0 | head) to Device/Head (0x13001C)
    4. Write cylinder low to 0x130018
    5. Write cylinder high to 0x13001A
    6. Write sector number to 0x130016
    7. Write 0x20 (Read) to Command (0x13001E)
    8. Wait for DRQ (Status & 0xC8 == 0x48)
    9. Read 256 words from Data register (0x130010)
    10. Wait for completion (Status & 0xC0 == 0x40)
    11. Check error bit (Status & 0x01)
```

### 4. Write Sectors (0x29769B)

```
Write_Sectors:
    1. Wait for drive ready
    2. Write 0x01 to Sector Count (0x130014)
    3. Write (0xA0 | head) to Device/Head (0x13001C)
    4. Write CHS address to registers
    5. Write 0x30 (Write) to Command (0x13001E)
    6. Wait for DRQ
    7. Write 256 words to Data register (0x130010)
    8. Wait for completion
    9. Check error bit
```

### 5. Identify Device (0x297884)

```
Identify_Device:
    1. Wait for drive ready
    2. Write 0xFF to all address registers
    3. Write 0xA0 to Device/Head (0x13001C)
    4. Write 0xEC (Identify) to Command (0x13001E)
    5. Wait for DRQ
    6. Read 256 words from Data register to 0x200000
    7. Parse CHS geometry from identification data
```

### 6. Reset Controller (0x29747A)

```
Reset_HD:
    1. Write 0x0E to Device Control (0x130020) - SRST + nIEN
    2. Write 0x0A to Device Control (0x130020) - Clear reset, keep nIEN
    3. Wait for drive ready
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
| 08 | Send data to PC | Send data block to PC |
| 10 | Rcv data from PC | Receive data from PC |
| 11 | Save memory to HD | Save RAM contents to file |
| 16 | Delete files | Remove files from disk |
| 17 | Format HD | Low-level disk format |
| 18 | Switch HD-motor off | Spin down drive motor |

## PC Parallel Port Protocol

The HD-TechManager5000 Windows software (ppkn50.dll) communicates with the HDAE5000 using a bidirectional parallel port protocol. This section documents the low-level handshaking derived from disassembly of ppkn50.dll.

### Physical Interface

**PC Parallel Port (Standard SPP):**

| Port Address | Register | Direction | Function |
|--------------|----------|-----------|----------|
| base+0 (0x378) | Data | Bidirectional | 8-bit data byte |
| base+1 (0x379) | Status | Input | Status signals from HDAE5000 |
| base+2 (0x37A) | Control | Output | Control signals to HDAE5000 |

**HDAE5000 PPI (Intel 8255 at 0x160000):**

| Address | Port | Direction | Function |
|---------|------|-----------|----------|
| 0x160000 | Port A | Bidirectional | Data byte to/from PC |
| 0x160002 | Port B | Input | Status from PC |
| 0x160004 | Port C | Output | Control signals to PC |

### Status Port Bits (base+1)

| Bit | Name | Description |
|-----|------|-------------|
| 7 | BUSY | Inverted; 0=HDAE5000 busy, 1=ready |
| 6 | ACK | Acknowledge signal |
| 4 | SELECT | HDAE5000 online indicator |
| 3 | ERROR | Error condition |

**Note:** Bit 7 (BUSY) is inverted in hardware by the PC parallel port. The ppkn50.dll XORs with 0x80 after reading to compensate.

### Control Port Bits (base+2)

| Bit | Name | Description |
|-----|------|-------------|
| 3 | SELECT_IN | Select printer |
| 2 | INIT | Initialize/reset |
| 1 | AUTOFEED | Strobe acknowledge |
| 0 | STROBE | Data strobe signal |

### Byte Transfer Handshaking

**Send Byte to HDAE5000:**

```
PC                          HDAE5000
 |                              |
 |-- Write Data to Data Port -->|
 |-- Assert Strobe (bit 1) ---->|
 |                              |
 |<---- BUSY goes LOW ----------|  (data received)
 |                              |
 |-- Deassert Strobe ---------->|
 |                              |
 |<---- BUSY goes HIGH ---------|  (ready for next)
```

**Receive Byte from HDAE5000:**

```
PC                          HDAE5000
 |                              |
 |<---- BUSY goes LOW ----------|  (data available)
 |                              |
 |-- Read Data from Data Port --|
 |-- Assert ACK (bit 1) ------->|
 |                              |
 |<---- BUSY goes HIGH ---------|  (acknowledged)
 |                              |
 |-- Deassert ACK ------------->|
```

### Timeout Values

- **Byte transfer timeout**: 10,000ms (0x2710)
- **Polling iterations**: 512 before time check
- **Connection test retries**: 5 times with 1000ms delay

### Error Codes (from ppkn50.dll)

| Code | Meaning |
|------|---------|
| 0 | Success |
| -1 | DLL not initialized |
| -2 | Port not open / connection failed |
| -3 | Handshake timeout |
| -4 | Transfer error |
| -5 | Port busy |
| -10 | Escape pressed |
| -20 | Invalid port number |

### DLL Exported Functions

The ppkn50.dll exports these functions for PC applications:

| Function | Command | Description |
|----------|---------|-------------|
| `InitializeTheDllPP50` | - | Initialize DLL |
| `OpenThePortNumberPP50` | - | Select LPT port (1-3) |
| `CloseThePortPP50` | - | Close parallel port |
| `TestTheKNPPPP50` | 0x01 | Test connection |
| `ReadFsbFromKnHdToKnMemPP50` | 0x03 | Read FSB from HD |
| `SendFsbFromKnMemToPCPP50` | 0x04 | Transfer FSB to PC |
| `SendFsbFromPCToKnMemPP50` | 0x05 | Transfer FSB to KN |
| `LoadFileFromKnHdToKnMemPP50` | 0x07 | Load file HD→KN |
| `DeleteFileOnKnHdPP50` | 0x16 | Delete file |
| `FormatTheKn50HardDiskPP50` | 0x17 | Format HD |
| `TurnOffTheKn50HdMotorPP50` | 0x18 | Spin down motor |

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

1. **Direct ATA Register Mapping**: ATA registers at 0x130010-0x130020
   - Data register (16-bit): 0x130010
   - Command block registers (8-bit): 0x130012-0x13001E
   - Device Control (8-bit): 0x130020
2. **PPI Emulation**: Full 8255 PPI at 0x160000 for PC communication (not for IDE)
3. **IDE Drive Model**: CHS-addressed IDE drive simulation
4. **Status Bits**: Proper BSY/DRDY/DRQ/ERR flag handling
5. **PIO Mode**: All transfers are PIO (no DMA observed)
6. **Custom Filesystem**: FSB/FGB/FEB structure parsing

## Verified Implementation Details

The following details were confirmed through firmware analysis:

- **Base Address**: ATA registers start at 0x130010, not 0x130000
- **Transfer Mode**: All data transfers use PIO mode via 16-bit Data register
- **Sector Size**: 512 bytes (256 word transfers)
- **Addressing**: CHS mode only (no LBA observed)
- **Timeout**: Drive ready timeout uses 0x3FFFFF (~4M) iteration loop
- **Status Polling**: Firmware polls Status register in tight loops (no interrupts)

## Further Research

Areas requiring additional investigation:
- Filesystem structure details (FSB/FGB/FEB layout)
- Error recovery procedures
- Exact timing requirements for real hardware

**Completed:**
- PC parallel port protocol details (documented above from ppkn50.dll analysis)

## Related Documentation

- [HDAE5000 Overview]({{ site.baseurl }}/hdae5000/) - Firmware and initialization
- [Memory Map]({{ site.baseurl }}/memory-map/) - Address space layout
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - System overview

## References

- ATA/ATAPI-4 Specification (T13/1153D)
- Intel 8255A PPI Datasheet
- HDAE5000 ROM disassembly analysis
- ppkn50.dll disassembly (HD-TechManager5000 parallel port DLL)
