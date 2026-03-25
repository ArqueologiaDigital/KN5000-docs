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

The v10 version adds **14 bytes** of net code growth. Because both source trees use symbolic label references for function calls and data pointers, this address shift is invisible in the source diff — the linker resolves all labels automatically.

### 2. Updated HDAE5000 Extension Data Handler

The `HdaeRom_DataHandler` and `HdaeRom_DataDispatch` routines — which manage communication with the optional HD-AE5000 hard disk expansion board — were revised. The dispatch table was restructured and the block transfer protocol adjusted. These changes are directly adjacent to the SendPartDataBlock rewrite.

### 3. Flash Memory Save/Restore Adjustments

The `TmFlash_WriteRoutine` and `PostTmSave`/`PostTmLoad` functions received minor adjustments to their internal branch targets and parameter passing, likely to accommodate the SendPartDataBlock restructuring.

### 4. Debug Utility Code Changes

The `Debug_UartHelpers` and `ROM_PaddingFF` routines at the very end of the ROM (just before the interrupt vector table) contain different code between versions. The debug UART serial output helpers were adjusted — possibly reflecting changes to the debug console protocol or baud rate configuration.

### 5. Version Byte

The firmware version identifier at address `0xFFFFE8` changed from `0x09` (v9) to `0x0A` (v10). This byte is read by `Get_Firmware_Version` and displayed on the splash screen.

### 6. Widget Data Correction

One NAKA widget descriptor field changed: `naka_style_bitmaps.c` field `field_0772` went from `0x0549` to `0x054A` — a single-bit correction in a style bitmap display parameter.

## What Did NOT Change

- **Boot sequence**: Identical initialization, self-test, and hardware setup.
- **UI framework**: All NAKA widget descriptors, screen layouts, and event handlers are identical (except the one bitmap field above).
- **MIDI subsystem**: Core MIDI dispatch, SysEx handling, and serial I/O are unchanged.
- **Sequencer engine**: Song playback, SMF processing, and accompaniment are the same.
- **Display/VGA subsystem**: Graphics primitives, text rendering, and scoop display code are unchanged.
- **Floppy disk controller**: FDC routines are identical.
- **SubCPU boot ROM**: Same across all firmware versions.
- **Table Data ROM**: Same across all firmware versions.

---

## Detailed Change Report

### Files Modified

10 source files differ between v9 and v10. Both versions use fully disassembled native instructions (no raw `.byte` code blocks), symbolic label references for `call`/`jp`/`lda_24`, parenthesized direct address operands, and normalized lowercase hex — so the diff shows only genuine firmware changes. The diff has been systematically minimized from 5,388 lines (initial raw comparison) to just **106 lines** across 10 files.

| Category | Files | Changed Lines | Description |
|----------|-------|--------------|-------------|
| SendPartDataBlock / HDAE rewrite | 1 | ~30 | Core protocol change (instruction-level diff) |
| Symbolic pointer fixes | 3 | ~10 | `.long (label + 14)` → `.long label` (offset eliminated) |
| Other genuine changes | 6 | ~11 | Version byte, widget data, padding, label resolution, byte opcode |
| **Total** | **10** | **+28/−23** | **106 lines total diff** |

*Note: `call`, `jp`, and `lda_24` instructions use symbolic labels in both v9 and v10 source, so the 14-byte address shift is invisible in the diff. The remaining `.long (label + N)` offsets have been resolved to direct `.long label` references by adjusting label placement to point to the correct v10 addresses.*

### Genuine Code Changes

#### `audio/note_voice_mapping.s` — SubCPU Data Transfer Rewrite

This is the dominant change. The `SendPartDataBlock` region (addresses `0xFEF99E`–`0xFF04F8`) was substantially rewritten between v9 and v10. Both versions are fully disassembled to native instructions, so the diff shows the actual instruction-level differences.

**Functions affected:**

| Function | v9 Size | v10 Size | Change |
|----------|---------|----------|--------|
| `SendPartDataBlock_DoGetError` | 11 bytes | 22 bytes | Expanded error checking |
| `SendPartDataBlock_Data` | 1,612 bytes | 1,612 bytes | Restructured field copy |
| `SendPartDataBlock_Data2`–`Data5` | ~280 bytes | ~290 bytes | Parameter tables updated |
| `SendPartDataBlock_InitVal4`–`InitVal9` | ~180 bytes | ~180 bytes | Minor adjustments |
| `HdaeRom_DataHandler` | 34 bytes | 34 bytes | Protocol changes |
| `HdaeRom_DataDispatch` | 470 bytes | 480 bytes | Dispatch table restructured |
| `HdaeRom_AltHandler/AltDispatch` | ~90 bytes | ~90 bytes | Adjusted |
| `PostTmLoad`/`PostTmSave` | ~80 bytes | ~80 bytes | Adjusted |
| **Total region** | **2,906 bytes** | **2,920 bytes** | **+14 bytes** |

