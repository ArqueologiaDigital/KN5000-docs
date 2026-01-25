---
layout: page
title: ROM Reconstruction
permalink: /rom-reconstruction/
---

# ROM Reconstruction

Goal: Rebuild all firmware ROMs from disassembled source with 100% byte accuracy.

## Current Status

| ROM | Size | Match % | Bytes Off | Source File |
|-----|------|---------|-----------|-------------|
| Main CPU | 2MB | 99.99% | 177 | `maincpu/kn5000_v10_program.asm` |
| Sub CPU Payload | 192KB | TBD | TBD | `subcpu/kn5000_subprogram_v142.asm` |
| Sub CPU Boot | 128KB | - | - | No source yet |
| Table Data | 2MB | 32.42% | 1,417,294 | `table_data/kn5000_table_data.asm` |
| Custom Data | 1MB | - | - | No source yet |
| HDAE5000 (HD Expansion) | 512KB | - | - | No source yet |

## Assembler

The project uses **ASL (Alfred Arnold's Macro Assembler)** version 1.42 Beta.

**Challenge**: ASL only supports TMP96C141, not TMP94C241F. Unsupported instructions are handled via macros in `tmp94c241.inc` that emit raw byte sequences.

## Known Divergences

### Main CPU (177 bytes)

*Analysis in progress - divergent byte offsets being cataloged.*

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

### Build Process

```bash
cd kn5000-roms-disasm
make all              # Build all ROMs
python compare_roms.py # Verify against originals
```
