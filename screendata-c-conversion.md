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

## Remaining Work

### Sound Editor UI (audio/sound_editor_ui.s)

- 30 screen data pairs (55 unique addresses)
- ~14 KB of data across addresses 0xF12B86-0xF163E1
- Inline .byte data interleaved with code
- Includes: DrumKit screens, WaveformSelect, RhythmTransport, etc.

### Accompaniment Engine (sequencer/accompaniment_engine.s)

- 1 screen data pair (~200 bytes)
- Addresses 0xF6AD37-0xF6AD67

### NOT in scope: NAKA Widget Tables

~74 screen definitions using a completely different format (hierarchical .long pointer chains). Separate rendering pipeline - future project.

## Conversion Pipeline

1. Python generator reads ROM binary at known offset
2. Parses ScreenData bytecodes into typed structs (screendata_types.h)
3. Emits C source with packed struct initializers
4. Self-referential handler addresses use SD_PTR(field) macro
5. clang compiles C to object, llvm-objcopy extracts .text section
6. Assembly .incbin includes the compiled binary
7. Verified by compare_roms.py (100% byte match required)

## Phase Plan

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Accompaniment engine (1 pair, ~200 bytes) | Not started |
| 2 | Sound editor inventory & tooling generalization | Not started |
| 3 | Sound editor extraction & conversion (~30 pairs) | Not started |
| 4 | Symbolic SD_PTR cross-references | Not started |
| 5 | Final verification & cleanup | Not started |
