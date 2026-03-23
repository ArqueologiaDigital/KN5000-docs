---
layout: page
title: "Firmware Changes: v9 vs v10"
permalink: /firmware-v9-vs-v10/
---

# Firmware Changes: Version 9 to Version 10

*Technics KN5000 Main CPU Program ROM — comparison of the last two firmware releases.*

**Version 9** was released January 26, 1999. **Version 10** (the final release) was released August 2, 1999.

Both ROMs are exactly 2 MB (2,097,152 bytes). Of those, **13,517 bytes differ** (0.64%). The changes are concentrated in a single subsystem: the **SubCPU data transfer and HDAE5000 extension handler** routines.

## Summary of Key Changes

### 1. Rewritten SubCPU Data Block Transfer (SendPartDataBlock)

The largest change is a complete rewrite of the `SendPartDataBlock` family of functions in `audio/note_voice_mapping.s`. This code handles transferring voice parameter data blocks between the main CPU and the tone generator SubCPU.

- **v9:** 2,906 bytes — uses a compact loop-based approach with shared parameter load routines
- **v10:** 2,920 bytes — restructured with explicit per-field copy sequences and additional validation

The v10 version adds **14 bytes** of net code growth, which shifts all subsequent code addresses by +14. This single change accounts for the vast majority of the 13,517 byte differences: the remaining ~12,500 bytes are **pointer adjustments** cascading through the ROM to reflect the new addresses.

### 2. Updated HDAE5000 Extension Data Handler

The `HdaeRom_DataHandler` and `HdaeRom_DataDispatch` routines — which manage communication with the optional HD-AE5000 hard disk expansion board — were revised. The dispatch table was restructured and the block transfer protocol adjusted. These changes are directly adjacent to the SendPartDataBlock rewrite.

### 3. Flash Memory Save/Restore Adjustments

The `TmFlash_WriteRoutine` and `PostTmSave`/`PostTmLoad` functions received minor adjustments to their internal branch targets and parameter passing, likely to accommodate the SendPartDataBlock restructuring.

### 4. Debug Utility Code Relocation

The `Debug_UartHelpers` and `ROM_PaddingFF` routines at the very end of the ROM (just before the interrupt vector table) contain different code between versions. The debug UART serial output helpers were adjusted — possibly reflecting changes to the debug console protocol or baud rate configuration.

### 5. Version Byte

The firmware version identifier at address `0xFFFFE8` changed from `0x09` (v9) to `0x0A` (v10). This byte is read by `Get_Firmware_Version` and displayed on the splash screen.

### 6. Widget Data Correction

One NAKA widget descriptor field changed: `naka_style_bitmaps.c` field `field_0772` went from `0x0549` to `0x054A` — a single-bit correction in a style bitmap display parameter.

## What Did NOT Change

- **Boot sequence**: Identical initialization, self-test, and hardware setup.
- **UI framework**: All NAKA widget descriptors, screen layouts, and event handlers are identical (except the one bitmap field above).
- **MIDI subsystem**: Core MIDI dispatch, SysEx handling, and serial I/O are unchanged — only address operands were adjusted.
- **Sequencer engine**: Song playback, SMF processing, and accompaniment are the same.
- **Display/VGA subsystem**: Graphics primitives, text rendering, and scoop display code are unchanged.
- **Floppy disk controller**: FDC routines are identical.
- **SubCPU boot ROM**: Same across all firmware versions.
- **Table Data ROM**: Same across all firmware versions.

---

## Detailed Change Report

### Files Modified

37 source files differ between v9 and v10. Of these, only **4 files** contain genuine code/data changes. The remaining **33 files** contain only mechanical address operand adjustments caused by the 14-byte code growth.

| Category | Files | Changed Lines | Description |
|----------|-------|--------------|-------------|
| Genuine code changes | 4 | ~1,500 | Actual different code/data |
| Address adjustments | 33 | ~800 | Pointer operands shifted by ±14 |
| **Total** | **37** | **~2,300** | |

### Genuine Code Changes (4 files)

#### `audio/note_voice_mapping.s` — SubCPU Data Transfer Rewrite

This is the dominant change. The `SendPartDataBlock` region (addresses `0xFEF99E`–`0xFF04F8`) was substantially rewritten between v9 and v10.

**Functions affected:**

| Function | v9 Size | v10 Size | Change |
|----------|---------|----------|--------|
| `SendPartDataBlock_DoGetError` | 11 bytes | 22 bytes | Expanded error checking |
| `SendPartDataBlock_Data` | 1,612 bytes | 1,612 bytes | Restructured field copy |
| `SendPartDataBlock_Data2` through `Data5` | ~280 bytes | ~290 bytes | Parameter tables updated |
| `SendPartDataBlock_InitVal4`–`InitVal9` | ~180 bytes | ~180 bytes | Minor adjustments |
| `HdaeRom_DataHandler` | 34 bytes | 34 bytes | Protocol changes |
| `HdaeRom_DataDispatch` | 470 bytes | 480 bytes | Dispatch table restructured |
| `HdaeRom_AltHandler/AltDispatch` | ~90 bytes | ~90 bytes | Adjusted |
| `PostTmLoad`/`PostTmSave` | ~80 bytes | ~80 bytes | Adjusted |
| **Total region** | **2,906 bytes** | **2,920 bytes** | **+14 bytes** |

