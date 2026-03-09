---
layout: page
title: "Dispatch Tables Inventory"
permalink: /dispatch-tables/
---

# Dispatch Tables Inventory

This page catalogs all indirect call/jump dispatch tables found in the KN5000 ROM disassembly. These are sites where firmware computes a target address at runtime using an index into a table of function pointers or offsets.

**Last updated:** March 9, 2026

## Summary

| Dispatch Type | Total Sites | Documented | Undocumented |
|---------------|-------------|------------|--------------|
| `call (xreg)` — indirect call through pointer table | 49 | 16 | 33 |
| `jp (xreg)` — indirect jump through pointer table | 18 | 10 | 8 |
| `jp_dri` — register-indexed jump via offset table | 317 | 8 | 309 |
| **Total** | **384** | **34** | **350** |

"Documented" means the dispatch site and/or its table have meaningful semantic labels. "Undocumented" means they still use auto-generated `LABEL_XXXXXX` names.

---

## Dispatch Patterns

The firmware uses three main patterns for runtime code dispatch:

### Pattern 1: Pointer Table via `call (xreg)` / `jp (xreg)`

```asm
ldda8 a, <state_var>      ; load index from DRAM
extz wa                    ; zero-extend to 16-bit
sla wa, 2                  ; multiply by 4 (pointer size)
lda_24 xbc, <table_base>  ; load table base address
ld_sril3 XHL, ...         ; indexed load: xhl = table[index]
call (xhl)                 ; dispatch to handler
```

Table contains `.long` entries pointing to handler functions. Entry size is 4 bytes (24-bit addresses stored in 32-bit slots).

### Pattern 2: Offset Table via `jp_dri`

```asm
cp wa, <max_index>         ; bounds check
jr gt, .default
add wa, wa                 ; multiply by 2 (offset size)
lda_24 xix, <offset_table> ; load offset table address
ld_sriw3 WA, ...          ; indexed load: wa = offsets[index]
lda_24 xix, <dispatch_base> ; load dispatch base address
jp_dri 8, ...              ; jump to base + offset
```

Table contains 16-bit relative offsets. More compact than pointer tables. Used extensively (317 sites).

### Pattern 3: Two-Level Dispatch

```asm
; Level 1: byte lookup
ld a, (xix + <byte_table>)  ; byte_table[index] → secondary index
extz wa
sll wa, ...
; Level 2: offset table
lda_24 xix, <offset_table>
jp_dri ...
```

6 sites use this cascaded pattern for more complex routing.

---

## Documented Dispatch Tables

These tables have meaningful semantic labels and are reasonably well understood.

### Main CPU — Sequencer & Timing

| # | Label | File | Line | Table Base | Index Source | Entries | Type |
|---|-------|------|------|-----------|-------------|---------|------|
| 1 | `SeqStep_TimerDispatchA` | seq_step_routines.s | 2516 | 0xE44F00 | DRAM[8956] | ~23 | jp (xhl) |
| 2 | `SeqStep_TimerDispatchB` | seq_step_routines.s | 2524 | 0xE44F5C | DRAM[8956] | ~23 | jp (xhl) |
| 3 | `SeqStep_TimerDispatchC` | seq_step_routines.s | 2532 | 0xE44FB8 | DRAM[8956] | ~23 | jp (xhl) |
| 4 | `AccPlayMode_Dispatch_Execute` | accompaniment_engine.s | 8061 | 0xF5ADF9 | flags in reg l | ~32 | call (xhl) |
| 5 | `AccFlags_Dispatch` | accompaniment_engine.s | 5356 | 0xF59517 | reg w & 0xF | ~16 | jp (xhl) |
| 6 | `DrumSlot_ClampAndLookup` | accompaniment_engine.s | 22127 | 0xF64D75 | reg hl | var | call (xhl) |
| 7 | `NoteEditSy_HandleUpScroll` | sequencer_engine.s | 22430 | 0xE44A6A | xde (<=0xE) | 15 | jp_dri |
| 8 | `NoteEditSy_HandleDownScroll` | sequencer_engine.s | 22491 | 0xE44A52 | xde (<=0xB) | 12 | jp_dri |
| 9 | `DspItem0_TypeChangeHandler` | sequencer_ui.s | 13583 | 0xE34D92 | xde (<=0x8) | 9 | jp_dri |

### Main CPU — UI & Control Panel

| # | Label | File | Line | Table Base | Index Source | Entries | Type |
|---|-------|------|------|-----------|-------------|---------|------|
| 10 | `UI_STATE_2_SUBSTATE` | style_data_init.s | 561 | 0xEF0DA5 | DRAM[1042] & 0xF | ~16 | jp (xhl) |
| 11 | `CtrlPanel_DispatchByIndex` | tonegen_voice_ctrl.s | 4113 | 0xEA9A04 | wa (<=0x2A) | 43 | jp_dri |
| 12 | `CPanel_EncoderDispatch` | midi_encoder_routines.s | 33 | 0xEDA0BC | 5-bit idx | ~32 | jp (xhl) |
| 13 | `Scoop_EventLoop_12Entry` | scoop_display.s | 9770 | (stack) | reg c | ~12 | call (xhl) |

