---
layout: page
title: "ScreenData C Conversion Plan"
permalink: /screendata-c-conversion/
---

## Overview

The KN5000 Style UI and other subsystems use a bytecode format (ScreenData) to describe screen layouts. We are converting all raw `.byte` assembly data to typed C struct source files for readability and maintainability.

## What is ScreenData?

Packed binary commands with opcodes: 0x01 HLINE, 0x02 WIDGET/VLINE, 0x06 LABELED_REF, 0x09 RECT, 0x0A FILLED_RECT, 0x20 STRING. Rendered by GraphicsRender_Start / GraphicsRender_TwoTable. SETUP/CTRL blocks define cursor navigation and value display tables.

## Already Converted (Style UI)

| File | Size | Description |
|------|------|-------------|
| style_ui/main.c | 3,531 bytes | Main screen layout (~200 commands) |
| style_ui/meascursor.c | 184 bytes | Measure cursor overlay |
| style_ui/yesctl.c | 228 bytes | Yes/No confirmation dialog |
| style_ui/ctlonly.c | 551 bytes | Control-only variant |
| style_ui/paramblock/*.c (12 files) | 39-250 bytes each | Parameter display blocks |

## Converted (Sound Editor + Accompaniment)

22 sound editor screen data files and 1 accompaniment engine file, totaling 3,515 bytes across 23 C source files. All verified 100% byte-match against the original ROM.

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
| se_setup_sel{1-4}.c | 10-30 bytes | 1-2 | Selection rect entries |
| accomp_display.c | 277 bytes | 13 | Accompaniment editor display |

### Remaining: Build Integration

These C files currently serve as typed documentation. The original data remains as inline `.byte` directives in `sound_editor_ui.s` and `accompaniment_engine.s`. Replacing the inline data with `.incbin` references (making C the authoritative source) requires handling label dependencies within the data blocks — labels referenced by surrounding code point into the middle of these data regions.

### NOT in scope: NAKA Widget Tables

~74 screen definitions using a completely different format (hierarchical .long pointer chains). Separate rendering pipeline — future project.

## Conversion Pipeline

1. `screendata_parser.py` reads ROM binary and parses ScreenData bytecodes
2. `generate_all_screendata.py` generates typed C struct source files for all known blocks
3. Self-referential handler addresses use `SD_PTR(field)` macro
4. `clang -target tlcs900` compiles C to object, `llvm-objcopy` extracts `.text` section
5. For Style UI: assembly `.incbin` includes the compiled binary (authoritative)
6. For sound editor/accompaniment: C files verified against ROM but not yet integrated into build
7. All verified by `compare_roms.py` (100% byte match required)

## Phase Plan

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Accompaniment engine (1 pair, 277 bytes) | **Done** |
| 2 | Sound editor inventory & tooling generalization | **Done** |
| 3 | Sound editor extraction & conversion (22 files, 3,238 bytes) | **Done** |
| 4 | Symbolic SD_PTR cross-references | Not started |
| 5 | Build integration (replace inline .byte with .incbin) | Not started |
