---
layout: page
title: "Dispatch Tables Inventory"
permalink: /dispatch-tables/
---

# Dispatch Tables Inventory

This page catalogs all indirect call/jump dispatch tables found in the KN5000 ROM disassembly. These are sites where firmware computes a target address at runtime using an index into a table of function pointers or offsets.

**Last updated:** March 9, 2026

## Progress: 494 / 1583 dispatch sites documented (31%)

A dispatch site is "documented" when the containing function has a meaningful semantic label (not a generic `LABEL_XXXXXX` name).

### Per-File Coverage

| File | jp_dri | call/jp | Total | Labeled | Coverage |
|------|--------|---------|-------|---------|----------|
| hdae5000/hd-ae5000_v2_06i.s | 2/54 | 98/1003 | 1057 | 100 | 9% |
| maincpu/sound_editor_ui.s | 16/17 | 4/41 | 58 | 20 | 34% |
| maincpu/ui_widget_defs.s | 4/11 | 6/20 | 31 | 10 | 32% |
| maincpu/drawbar_panel_ui.s | 8/15 | 2/14 | 29 | 10 | 34% |
| maincpu/kn5000_v10_program.s | 44/46 | 2/3 | 49 | 46 | 94% |
| maincpu/file_io/single_load.s | 0/0 | 28/33 | 33 | 28 | 85% |
| maincpu/sequencer_ui.s | 29/33 | 0/0 | 33 | 29 | 88% |
| subcpu/kn5000_subprogram_v142.s | 14/21 | 1/2 | 23 | 15 | 65% |
| maincpu/mode_screens.s | 22/23 | 1/1 | 24 | 23 | 96% |
| maincpu/seq_task_sched.s | 2/2 | 14/16 | 18 | 16 | 89% |
| maincpu/sequencer_engine.s | 14/16 | 0/0 | 16 | 14 | 88% |
| maincpu/file_io_engine.s | 0/0 | 10/14 | 14 | 10 | 71% |
| maincpu/midi_voice_routing.s | 3/3 | 4/7 | 10 | 7 | 70% |
| maincpu/dsp_config_sysex.s | 3/3 | 4/7 | 10 | 7 | 70% |
| maincpu/midipkt_routines.s | 0/0 | 9/10 | 10 | 9 | 90% |
| maincpu/note_voice_mapping.s | 3/8 | 1/1 | 9 | 4 | 44% |
| maincpu/voice_midi_buf.s | 6/6 | 1/2 | 8 | 7 | 88% |
| maincpu/accompaniment_engine.s | 23/23 | 5/5 | 28 | 28 | 100% |
| maincpu/audio_cmd_encoder.s | 1/1 | 56/56 | 57 | 57 | 100% |
| maincpu/seq_step_routines.s | 3/3 | 3/3 | 6 | 6 | 100% |
| maincpu/scoop_display.s | 0/0 | 3/5 | 5 | 3 | 60% |
| maincpu/style_data_init.s | 1/1 | 3/4 | 5 | 4 | 80% |
| maincpu/hama/hama_code.s | 2/2 | 3/3 | 5 | 5 | 100% |
| maincpu/sndparam_routines.s | 0/0 | 5/5 | 5 | 5 | 100% |
| maincpu/file_demo_proc.s | 2/2 | 0/2 | 4 | 2 | 50% |
| maincpu/voice_synth.s | 1/4 | 0/0 | 4 | 1 | 25% |
| maincpu/cpanel_routines.s | 0/0 | 4/4 | 4 | 4 | 100% |
| maincpu/demo_routines.s | 3/3 | 0/0 | 3 | 3 | 100% |
| maincpu/tonegen_voice_ctrl.s | 2/3 | 0/0 | 3 | 2 | 67% |
| table_data/kn5000_table_data.s | 1/1 | 2/2 | 3 | 3 | 100% |
| maincpu/sysex_routines.s | 6/6 | 0/0 | 6 | 6 | 100% |
| maincpu/computer_interface_pcg.s | 1/2 | 0/0 | 2 | 1 | 50% |
| maincpu/fdc_routines.s | 1/2 | 0/0 | 2 | 1 | 50% |
| Other files (100%) | 8/8 | 67/67 | 15 | 15 | 100% |
| **TOTAL** | **222/316** | **272/1267** | **1583** | **494** | **31%** |

### Coverage by ROM

