---
layout: page
title: ROM Reconstruction
permalink: /rom-reconstruction/
---

# ROM Reconstruction

Goal: Rebuild all firmware ROMs from disassembled source with 100% byte accuracy.

## Firmware Version History

Official firmware updates were distributed on floppy disk. All versions are archived at [archive.org](https://archive.org/details/technics-kn5000-system-update-disks).

### Main Board Firmware

| Version | Release Date | Notes |
|---------|--------------|-------|
| v5 | 1997-11-12 | Earliest available |
| v6 | 1998-01-16 | |
| v7 | 1998-06-26 | |
| v8 | 1998-11-13 | |
| v9 | 1999-01-26 | |
| **v10** | 1999-08-02 | **Current disassembly target** |

### HD-AE5000 Firmware

| Version | Release Date | Notes |
|---------|--------------|-------|
| v1.10i | 1998-07-06 | Initial release |
| v1.15i | 1998-10-13 | |
| v2.0i | 1999-01-15 | Added lyrics display |

## Current Status

| ROM | Size | Match % | Bytes Off | Source File |
|-----|------|---------|-----------|-------------|
| Main CPU | 2MB | 99.99% | 177 | `maincpu/kn5000_v10_program.asm` |
| Sub CPU Payload | 192KB | **100%** | 0 | `subcpu/kn5000_subprogram_v142.asm` |
| Sub CPU Boot | 128KB | 98.48% | 1,981 | `subcpu_boot/kn5000_subcpu_boot.asm` |
| Table Data | 2MB | 32.42% | 1,417,294 | `table_data/kn5000_table_data.asm` |
| Custom Data | 1MB | - | - | No source yet |
| HDAE5000 (HD Expansion) | 512KB | - | - | No source yet |

## Assembler

The project uses **ASL (Alfred Arnold's Macro Assembler)** version 1.42 Beta.

**Challenge**: ASL only supports TMP96C141, not TMP94C241F. Unsupported instructions are handled via macros in `tmp94c241.inc` that emit raw byte sequences.

## Known Divergences

### Main CPU (177 bytes)

*Analysis in progress - divergent byte offsets being cataloged.*

Two color palettes have been extracted as binary includes:
- **Palette 1** at 0xEB37DE - first palette (inline in sequential section)
- **Palette 2** at 0xEEFAF0 - second palette (`Palette_8bit_RGBA_2.bin`)

### Sub CPU Boot (1,981 bytes)

The Sub CPU boot ROM is now buildable and at 98.48% match. Recent progress includes:

**Routines discovered and added:**
- `SUB_8437` (0xFF8437) - Tone generator initialization loop
- `SUB_850E` (0xFF850E) - Multi-register push/call wrapper
- `SUB_853A` (0xFF853A) - Write register pairs to tone generator
- `COPY_WORDS` (0xFF858B) - Word block copy using `ldirw`
- `FILL_WORDS` (0xFF8594) - Memory fill with word values
- `CHECKSUM_CALC` (0xFF859B) - Calculate checksum over memory range
- Stub routines at 0xFF8496-0xFF85AB returning 0 in HL

**Encoding fixes applied:**
- `jrl T` (3-byte relative long jump) vs `jp` (4-byte absolute)
- `ldir` encoding: TMP94C241 uses `83 11`, ASL generates `85 11`
- `ld D, imm8` encoding: TMP94C241 uses `24 nn`, ASL generates different encoding
- `ld A, imm8` encoding: TMP94C241 uses `21 nn`

**Remaining divergences** (~850 bytes from 0xFF8604-0xFF8955) include DMA transfer routines and inter-CPU communication handlers that need to be disassembled.

### Table Data (67.58% incorrect)

This ROM contains mostly binary data (images, sound samples, lookup tables). The divergences are likely due to:
- Missing or incorrect binary includes
- Endianness issues in data definitions

## Technical Notes

### TMP94C241F vs TMP96C141

Instructions unique to TMP94C241F that require macro workarounds:
- Memory-to-memory `LD` (not supported by TLCS-900)
- Certain shift/rotate variants
- Some MUL/DIV variants
- LDI, LDIR, LDD, LDDR block transfer instructions
- DMA control register access (`LDC` with DMAS/DMAD/DMAC/DMAM registers)

### ASL Macro Workarounds (tmp94c241.inc)

The `tmp94c241.inc` file contains macros that emit raw byte sequences for unsupported instructions.

**DMA Register Macros:**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `LDC_DMAS0_XWA` | `e8 2e 00` | Load DMA source 0 from XWA |
| `LDC_DMAD0_XWA` | `e8 2e 20` | Load DMA destination 0 from XWA |
| `LDC_DMAD0_XBC` | `e9 2e 20` | Load DMA destination 0 from XBC |
| `LDC_DMAD2_XWA` | `e8 2e 28` | Load DMA destination 2 from XWA |
| `LDC_DMAC0_WA` | `d8 2e 40` | Load DMA count 0 from WA |
| `LDC_DMAC0_A` | `c9 2e 42` | Load DMA count 0 from A |
| `LDC_DMAC2_A` | `c9 2e 4a` | Load DMA count 2 from A |

**Additional Sub CPU Boot ROM Macros:**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `INC_0_XBC` | `e9 60` | Increment XBC by 1 |
| `PUSH_WORD value` | `0b LL HH` | Push 16-bit immediate |
| `CP_pXWA_WORD value` | `90 3f LL HH` | Compare (XWA) with 16-bit immediate |
| `CP_pXBC_d_WORD d,val` | `99 dd 3f LL HH` | Compare (XBC+d) with 16-bit immediate |
| `LDA_XWA_IMM24 value` | `f2 LL MM HH 30` | Load 24-bit address into XWA |
| `CALR target` | `1e LL HH` | Call relative (3-byte encoding) |
| `CALL_ABS24 target` | `1d LL MM HH` | Call absolute with 24-bit address |
| `JRL_T target` | `78 LL HH` | Jump relative long (always true) |
| `LDIR_94` | `83 11` | Block copy (TMP94C241 encoding) |
| `LD_A value` | `21 nn` | Load immediate to A register |
| `LD_D value` | `24 nn` | Load immediate to D register |

### Encoding Differences

ASL sometimes chooses different (but functionally equivalent) encodings than the original ROM:

| Instruction | Original | ASL Default | Notes |
|-------------|----------|-------------|-------|
| `lda XWA, imm16` | 5-byte (24-bit addr) | 4-byte (16-bit) | Use `LDA_XWA_IMM24` macro |
| `call addr` | 3-byte `calr` | 4-byte `call` | Use `CALR` macro when target is within range |
| `jp addr` | 3-byte `jrl T` | 4-byte `jp` | Use `JRL_T` macro for relative long jump |
| `ldir` | `83 11` | `85 11` | Use `LDIR_94` macro for TMP94C241 encoding |
| `ld A, imm8` | `21 nn` | Different | Use `LD_A` macro |
| `ld D, imm8` | `24 nn` | Different | Use `LD_D` macro |

These encoding differences cause byte mismatches even when the code is functionally correct.

### Build Process

```bash
cd kn5000-roms-disasm
make all              # Build all ROMs
python compare_roms.py # Verify against originals
```
