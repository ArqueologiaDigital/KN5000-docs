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
| [Main CPU](#main-cpu-2mb) | 2MB | `maincpu/kn5000_v10_program.s` | 94 | Primary firmware — UI, audio, sequencer, MIDI, file I/O |
| [Sub CPU Payload](#sub-cpu-payload-192kb) | 192KB | `subcpu/kn5000_subprogram_v142.s` | 3 | Audio engine — tone generation, voice management, DSP |
| [Sub CPU Boot](#sub-cpu-boot-128kb) | 128KB | `subcpu/boot/kn5000_subcpu_boot.s` | 0 | Sub CPU bootstrap and payload decompression |
| [HDAE5000](#hdae5000-extension-512kb) | 512KB | `hdae5000/hd-ae5000_v2_06i.s` | 5 | Hard disk expansion — IDE/ATA driver, FAT16, file manager UI |
| [Table Data](#table-data-2mb) | 2MB | `table_data/kn5000_table_data.s` | 7 | Accompaniment style patterns, rhythm data |
| [Custom Data](#custom-data-1mb) | 1MB | `custom_data/kn5000_custom_data.s` | 0 | User-modifiable flash storage (factory defaults) |

---

## Main CPU (2MB)

The main CPU ROM contains the entire user-facing firmware: the UI framework, display rendering, audio parameter control, sequencer, accompaniment engine, MIDI processing, file I/O, floppy disk controller, and control panel handling. It is split across **94 include files** organized by subsystem.

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

### Boot & System Initialization

| File | Lines | Description |
|------|-------|-------------|
| `shared/boot_hw_init.s` | 139 | Hardware register initialization (shared with Table Data ROM) |
| `shared/boot_routines.s` | 87 | Region detection and boot helper routines |
| `shared/boot_call_init_handlers.s` | 85 | Walk initialization handler table at boot |
| `system_handlers.s` | 8,251 | Interrupt handlers (NMI, timers), UI state machine, task scheduler, flash memory update, LZSS decompression |
| `shared/vga_init.s` | 434 | VGA controller initialization sequence |
| `shared/vga_io.s` | 51 | VGA register read/write primitives |

### Display & Graphics

| File | Lines | Description |
|------|-------|-------------|
| `scoop_display.s` | 10,370 | Display dirty-region tracking, performance mode parameter handlers, scoop (oscilloscope) editor UI |
| `graphics_text_vga.s` | 4,211 | VGA palette initialization, text rendering, string layout, VRAM operations |
| `bitmap_out_routines.s` | 4,347 | Bitmap blitting and palette loading for VGA display |
| `drawing_primitives.s` | 4,567 | Line drawing (Bresenham), rectangle fill, reverse string rendering |
| `screen_group_dispatch.s` | 264 | Boot screen group dispatcher (startup screens, error dialogs) |

### UI Framework

| File | Lines | Description |
|------|-------|-------------|
| `ui_widget_defs.s` | 19,640 | Grid box, exit window, title/resource widgets, event dispatch loops, object enumeration |
| `ui_window_procs.s` | 8,046 | Window procedure handlers: ModeEdit, TitleEdit, StringBox, Label, Bitmap, Icon, Line, Frame, EditSw, TextBox, VwBox, ListBox, RadioBox, TempoBox, GridBox |
| `ui_control_panel.s` | 4,086 | Control panel key dispatch, UI task control, slider/scrollbar handlers, GroupBoxProc container widget |
| `ui_mode_handlers.s` | 12,927 | UI mode handlers for Pmem (parametric), bank editor, filter grid, RVari (variable screen), effect modes |
| `main_title_ctrl_panel.s` | 611 | System initialization (graphics, events, timers, LCD), main title UI event loop |
| `psgridbox_routines.s` | 1,138 | PS Grid Box widget initialization and event handling |
| `rvari_routines.s` | 2,752 | RVari (variable selection) screen renderer and interaction handlers |
| `setwall_routines.s` | 1,940 | Wallpaper loading and wall display update routines |

### Sound & Audio Control

| File | Lines | Description |
|------|-------|-------------|
| `sound_navigation.s` | 495 | Sound bank browsing: MainGetSoundName, Sound_Navigate_*, MainGetRhythmName, MainGetPmemName |
| `sound_editor_ui.s` | 11,946 | Sound editor UI: patch/bank selection, parameter editing, drum kit editor |
| `sound_editor_routines.s` | 629 | Sound editor helper routines |
| `semenu_routines.s` | 3,431 | Sound editor menu (SeMenu) event handling and navigation |
| `sndparam_routines.s` | 2,042 | Sound parameter probe, match, and heap allocation |
| `audio_control_engine.s` | 8,377 | MIDI stream processing, control panel LED management, voice/tone control, sound preset dispatch |
| `audio_cmd_encoder.s` | 3,100 | Audio command encoder — printf-like formatter for SubCPU commands |
| `audioinit_routines.s` | 2,505 | Audio subsystem initialization, stereo voice configuration |
| `dsp_config_sysex.s` | 5,626 | DSP effect parameter handlers (reverb, chorus, EQ, compressor), SysEx command processing |

### Sequencer & Accompaniment

| File | Lines | Description |
|------|-------|-------------|
| `sequencer_engine.s` | 32,094 | Core sequencer: note editor UI, playback control, voice allocation, application event framework, part/voice data management |
| `sequencer_ui.s` | 14,372 | Sequencer editing UI, track display, bitmap drum editor |
| `seq_step_routines.s` | 3,103 | Step recording, note event dispatch, step playback |
| `smf_event_processor.s` | 8,247 | SMF (Standard MIDI File) event processing, tone generation dispatch, voice channel management |
| `smf_config_routines.s` | 3,263 | SMF configuration and parameter setup |
| `smf_playback.s` | 708 | SMF playback control entry points |
| `accompaniment_engine.s` | 32,617 | Rhythm dispatch, accompaniment voice selection, timing, patches, drum configuration, style conversion |
| `accompseq_routines.s` | 1,961 | Accompaniment sequencer periodic processing |
| `rhythm_routines.s` | 1,580 | Rhythm pattern comparison, trigger, and transposition |
| `msp_factory_defaults.s` | 709 | MSP (Music Style Preset) factory default data |
| `ssf_gate_states.s` | 1,492 | SSF (Style Synthesis Format) gate state arrays for accompaniment patterns |

### MIDI Processing

| File | Lines | Description |
|------|-------|-------------|
| `midi_dispatch_handlers.s` | 11,505 | MIDI CC handlers (22 types), serial input parsing, file data validation, sound mode handlers, arpeggiator queue |
| `midi_serial_routines.s` | 995 | MIDI serial communication (SC0): TX/RX handlers, initialization |
| `midi_encoder_routines.s` | 275 | MIDI encoder timing and output dispatch |
| `midipkt_routines.s` | 1,178 | MIDI packet extraction, packing, and queue management |
| `note_voice_mapping.s` | 26,105 | Note-on processing, voice allocation/stealing, NoteMap (91 functions), sequence playback, MIDI output, sound parameters, utility routines |
| `sysex_routines.s` | 239 | System Exclusive message handling |

### File I/O & Storage

| File | Lines | Description |
|------|-------|-------------|
| `fdc_routines.s` | 1,503 | Floppy disk controller: register access, sector read/write, disk change detection |
| `flash_floppy_handlers.s` | 4,695 | Flash memory sector write, floppy disk note event loading, FDC format UI |
| `file_demo_proc.s` | 8,359 | File demo procedures and title handlers |
| `password_slot_routines.s` | 38 | Password slot management stubs |
| `file_io/disk_operations.s` | 1,297 | Disk file copy, rename, format, disk info |
| `file_io/filename_password.s` | 807 | Filename and password entry UI |
| `file_io/composer_filters.s` | 968 | Composer load and filter operations |
| `file_io/smf_operations.s` | 1,312 | Standard MIDI File load, save, naming |
| `file_io/wallpaper.s` | 673 | Wallpaper image loading from disk |
| `file_io/single_load.s` | 2,299 | Single file load with source/destination selection |
| `file_io/medley.s` | 4,715 | Medley playback: internal, disk, SMF, performance data modes |
| `file_io/misc_ui.s` | 969 | Miscellaneous file I/O UI (jump insert, file priority, setup) |
| `file_io/title_handlers.s` | 349 | File title display handlers |

### Control Panel & Computer Interface

| File | Lines | Description |
|------|-------|-------------|
| `cpanel_routines.s` | 1,559 | Control panel hardware: serial RX/TX processing, button polling, LED control |
| `computer_interface_config.s` | 310 | MIDI computer interface configuration |
| `computer_interface_pcg.s` | 704 | Computer interface program change (PCG) handlers |

### Drawbar & Demo

| File | Lines | Description |
|------|-------|-------------|
| `drawbar_panel_ui.s` | 15,581 | Drawbar organ slider UI, DSP effect controls, presentation system, demo menu |
| `fdemotext_routines.s` | 2,334 | Feature demo text processing: voice probing, flag processing, output formatting |
| `demo_routines.s` | 294 | Demo mode entry and control |

### Bitmap Drum Editor

| File | Lines | Description |
|------|-------|-------------|
| `bmdredit_routines.s` | 4,434 | Bitmap drum editor: stream positioning, sequence display, voice allocation UI |

### NAKA UI Descriptors

The NAKA format defines UI screen layouts as hierarchical widget trees. These files contain the screen definitions for nearly every UI mode.

| File | Lines | Description |
|------|-------|-------------|
| `naka_descriptors.s` | 9,325 | UI element type definitions and descriptor tables |
| `naka_dispatch.s` | 9,751 | NAKA event dispatch: string pointer tables, screen routing |
| `naka_style_bitmap.s` | 5,910 | Style selection bitmap resources |
| `naka/naka_e0e974_e15b20.s` | 6,116 | Feature Demo screens, style category menus, accompaniment UI |
| `naka/naka_e176e4_e1a704.s` | 2,745 | Style presentation and performance UI |
| `naka/naka_e1ab58_e1b7d2.s` | 683 | Mixed NAKA data and strings |
| `naka/naka_e2107c_e24034.s` | 2,694 | Rhythm variation selection, song/sequencer parameter screens |
| `naka/naka_e27408_e27556.s` | 151 | Equalizer and effect parameter UI |
| `naka/naka_e27fa4_e30932.s` | 8,274 | Accompaniment memory/PCG output grids, MIDI controller UI |
| `naka/naka_e55e38_e5a38e.s` | 2,910 | MIDI controller messages, accompaniment input grid |
| `naka/naka_e812e8_e818e6.s` | 286 | Menu item pagination UI |
| `naka/naka_e81cce_e85f46.s` | 3,708 | Tech Chord dispatch, chord/transpose UI |
| `naka/naka_ea13cc_ea8c9e.s` | 5,503 | Disk format dialogs (multi-language), Tech Chord configuration |
| `naka/naka_block_012.s` | 552 | User bitmap viewer, track chord UI, language text, integration setup |
| `naka/naka_eb2afe_eb71be.s` | 1,247 | Style bitmap and dispatch table wrapper |
| `naka/naka_block_007.s` | 86 | Additional NAKA block |
| `naka/naka_ed2a9c_ed2b96.s` | 189 | Toshi-region NAKA descriptor |
| `naka/naka_ed333c_ed35e4.s` | 182 | Toshi-region NAKA descriptor |
| `naka/naka_ed3cc0_ed665a.s` | 1,940 | Toshi-region NAKA data |
| `naka/naka_ed803c_eda02c.s` | 2,727 | Toshi-region NAKA data |
| `naka/naka_eee718_eef588.s` | 1,015 | Final NAKA block before boot code |

### Extension Device Support (TOSHI)

| File | Lines | Description |
|------|-------|-------------|
| `toshi/toshi_code.s` | 107 | Extension slot driver framework: device registration and initialization |
| `toshi/toshi_data.s` | 6,708 | Extension device data tables and NAKA descriptors |

### Developer Test Code (HAMA)

| File | Lines | Description |
|------|-------|-------------|
| `hama/hama_code.s` | 503 | Hama developer test code (includes floppy disk test) |
| `hama/hama_data.s` | 252 | Hama test configuration data |
| `hama/fd_test_code.s` | 372 | Floppy disk test execution routines |
| `hama/fd_test_data.s` | 418 | Floppy disk test parameters |

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
