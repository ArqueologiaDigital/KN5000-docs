---
layout: page
title: Source Code Map
permalink: /source-map/
---

# Source Code Map

This page describes every source file in the [disassembly repository](https://github.com/ArqueologiaDigital/kn5000-roms-disasm). The firmware is reconstructed from TLCS-900/H2 assembly using LLVM's `llvm-mc` assembler. All 6 ROMs build to **100% byte-identical** copies of the originals.

## ROM Overview

| ROM | Size | Top-level Source | Include Files | Purpose |
|-----|------|-----------------|---------------|---------|
| [Main CPU](#main-cpu-2mb) | 2MB | `maincpu/kn5000_v10_program.s` | 143 | Primary firmware — UI, audio, sequencer, MIDI, file I/O |
| [Sub CPU Payload](#sub-cpu-payload-192kb) | 192KB | `subcpu/kn5000_subprogram_v142.s` | 3 | Audio engine — tone generation, voice management, DSP |
| [Sub CPU Boot](#sub-cpu-boot-128kb) | 128KB | `subcpu/boot/kn5000_subcpu_boot.s` | 0 | Sub CPU bootstrap and payload decompression |
| [HDAE5000](#hdae5000-extension-512kb) | 512KB | `hdae5000/hd-ae5000_v2_06i.s` | 5 | Hard disk expansion — IDE/ATA driver, FAT16, file manager UI |
| [Table Data](#table-data-2mb) | 2MB | `table_data/kn5000_table_data.s` | 7 | Accompaniment style patterns, rhythm data |
| [Custom Data](#custom-data-1mb) | 1MB | `custom_data/kn5000_custom_data.s` | 0 | User-modifiable flash storage (factory defaults) |

---

## Main CPU (2MB)

The main CPU ROM contains the entire user-facing firmware: the UI framework, display rendering, audio parameter control, sequencer, accompaniment engine, MIDI processing, file I/O, floppy disk controller, and control panel handling. It is split across **143 include files** organized into **15 subdirectories** by subsystem.

### Directory Structure

```
maincpu/
  kn5000_v10_program.s       # Top-level file (ROM layout & inline data)
  *_constants.s (4 files)    # Subsystem constant definitions
  msp_factory_defaults.s     # MSP factory default data
  shared/     (9 files)      # Cross-ROM shared: macros, SFR, VGA, boot
  boot/       (3 files)      # System startup, interrupt handlers, init
  ui/         (13 files)     # UI framework, widgets, drawing, panels
  display/    (3 files)      # VGA graphics, text rendering, scoop editor
  audio/      (27 files)     # Audio control, sound editor, DSP config, sound data
  midi/       (9 files)      # MIDI serial, dispatch, SysEx, computer I/F
  sequencer/  (14 files)     # Sequencer, SMF, accompaniment, rhythm
  storage/    (2 files)      # Flash memory, floppy disk controller
  demo/          (4 files)   # Feature demo mode
  ui_widgets/    (27 files)  # UI screen layout descriptors (codename: NAKA)
  file_io/       (9 files)   # Disk file operations
  factory_test/  (4 files)   # Factory diagnostics (codename: HAMA)
  includes/      (18 files)  # Style UI parameter blocks, screen data, GUI strings
  extensions/    (2 files)   # Extension device support (codename: TOSHI)
```

### Constants & Macros

| File | Lines | Description |
|------|-------|-------------|
| `shared/macros.s` | 124 | Assembler helper macros |
| `shared/sfr_tmp94c241.s` | 241 | TMP94C241F special function register definitions |
| `shared/vga_constants.s` | 74 | VGA display register constants |
| `shared/event_codes.s` | 46 | System event code definitions |
| `fdc_constants.s` | 75 | Floppy disk controller register constants |
| `gui_constants.s` | 56 | GUI framework constants (widget types, flags) |
| `cpanel_constants.s` | 197 | Control panel button/LED segment constants |
| `midi_encoder_constants.s` | 91 | MIDI encoding format constants |

### `boot/` — System Startup & Core Handlers

| File | Lines | Description |
|------|-------|-------------|
| `shared/boot_hw_init.s` | 139 | Hardware register initialization (shared with Table Data ROM) |
| `shared/boot_routines.s` | 87 | Region detection and boot helper routines |
| `shared/boot_call_init_handlers.s` | 85 | Walk initialization handler table at boot |
| `boot/system_handlers.s` | 8,251 | Interrupt handlers (NMI, timers), UI state machine, task scheduler, flash memory update, LZSS decompression |
| `boot/main_title_ctrl_panel.s` | 611 | System initialization (graphics, events, timers, LCD), main title UI event loop |
| `boot/screen_group_dispatch.s` | 264 | Boot screen group dispatcher (startup screens, error dialogs) |
| `shared/vga_init.s` | 434 | VGA controller initialization sequence |
| `shared/vga_io.s` | 51 | VGA register read/write primitives |

### `display/` — VGA Graphics & Text Rendering

| File | Lines | Description |
|------|-------|-------------|
| `display/scoop_display.s` | 10,370 | Display dirty-region tracking, performance mode parameter handlers, scoop (oscilloscope) editor UI |
| `display/graphics_text_vga.s` | 4,211 | VGA palette initialization, text rendering, string layout, VRAM operations |
| `display/scoop_editor_data.s` | 1,177 | Sound editor display data, performance mode parameter bytecode, scoop config tables |

### `ui/` — UI Framework & Widgets

| File | Lines | Description |
|------|-------|-------------|
| `ui/ui_widget_defs.s` | 19,640 | Grid box, exit window, title/resource widgets, event dispatch loops, object enumeration |
| `ui/ui_window_procs.s` | 8,046 | Window procedure handlers: ModeEdit, TitleEdit, StringBox, Label, Bitmap, Icon, Line, Frame, EditSw, TextBox, VwBox, ListBox, RadioBox, TempoBox, GridBox |
| `ui/ui_control_panel.s` | 4,086 | Control panel key dispatch, UI task control, slider/scrollbar handlers, GroupBoxProc container widget |
| `ui/ui_mode_handlers.s` | 12,927 | UI mode handlers for Pmem (parametric), bank editor, filter grid, RVari (variable screen), effect modes |
| `ui/drawbar_panel_ui.s` | 15,581 | Drawbar organ slider UI, DSP effect controls, presentation system, demo menu |
| `ui/bitmap_out_routines.s` | 4,347 | Bitmap blitting and palette loading for VGA display |
| `ui/drawing_primitives.s` | 4,567 | Line drawing (Bresenham), rectangle fill, reverse string rendering |
| `ui/psgridbox_routines.s` | 1,138 | PS Grid Box widget initialization and event handling |
| `ui/rvari_routines.s` | 2,752 | RVari (variable selection) screen renderer and interaction handlers |
| `ui/setwall_routines.s` | 1,940 | Wallpaper loading and wall display update routines |
| `ui/cpanel_routines.s` | 1,559 | Control panel hardware: serial RX/TX processing, button polling, LED control |
| `ui/password_slot_routines.s` | 38 | Password slot management stubs |
| `ui/ui_playback_modes.s` | 3,042 | UI state event handling and playback mode control: voice parameter handlers, sequencer timer/tempo, part validation, play/song/medley mode dispatch |

### `audio/` — Sound & Audio Control

| File | Lines | Description |
|------|-------|-------------|
| `audio/audio_control_engine.s` | 8,377 | MIDI stream processing, control panel LED management, voice/tone control, sound preset dispatch |
| `audio/audio_cmd_encoder.s` | 3,100 | Audio command encoder — printf-like formatter for SubCPU commands |
| `audio/audioinit_routines.s` | 2,505 | Audio subsystem initialization, stereo voice configuration |
| `audio/dsp_config_sysex.s` | 5,626 | DSP effect parameter handlers (reverb, chorus, EQ, compressor), SysEx command processing |
| `audio/sound_editor_ui.s` | 11,946 | Sound editor UI: patch/bank selection, parameter editing, drum kit editor |
| `audio/sound_editor_routines.s` | 629 | Sound editor helper routines |
| `audio/semenu_routines.s` | 3,431 | Sound editor menu (SeMenu) event handling and navigation |
| `audio/sound_navigation.s` | 495 | Sound bank browsing: MainGetSoundName, Sound_Navigate_*, MainGetRhythmName, MainGetPmemName |
| `audio/presentation_sound_nav.s` | 1,762 | SSF presentation workspace building, sound navigation, voice control, presentation control proc |
| `audio/tonegen_fileio_handlers.s` | 1,071 | Tone generator config initialization, DSP config entry setup, FileIO callback handlers |
| `audio/sndparam_routines.s` | 2,042 | Sound parameter probe, match, and heap allocation |
| `audio/note_voice_mapping.s` | 26,105 | Note-on processing, voice allocation/stealing, NoteMap (91 functions), sequence playback, MIDI output, sound parameters, utility routines |
| `audio/sound_data_piano.s` | 2,188 | Piano sound data: 128-byte header + 2048 tone mapping pairs |
| `audio/sound_data_strings_vocal.s` | 2,188 | Strings/vocal sound data: 128-byte header + 2048 tone mapping pairs |
| `audio/sound_data_mallet_orch_perc.s` | 461 | Mallet/orchestral percussion sound data |
| `audio/sound_data_flute_extra.s` | 305 | Extended flute sound data |
| `audio/sound_data_flute.s` | 162 | Flute sound data |
| `audio/sound_data_guitar.s` | 95 | Guitar sound data |
| `audio/sound_data_sax_reed.s` | 95 | Saxophone/reed sound data |
| `audio/tonegen_param_table.s` | 92 | Tone generator parameter lookup table |
| `audio/sound_data_synth.s` | 20 | Synth sound data |
| `audio/sound_data_drum_kits.s` | 18 | Drum kit sound data |
| `audio/sound_data_orchestral_pad.s` | 12 | Orchestral pad sound data |
| `audio/sound_data_accordion_reg.s` | 6 | Accordion/register sound data |
| `audio/sound_data_bass.s` | 6 | Bass sound data |
| `audio/sound_data_digital_drawbar.s` | 6 | Digital drawbar sound data |
| `audio/sound_data_gm_special.s` | 6 | GM special sound data |

### `midi/` — MIDI Processing & Computer Interface

| File | Lines | Description |
|------|-------|-------------|
| `midi/midi_dispatch_handlers.s` | 11,505 | MIDI CC handlers (22 types), serial input parsing, file data validation, sound mode handlers, arpeggiator queue |
| `midi/midi_serial_routines.s` | 995 | MIDI serial communication (SC0): TX/RX handlers, initialization |
| `midi/midi_encoder_routines.s` | 275 | MIDI encoder timing and output dispatch |
| `midi/midipkt_routines.s` | 1,178 | MIDI packet extraction, packing, and queue management |
| `midi/sysex_routines.s` | 239 | System Exclusive message handling |
| `midi/ac_listener_handlers.s` | 1,884 | AcLswFuncBoxProc event dispatch, parameter processing, mixer controls, TtMd exclusion routines |
| `midi/param_load_routines.s` | 658 | ParaLoadOpt parameter loading options, audio flag processing, event posting |
| `midi/computer_interface_config.s` | 310 | MIDI computer interface configuration |
| `midi/computer_interface_pcg.s` | 704 | Computer interface program change (PCG) handlers |

### `sequencer/` — Sequencer & Accompaniment

| File | Lines | Description |
|------|-------|-------------|
| `sequencer/sequencer_engine.s` | 32,094 | Core sequencer: note editor UI, playback control, voice allocation, application event framework, part/voice data management |
| `sequencer/sequencer_ui.s` | 14,372 | Sequencer editing UI, track display, bitmap drum editor |
| `sequencer/seq_step_routines.s` | 3,103 | Step recording, note event dispatch, step playback |
| `sequencer/smf_event_processor.s` | 8,247 | SMF (Standard MIDI File) event processing, tone generation dispatch, voice channel management |
| `sequencer/smf_config_routines.s` | 3,263 | SMF configuration and parameter setup |
| `sequencer/smf_playback.s` | 708 | SMF playback control entry points |
| `sequencer/smf_tonegen_core.s` | 5,194 | Sequencer-driven tone generation: floppy I/O integration, SMF track event parsing, voice channel management, tone generator block writes, voice synthesis dispatch |
| `sequencer/seq_event_playback.s` | 4,220 | Sequencer event buffer processing, voice slot scanning, note/channel decoding, accompaniment playback loop, tempo event dispatch, MIDI sustain, ring buffer management |
| `sequencer/seq_audio_mode.s` | 2,010 | Audio mode stereo flags, accompaniment pedal processing, sequencer timing, part activation |
| `sequencer/accompaniment_engine.s` | 32,617 | Rhythm dispatch, accompaniment voice selection, timing, patches, drum configuration, style conversion |
| `sequencer/accompseq_routines.s` | 1,961 | Accompaniment sequencer periodic processing |
| `sequencer/rhythm_routines.s` | 1,580 | Rhythm pattern comparison, trigger, and transposition |
| `sequencer/ssf_gate_states.s` | 1,492 | SSF (Style Synthesis Format) gate state arrays for accompaniment patterns |
| `sequencer/bmdredit_routines.s` | 4,434 | Bitmap drum editor: stream positioning, sequence display, voice allocation UI |

### `storage/` — Flash & Floppy

| File | Lines | Description |
|------|-------|-------------|
| `storage/flash_floppy_handlers.s` | 4,695 | Flash memory sector write, floppy disk note event loading, FDC format UI |
| `storage/fdc_routines.s` | 1,503 | Floppy disk controller: register access, sector read/write, disk change detection |

### `demo/` — Feature Demo Mode

| File | Lines | Description |
|------|-------|-------------|
| `demo/demo_routines.s` | 294 | Demo mode entry and control |
| `demo/fdemotext_routines.s` | 2,334 | Feature demo text processing: voice probing, flag processing, output formatting |
| `demo/file_demo_proc.s` | 8,359 | File demo procedures and title handlers |
| `demo/demo_seq_bridge.s` | 1,060 | MiddleFuncCall dispatcher, SqTrSel (sequencer track select), demo-sequencer bridge |

### `file_io/` — Disk File Operations

| File | Lines | Description |
|------|-------|-------------|
| `file_io/disk_operations.s` | 1,297 | Disk file copy, rename, format, disk info |
| `file_io/filename_password.s` | 807 | Filename and password entry UI |
| `file_io/composer_filters.s` | 968 | Composer load and filter operations |
| `file_io/smf_operations.s` | 1,312 | Standard MIDI File load, save, naming |
| `file_io/wallpaper.s` | 673 | Wallpaper image loading from disk |
| `file_io/single_load.s` | 2,299 | Single file load with source/destination selection |
| `file_io/medley.s` | 4,715 | Medley playback: internal, disk, SMF, performance data modes |
| `file_io/misc_ui.s` | 969 | Miscellaneous file I/O UI (jump insert, file priority, setup) |
| `file_io/title_handlers.s` | 349 | File title display handlers |

### `ui_widgets/` — UI Screen Layout Descriptors (codename: NAKA)

The "NAKA" widget format defines UI screen layouts as hierarchical widget trees. These files contain the screen definitions for nearly every UI mode. "NAKA" is a Matsushita/Technics developer codename; all original symbol names (`InitializeNaka`, `NAKA_TYPE_*`, etc.) are preserved in the code.

| File | Lines | Description |
|------|-------|-------------|
| `ui_widgets/widget_descriptors.s` | 9,325 | Widget type definitions and descriptor tables |
| `ui_widgets/widget_dispatch.s` | 9,751 | Widget event dispatch: string pointer tables, screen routing |
| `ui_widgets/naka_screen_dispatch.s` | 2,295 | Screen definition tables: SeqToComposer, SeqCopy, EasyComposer, ModeSelect, ExpandMode |
| `ui_widgets/technichord_string_data.s` | 3,658 | TechniChord style dispatch tables, style names, dialog text, multilingual UI strings |
| `ui_widgets/disk_warning_strings.s` | 2,344 | Multilingual disk format/delete/operation warning messages (EN/ES/DE/FR/ID/IT) |
| `ui_widgets/widget_names_charmap.s` | 2,396 | Widget type name strings, character encoding/mapping tables, NAKA presentation state |
| `ui_widgets/naka_widget_tables_1.s` | 1,909 | Widget pointer tables: SmfDp, DocDp, PdDp, KssDp, DrumDp screen groups |
| `ui_widgets/naka_widget_tables_2.s` | 1,668 | Widget data tables: CtlMsgGridBox, MidiControlMessage, additional NAKA types |
| `ui_widgets/style_bitmaps.s` | 5,910 | Style selection bitmap resources |
| `ui_widgets/e0e974_e15b20.s` | 6,116 | Feature Demo screens, style category menus, accompaniment UI |
| `ui_widgets/e176e4_e1a704.s` | 2,745 | Style presentation and performance UI |
| `ui_widgets/e1ab58_e1b7d2.s` | 683 | Mixed widget data and strings |
| `ui_widgets/e2107c_e24034.s` | 2,694 | Rhythm variation selection, song/sequencer parameter screens |
| `ui_widgets/e27408_e27556.s` | 151 | Equalizer and effect parameter UI |
| `ui_widgets/e27fa4_e30932.s` | 8,274 | Accompaniment memory/PCG output grids, MIDI controller UI |
| `ui_widgets/e55e38_e5a38e.s` | 2,910 | MIDI controller messages, accompaniment input grid |
| `ui_widgets/e812e8_e818e6.s` | 286 | Menu item pagination UI |
| `ui_widgets/e81cce_e85f46.s` | 3,708 | Tech Chord dispatch, chord/transpose UI |
| `ui_widgets/ea13cc_ea8c9e.s` | 5,503 | Disk format dialogs (multi-language), Tech Chord configuration |
| `ui_widgets/block_012.s` | 552 | User bitmap viewer, track chord UI, language text, integration setup |
| `ui_widgets/eb2afe_eb71be.s` | 1,247 | Style bitmap and dispatch table wrapper |
| `ui_widgets/block_007.s` | 86 | Additional widget block |
| `ui_widgets/ed2a9c_ed2b96.s` | 189 | Extension-region widget descriptor |
| `ui_widgets/ed333c_ed35e4.s` | 182 | Extension-region widget descriptor |
| `ui_widgets/ed3cc0_ed665a.s` | 1,940 | Extension-region widget data |
| `ui_widgets/ed803c_eda02c.s` | 2,727 | Extension-region widget data |
| `ui_widgets/eee718_eef588.s` | 1,015 | Final widget block before boot code |

### `includes/` — Style UI Parameter Blocks & Screen Data

Data files for the style UI subsystem: parameter block definitions for different style editing modes, screen layout data, GUI display structures, and format strings.

| File | Lines | Description |
|------|-------|-------------|
| `includes/gui_display_struct_data.s` | 328 | GUI display structure data tables |
| `includes/style_ui_screendata_main.s` | 226 | Main style UI screen layout data |
| `includes/gui_format_strings.s` | 49 | GUI number/text format strings |
| `includes/style_ui_screendata_ctlonly.s` | 40 | Control-only style screen data |
| `includes/style_ui_paramblock_bal.s` | 20 | Style balance parameter block |
| `includes/style_ui_screendata_yesctl.s` | 19 | Yes/control style screen data |
| `includes/style_ui_screendata_meascursor.s` | 16 | Measure cursor screen data |
| `includes/style_ui_paramblock_medium.s` | 16 | Medium-size parameter block |
| `includes/style_ui_paramblock_extended.s` | 16 | Extended parameter block |
| `includes/style_ui_paramblock_meas.s` | 14 | Measure parameter block |
| `includes/style_ui_paramblock_common.s` | 14 | Common parameter block |
| `includes/style_ui_paramblock_alte.s` | 12 | Alt-E parameter block variant |
| `includes/style_ui_paramblock_altc.s` | 11 | Alt-C parameter block variant |
| `includes/style_ui_paramblock_altd.s` | 9 | Alt-D parameter block variant |
| `includes/style_ui_paramblock_alta.s` | 7 | Alt-A parameter block variant |
| `includes/style_ui_paramblock_altb.s` | 7 | Alt-B parameter block variant |
| `includes/style_ui_paramblock_short.s` | 7 | Short parameter block |
| `includes/style_ui_paramblock_value.s` | 7 | Value parameter block |

### `extensions/` — Extension Device Support (codename: TOSHI)

Registers expansion slot devices (such as the HD-AE5000 hard disk board) with the main firmware. "TOSHI" is a Matsushita/Technics developer codename; original symbols (`InitializeToshi`, etc.) are preserved.

| File | Lines | Description |
|------|-------|-------------|
| `extensions/extension_init.s` | 107 | Extension slot driver framework: device registration and initialization |
| `extensions/extension_data.s` | 6,708 | Extension device data tables and widget descriptors |

### `factory_test/` — Factory Diagnostic Tests (codename: HAMA)

Factory diagnostic test modes for hardware validation during manufacturing, including floppy disk and hard disk extension tests. "HAMA" is a Matsushita/Technics developer codename; original symbols (`InitializeHama`, `RegObjTableHama`, etc.) are preserved.

| File | Lines | Description |
|------|-------|-------------|
| `factory_test/test_init.s` | 503 | Test mode registration and macro definitions |
| `factory_test/test_data.s` | 252 | Test UI configuration data |
| `factory_test/fd_test_code.s` | 372 | Floppy disk test execution routines |
| `factory_test/fd_test_data.s` | 418 | Floppy disk test parameters and dialog data |

### Factory Defaults

| File | Lines | Description |
|------|-------|-------------|
| `msp_factory_defaults.s` | 709 | MSP (Music Style Preset) factory default data |

---

## Sub CPU Payload (192KB)

The Sub CPU runs the real-time audio engine. It receives commands from the Main CPU via a latch interface and directly controls the tone generator hardware and DSP effects.

| File | Lines | Description |
|------|-------|-------------|
| `kn5000_subprogram_v142.s` | 43,772 | **Core audio engine**: RESET handler, initialization, main audio loop, voice slot management, tone generator command emission, pitch/envelope processing, DSP register writes |
| `subcpu_vectors.s` | 200 | Interrupt vector table and 45 interrupt handler stubs (INT_HANDLER_00 through INT_HANDLER_2C) |
| `subcpu_data_tables.s` | 8,897 | Firmware configuration, floating-point constants, serial I/O buffers, command dispatch table, voice polyphony limits, pitch/MIDI lookup tables |
| `subcpu_fp_math.s` | 3,144 | IEEE 754 floating-point math library: double/single precision arithmetic, mantissa operations, multiply-add, division, pitch slide engine, amplitude convergence, NaN/overflow handling |

---

## Sub CPU Boot (128KB)

| File | Lines | Description |
|------|-------|-------------|
| `boot/kn5000_subcpu_boot.s` | 100,869 | Sub CPU bootstrap ROM: hardware initialization, LZSS decompressor for payload, DMA transfer setup. Large file due to extensive data tables (waveform ROM address maps, voice parameter defaults) |

---

## HDAE5000 Extension (512KB)

The HD-AE5000 is an optional hard disk expansion board. Its firmware provides IDE/ATA disk access, a FAT16 filesystem, and a file manager UI that integrates with the main keyboard interface.

| File | Lines | Description |
|------|-------|-------------|
| `hd-ae5000_v2_06i.s` | 4,101 | **Core**: ROM header, entry vectors, handler registration, memory allocation, event handling |
| `hdae5000_hd_driver.s` | 5,994 | IDE/ATA hard disk driver: drive setup, identify, seek, read/write, error handling, CHS calculation, partition management |
| `hdae5000_filesystem.s` | 5,058 | FAT16 filesystem: initialization, FSB (filesystem block) read/write, directory scanning, entry lookup |
| `hdae5000_ui_display.s` | 24,517 | File manager UI: menu registration, display scrolling, cell rendering, palette setup, event dispatch |
| `hdae5000_utilities.s` | 2,043 | Utility functions: memory copy/compare, multiply, divide (signed/unsigned), string operations |
| `hdae5000_data_tables.s` | 36,736 | UI configuration, record tables, page titles, graphics resources, fonts, localization strings, palette data |

---

## Table Data (2MB)

| File | Lines | Description |
|------|-------|-------------|
| `kn5000_table_data.s` | 3,995 | Accompaniment style pattern data, rhythm tables. Shares boot code with Main CPU ROM (`shared/boot_hw_init.s`, `shared/vga_init.s`). Mostly binary data includes. |

---

## Custom Data (1MB)

| File | Lines | Description |
|------|-------|-------------|
| `kn5000_custom_data.s` | 146 | User-modifiable flash memory containing factory default settings. Written during firmware update; preserved across power cycles. |

---

## Build System

All ROMs are built with `make all` from the repository root:

```
llvm-mc -triple=tlcs900  →  ld.lld  →  llvm-objcopy  →  raw binary
```

Each ROM is verified against the original dump using `python scripts/compare_roms.py`, which reports byte-level similarity (target: 100.00% for all 6 ROMs).
