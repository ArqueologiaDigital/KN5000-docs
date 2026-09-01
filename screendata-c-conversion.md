---
layout: page
title: "ScreenData C Conversion"
permalink: /screendata-c-conversion/
---

## Overview

The KN5000 uses a bytecode format (ScreenData) to describe screen layouts. We have converted all identified ScreenData blocks to typed C struct source files for readability and maintainability.

## What is ScreenData?

Packed binary commands with opcodes: 0x01 HLINE, 0x02 WIDGET/VLINE, 0x05 SELECT_RECT, 0x06 LABELED_REF, 0x07 SHORT_REF, 0x08 MESSAGE, 0x09 RECT, 0x0A FILLED_RECT, 0x17 PARAM_LABEL, 0x1B BOUNDARY, 0x1C FIELD_LABEL, 0x20 STRING. Rendered by `GraphicsRender_Start` / `GraphicsRender_TwoTable`. SETUP/CTRL blocks define cursor navigation and value display tables.

## Coverage — Complete Inventory

Three subsystems use ScreenData bytecodes. All blocks have been identified and converted.

### Subsystem 1: Style UI (16 files, authoritative)

Already integrated into the build as `.incbin` directives in `style_ui_params.s`. C source is compiled to binary and included in the ROM.

| File | Size | Description |
|------|------|-------------|
| style_ui/main.c | 3,531 bytes | Main screen layout (~200 commands) |
| style_ui/meascursor.c | 184 bytes | Measure cursor overlay |
| style_ui/yesctl.c | 228 bytes | Yes/No confirmation dialog |
| style_ui/ctlonly.c | 551 bytes | Control-only variant |
| style_ui/paramblock/*.c (12 files) | 39–250 bytes each | Parameter display blocks |

The scoop display subsystem (`scoop_display.s`) loads XIY/XIX pointers into these blocks at various sub-offsets (~40 distinct entry points). It does not have its own ScreenData — it reuses Style UI data.

### Subsystem 2: Sound Editor (23 files, documentation)

Located in `maincpu/audio/sound_editor_screens/`. The original data remains as inline `.byte` in `sound_editor_ui.s`.

| File | Size | Commands | Description |
|------|------|----------|-------------|
| se_drumkit_display.c | 293 bytes | 27 | Drum kit variant selection |
| se_general_edit.c | 96 bytes | 7 | General parameter edit |
| se_compare_screen.c | 139 bytes | 13 | Compare/apply screen |
| se_name_editor.c | 218 bytes | 18 | Sound name editor |
| se_parameter_grid.c | 221 bytes | 18 | Parameter grid display |
| se_transport_display.c | 141 bytes | 10 | Transport controls |
| se_apply_confirm.c | 55 bytes | 5 | Apply confirmation |
| se_setup_params_full.c | 471 bytes | 52 | Full parameter setup |
| se_setup_nav_full.c | 293 bytes | 35 | Navigation setup |
| se_setup_editor_full.c | 266 bytes | 28 | Editor setup |
| se_setup_waveform.c | 206 bytes | 22 | Waveform selection |
| se_setup_rhythm.c | 191 bytes | 23 | Rhythm setup |
| se_setup_ctrl_full.c | 167 bytes | 21 | Controller setup |
| se_setup_ctrl_list.c | 130 bytes | 14 | Controller list |
| se_setup_transport.c | 107 bytes | 11 | Transport setup |
| se_setup_env.c | 107 bytes | 13 | Envelope setup |
| se_setup_labels.c | 47 bytes | 5 | Label definitions |
| se_setup_sel_rects.c | 30 bytes | 3 | Selection rectangles |
| se_setup_sel{1-4}.c | 10–30 bytes | 1–2 | Selection rect entries |
| se_rhythm_transport_tables.c | 220 bytes | 16 | Rhythm/drum-sound transport, with 2 dispatch tables |

### Subsystem 3: Accompaniment Engine (3 files, documentation)

Located in `maincpu/sequencer/accomp_screens/`. The original data remains as inline `.byte` in `accompaniment_engine.s`.

| File | Size | Commands | Description |
|------|------|----------|-------------|
| accomp_section_widget.c | 15 bytes | 1 | Section selector widget |
| accomp_part_widget.c | 15 bytes | 1 | Part selector widget |
| accomp_display_full.c | 287 bytes | 14 | Full accompaniment display |

### Totals

| Subsystem | Files | Bytes | Status |
|-----------|-------|-------|--------|
| Style UI | 16 | ~6,193 | Build-integrated (authoritative) |
| Sound Editor | 23 | 3,458 | Typed documentation |
| Accompaniment | 3 | 317 | Typed documentation |
| **Total** | **42** | **~9,968** | 26 files verified 100% byte-match |

### NOT in scope: NAKA Widget Tables

~74 screen definitions using a completely different format (hierarchical `.long` pointer chains). Separate rendering pipeline — future project.

## Tooling

- `screendata_parser.py` — Generic ScreenData bytecode parser + C code generator library. Supports 16 opcodes with automatic SD_PTR detection for self-referential WIDGET handlers.
- `generate_all_screendata.py` — Batch generator for all non-Style-UI blocks (25 files). Includes compilation and ROM byte-match verification.
- `generate_screendata_main_c.py` — Style UI main block generator with typed setup/control fields.

### Conversion Pipeline

1. `screendata_parser.py` reads ROM binary and parses ScreenData bytecodes
2. Generator scripts produce typed C struct source files
3. Self-referential handler addresses use `SD_PTR(field)` macro
4. `clang -target tlcs900 -ffreestanding -c -O2` compiles C to object
5. `llvm-objcopy -O binary -j .text` extracts raw binary
6. Verified by byte comparison against original ROM (100% match required)

## Build Integration Status

**Style UI:** Fully integrated. C files are compiled and included via `.incbin` in `style_ui_params.s`.

**Sound Editor:** Partially integrated. Two blocks with dispatch tables have been absorbed into C:
- `se_drumkit_display.c` (329 bytes) — includes DrumKit_VariantSelect_Table (9 entries)
- `se_rhythm_transport_tables.c` (220 bytes) — includes RhythmTransport_Control_Table (6 entries) and DrumSound_ParamEdit_Table (10 entries), both with self-referencing entries

The remaining 20 Sound Editor files are documentation-only (no dispatch tables to absorb).

**Accompaniment:** Fully integrated. The 2,096-byte data block in `accompaniment_engine.s` has been split into 7 segments with 3 `.incbin` directives for the ScreenData blocks (`accomp_section_widget.c`, `accomp_part_widget.c`, `accomp_display_full.c`).

All integrated blocks load data by raw immediate address (`ld xiy, 0xF6AD37`), not by label — binary position must remain exact, which byte-matching guarantees.
