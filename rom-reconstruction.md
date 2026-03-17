---
layout: page
title: ROM Reconstruction
permalink: /rom-reconstruction/
---

# ROM Reconstruction

Goal: Rebuild all firmware ROMs from disassembled source with 100% byte accuracy.

## Firmware Version History

Official firmware updates were distributed on floppy disk. All versions are archived at [archive.org](https://archive.org/details/technics-kn5000-system-update-disks).

### Main Board Firmware

| Version | Release Date | Notes |
|---------|--------------|-------|
| v5 | 1997-11-12 | Earliest available |
| v6 | 1998-01-16 | |
| v7 | 1998-06-26 | |
| v8 | 1998-11-13 | |
| v9 | 1999-01-26 | |
| **v10** | 1999-08-02 | **Current disassembly target** |

### HD-AE5000 Firmware

| Version | Release Date | Notes |
|---------|--------------|-------|
| v1.10i | 1998-07-06 | Initial release |
| v1.15i | 1998-10-13 | |
| v2.0i | 1999-01-15 | Added lyrics display |

## Current Status

| ROM | Size | Match % | Bytes Off | Source File |
|-----|------|---------|-----------|-------------|
| Main CPU | 2MB | **100%** | 0 | `maincpu/kn5000_v10_program.s` |
| Sub CPU Payload | 192KB | **100%** | 0 | `subcpu/kn5000_subprogram_v142.s` |
| Sub CPU Boot | 128KB | **100%** | 0 | `subcpu/boot/kn5000_subcpu_boot.s` |
| Table Data | 2MB | **100%** | 0 | `table_data/kn5000_table_data.s` |
| Custom Data | 1MB | **100%** | 0 | `custom_data/kn5000_custom_data.s` |
| HDAE5000 (HD Expansion) | 512KB | **100%** | 0 | `hdae5000/hd-ae5000_v2_06i.s` |

### Disassembly Status Visualization

The diagram below shows the disassembly status of each ROM component. Colors indicate the type of content at each address:

![ROM Status Diagram]({{ "/assets/images/rom-status-diagram.png" | relative_url }})

**Legend:**
- **Green** = Disassembled code (symbolic instructions with meaningful labels)
- **Blue** = Known data structures (documented tables, configs)
- **Cyan** = String data (text, messages, labels)
- **Light Green** = Pointer/jump tables (address references)
- **Purple** = Binary includes (external files not yet analyzed)
- **Red** = Raw bytes with unknown meaning (needs investigation)
- **Orange** = Raw bytes known to be code (awaiting disassembly)
- **Gray** = Padding/unused (0x00 or 0xFF fill)
- **Yellow** = Undetermined (not yet categorized)

The width of each rectangle is proportional to the ROM's file size. This visualization is automatically regenerated via `make website` to stay in sync with disassembly progress.

## Original ROM Files

The original firmware dumps are stored in `original_ROMs/`:

| File | Size | Description |
|------|------|-------------|
| `kn5000_v10_program.rom` | 2MB | Main CPU program ROM |
| `kn5000_subprogram_v142.rom` | 192KB | Sub CPU payload (sent by main CPU at boot) |
| `kn5000_subcpu_boot.ic30` | 128KB | Sub CPU boot ROM |
| `kn5000_table_data_rom_odd.ic1` | 1MB | Table data ROM (odd bytes) |
| `kn5000_table_data_rom_even.ic3` | 1MB | Table data ROM (even bytes) |
| `kn5000_custom_data.ic19` | 1MB | Custom data flash (user storage) |
| `hd-ae5000_v2_06i.ic4` | 512KB | HDAE5000 hard disk expansion ROM |

Reference disassembly files (`.unidasm`) are generated with MAME's `unidasm` tool for analysis.

## Assembler

The project uses a **custom LLVM backend** (`llvm-mc -triple=tlcs900`) for assembly. All ~370,000 instructions are encoded natively — no workaround macros needed.

**Build Process:**
1. `llvm-mc` assembles `.s` files to ELF object files
2. `ld.lld` links with a linker script to set the ROM base address
3. `llvm-objcopy` extracts the raw binary from the ELF
4. `compare_roms.py` verifies byte-for-byte match against originals

**History:** The project originally used ASL (Alfred Arnold's Macro Assembler), which only supported TMP96C141 — requiring 110+ workaround macros for TMP94C241F-specific instructions. The LLVM backend was developed to encode all TLCS-900/H2 instructions natively. ASL sources are archived in `archive/asl/` for reference.

## Milestone: 100% Byte-Matching ROMs

As of March 2026, **all six ROMs** rebuild with 100% byte accuracy using LLVM assembly (~370,000 native instructions, 0 workaround macros):

- **Main CPU** (2MB) - Complete disassembly with symbolic labels (239,683 native instructions, 0 code .byte remaining)
- **Sub CPU Payload** (192KB) - Full protocol implementation (35,747 instructions)
- **Sub CPU Boot** (128KB) - Boot ROM with VGA initialization (1,357 instructions)
- **Table Data** (2MB) - Feature demo, wallpapers, icons, bootloader (1,678 instructions)
- **HDAE5000** (512KB) - Hard disk expansion firmware (502 instructions)
- **Custom Data** (1MB) - User storage (data-only, byte-exact reconstruction)

## Source File Organization

### Main CPU

The Main CPU disassembly is organized into modular source files for maintainability:

| File | Lines | Description |
|------|-------|-------------|
| `maincpu/kn5000_v10_program.s` | ~43,000 | Main source file (includes 94+ other files) |
| `maincpu/gui_constants.s` | 57 | Display state variables, offscreen buffers |
| `maincpu/fdc_constants.s` | 75 | FDC I/O addresses, commands, status bits |
| `maincpu/fdc_routines.s` | 1,403 | FDC read/write/seek routines |
| `maincpu/midi_encoder_constants.s` | 85 | MIDI CC and encoder RAM/ROM addresses |
| `maincpu/midi_encoder_routines.s` | 268 | Encoder dispatch and MIDI CC processing |
| `maincpu/cpanel_constants.s` | 164 | Control panel state, buffers, button/LED mappings |
| `maincpu/cpanel_routines.s` | 1,506 | Control panel serial protocol handlers |
| `maincpu/sysex_routines.s` | 239 | MIDI System Exclusive message handlers |
| `maincpu/demo_routines.s` | 290 | Feature Demo mode handlers |
| `maincpu/computer_interface_config.s` | 310 | Computer Interface connection configuration |
| `maincpu/computer_interface_pcg.s` | 703 | Computer Interface PCG (Program Change) output |
| `maincpu/midi_serial_routines.s` | 995 | MIDI serial communication (SC0) |
| `maincpu/sound_editor_routines.s` | 629 | Sound Editor mode and title functions |
| `maincpu/smf_playback.s` | 695 | SMF song playback routines |
| `maincpu/smf_config_routines.s` | 3,263 | SMF configuration and slot parameters |
| `maincpu/seq_step_routines.s` | 3,089 | Step-mode sequencer routines |
| `maincpu/audio_cmd_encoder.s` | 3,100 | Audio command byte formatter |
| `maincpu/semenu_routines.s` | 3,431 | Sound editor menu system |
| `maincpu/setwall_routines.s` | 1,940 | Accompaniment style wall parser |
| `maincpu/rhythm_routines.s` | 1,580 | Rhythm pattern processing |
| `maincpu/accompseq_routines.s` | 1,961 | Accompaniment sequencer |
| `maincpu/audioinit_routines.s` | 2,505 | Audio subsystem initialization |
| `maincpu/bmdredit_routines.s` | 4,434 | Beat/drum editor |
| `maincpu/drawing_primitives.s` | 4,567 | Line/box/frame/bitmap/string drawing |
| `maincpu/bitmap_out_routines.s` | 4,347 | Bitmap output/display compositing |
| `maincpu/rvari_routines.s` | 2,752 | Registration variation selection UI |
| `maincpu/psgridbox_routines.s` | 1,138 | Performance settings grid box UI |
| `maincpu/fdemotext_routines.s` | 2,334 | Feature demo text rendering |
| `maincpu/sndparam_routines.s` | 2,042 | Sound parameter lookup/storage |
| `maincpu/midipkt_routines.s` | 1,178 | MIDI packet construction |
| `maincpu/msp_factory_defaults.s` | — | MSP factory default settings |
| `maincpu/file_io/title_handlers.s` | 349 | File I/O title entry handlers |
| `maincpu/file_io/disk_operations.s` | 1,297 | File copy, rename, format, disk info |
| `maincpu/file_io/filename_password.s` | 807 | Filename and password UI |
| `maincpu/file_io/composer_filters.s` | 968 | Composer load and filter operations |
| `maincpu/file_io/smf_operations.s` | 1,312 | Standard MIDI File operations |
| `maincpu/file_io/wallpaper.s` | 519 | Wallpaper loading |
| `maincpu/file_io/single_load.s` | 2,298 | Single file load operations |
| `maincpu/file_io/medley.s` | 4,690 | Medley playback (disk, internal, SMF, PD, doc) |
| `maincpu/file_io/misc_ui.s` | 969 | Jump insert, priority, setup, filename box |

| `maincpu/accompaniment_engine.s` | 32,516 | Accompaniment, auto-play, pedal, style engine |
| `maincpu/sequencer_engine.s` | 32,056 | Sequencer part/play, note editing |
| `maincpu/note_voice_mapping.s` | 26,090 | Note mapping, voice management, MIDI routing |
| `maincpu/ui_widget_defs.s` | 19,616 | UI widget definitions, screen/window/view IDs |
| `maincpu/sound_editor_ui.s` | 16,567 | Sound editor menus and grids |
| `maincpu/drawbar_panel_ui.s` | 15,526 | Drawbar, accordion, panel memory UI |
| `maincpu/sequencer_ui.s` | 14,292 | Sequencer playback/edit UI |
| `maincpu/mode_screens.s` | 12,905 | MSA mode, panel memory, effect mode screens |
| `maincpu/midi_voice_routing.s` | 11,498 | MIDI dispatch, voice routing |
| `maincpu/scoop_display.s` | 10,363 | Display update manager |
| `maincpu/naka_dispatch.s` | 9,746 | Central dispatch, UI state |
| `maincpu/naka_descriptors.s` | 9,324 | Descriptor tables, bitmap data |
| `maincpu/file_demo_proc.s` | 8,355 | File I/O, demo processing |
| `maincpu/style_data_init.s` | 8,246 | Style data, task scheduling |
| `maincpu/voice_synth.s` | 8,042 | Sound generation, voice synthesis |
| `maincpu/dsp_config_sysex.s` | 5,881 | DSP config, SysEx handlers |
| `maincpu/naka_style_bitmap.s` | 5,909 | Style groups, bitmap data |
| `maincpu/tonegen_voice_ctrl.s` | 5,185 | Tone generator, voice control |
| `maincpu/voice_midi_buf.s` | 4,202 | Voice MIDI buffers |

**Total extracted code: ~384,000 lines across 94 include files (90% of main CPU source)**

**Subsystem Descriptions:**

**FDC (Floppy Disk Controller):**
- `fdc_constants.s`: Memory-mapped I/O addresses (0x110000 base), command codes (uPD765-compatible), status register bit definitions
- `fdc_routines.s`: Complete FDC handler including `FDC_COMMAND_DISPATCHER`, `FDC_HANDLER_01` through `FDC_HANDLER_11`, `Reset_Floppy_Disk_Controller`, `Check_for_Floppy_Disk_Change`

**MIDI/Encoder:**
- `midi_encoder_constants.s`: MIDI CC value storage, raw encoder inputs, lookup table addresses
- `midi_encoder_routines.s`: `CPanel_EncoderDispatch`, `Encoder_ProcessModwheel`, `Encoder_ProcessVolume`, `Encoder_ProcessBreath`, `Encoder_ProcessFoot`, `Encoder_ProcessExpression`

**Control Panel:**
- `cpanel_constants.s`: State machine variables, RX/TX buffers, button state arrays with bit mappings, LED row/pattern mappings
- `cpanel_routines.s`: Serial protocol handlers (`CPanel_SM_*`), packet processors (`CPanel_RX_*`), LED control, buffer management

**SysEx (System Exclusive):**
- `sysex_routines.s`: `ExcSendFunc`, `ExcPmemFunc` (Panel Memory), `ExcSmemFunc` (Sound Memory), `ExcCompFunc` (Composer), `ExcSeqFunc` (Sequence), `ExcMspFunc` (MSP)

**Feature Demo:**
- `demo_routines.s`: `DemoModeFunc`, `DemoStyleTtlFunc`, `DemoSoundTtlFunc`, `DemoRhyTtlFunc`

**Computer Interface:**
- `computer_interface_config.s`: `TtComputerConnection`, `MdCmptCnctFunc`, `MdPcgModeFunc`, `MdDrumTypeFunc`, `MdSetupLoadFunc`
- `computer_interface_pcg.s`: `TtMdPcgOut`, `AcPcgOutGridBoxProc`, `PcgOutGridCheck`, `PcgOutSendFunc`, `MainPcgOutSend`

**MIDI Serial (SC0):**
- `midi_serial_routines.s`: `INTTX0_HANDLER`, `INTRX0_HANDLER`, `READ_COM_SELECT_SWITCH`, SC0 initialization

**Sound Editor:**
- `sound_editor_routines.s`: 32 Sound Editor functions including `SeMenuModeFunc`, `SeMenuTitleFunc`, `SeEasyTitleFunc`, `SeTonTon1/2TitleFunc`, `SePitPit1TitleFunc`, `SeAmpAmp1/2TitleFunc`, `SeFilLpq1TitleFunc`, `SeDigEffTitleFunc`, `SeCtr2/3TitleFunc`, `SeCopyTitleFunc`, `SeWrtMemTitleFunc`, `SeWrtSndTitleFunc`

**File I/O & Disk Operations** (in `maincpu/file_io/` subdirectory):
- `title_handlers.s`: Entry handlers (`LoadTtlJgFunc`, `SaveTtlJgFunc`, `SetupFlashFunc`, `FmmUtilityTitleFunc`)
- `disk_operations.s`: File operations (`FileCopyFunc`, `FileRenameFunc`, `FmmFormatFunc`, `DiskNameFunc`, `DiskInfoFunc`)
- `filename_password.s`: UI routines (`FmmPasswordFunc`, `FmmFileNameFunc`)
- `composer_filters.s`: Composer and filters (`FmmComposerLoadFunc`, `FmmLoadFilterFunc`, `FmmSaveFilterFunc`)
- `smf_operations.s`: Standard MIDI File (`FmmSmfLoadTitleFunc`, `SmfLoadAsFunc`, `FmmSmfFileNameFunc`)
- `wallpaper.s`: Wallpaper loading (`FmmWallpaperLoadFunc`)
- `single_load.s`: Single file load (`SingleLoadModeFunc`, `SingleLoadSrcFunc`, `SingleLoadDstFunc`)
- `medley.s`: All medley modes (`FmmIntMedleyFunc`, `FmmDiskMedley*Func`, `FmmSmfMedleyFunc`, `FmmDocMedleyFunc`)
- `misc_ui.s`: Utilities (`JumpInsertFunc`, `SetupOkFunc`, `PsFileNameBoxProc`)

**Sequencer (Reference Only):**
- `sequencer_reference.s`: Documents 61 sequencer functions scattered across the ROM (not extracted due to interleaving with other code)

**GUI Constants:**
- `gui_constants.s`: Display dirty flags (0x0205E4), offscreen buffer addresses (0x043C00, 0x056800, 0x05FE00, 0x069400), screen dimensions (320x240 @ 8bpp)

**Palettes:**

Two color palettes have been extracted as binary includes:
- **Palette 1** at 0xEB37DE - first palette (inline in sequential section)
- **Palette 2** at 0xEEFAF0 - second palette (`Palette_8bit_RGBA_2.bin`)

### Sub CPU Boot (100% COMPLETE!)

The Sub CPU boot ROM has achieved **100% byte-perfect reconstruction!**

**All routines fully disassembled:**
- `SUB_8437` (0xFF8437) - Tone generator initialization loop
- `SUB_850E` (0xFF850E) - Multi-register push/call wrapper
- `SUB_853A` (0xFF853A) - Write register pairs to tone generator
- `COPY_WORDS` (0xFF858B) - Word block copy using `ldirw`
- `FILL_WORDS` (0xFF8594) - Memory fill with word values
- `CHECKSUM_CALC` (0xFF859B) - Calculate checksum over memory range
- `SUB_8B37` (0xFF8B37) - LED/output bit manipulation routine
- `SUB_8B89` (0xFF8B89) - Inter-CPU communication handler (reads from 0x110000 latches)
- `SUB_8BD2` (0xFF8BD2) - Note/velocity calculation with lookup tables
- `SUB_8C75` (0xFF8C75) - Hardware register write helper (0x100000)
- `SUB_8C80` (0xFF8C80) - Hardware calibration routine with timeout loop
- `SUB_8D0A` (0xFF8D0A) - Hardware parameter write (21 param pairs)
- `SUB_8F57` (0xFF8F57) - Hardware write with delay
- `SUB_FE80-FEC1` (0xFFFE80) - Debug/diagnostic routines (hex output, string output)
- Vector trampolines and interrupt handlers

**DMA Transfer Routines (0xFF8604-0xFF881E):**

These routines handle DMA-based data transfer between the Sub CPU and Main CPU:

| Routine | Address | Size | Description |
|---------|---------|------|-------------|
| `SendData_Chunked` | 0xFF8604 | 69 bytes | Send data in 32-byte chunks via DMA |
| `SendData_Block` | 0xFF8649 | 99 bytes | Send single data block via DMA |
| `SendCmd_E3` | 0xFF86AC | 48 bytes | Send E3 (payload ready) command |
| `SendParams_E2` | 0xFF86DC | 112 bytes | Wait for DMA, then send E2 command |
| `TwoPhase_Transfer` | 0xFF874C | 211 bytes | Two-phase DMA with E1 command, 200-cycle delays |

**Inter-CPU Communication Protocol:**
- Uses handshaking via `INTERCPU_STATUS` register at 0x34:
  - Bit 0: Sub CPU ready flag (set when ready, cleared when starting transfer)
  - Bit 1: Completion signal from interrupt handler
  - Bit 2: Gate for command processing in InterCPU_RX_Handler
  - Bit 4: Main CPU ready flag (polled by sub CPU)
- Commands sent via `INTER_CPU_LATCH` at 0x120000:
  - E1 command: Multi-stage DMA transfer (two-phase with 200-cycle delays)
  - E2 command: Payload transfer (10-byte parameter block)
  - E3 command: Payload ready signal (sets bit 6 of SUBCPU_STATUS_FLAGS)
  - Other: Low 5 bits = byte count-1, high 3 bits = handler index from table

**Key memory locations discovered:**
- `DMA_BURST_CTRL` (0x0102) - DMA burst mode configuration register
- `PAYLOAD_LOADED_FLAG` (0x04FE) - Payload ready indication flag
- `DMA_SETUP_PARAMS` (0x0502) - DMA parameter storage (XWA, XDE, BC)
- `E1_XFER_PARAMS` (0x050C) - E1 command transfer parameters (two-phase phase 1)
- `DMA_XFER_STATE` (0x0516) - DMA transfer state: 0=idle, 1=single xfer, 2=two-phase
- `E2_XFER_PARAMS` (0x053E) - E2 command transfer parameters (two-phase phase 2)
- `AUDIO_HW_BASE` (0x100000) - Audio hardware registers (DSP/DAC)

**Encoding fixes applied:**
- `jrl T` (3-byte relative long jump) vs `jp` (4-byte absolute)
- `ldir` encoding: TMP94C241 uses `83 11`, ASL generates `85 11`
- `ld r, imm8` encoding: TMP94C241 uses different opcodes for A, D, E, L, W
- `ld (XIX/XHL), imm16` encoding: 4-byte vs 3-byte
- `ld (24-bit addr), imm16` encoding: 7-byte `LD_MEM24_IMM16` macro

This marks the second 100% complete ROM in the project, after Sub CPU Payload!

### Table Data (66.70% incorrect)

The Table Data ROM contains the first-stage bootloader, Feature Demo presentation data, and various lookup tables.

**First-Stage Bootloader (100% matching):**

The boot code section (0x9FB4D2-0x9FFFFF, 19,246 bytes) is now **100% byte-matching**. This includes:

| Component | Address Range | Size | Description |
|-----------|---------------|------|-------------|
| `Boot_BitMaskTable` | 0x9FB4D2-0x9FB4E7 | 22 bytes | Initialization data tables |
| `Boot_Init` | 0x9FB4E8-0x9FB704 | 540 bytes | CPU/memory controller initialization |
| `Boot_EnterHalt` | 0x9FB705-0x9FB73F | 59 bytes | HALT handler and interrupt dispatcher |
| `Boot_ClearRAM` | 0x9FB740-0x9FB7F1 | 178 bytes | RAM initialization and data copy |
| Boot routines (pre-LZSS) | 0x9FB7F2-0x9FC8C1 | 4,304 bytes | Flash update, FDC, display utilities |
| **LZSS Decoder Suite** | 0x9FC8C2-0x9FCA4F | 872 bytes | Complete decompression subsystem |
| Boot routines (post-LZSS) | 0x9FCC2A-0x9FFEE0 | 12,982 bytes | Remaining boot utilities |
| `RESET_HANDLER` | 0x9FFEE0-0x9FFEFF | 32 bytes | Entry vector (JP to Boot_Init) |
| Interrupt vectors | 0x9FFF00-0x9FFFFF | 256 bytes | TMP94C241F vector table |

**LZSS Decoder Routines (fully disassembled):**

| Routine | Address | Size | Purpose |
|---------|---------|------|---------|
| `LZSS_ReadByte` | 0x9FC8C2 | 115 bytes | Read from compressed stream with sector buffering |
| `LZSS_OutputByte` | 0x9FC935 | 63 bytes | Write decompressed bytes with 32-bit batching |
| `LZSS_OutputByte_Alt` | 0x9FC974 | 63 bytes | Alternative output for flash update mode |
| `LZSS_ParseHeader` | 0x9FC9B3 | 157 bytes | Parse/validate firmware header, setup source |
| `LZSS_Decompress` | 0x9FCA50 | 474 bytes | Main decompression loop with sliding window |

The LZSS decoder uses the SLIDE4K format (4KB sliding window, 12-bit offset, 4-bit length) and is invoked during flash firmware updates to decompress packed firmware files.

**Key discovery:** The interrupt vector table contains boot-time addresses (0xFFxxxx) because at reset the table_data ROM is mapped at 0xE00000-0xFFFFFF, not 0x800000-0x9FFFFF. The bootloader reconfigures the memory controller to remap the ROMs.

**System Update Bitmaps (shared with Main CPU):**

The Table Data ROM contains 8 system update message bitmaps at `0x9FA156`. These are 1-bit monochrome images (224x22 pixels, 616 bytes each) that are **byte-identical** to the Main CPU versions. The disassembly source shares the same bitmap files between both ROMs.

| Address | Image | Purpose |
|---------|-------|---------|
| 0x9FA156 | Flash Memory Update | Update in progress |
| 0x9FA3BE | Now Erasing | Flash erase in progress |
| 0x9FA626 | FD to Flash Memory | Copying from floppy |
| 0x9FA88E | Completed | Operation complete |
| 0x9FAAF6 | Please Wait | Processing |
| 0x9FAD5E | Change FD 2 of 2 | Multi-disk prompt |
| 0x9FAFC6 | Illegal Disk | Invalid disk error |
| 0x9FB22E | Turn On AGAIN | Restart instruction |

**ROM Interleaving:** The Table Data ROM uses 16-bit **word-level** interleaving across two physical chips (odd.ic1 and even.ic3). The combined ROM file `kn5000_table_data.rom` is created by alternating 16-bit words from each chip, not individual bytes.

**Shared Code with Main CPU (bootloader routines):**

Analysis revealed that several bootloader routines in the Table Data ROM are **byte-identical** or **semantically identical** to utility routines in the Main CPU ROM. This indicates both ROMs were built from common source code.

**Shared Source Files (in `shared/` directory):**

The disassembly now uses actual shared source files that are included by both ROMs:

| File | Lines | Description |
|------|-------|-------------|
| `shared/vga_constants.s` | 58 | VGA register addresses and constants |
| `shared/vga_init.s` | 135 | VGA initialization data tables |
| `shared/vga_init.s` | 28 | VGA init completion code |
| `shared/vga_io.s` | 51 | VGA register I/O routines (byte-identical) |
| `shared/boot_call_init_handlers.s` | 87 | Init handler dispatch (conditional assembly) |
| `shared/boot_routines.s` | 630 | Boot initialization routines |
| `shared/boot_routines.s` | 85 | LZSS compression decoder |

**Total shared source: 1,074 lines across 7 files**

**Shared Routine Mapping:**

| Table Data | Main CPU | Size | Routine |
|------------|----------|------|---------|
| 0x9FCDFC-0x9FCE1D | 0xEF5141-0xEF515F | 30-34 bytes | `Write_VGA_Register`, `Read_VGA_Register` |
| 0x9FB70A-0x9FB73F | 0xEF086F-0xEF08A3 | 53-54 bytes | `Boot_CallInitHandlers` |
| 0x9FCD9A-0x9FD7BD | 0xEF50DF-0xEF5B02 | 2,596 bytes | `VRAM_FillRect` and display routines |
| 0x9FBC3C-0x9FBECF | 0xEF3CE0-0xEF3F73 | 660 bytes | Boot utility routines |
| 0x9FB4F2-0x9FB622 | 0xEF03D0-0xEF0500 | 305 bytes | Boot initialization code |

**Conditional Assembly:**

Some shared routines have minor encoding differences between ROMs (e.g., byte vs word comparison, different helper addresses). These are handled with conditional assembly:

```asm
; Example from boot_call_init_handlers.s
IF INIT_FLAG_COMPARE_WORD
  ; table_data: CP (0xFFFEEE), 0xFFFF (7 bytes)
  db 0D2h, 0EEh, 0FEh, 0FFh, 03Fh, 0FFh, 0FFh
ELSE
  ; maincpu: CP (0xFFFEEE), 0xFF (6 bytes)
  db 0C2h, 0EEh, 0FEh, 0FFh, 03Fh, 0FFh
ENDIF
```

Each ROM defines the required parameters before including the shared file.

**Compressed Data Identified:**

| Address | Contents | Format |
|---------|----------|--------|
| 0x8E0000 | Compressed preset/parameter data | SLIDE4K LZSS (~33KB decompressed) |
| 0x9FA000 | Update file type headers | "SLIDE" markers |

**Note:** The LZSS data at 0x8E0000 decompresses to ~33KB of parameter data, NOT the ~192KB Sub CPU executable. See [LZSS Compression](lzss-compression.md) for analysis.

**Reference disassembly:** `original_ROMs/table_data_bootcode.unidasm` (6,704 lines)

**Remaining work:**
- Feature Demo XML and BMP images (documented but not all extracted)
- Analysis of decompressed parameter data from 0x8E0000
- Trace Sub CPU payload transfer path during boot
- Various lookup tables and data structures
- Boot routines in `bootcode_pre_lzss.bin` and `bootcode_post_lzss.bin`

## Technical Notes

### TMP94C241F vs TMP96C141

Instructions unique to TMP94C241F that require macro workarounds:
- Memory-to-memory `LD` (not supported by TLCS-900)
- Certain shift/rotate variants
- Some MUL/DIV variants
- LDI, LDIR, LDD, LDDR block transfer instructions
- DMA control register access (`LDC` with DMAS/DMAD/DMAC/DMAM registers)

### ASL Macro Workarounds (tmp94c241.inc)

The `tmp94c241.inc` file contains macros that emit raw byte sequences for unsupported instructions.

**DMA Register Macros:**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `LDC_DMAS0_XWA` | `e8 2e 00` | Load DMA source 0 from XWA |
| `LDC_DMAS2_XDE` | `ea 2e 08` | Load DMA source 2 from XDE |
| `LDC_DMAS2_XHL` | `eb 2e 08` | Load DMA source 2 from XHL |
| `LDC_DMAD0_XWA` | `e8 2e 20` | Load DMA destination 0 from XWA |
| `LDC_DMAD0_XBC` | `e9 2e 20` | Load DMA destination 0 from XBC |
| `LDC_DMAD2_XWA` | `e8 2e 28` | Load DMA destination 2 from XWA |
| `LDC_DMAC0_WA` | `d8 2e 40` | Load DMA count 0 from WA |
| `LDC_DMAC0_A` | `c9 2e 42` | Load DMA count 0 from A |
| `LDC_DMAC2_A` | `c9 2e 4a` | Load DMA count 2 from A |
| `LDC_DMAC2_BC` | `d9 2e 48` | Load DMA count 2 from BC |
| `LDC_DMAC2_WA` | `d8 2e 48` | Load DMA count 2 from WA |

**Additional Sub CPU Boot ROM Macros:**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `INC_0_XBC` | `e9 60` | Increment XBC by 1 |
| `PUSH_WORD value` | `0b LL HH` | Push 16-bit immediate |
| `CP_pXWA_WORD value` | `90 3f LL HH` | Compare (XWA) with 16-bit immediate |
| `CP_pXBC_d_WORD d,val` | `99 dd 3f LL HH` | Compare (XBC+d) with 16-bit immediate |
| `LDA_XWA_IMM24 value` | `f2 LL MM HH 30` | Load 24-bit address into XWA |
| `CALR target` | `1e LL HH` | Call relative (3-byte encoding) |
| `CALL_ABS24 target` | `1d LL MM HH` | Call absolute with 24-bit address |
| `JRL_T target` | `78 LL HH` | Jump relative long (always true) |
| `LDIR_94` | `83 11` | Block copy (TMP94C241 encoding) |
| `LD_A value` | `21 nn` | Load immediate to A register |
| `LD_D value` | `24 nn` | Load immediate to D register |
| `LD_E value` | `25 nn` | Load immediate to E register |
| `LD_L value` | `27 nn` | Load immediate to L register |
| `LD_W value` | `20 nn` | Load immediate to W register |
| `LD_pXIX_IMM16 value` | `b4 02 LL HH` | Store 16-bit imm to (XIX) |
| `LD_pXHL_IMM16 value` | `b3 02 LL HH` | Store 16-bit imm to (XHL) |
| `LD_MEM24_IMM16 addr,val` | `f2 LL MM HH 02 VV WW` | Store 16-bit to 24-bit addr |

**Stack Frame and Register Macros (DMA routines):**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `DEC_6_XSP` | `ef 6e` | Decrement XSP by 6 (allocate stack frame) |
| `INC_6_XSP` | `ef 66` | Increment XSP by 6 (deallocate stack frame) |
| `LD_IZ_BC` | `d9 8e` | Load IZ from BC |
| `CP_IZ_imm16 val` | `de cf LL HH` | Compare IZ with 16-bit immediate |
| `SUB_IZ_imm16 val` | `de ca LL HH` | Subtract 16-bit immediate from IZ |
| `LD_C_IZL` | `c7 f8 8b` | Load C from low byte of IZ |
| `EXTZ_WA` | `d8 12` | Zero-extend A to WA |
| `EXTZ_BC` | `d9 12` | Zero-extend C to BC |

**Stack-Relative Addressing Macros:**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `LD_A_pXSP_d disp` | `8f dd 21` | Load A from (XSP+disp) |
| `LD_XDE_pXSP_d disp` | `af dd 22` | Load XDE from (XSP+disp) |
| `LD_XBC_pXSP_d disp` | `af dd 21` | Load XBC from (XSP+disp) |
| `LD_pXSP_d_A disp` | `bf dd 41` | Store A to (XSP+disp) |
| `LD_pXSP_d_XDE disp` | `bf dd 62` | Store XDE to (XSP+disp) |
| `ADD_pXSP_d_XWA disp` | `af dd 88` | Add XWA to (XSP+disp) |

### Encoding Differences

ASL sometimes chooses different (but functionally equivalent) encodings than the original ROM:

| Instruction | Original | ASL Default | Notes |
|-------------|----------|-------------|-------|
| `lda XWA, imm16` | 5-byte (24-bit addr) | 4-byte (16-bit) | Use `LDA_XWA_IMM24` macro |
| `call addr` | 3-byte `calr` | 4-byte `call` | Use `CALR` macro when target is within range |
| `jp addr` | 3-byte `jrl T` | 4-byte `jp` | Use `JRL_T` macro for relative long jump |
| `ldir` | `83 11` | `85 11` | Use `LDIR_94` macro for TMP94C241 encoding |
| `ld A, imm8` | `21 nn` | Different | Use `LD_A` macro |
| `ld D, imm8` | `24 nn` | Different | Use `LD_D` macro |

These encoding differences cause byte mismatches even when the code is functionally correct.

### Build Process

```bash
cd kn5000-roms-disasm
make all              # Build all ROMs
python compare_roms.py # Verify against originals
```

## Recent Improvements

### March 2026: Sound Data C Struct Conversion and Code Quality

**15 sound data files converted to C structs** — Raw byte arrays in `maincpu/audio/sound_data/` converted to typed C struct arrays with named fields, section labels, and `_Static_assert` size verification. Files include piano, guitar, strings/vocal, organ, brass, flute, sax/reed, mallet/orch perc, drum kits, and more. The `sepaout_config.s` data was also converted to a C struct with separator/output configuration fields.

**1,398 generic labels renamed to semantic names** — Remaining hex-suffixed parameter labels, `.set` aliases, and address-based labels across all source files replaced with sequential or descriptive names.

**LLVM backend improvements** — Misaligned memory access fix, D7 prevbank disassembler fix, SRI prefix encoding fix for R+d16 addressing, F0 8-bit direct memory support, auto-increment addressing, round-trip assembly tests, `.word`/`.hword` directive support, and `calr` relative call fix. Backend documentation added.

**MAME driver style audit passed** — All upstream PR branches reviewed for MAME code style compliance.

### March 2026: Complete LABEL_XXXXXX Elimination

**All address-based labels replaced with semantic names across the entire ROM set.** Every `LABEL_XXXXXX` placeholder (e.g., `FileIO_ValidateWithExtHeader`) has been analyzed and renamed to a meaningful, descriptive name reflecting its purpose (e.g., `FileIO_ValidateWithExtHeader`, `SeqByteBlock_DispatchJumpTable`). This represents the completion of a major project goal:

- **~10,000 labels renamed** across 94+ source files in maincpu alone
- **0 LABEL_XXXXXX remaining** in any ROM directory (maincpu, subcpu, hdae5000, table_data, custom_data)
- All renames verified with full `make clean && make all` + `compare_roms.py` (100% byte match maintained)
- Cross-file references updated atomically to prevent broken symbol errors

This milestone significantly improves codebase navigability and makes the disassembly a true semantic representation of the firmware, not just a mechanical address-to-instruction translation.

### March 2026: R+d16 Addressing, Semantic Naming, Symbolic Handlers, Waveform ROM

**357 R+d16 .byte instructions converted to native mnemonics** — With new LLVM backend support for R+d16 source memory addressing (C3/D3/E3 SRI prefix), 357 `.byte` fallbacks across maincpu and subcpu ROMs were converted to native assembly. Largest contributors: midi_dispatch_handlers (173), subprogram (26), sequencer_ui (25), scoop_display (23), graphics_text_vga (22). All 6 ROMs maintain 100% byte match.

**16 NAKA UI widget files renamed to semantic names** — Previously opaque address-based filenames (e.g., `ui_widgets_EBxxxx.s`) renamed to descriptive names based on reverse engineering research (e.g., `technichord_string_data.s`, `sound_editor_widgets.s`), improving codebase navigability.

**All 26 NAKA widget C files converted to named struct format** — Raw `unsigned char data[N] = { 0xNN, ... }` byte arrays replaced with packed C structs using named fields, `NAKA_HDR()` type headers, `NAKA_ADDR()` pointer symbol resolution, and `_Static_assert` size verification. Pointer tables have 800+ external symbols resolved via ELF symbol table. Named regions derived from `.equ` offsets in assembly wrappers provide clear structural decomposition of widget descriptors, string tables, bitmap data, palette entries, and handler configuration.

**All C screen data `.handler` fields now use symbolic references** — 52 handler symbols across 2 linker scripts (`maincpu.ld`, `ctlonly.ld`) replace raw numeric addresses in the C-compiled screen data structures, enabling cross-reference navigation and maintaining the link between C UI definitions and assembly handler routines.

**IC307 waveform ROM format fully decoded** — The waveform ROM (IC307, 4MB) format has been fully reverse-engineered: 16-bit signed PCM samples at 32kHz, organized as a sample table (512 entries with start/end/loop addresses) followed by raw sample data. See [Waveform ROM Format](/waveform-rom-format/) for full documentation.

### Binary Include Splitting

Per project policy, binary includes are split when code references internal addresses. This ensures:
- Cross-references use symbolic labels instead of hardcoded addresses
- Smaller binary files are easier to analyze
- Data structure boundaries are explicitly marked

**Recently split:**
- `e02510_e06baf.bin` split into three parts:
  - `e02510_e0458f.bin` - Instrument category data (PIANO, ORGAN, etc.)
  - `e04590_e04b2f.bin` - GUITAR data
  - `e04b30_e06baf.bin` - STRINGS & VOCAL data
- `e06f30_e0adcf.bin` split into four parts:
  - `e06f30_e078f1.bin` - FLUTE sound data
  - `e078f2_e08baf.bin` - Additional FLUTE data
  - `e08bb0_e0914f.bin` - SAX & REED sound data
  - `e09150_e0adcf.bin` - MALLET & ORCH PERC sound data
- `e0bb90_e0e974.bin` split into seven parts for instrument data tables
- `e0b250_e0ba60.bin` split into nineteen parts for orchestral pad data (many internal cross-references)

### Control Panel Protocol Naming

Significant naming improvements applied to the control panel serial protocol code (0xFC3E00-0xFC7FFF):

**Packet Processing:**
- `CPanel_RX_ProcessWithFlag` / `CPanel_RX_Process` - Entry points
- `CPanel_RX_ParseNext` - Main packet processing loop
- `CPanel_RX_PacketHandlers` - Jump table for packet type dispatch

**Packet Type Handlers:**
- `CPanel_RX_ButtonPacket` - Button state packets (types 0, 1)
- `CPanel_RX_EncoderPacket` - Rotary encoder data (type 2)
- `CPanel_RX_SyncPacket` - Sync/ack packets (types 3, 4, 5)
- `CPanel_RX_MultiBytePacket` - Multi-byte packets (types 6, 7)

**LED and Initialization:**
- `CPanel_UpdateLEDs` - LED state transmission
- `CPanel_InitLEDBuffer` - Serial/LED initialization
- `CPanel_InitButtonState` - Button state array setup

**Variables:**
- `CPANEL_RX_PACKET_BYTE_1` / `CPANEL_RX_PACKET_BYTE_2` - Incoming packet bytes (formerly `CPANEL_UNUSED_2/3`)
