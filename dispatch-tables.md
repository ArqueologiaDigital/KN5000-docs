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
| `call (xreg)` — indirect call through pointer table | 49 | 25 | 24 |
| `jp (xreg)` — indirect jump through pointer table | 18 | 10 | 8 |
| `jp_dri` — register-indexed jump via offset table | 317 | 80 | 237 |
| **Total** | **384** | **115** | **269** |

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
ld a, (xix + <byte_table>)  ; byte_table[index] -> secondary index
extz wa
sll wa, ...
; Level 2: offset table
lda_24 xix, <offset_table>
jp_dri ...
```

6 sites use this cascaded pattern for more complex routing.

---

## Recently Documented (March 9, 2026)

The following 81 dispatch sites were labeled with semantic names during the dispatch table documentation sprint:

### Batch 1: Core Dispatch Sites (7 sites)
| Label | File | Type | Description |
|-------|------|------|-------------|
| `SeqRingBuf_WriteDispatch_Table` | kn5000_v10_program.s | call (xhl) | 8-entry sequencer ring buffer write, indexed by DRAM[1508] bits [7:5] |
| `MidiPkt_EventType_Table` | naka_dispatch.s | call (xhl) | 192-entry MIDI packet event type dispatch |
| `UIStateMachine_PrimaryDispatch` | style_data_init.s | jp (xhl) | 3-state UI state machine primary dispatch |
| `Timer_ModeDispatch` | scoop_display.s | call (xhl) | 4-entry timer mode dispatch |
| `E1DMA_TransferSetup` | style_data_init.s | call (xhl) | DMA transfer setup after SeqRingBuf dispatch |
| `VoiceSynth_CommandDispatch` | kn5000_v10_program.s | cascaded | Voice synthesis command dispatcher (DRAM[4012]) |
| `VoiceParam_CommandDispatch` | kn5000_v10_program.s | cascaded | Voice parameter command dispatcher (DRAM[4012]) |

### Batch 2: File I/O & MIDI Stream (7 sites)
| Label | File | Type | Description |
|-------|------|------|-------------|
| `RegBitManip_Dispatch` | file_io_engine.s | call (xhl) | 8-entry register bit manipulation dispatch |
| `MidiStream_ProcessorDispatch` | file_io_engine.s | call (xhl) | 8-entry MIDI stream processor A |
| `MidiStream_ProcessorDispatchB` | file_io_engine.s | call (xhl) | 8-entry MIDI stream processor B |
| `MidiStream_ProcessorDispatchC` | file_io_engine.s | call (xhl) | 16-entry MIDI stream processor C |
| `VoiceMode_ParamDispatch` | file_io_engine.s | call (xhl) | 8-entry voice mode parameter dispatch |
| `VoiceSynth_AlgoTableDispatch` | kn5000_v10_program.s | call (xhl) | 16-entry algorithm table via VoiceSynth_Algorithm_Table |
| `VoiceParam_ReadUpdateDispatch` | kn5000_v10_program.s | call (xhl) | 16-entry read-update table via VoiceParam_ReadUpdate_Table |

### Batch 3: Mode Screens UI (22 sites)
| Label | File | Description |
|-------|------|-------------|
| `TEST2FUNC_DispatchReturn` | mode_screens.s | 6-entry event dispatch (event 0x1C00013) |
| `TEST3FUNC_DispatchReturn` | mode_screens.s | 6-entry event dispatch |
| `TEST4FUNC_DispatchReturn` | mode_screens.s | 6-entry event dispatch |
| `TEST6FUNC_DispatchReturn` | mode_screens.s | 6-entry event dispatch |
| `MasterSetup_EventDispatch` | mode_screens.s | 7-entry UI event dispatch (table 0xED0D24) |
| `MstStyleAlp_EventDispatch` | mode_screens.s | 7-entry (table 0xED0D58) |
| `MstStyle_EventDispatch` | mode_screens.s | 7-entry (table 0xED0D66) |
| `MstStyle1Grid_EventDispatch` | mode_screens.s | 7-entry (table 0xED0D8A) |
| `MstStyle1_EventDispatch` | mode_screens.s | 7-entry (table 0xED0D9E) |
| `MstStyle1Sub_EventDispatch` | mode_screens.s | 7-entry (table 0xED0DC2) |
| `MstStyle1Page_EventDispatch` | mode_screens.s | 7-entry (table 0xED0E04) |
| `MstStyle2_EventDispatch` | mode_screens.s | 7-entry (table 0xED0ED2) |
| `TchSensGrid_EventDispatch` | mode_screens.s | 7-entry (table 0xED0F08) |
| `TchSens_EventDispatch` | mode_screens.s | 7-entry (table 0xED0F16) |
| `FSWAssGrid_EventDispatch` | mode_screens.s | 7-entry (table 0xED1226) |
| `FswAsIni_EventDispatch` | mode_screens.s | 6-entry (table 0xED1234) |
| `PmemPageCtl_EventDispatch` | mode_screens.s | 7-entry (table 0xED1420) |
| `PmExpFilter_EventDispatch` | mode_screens.s | 7-entry (table 0xED149A) |
| `PmExpFilter2_EventDispatch` | mode_screens.s | 7-entry (table 0xED14A8) |
| `DispTimeSet_EventDispatch` | mode_screens.s | 7-entry (table 0xED1582) |
| `MssName_EventDispatch` | mode_screens.s | 10-entry (table 0xED15AC) |
| `PmBkName_EventDispatch` | mode_screens.s | 10-entry (table 0xED15EE) |

### Batch 4: Sequencer UI (21 sites)
| Label | File | Description |
|-------|------|-------------|
| `MuteChSel_Dispatch` | sequencer_ui.s | SmfMuteChSelFunc dispatch |
| `SqTrAsPsSong_Dispatch` | sequencer_ui.s | Song track dispatch |
| `MuteChSet_Dispatch` | sequencer_ui.s | Mute channel set dispatch |
| `DemoMedDsp_Dispatch` | sequencer_ui.s | Demo medium display dispatch |
| `DPPlayDsp_Dispatch` | sequencer_ui.s | Demo play display dispatch |
| `DPPauseDsp_Dispatch` | sequencer_ui.s | Demo pause display dispatch |
| `NoteEditBox_EventDispatch1` | sequencer_ui.s | Note edit box event dispatch 1 |
| `NoteEditBox_EventDispatch2` | sequencer_ui.s | Note edit box event dispatch 2 |
| `NoteEditBox_GridDispatch` | sequencer_ui.s | Note edit box grid dispatch |
| `AcEntertainer_EventDispatch` | sequencer_ui.s | Accompaniment entertainer dispatch |
| `SndParam_Dispatch` | sequencer_ui.s | Sound parameter dispatch |
| `AccIll_Dispatch` | sequencer_ui.s | Accompaniment illustration dispatch |
| `EffectBox_Dispatch` | sequencer_ui.s | Effect box dispatch |
| `SeqAccomp_Dispatch` | sequencer_ui.s | Sequencer accompaniment dispatch |
| `Sqedt_ParamDispatch` | sequencer_ui.s | Sequencer editor param dispatch |
| `Sqedt_ValueDispatch` | sequencer_ui.s | Sequencer editor value dispatch |
| `SeqFormat_DispatchA` | sequencer_ui.s | Sequencer format dispatch A |
| `SeqFormat_DispatchB` | sequencer_ui.s | Sequencer format dispatch B |
| `DspItem0_TypeDispatch` | sequencer_ui.s | DSP item 0 type dispatch |
| `Equalizer_DispatchA` | sequencer_ui.s | Equalizer dispatch A |
| `Equalizer_DispatchB` | sequencer_ui.s | Equalizer dispatch B |

### Batch 5: Voice, MIDI & Sound (21 sites)
| Label | File | Description |
|-------|------|-------------|
| `VoiceEvent_Dispatch` | note_voice_mapping.s | 14-entry voice event handler (table 0xEE8F06) |
| `SeqPerformance_EventDispatch` | note_voice_mapping.s | 6-entry sequence performance dispatch |
| `UIParam_CallbackReturn` | note_voice_mapping.s | UI parameter callback return |
| `MidiSysMsg_Dispatch` | note_voice_mapping.s | 15-entry MIDI system message dispatch |
| `SndParam_TypeDispatch` | note_voice_mapping.s | 6-entry sound parameter type dispatch |
| `SndParam_OffsetDispatch` | note_voice_mapping.s | 6-entry sound parameter offset dispatch |
| `HdaeRom_DataDispatch` | note_voice_mapping.s | 6-entry HDAE5000 data dispatch |
| `HdaeRom_AltDispatch` | note_voice_mapping.s | 6-entry HDAE5000 alt dispatch |
| `ToneGen_ParamWriteDispatch` | voice_midi_buf.s | ToneGen param write dispatch table |
| `WallHomeEdit_EventDispatch` | voice_midi_buf.s | Wall home edit event dispatch |
| `WallMenuEdit_EventDispatch` | voice_midi_buf.s | Wall menu edit event dispatch |
| `WallOthEdit_EventDispatch` | voice_midi_buf.s | Wall other edit event dispatch |
| `MainSysCtrl_DispatchTable` | voice_midi_buf.s | Main system control dispatch |
| `CntIniFunc_EventDispatch` | voice_midi_buf.s | CntIniFunc event dispatch |
| `DspConfig_EventDispatch` | dsp_config_sysex.s | DSP config event dispatch |
| `WndEvt_EventCodeDispatch` | voice_synth.s | Window event code dispatch |
| `MidiChan_ParamDispatch` | midi_voice_routing.s | MIDI channel parameter dispatch |
| `SeqData_FieldDispatch` | midi_voice_routing.s | Sequence data field dispatch |
| `SysEx_SendDispatch` | midi_voice_routing.s | SysEx send dispatch |
| `TitleProc_EventDispatch` | ui_widget_defs.s | Title proc event dispatch |
| `SeqEvent_Dispatch` ... (3 more) | sequencer_engine.s | Sequencer engine dispatches |

---

## Previously Documented Dispatch Tables

These tables had meaningful semantic labels before the documentation sprint.

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

## Remaining Undocumented — By File

| File | Remaining Undocumented | Notes |
|------|----------------------|-------|
| kn5000_v10_program.s | ~41 jp_dri | Core firmware logic, event handling |
| accompaniment_engine.s | ~23 jp_dri | Chord processing, rhythm dispatch |
| hdae5000/hd-ae5000_v2_06i.s | ~54 jp_dri | Extension ROM command dispatch |
| subcpu/kn5000_subprogram_v142.s | ~19 jp_dri | Sub CPU audio processing |
| sound_editor_ui.s | ~17 jp_dri | Sound editing UI |
| drawbar_panel_ui.s | ~15 jp_dri + ~14 call | Drawbar organ interface |
| sequencer_ui.s | ~11 jp_dri | Sequencer UI (21 sites done) |
| sequencer_engine.s | ~7 jp_dri | Core sequencer (7 sites done) |
| mode_screens.s | ~1 jp_dri | Mode selection UI (22 sites done) |
| Other files (19) | ~67 scattered | UI widgets, file I/O, sysex, FDC |
| **Total remaining** | **~269** | |

---

## How to Help

Each undocumented dispatch table needs:

1. **Semantic label** for the dispatch site (e.g., `LABEL_F24F89` -> `VoiceSynth_AlgorithmDispatch`)
2. **Table annotation** — comment each `.long` or offset entry with what handler it points to
3. **Handler documentation** — brief comment on what each target function does
4. **Index variable documentation** — what the index represents (state ID, command type, etc.)

### Conventions

- Dispatch site labels: `<Subsystem>_<Purpose>_Dispatch` (e.g., `FileIO_StateA_Dispatch`)
- Table labels: `<Subsystem>_<Purpose>_Table` (e.g., `FileIO_StateA_Table`)
- Handler labels: `<Subsystem>_<Purpose>_Handler_<N>` or semantic name if known

---

*This inventory was generated by automated analysis of all `.s` files in the ROM disassembly. Manual review and documentation is ongoing.*