### Main CPU — MIDI & Sound

| # | Label | File | Line | Table Base | Index Source | Entries | Type |
|---|-------|------|------|-----------|-------------|---------|------|
| 14 | `MIDI_CHANNEL_MESSAGE_DISPATCHER` | midi_serial_routines.s | 690 | 0xFCF761 | DRAM[1059] & 0x70 | 8 | jp (xhl) |
| 15 | `PanelEvent_DispatchByIndex` | midi_voice_routing.s | 847 | (computed) | DRAM[0x964D] | var | call (xhl) |
| 16 | `SndParam_*` (5 tables) | sndparam_routines.s | 50-464 | 0xEE10D0-0xEE1148 | reg a/c | 5-7 | call (xhl) |
| 17 | `SeMenu_ValueEditor_*` | sound_editor_ui.s | 3098 | 0xE0E72D | a (0x20-0x3F) | ~32 | call (xhl) |
| 18 | `SeMenu_ListSelector_*` | sound_editor_ui.s | 3248 | 0xE0E72D | a (0x20-0x3F) | ~32 | call (xhl) |

### Main CPU — Interrupt Handlers

| # | Label | File | Line | Table Base | Index Source | Entries | Type |
|---|-------|------|------|-----------|-------------|---------|------|
| 19 | `INTTX1_HANDLER` | cpanel_routines.s | 724 | 0xFC4489 | DRAM[36234] | var | jp (xhl) |
| 20 | `INTRX1_HANDLER` | cpanel_routines.s | 746 | 0xFC4489 | DRAM[36234] | var | jp (xhl) |

### Sub CPU

| # | Label | File | Line | Table Base | Index Source | Entries | Type |
|---|-------|------|------|-----------|-------------|---------|------|
| 21 | SubCPU cmd dispatch | subprogram_v142.s | 11322 | 0x00F46C | latch[7:5] | 8 | call (xwa) |
| 22 | SubCPU boot dispatch | subcpu_boot.s | 99596 | 0xFF8000 | latch[7:5] | 8 | call (xwa) |
| 23 | `Voice_SystemMsg_DispatchJump` | subprogram_v142.s | 25730 | 0x00F74F | bc (<=0x16) | 23 | jp_dri |
| 24 | `CmdHandler2C_JumpDispatch` | subprogram_v142.s | 40501 | 0x0121BD | wa (<=0xE) | 15 | jp_dri |

### HDAE5000