| ROM | Total Sites | Labeled | Coverage |
|-----|-------------|---------|----------|
| Main CPU | 502 | 379 | 75% |
| Sub CPU | 24 | 15 | 63% |
| HDAE5000 | 1057 | 100 | 9% |
| Table Data | 3 | 3 | 100% |

**Note:** The HDAE5000 extension ROM dominates the count (67% of all sites). Its 1003 `call (xhl)` sites mostly follow a vtable dispatch pattern: `ld_sril XHL, (xwa + offset)` then `call (xhl)`. Documenting the vtable structure and method offsets will cover many sites at once.

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

Table contains 16-bit relative offsets. More compact than pointer tables. Used extensively (316 sites).

### Pattern 3: Vtable Dispatch (HDAE5000)

```asm
ld_sril XHL, (xwa + 0x00e4)  ; load method from object vtable
call (xhl)                     ; dispatch to method
```

HDAE5000 uses an object-oriented vtable pattern where XWA points to an object, and the method pointer is loaded from a fixed offset within the object structure. ~1003 call sites use this pattern with various method offsets.

### Pattern 4: Two-Level Dispatch

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

A total of **502 dispatch labels** were created during the dispatch table documentation sprint:
- 105 dispatch site labels (jp_dri/call/jp instruction sites)
- 397 dispatch handler target labels (case handlers within dispatch tables)

### Phase 1: Dispatch Sites (105 labels)

The following dispatch sites were labeled with semantic names:

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

### Phase 2: Handler Targets (~397 labels)

Dispatch handler targets (individual case labels) were labeled across these files:

| File | Targets Labeled | Key Handler Groups |
|------|----------------|-------------------|
| kn5000_v10_program.s | 152 | System (EditSwParam, WindowField, DirmdEmu, DSPCfg), Title functions (SqTrAs, SqMdlyPly, DkMdlyPly, DpMdly*, DpDoc*, DpPd*, DpSmf*, SqTrSel), Voice (AcVocalGrid, VocalistGrid, ParaLoadOpt) |
| sound_editor_ui.s | 68 | PartGrid columns, NoteEvent buffers, CmpSetP1/EasyCmp/FdcFormat grids, SndArgGrid, PsSCTxtBox |
| drawbar_panel_ui.s | 44 | ComSetGrid, PmemOutL, CtlMsgGrid, MidiSetup, IvSdpart, PsMixer, DemoMenu, AcPresCtrl |
| accompaniment_engine.s | 78 | RhythmParam, CmpMenuTtl/SetTtl/RealTtl, CmpBkslTtl fill-ins, CmpEsyTtl/NcpTtl, MainCmpSet, MspMenu/Name/Rec |
| sequencer_ui.s | 59 | TrAsGrid, MuteChSel, DemoMedDsp, NoteEditBox, Entertainer, SqedtFunc, DspItem0/Equalizer |
| sequencer_engine.s | 30 | SeqData/Event, AppEvent chain, SeqState, NoteEditSy, MainExeCall |

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

## Remaining Work — Priority Order

### 1. HDAE5000 Extension ROM (957 unlabeled sites)

The HDAE5000 has 1,057 dispatch sites total (54 jp_dri + 1,003 call/jp). Only 100 are in semantically-labeled functions. The ~1,003 `call (xhl)` sites use a vtable dispatch pattern where method pointers are loaded from object structures at fixed offsets. Key vtable offsets include:

- `+0x00E4` — RegisterObjectTable (most common, ~400+ call sites)
- `+0x0270` — Special dispatch
- `+0x03C4`, `+0x0538`, `+0x053C`, `+0x0124`, `+0x0108` — Various methods

Documenting the vtable structure and labeling the handler functions will cover many call sites at once.

### 2. Maincpu Files Below 100%

| File | Unlabeled | Priority |
|------|-----------|----------|
| sound_editor_ui.s | 38 | High — mostly call(xhl) |
| ui_widget_defs.s | 21 | High — UI framework |
| drawbar_panel_ui.s | 19 | Medium |
| note_voice_mapping.s | 5 | Medium |
| voice_synth.s | 3 | Low |
| file_io_engine.s | 4 | Low |
| dsp_config_sysex.s | 3 | Low |
| midi_voice_routing.s | 3 | Low |

### 3. Sub CPU (8 unlabeled sites)

The Sub CPU has 8 unlabeled jp_dri sites in `kn5000_subprogram_v142.s`.

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