In v10, the `SendPartDataBlock_Data` function was restructured from a compact loop-based approach to explicit per-field memory copies. This may reflect a bug fix or compatibility improvement in how voice parameters are transferred to the SubCPU's tone generator registers.

Also in this file: `TmFlashWrite_Block1` and `TmFlash_WriteRoutine` had relative branch displacements adjusted by +3, and several instruction operands updated to reflect the new layout of the SendPartDataBlock region.

#### `audio/audio_cmd_encoder.s` — Fill Padding Adjustment

A single address operand (`lda_24`) was adjusted, and the fill padding between the AudioCmd code block and the end-of-ROM debug functions changed from 12,710 bytes (v9) to 12,696 bytes (v10), absorbing the 14-byte code growth.

#### `boot/rom_end_structure.s` — Version Byte

The firmware version byte at `0xFFFFE8` changed from `0x09` to `0x0A`.

#### `ui_widgets/naka_style_bitmaps.c` — Widget Data Correction

Field `field_0772` changed from `0x0549` to `0x054A` — a minor data correction in a style bitmap widget descriptor.

### Mechanical Address Adjustments (33 files)

Due to the 14-byte code growth in the SendPartDataBlock region, every function and data pointer referencing an address above `0xFF04F8` shifted by +14. Similarly, addresses pointing into the rewritten region shifted by +11 (reflecting the internal layout change).

These adjustments appear in:

- **`call`/`calr`/`jrl`/`jr` instructions** with raw numeric operands (380+ adjustments)
- **`.byte` data tables** containing 3-byte LE addresses (90+ adjustments)
- **`.long` pointer tables** referencing shifted symbols (6 adjustments using `(LABEL + offset)` syntax)
- **C linker script** symbol addresses (not directly visible in the diff — resolved at compile time)

**Subsystem breakdown of address adjustments:**

| Subsystem | Files | Adjustments | Description |
|-----------|-------|-------------|-------------|
| `ui/` | 7 | 138 | Drawbar panel, mode handlers, widget defs, window procs |
| `midi/` | 7 | 81 | Dispatch handlers, AC listeners, PCG, SysEx |
| `sequencer/` | 5 | 70 | Event playback, SMF processor, sequencer UI |
| `demo/` | 3 | 55 | Demo text, file demo proc |
| `display/` | 2 | 28 | Scoop display, graphics/text VGA |
| `audio/` | 5 | 15 | Control engine, sound editor, various |
| `storage/` | 1 | 14 | Flash/floppy handlers |
| `ui_widgets/` | 1 | 6 | Widget dispatch table |
| `factory_test/` | 1 | 2 | Test data |
| `file_io/` | 1 | 1 | Misc UI |
| `boot/` | 1 | 0 | (version byte only) |

### Data Flow: How 14 Bytes Cascade Through 13,517 Changes

The following diagram illustrates how a single 14-byte code addition creates thousands of byte differences:

```
v9 ROM Layout:
  0xE00000 ─────────────────────── 0xFEF99E ──────── 0xFF04F2 ──── 0xFFFFFF
  │ Identical code (15.6 MB)     │ SendPartData    │ Post-region │
  │                               │ (2,906 bytes)   │ code        │
  │                               │                 │             │

v10 ROM Layout:
  0xE00000 ─────────────────────── 0xFEF99E ──────── 0xFF0506 ──── 0xFFFFFF
  │ Identical code (15.6 MB)     │ SendPartData    │ Post-region │
  │                               │ (2,920 bytes)   │ code        │
  │                               │ [+14 bytes]     │ [shifted]   │

Cascade effect:
  1. SendPartData grows by 14 bytes          →  2,920 bytes genuine changes
  2. All addresses after 0xFF04F8 shift +14  →  ~380 call/jp operands
  3. Jump table entries shift +14            →  ~90 .byte address patterns
  4. Label references shift +14              →  ~6 .long adjustments
  5. Fill padding shrinks by 14              →  12,696 vs 12,710
  6. IVT/debug code stays at fixed end       →  Same addresses
                                                ────────────────────
                                        Total:  13,517 byte differences
```

### Interpretation

The v9→v10 update appears to be a **targeted bug fix or protocol improvement** in the SubCPU voice parameter transfer system. The rewrite of `SendPartDataBlock_Data` from a loop-based to an explicit-copy approach suggests one of:

1. **A timing-sensitive bug fix** — the loop-based approach in v9 may have caused race conditions with the SubCPU's tone generator during rapid voice changes.
2. **A parameter format change** — v10 may transfer additional fields or handle edge cases differently.
3. **A compatibility fix** — the HDAE5000 extension data handler was also restructured, suggesting the fix relates to save/restore operations with the hard disk expansion.

The conservative nature of the change (only touching one subsystem, with 99.36% of the ROM identical) is consistent with a late-stage maintenance release fixing a specific customer-reported issue.