In v10, the `SendPartDataBlock_Data` function was restructured from a compact loop-based approach to explicit per-field memory copies. This may reflect a bug fix or compatibility improvement in how voice parameters are transferred to the SubCPU's tone generator registers.

Also in this file: `TmFlashWrite_Block1` and `TmFlash_WriteRoutine` had relative branch displacements adjusted, and several instruction operands updated to reflect the new layout of the SendPartDataBlock region.

#### `audio/sprintf_core.s` — Fill Padding Adjustment

The fill padding between the sprintf code block and the interrupt vector table changed from 12,710 bytes (v9) to 12,696 bytes (v10), absorbing the 14-byte code growth.

#### `boot/rom_end_structure.s` — Version Byte

The firmware version byte at `0xFFFFE8` changed from `0x09` to `0x0A`.

#### `audio/sound_editor_ui.s` — Symbolic Label Resolution

A raw address literal `0xff182c` was resolved to its symbolic label `Sprintf_Octal_ZeroFill_0x7`. This is a genuine address difference caused by the 14-byte shift — the v10 label points to the correct location.

#### `ui_widgets/naka_style_bitmaps.c` — Widget Data Correction

Field `field_0772` changed from `0x0549` to `0x054A` — a minor data correction in a style bitmap widget descriptor.

### Remaining Symbolic Pointer Adjustments (4 files)

Most address-bearing `.long` references have been resolved to direct symbolic labels, eliminating the `+ 14` offsets that previously appeared throughout the diff. The remaining differences in pointer-bearing files are:

| File | Hunks | Description |
|------|-------|-------------|
| `sequencer/smf_event_processor.s` | 1 | `.long (Sprintf_FillToVectors + 14)` → `.long Sprintf_FillToVectors` |
| `storage/flash_floppy_handlers.s` | 2 | `.long (TmFlashWrite_Block2/3 + 14)` → `.long TmFlashWrite_Block2/3` |
| `ui_widgets/widget_dispatch.s` | 4 | `.long (SendPartDataBlock_Data2/3 + 11)` → `.long SendPartDataBlock_Data2/3` |
| `demo/file_demo_proc.s` | 1 | Single `.byte` opcode change |

These represent genuine firmware differences — the v10 label positions were adjusted so the labels point directly to the correct addresses without offset arithmetic.

### Binary Layout: How 14 Bytes Propagate

```
v9 ROM Layout:
  0xE00000 ─────────────────────── 0xFEF99E ──────── 0xFF04F2 ──── 0xFFFFFF
  │ Identical code               │ SendPartData    │ Post-region │
  │                               │ (2,906 bytes)   │ code        │

v10 ROM Layout:
  0xE00000 ─────────────────────── 0xFEF99E ──────── 0xFF0506 ──── 0xFFFFFF
  │ Identical code               │ SendPartData    │ Post-region │
  │                               │ (2,920 bytes)   │ code        │
  │                               │ [+14 bytes]     │ [shifted]   │

Source-level impact (after systematic diff minimization):
  1. SendPartData / HDAE rewrite            →  ~30 lines (genuine code changes)
  2. call/jp/lda_24 to symbolic labels      →  invisible (linker resolves)
  3. .long pointer offset elimination       →  ~10 lines (4 files, +14/+11 offsets removed)
  4. Fill padding adjustment               →  1 line (12,710 → 12,696)
  5. Version byte + comment                →  2 lines (0x09 → 0x0A)
  6. Widget data correction                →  1 line
  7. Symbolic label resolution              →  1 line (sound_editor_ui.s)
  8. Byte opcode differences               →  ~3 lines
                                              ────────────────────
                               Source diff:   +28 / −23 lines (106 total)
                               Binary diff:   13,517 bytes (0.64%)

  Diff reduction history:
    Initial raw comparison:                5,388 lines
    After symbolic call/jp/lda_24:         ~300 lines
    After pointer offset elimination:        231 lines
    After parenthesized direct addr:        106 lines (current)
```

### Interpretation

The v9→v10 update appears to be a **targeted bug fix or protocol improvement** in the SubCPU voice parameter transfer system. The rewrite of `SendPartDataBlock_Data` from a loop-based to an explicit-copy approach suggests one of:

1. **A timing-sensitive bug fix** — the loop-based approach in v9 may have caused race conditions with the SubCPU's tone generator during rapid voice changes.
2. **A parameter format change** — v10 may transfer additional fields or handle edge cases differently.
3. **A compatibility fix** — the HDAE5000 extension data handler was also restructured, suggesting the fix relates to save/restore operations with the hard disk expansion.

The conservative nature of the change (only touching one subsystem, with 99.36% of the ROM identical) is consistent with a late-stage maintenance release fixing a specific customer-reported issue.