| # | Label | File | Line | Table Base | Index Source | Entries | Type |
|---|-------|------|------|-----------|-------------|---------|------|
| 25 | ATA command dispatch | hd-ae5000_v2_06i.s | 30631 | 0x295146 | wa (cmd#) | ~10 | call (xhl) |
| 26 | `TitleFunc_LifecycleDispatch` | hama/hama_code.s | 159 | 0xE1FDFE | xwa (<=0x7) | 8 | jp_dri |
| 27 | `GetResouceInfo` | kn5000_v10_program.s | 19638 | 0xE1FFD2 | wa (<=0x9) | 10 | jp_dri |

### Table Data ROM

| # | Label | File | Line | Table Base | Index Source | Entries | Type |
|---|-------|------|------|-----------|-------------|---------|------|
| 28 | Boot transfer | kn5000_table_data.s | 537 | 0xFFFEDC | -- | 1 | jp (xwa) |

---

## Undocumented Dispatch Tables — By Priority

### High Priority (Core System Dispatch)

These are major system-level dispatch tables that route to many handlers. Understanding them is key to firmware comprehension.

| File | Line | Table Base | Index Source | Scale | Sites | Description Guess |
|------|------|-----------|-------------|-------|-------|-------------------|
| style_data_init.s | 529 | 0xEF0D64 | DRAM[1041] | x4 | 1 | UI state machine primary dispatch |
| kn5000_v10_program.s | 26932 | 0xF24FA0 | reg a | x4 | 1 | Voice synthesis algorithm dispatch |
| kn5000_v10_program.s | 27639 | 0xF256B9 | reg a | x4 | 1 | Voice parameter dispatch |
| style_data_init.s | 5506 | 0xE00012 | c[7:5] | x4 | 1 | Top-level command router (3-bit index) |
| midipkt_routines.s | 275 | 0xEE304C | event byte | x4 | 1 | MIDI packet event type dispatch |

### Medium Priority (Subsystem Dispatch)

| File | Line | Table Base | Index Source | Scale | Sites | Description Guess |
|------|------|-----------|-------------|-------|-------|-------------------|
| drawbar_panel_ui.s | 10199+ | 0xE9F11C | (xwa+2) | x4 | 14 | Drawbar widget method dispatch |
| midipkt_routines.s | 307+ | 0xEE4F52 | (xbc+16) type | x4 | 9 | MIDI packet type handler |
| single_load.s | 652+ | 0xEA0996 | DRAM[0x89F8] | x4 | 6 | File I/O state machine A |
| single_load.s | 1306+ | 0xEA0A16 | DRAM[0x89F8] | x4 | 12 | File I/O state machine B |
| single_load.s | 1645+ | 0xEA0A2A | DRAM[0x89F8] | x4 | 7 | File I/O state machine C |
| single_load.s | 1832+ | 0xEA0A3E | DRAM[0x89F8] | x4 | 8 | File I/O state machine D |
| file_io_engine.s | 3224 | 0xEDAA64 | DRAM[0x9127] | x4 | 1 | File engine state dispatch |
| file_io_engine.s | 5704+ | 0xFCA4F9-0xFCB46F | various | x4 | 6 | File I/O sub-dispatchers |
| dsp_config_sysex.s | 4963+ | 0xEE8C7E-0xEE8CF4 | DRAM/computed | x4 | 5 | DSP config command dispatch |
| accompaniment_engine.s | 22526 | 0xF652BB | l & 0xF | x4 | 1 | Accompaniment sub-dispatch |
| midi_voice_routing.s | 10488 | 0xEE2F8C | SeqData field | x4 | 1 | Sequencer data field dispatch |
| note_voice_mapping.s | 13971 | 0xEEAE04 | DRAM[0xE9BE] | x4 | 1 | Voice mapping type dispatch |
| cpanel_routines.s | 1207 | 0xFC4965 | I/O reg & 0x38 | x4 | 1 | CPanel RX packet type |
| cpanel_routines.s | 1449 | 0xFC4B85 | I/O reg & 0x30 | x4 | 1 | CPanel LED TX packet type |

### jp_dri Undocumented Tables — By File

#### kn5000_v10_program.s (45 undocumented jp_dri sites)

The main program file has the highest concentration of undocumented dispatch tables. These cover the core firmware logic — event handling, parameter routing, mode switching.

#### sequencer_ui.s (32 undocumented jp_dri sites)

Sequencer UI event routing — screen updates, note editing, pattern display.

#### mode_screens.s (23 undocumented jp_dri sites)

Mode selection and screen rendering dispatch — one of the most UI-visible subsystems.

#### accompaniment_engine.s (23 undocumented jp_dri sites)

Accompaniment style engine — chord processing, pattern playback, rhythm dispatch.

#### hdae5000/hd-ae5000_v2_06i.s (54 undocumented jp_dri sites)

HDAE5000 extension ROM — serial protocol command dispatch, IDE/ATA command routing, filesystem operations.

#### sound_editor_ui.s (17 undocumented jp_dri sites)

Sound editing UI — waveform selection, parameter adjustment, effect configuration.

#### drawbar_panel_ui.s (15 undocumented jp_dri sites)

Drawbar organ interface — slider mapping, tone control, registration dispatch.

#### sequencer_engine.s (14 undocumented jp_dri sites)

Core sequencer engine — playback state machine, track control, tempo management.

#### subcpu/kn5000_subprogram_v142.s (19 undocumented jp_dri sites)

Sub CPU payload — audio processing dispatch, voice management, DSP command routing.

#### Other files (67 undocumented jp_dri sites across 19 files)

Scattered dispatch tables in UI widgets, file I/O, voice MIDI buffer, sysex processing, FDC routines, bitmap output, and computer interface code.

---

## How to Help

Each undocumented dispatch table needs:

1. **Semantic label** for the dispatch site (e.g., `LABEL_F24F89` → `VoiceSynth_AlgorithmDispatch`)
2. **Table annotation** — comment each `.long` or offset entry with what handler it points to
3. **Handler documentation** — brief comment on what each target function does
4. **Index variable documentation** — what the index represents (state ID, command type, etc.)

### Priority Order

1. Core system dispatch (style_data_init.s UI state machine, command router)
2. MIDI subsystem (midipkt_routines.s event dispatch, voice routing)
3. File I/O state machines (single_load.s, file_io_engine.s)
4. Sequencer engine (accompaniment_engine.s, sequencer_engine.s)
5. UI subsystem (mode_screens.s, drawbar_panel_ui.s, sequencer_ui.s)
6. Sub CPU and HDAE5000 (separate ROM regions)

### Conventions

- Dispatch site labels: `<Subsystem>_<Purpose>_Dispatch` (e.g., `FileIO_StateA_Dispatch`)
- Table labels: `<Subsystem>_<Purpose>_Table` (e.g., `FileIO_StateA_Table`)
- Handler labels: `<Subsystem>_<Purpose>_Handler_<N>` or semantic name if known

---

*This inventory was generated by automated analysis of all `.s` files in the ROM disassembly. Some entries may be misclassified (e.g., callback calls vs table dispatch). Manual review is ongoing.*
