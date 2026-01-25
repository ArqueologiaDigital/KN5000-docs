---
layout: page
title: Reverse Engineering
permalink: /reverse-engineering/
---

# Reverse Engineering Strategies

Documented approaches for understanding undocumented aspects of the KN5000 system.

## HDAE5000 Hard Disk Expansion

The HD-AE5000 is an optional hard disk expansion that provides 1.08GB storage for music files. Reverse engineering it requires understanding multiple layers.

### PPI Interface (0x160000)

The main CPU communicates with the HDAE5000 via an 8255 PPI (Programmable Peripheral Interface).

**Tasks:**
1. Document Port A/B/C assignments and control register settings
2. Trace all main CPU firmware accesses to `0x160000`
3. Identify command/response protocol

### HDAE5000 ROM (0x280000)

A 512KB ROM contains the HDAE5000 firmware.

**Tasks:**
1. Disassemble the ROM (determine CPU type first)
2. Identify command handlers and filesystem routines
3. Document the command set

### Filesystem Structure

The 1.08GB hard disk uses a custom or standard filesystem.

**Tasks:**
1. Analyze directory structure and file allocation
2. Document how Flash-ROM/SRAM provides quick directory access
3. Compare with standard FAT if applicable

### Parallel Port Protocol

The HD-TechManager5000 PC software communicates via parallel port.

**Tasks:**
1. Capture and analyze parallel port traffic
2. Document handshaking, command format, file transfer protocol
3. Reverse engineer the Windows software (available at [archive.org](https://archive.org/details/technics-kn5000-system-update-disks))

### Interface Cable Pinout

**Tasks:**
1. Identify connector types from service manual
2. Document signal assignments (accent data/control/bus/power)
3. Verify voltage levels

---

## Sub CPU Payload Loading

The main CPU (TMP94C241F) loads a 192KB executable payload to the sub CPU (IC27) at boot time using MicroDMA.

### MicroDMA Mechanism

The TMP94C241F has a built-in MicroDMA controller for high-speed transfers.

**Key Registers:**
- `DMAS` - DMA Source address
- `DMAD` - DMA Destination address
- `DMAC` - DMA Count (transfer size)
- `DMAM` - DMA Mode (transfer settings)

**Tasks:**
1. Document MicroDMA register addresses and bit definitions from TMP94C241F datasheet
2. Identify which DMA channel is used for sub CPU transfer
3. Find initialization code in main CPU firmware

### Inter-CPU Communication (0x120000)

The main and sub CPUs communicate via latches at `0x120000`.

**Tasks:**
1. Document latch register layout (command, status, data bytes)
2. Identify handshaking signals
3. Trace how main CPU signals "payload ready"
4. Trace how sub CPU acknowledges receipt

### Boot Sequence

**Expected flow:**
1. Main CPU initializes after reset
2. Sub CPU held in reset (or waiting)
3. Main CPU configures DMA: source = payload in ROM, dest = sub CPU memory
4. DMA transfer executes (192KB)
5. Main CPU signals transfer complete via latch
6. Sub CPU boot ROM jumps to payload entry point
7. Sub CPU signals ready to main CPU

**Tasks:**
1. Trace complete boot sequence in main CPU firmware
2. Identify sub CPU type (IC27) from service manual
3. Document sub CPU memory map
4. Analyze 192KB payload structure (entry point, vectors, segments)

### Payload Structure

The sub CPU payload (`subcpu/kn5000_subprogram_v142.asm`) is 192KB.

**Layout to document:**
- Entry point address
- Interrupt vector table
- Code segments
- Data segments
- Embedded wavetables or lookup data
- Relationship to 128KB boot ROM

---

## Embedded Images

The ROMs contain icons, UI elements, and splash screens for the LCD display.

### Image Locations

**Main CPU ROM:**
- 1-bit status bitmaps (Please Wait, Completed, etc.)
- UI elements (drawbar sliders, icons)
- Various graphics referenced by display routines

**Table Data ROM:**
- Feature demo BMP images (FTBMP01-06)
- Additional UI assets

### Image Format

The LCD controller is IC206 (MN89304) with 4Mbit Video RAM (IC207).

**Format characteristics to document:**
- Pixel depth (1bpp, 4bpp, 8bpp, or RGB)
- Dimension encoding
- Palette format (if indexed color)
- Compression (if any)
- Header structure

### Extraction Workflow

1. **Scan ROMs** for image signatures (BMP headers: `0x42 0x4D`)
2. **Trace display code** to find image address references
3. **Extract to binary files** in `maincpu/images/` and `table_data/images/`
4. **Name descriptively** based on apparent purpose
5. **Update assembly sources** with `incbin` directives
6. **Verify byte-match** after rebuild

### Current Progress

**Already extracted:**
- `maincpu/images/` - 18+ files (1-bit bitmaps, UI elements)
- `table_data/images/` - 6 BMP files (feature demo screens)

**Tools:**
- `extract_include_binaries.py` - Extraction script

### Conversion for Documentation

For website documentation, images can be converted to PNG format for viewing. This helps identify what each image represents and aids in understanding the UI.

---

## References

- [Service Manual PDF]({{ site.baseurl }}/service_manual/technics_sx-kn5000.pdf)
- [System Update Disks Archive](https://archive.org/details/technics-kn5000-system-update-disks)
- [HDAE5000 Technical Info](https://www.keysoftservice.ch/hdae5000-e.htm)
