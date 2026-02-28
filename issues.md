---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 237 (82 open, 154 closed)

**Quick Links:** 
[Feature Demo](#feature-demo) (11) · [Firmware Update](#firmware-update) (8) · [HD-AE5000 Expansion](#hd-ae5000-expansion) (2) · [Other](#other) (51) · [Sound & Audio](#sound-audio) (10)

---

## Open Issues

### Feature Demo {#feature-demo}

#### 🟠 FeatureDemo: Identify and catalog UI widget types {#issue-kn5000-x13}

**ID:** `kn5000-x13` | **Priority:** High | **Created:** 2026-01-25

Analyze slide rendering code to identify all widget types: static text, styled text, images/icons, rectangles, lines, buttons, animations, piano keyboard display, waveform display, level meters. Document rendering parameters for each type.

---

#### 🟠 FeatureDemo: Locate slide data structures in ROM {#issue-kn5000-h7o}

**ID:** `kn5000-h7o` | **Priority:** High | **Created:** 2026-01-25

Find where Feature Demo presentation data is stored. Search for references to FTBMP01-06 images. Identify: slide table/index, per-slide data records, pointers to resources (images, text, MIDI). Document base addresses and overall structure.

---

#### 🟠 FeatureDemo: Reverse engineer slide record format {#issue-kn5000-bds}

**ID:** `kn5000-bds` | **Priority:** High | **Created:** 2026-01-25

Document the binary format of each slide record. Identify fields: slide type, duration/timing, background image ID, widget list pointer, MIDI file pointer, transition effects. Create struct definition documenting each field offset and size.

---

#### 🟡 FeatureDemo: Create ASL macros for slide definitions {#issue-kn5000-4q0}

**ID:** `kn5000-4q0` | **Priority:** Medium | **Created:** 2026-01-25

Design and implement ASL assembler macros for concise slide definitions: SLIDE_BEGIN/END, WIDGET_TEXT, WIDGET_IMAGE, WIDGET_RECT, SLIDE_MIDI, SLIDE_TIMING, etc. Macros should emit correct binary format while being human-readable.

---

#### 🟡 FeatureDemo: Create ASL macros for widget definitions {#issue-kn5000-br1}

**ID:** `kn5000-br1` | **Priority:** Medium | **Created:** 2026-01-25

Implement widget-specific macros: TEXT x,y,font,color,"string" / IMAGE x,y,id / RECT x,y,w,h,color / LINE x1,y1,x2,y2,color / BUTTON x,y,w,h,label. Ensure macros handle alignment and padding correctly.

---

#### 🟡 FeatureDemo: Document widget parameter formats {#issue-kn5000-dqi}

**ID:** `kn5000-dqi` | **Priority:** Medium | **Created:** 2026-01-25

For each widget type, document all parameters: position (x,y), size (w,h), colors, font ID, text string pointer, image ID, alignment, padding, border style, animation params. Create comprehensive widget parameter reference.

---

#### 🟡 FeatureDemo: Extract MIDI files as standalone files {#issue-kn5000-kxw}

**ID:** `kn5000-kxw` | **Priority:** Medium | **Created:** 2026-01-25

Extract all embedded MIDI data as playable .mid files. Parse MIDI structure to find exact boundaries. Name files descriptively. Verify extracted files play correctly in standard MIDI player. Add to project assets.

---

#### 🟡 FeatureDemo: Locate embedded MIDI data {#issue-kn5000-qjx}

**ID:** `kn5000-qjx` | **Priority:** Medium | **Created:** 2026-01-25

Find all embedded MIDI files in the ROM. Search for MIDI headers (4D 54 68 64 = 'MThd'). Document: offset, size, apparent purpose (demo song, UI sound, jingle). May be in main CPU ROM or table data ROM.

---

#### 🟡 FeatureDemo: Refactor assembly to use slide macros {#issue-kn5000-21e}

**ID:** `kn5000-21e` | **Priority:** Medium | **Created:** 2026-01-25

Replace raw data definitions in assembly source with new macros. Convert existing db/dw sequences to SLIDE_BEGIN, WIDGET_*, SLIDE_END. Verify rebuilt ROM still matches original byte-for-byte. Measure source code line reduction.

---

#### ⚪ FeatureDemo: Create slide viewer/editor tool {#issue-kn5000-waa}

**ID:** `kn5000-waa` | **Priority:** Low | **Created:** 2026-01-25

Build a tool to parse and display Feature Demo slides outside the keyboard. Could be Python script with PIL/Pillow for rendering. Useful for: verifying extraction, editing slides, creating custom demos. Output as PNG or HTML.

---

#### ⚪ FeatureDemo: Document demo sequence and timing {#issue-kn5000-0bq}

**ID:** `kn5000-0bq` | **Priority:** Low | **Created:** 2026-01-25

Create complete documentation of the Feature Demo: slide order, timing between slides, which MIDI plays when, user interaction points (if any), loop behavior. Add screenshots/video to documentation website.

---

### Firmware Update {#firmware-update}

#### 🟡 Update: Document FDC interaction during update {#issue-kn5000-70b}

**ID:** `kn5000-70b` | **Priority:** Medium | **Created:** 2026-01-25

Trace how the Floppy Disk Controller (0x110000) is used during updates. Document: disk detection, file reading sequence, sector layout, error recovery, multi-disk handling (Change FD 2 of 2 message).

---

#### 🟡 Update: Document HDAE5000 update procedure {#issue-kn5000-e7f}

**ID:** `kn5000-e7f` | **Priority:** Medium | **Created:** 2026-01-25

Analyze how HD-AE5000 firmware is updated. Document: separate update disk format, communication via PPI (0x160000), Flash chips on expansion board, version compatibility checks. Reference v1.10i through v2.0i updates.

---

#### 🟡 Update: Document update progress display {#issue-kn5000-6f7}

**ID:** `kn5000-6f7` | **Priority:** Medium | **Created:** 2026-01-25

Analyze LCD messages during update process. Correlate extracted 1-bit bitmaps with update stages: Flash Memory Update, Please Wait, Now Erasing, FD to Flash Memory, Completed, Turn On AGAIN, Illegal Disk. Document state machine.

---

#### 🟡 Update: Document validation and error handling {#issue-kn5000-acu}

**ID:** `kn5000-acu` | **Priority:** Medium | **Created:** 2026-01-25

Trace update validation routines. Document: file header validation, checksum algorithms, version checking, ROM verification after write, error recovery procedures, what triggers 'Illegal Disk' message.

---

#### 🟡 Update: Reverse engineer Flash erase algorithm {#issue-kn5000-dkx}

**ID:** `kn5000-dkx` | **Priority:** Medium | **Created:** 2026-01-25

Trace the Flash ROM erase routine in firmware. Document: chip unlock sequence, sector erase commands, chip erase commands, erase verification, timeout handling. Note any chip-specific variations. Cross-reference with Flash datasheet.

---

#### 🟡 Update: Reverse engineer Flash program algorithm {#issue-kn5000-1tn}

**ID:** `kn5000-1tn` | **Priority:** Medium | **Created:** 2026-01-25

Trace the Flash ROM programming routine. Document: byte/word program commands, unlock sequences, program verification, error handling, write protection. Identify if using byte-program or page-buffer mode.

---

#### ⚪ Update: Create update file parser tool {#issue-kn5000-87m}

**ID:** `kn5000-87m` | **Priority:** Low | **Created:** 2026-01-25

Build Python tool to parse and analyze update floppy files. Extract: header info, version numbers, payload data, checksums. Enable creation of custom update files for homebrew development.

---

#### ⚪ Update: Document complete update procedure for users {#issue-kn5000-7v8}

**ID:** `kn5000-7v8` | **Priority:** Low | **Created:** 2026-01-25

Write end-user documentation for performing system updates. Include: required materials, step-by-step instructions, troubleshooting, safety warnings about power loss during update. Add to documentation website.

---

### HD-AE5000 Expansion {#hd-ae5000-expansion}

#### 🟡 HDAE5000: Document interface cable pinout {#issue-kn5000-mzz}

**ID:** `kn5000-mzz` | **Priority:** Medium | **Created:** 2026-01-25

Determine the pinout of the cable connecting HD-AE5000 to KN5000. Identify connector types, signal assignments (accent data, accent control, accent bus, accent power), and voltage levels. Reference service manual if available.

---

#### ⚪ HDAE5000: Analyze HD-TechManager5000 software {#issue-kn5000-qnf}

**ID:** `kn5000-qnf` | **Priority:** Low | **Created:** 2026-01-25

Reverse engineer the Windows HD-TechManager5000 software to understand the PC side of the parallel port protocol. Extract command definitions, file format handling, and UI functionality. Installation disks available at archive.org.

---

### Other {#other}

#### 🔴 Phase 1 Completion: All MAME blockers resolved {#issue-kn5000-dbi}

**ID:** `kn5000-dbi` | **Priority:** Critical | **Created:** 2026-01-31

**Notes:** Meta-issue tracking Phase 1 completion (Foundation - MAME Blockers).

## Phase 1 Goals
Get basic MAME emulator running with display and sound output.

## Component Milestones
- kn5000-8z5: Display subsystem emulation
- kn5000-y18: Audio subsystem emulation
- kn5000-5a0: Fix 177 divergent bytes
- kn5000-d1x: Table Data ROM structure

## Blockers to Resolve
1. **Display** - Need pixel format, palette, framebuffer layout
2. **Audio** - Need DSP effects, Sub CPU command protocol
3. **ROM** - 177 bytes at 0xFDDE5F need instruction audit

## Success Criteria
- [ ] MAME boots to splash screen
- [ ] Basic audio output works
- [ ] Main CPU ROM at 100%
- [ ] All P1 display issues closed
- [ ] All P1 audio issues closed

## Timeline Estimate
Phase 1 represents the critical path to functional emulation.

---

#### 🔴 Plan: Long-term project roadmap and phase tracking {#issue-kn5000-3go}

**ID:** `kn5000-3go` | **Priority:** Critical | **Created:** 2026-01-30

**Notes:** Master roadmap for KN5000 reverse engineering project.

## Project Goals
1. **100% ROM Reconstruction** - Byte-accurate rebuilds of all firmware
2. **MAME Emulation** - Full system emulation for preservation
3. **Homebrew Development** - Enable custom software creation
4. **Documentation** - Complete technical reference

## Phase Structure with Tracking Issues

### Phase 1: Foundation (MAME Blockers) - kn5000-dbi
*Goal: Get basic emulator running with display and sound*

**Display System (kn5000-8z5):**
- kn5000-ezo: VGA register documentation [P1]
- kn5000-3c5: Framebuffer memory layout [P1]
- kn5000-hy8: Pixel format and palette [P1]
- kn5000-gln: Drawing primitives [P1]

**Audio System (kn5000-y18):**
- kn5000-1oy: DSP effects processing [P1]
- kn5000-xv2: DSP IC311 documentation [P1]
- kn5000-xel: DAC IC310 documentation [P1]

**ROM Reconstruction:**
- kn5000-5a0: Fix 177 divergent bytes [P1]
- kn5000-d1x: Table Data ROM structure [P1]

### Phase 2: Core Functionality - kn5000-dnl
*Goal: User interaction and file I/O working*

**UI/Input (kn5000-1vz):**
- kn5000-kev: Font system [P2]
- kn5000-5dc: Widget rendering [P2]
- kn5000-qhm: Control panel HLE [P2]
- kn5000-3c7: Analog controllers [P2]

**Storage (kn5000-a0k):**
- kn5000-ima: FDC subsystem [P2]
- kn5000-kuu: HDAE5000 ROM [P1]

### Phase 3: Complete Documentation - kn5000-9m6
*Goal: All subsystems fully documented*

**Documentation (kn5000-8ro):**
- Complete all placeholder subsystem pages
- audio-subsystem.md, display-subsystem.md, midi-subsystem.md
- ui-framework.md, sequencer.md, storage-subsystem.md

**Audio Details:**
- kn5000-81p: Technics SysEx format
- kn5000-5ck: Proprietary CC handlers
- kn5000-rlb: Voice allocation

**Storage Details:**
- kn5000-bqe: Custom Data Flash
- kn5000-44c: HDAE5000 filesystem

**Boot/Init:**
- kn5000-mhj: Complete boot timeline
- kn5000-izk: HDAE5000 detection

### Phase 4: Quality & Polish - kn5000-nca
*Goal: Production-ready emulation and homebrew support*

**Symbol Cleanup:**
- kn5000-9jq: Sub CPU symbols
- kn5000-4bt: UI framework symbols
- kn5000-aar: Naming convention guide

**Tools (kn5000-5jy):**
- kn5000-waa: Slide viewer/editor
- kn5000-87m: Update file parser
- kn5000-pkx: Image converter

**Documentation:**
- kn5000-9a0: Website maintenance
- kn5000-sf8: Code reference tables

**Validation (kn5000-a8s):**
- Emulation validation procedures

## Current Status (Jan 2026)
- ROM reconstruction: 59.54% overall
- Main CPU: 99.99% (177 bytes divergent)
- Sub CPU: 100% complete
- Table Data: 32.42%
- MAME PR: #14558 in progress

## Success Criteria
- [ ] All ROMs 100% byte-matching
- [ ] MAME driver merged upstream
- [ ] All subsystems documented
- [ ] Homebrew SDK available

## Phase Tracking Issues
- Phase 1: kn5000-dbi (P0 - Current Focus)
- Phase 2: kn5000-dnl (P1)
- Phase 3: kn5000-9m6 (P2)
- Phase 4: kn5000-nca (P3)

---

#### 🟠 Audio: Analyze DSP effects processing algorithms {#issue-kn5000-1oy}

**ID:** `kn5000-1oy` | **Priority:** High | **Created:** 2026-01-30

**Notes:** DSP effects processing is critical for audio emulation.

**Current state:** Dual DSP architecture documented, but register meanings and effect algorithms unknown.

**Required work:**
- Trace DSP register writes at 0x130000
- Document effect parameter mapping
- Analyze reverb, chorus, delay implementations
- Map effect chain configuration

**Phase:** 1 - Foundation (MAME Blockers)
**Blocks:** Audio synthesis in MAME
**Dependencies:** Audio hardware documentation
**Related:** kn5000-xv2 (DSP IC311), kn5000-si0 (effects chain)

---

#### 🟠 Display: Document VGA register set for MN89304 controller {#issue-kn5000-ezo}

**ID:** `kn5000-ezo` | **Priority:** High | **Created:** 2026-01-30

**Notes:** The MN89304 VGA controller at 0x170000 needs complete register documentation.

**Current state:** Hardware location known, but register meanings undocumented.

**Required work:**
- Identify VGA register port addresses (standard VGA at 0x3C0-0x3DF?)
- Document initialization sequence from boot code
- Map control registers for resolution, timing, color depth
- Document any non-standard extensions

**Phase:** 1 - Foundation (MAME Blockers)
**Blocks:** Display rendering in MAME emulator
**Dependencies:** None
**Related:** kn5000-hy8 (color palette), kn5000-gln (drawing primitives)

---

#### 🟠 Document jump tables in maincpu ROM {#issue-kn5000-6je}

**ID:** `kn5000-6je` | **Priority:** High | **Created:** 2026-01-26

**Notes:** The maincpu ROM contains numerous jump tables used for dispatch. Found patterns include:

**Indirect call patterns:**
- CALL T, XHL - calls through XHL register
- CALL T, XIX - calls through XIX register
- JP T, XIX + WA - indexed jump with WA offset
- JP T, XIX + BC - indexed jump with BC offset
- JP T, XIX + DE - indexed jump with DE offset

**Known jump tables:**
1. HANDLE_UPDATE_OFFSETS (0xE00178) - 16-bit offset table for update file handling
2. LABEL_EF0D64 - 3-entry address table for state machine
3. LABEL_EF0DA5 - 16-entry address table for sub-state handling
4. Large address table at line 36362 (~170 entries for handler dispatch)
5. Address tables at E1611A, E16128, E16136 (encoder handling)
6. Jump table at F97D8D with 12+ undisassembled target routines

**Work needed:**
- Label all jump tables with meaningful names
- Ensure all target routines are disassembled
- Document the purpose of each table
- Create cross-references in comments

---

#### 🟠 Extract hardware info from service manual schematics {#issue-kn5000-z9k}

**ID:** `kn5000-z9k` | **Priority:** High | **Created:** 2026-01-25

Analyze the KN5000 service manual (59 pages) to extract hardware architecture details. Focus on: CPU section (II-11), Control section (II-9), Block diagram (II-3/4), Control panel boards (II-35, II-38). Document IC pinouts, signal names, and interconnections.

**Notes:** Significant progress: Analyzed schematic pages II-9 to II-38. Documented main CPU (TMP94C241F), all memory ICs, control panel MCUs (M37471M2196S), button mappings, serial signals. Created hardware-architecture.md page.

**Depends on:** [`kn5000-bcn`](#issue-kn5000-bcn), [`kn5000-jwk`](#issue-kn5000-jwk), [`kn5000-xhi`](#issue-kn5000-xhi)

---

#### 🟠 LLVM: Fix bug #10 — register x/y swap on inlining {#issue-kn5000-8zr}

**ID:** `kn5000-8zr` | **Priority:** High | **Created:** 2026-02-21

**Notes:** LLVM TLCS-900 backend bug #10: When functions are inlined, IX and IY registers get swapped in the generated code. Current workaround: use __attribute__((noinline)) on affected functions (e.g., tile_vram_ptr in Mines). This is one of 2 remaining active bugs in the TLCS-900 backend. Tracked in Mines memory (llvm-encoding-bugs.md).

---

#### 🟠 LLVM: Fix bug #11 — for-loop with uint16_t counter exits after 1 iteration {#issue-kn5000-o3u}

**ID:** `kn5000-o3u` | **Priority:** High | **Created:** 2026-02-21

**Notes:** LLVM TLCS-900 backend bug #11: for-loops using uint16_t counter variables exit after only 1 iteration. Current workaround: use do-while loops with uint32_t counters. Affects VRAM clear and other iteration-heavy code. This is one of 2 remaining active bugs in the TLCS-900 backend. Tracked in Mines memory (llvm-encoding-bugs.md).

---

#### 🟠 MAME: Audio subsystem emulation milestone {#issue-kn5000-y18}

**ID:** `kn5000-y18` | **Priority:** High | **Created:** 2026-01-31

**Notes:** Track completion of audio subsystem emulation for MAME.

## Required Components
- [ ] Sub CPU emulation (ROM at 0xFE0000)
- [ ] Inter-CPU latch communication (0x120000)
- [ ] Payload transfer from Main CPU
- [ ] DSP effects processing
- [ ] Tone generator/voice allocation
- [ ] DAC output

## Related Issues
- kn5000-1oy: DSP effects processing
- kn5000-xv2: DSP IC311 documentation
- kn5000-xel: DAC IC310 documentation
- kn5000-061: Main to Sub CPU command protocol

## Success Criteria
- Sub CPU boots from payload
- Basic sound output works
- MIDI input produces audio

---

#### 🟠 MAME: Display subsystem emulation milestone {#issue-kn5000-8z5}

**ID:** `kn5000-8z5` | **Priority:** High | **Created:** 2026-01-31

**Notes:** Track completion of display subsystem emulation for MAME.

## Required Components
- [ ] VGA register emulation (MN89304 controller)
- [ ] Framebuffer memory at 0x1A0000
- [ ] Pixel format (16-bit RGB565 suspected)
- [ ] Color palette handling
- [ ] Drawing primitives

## Related Issues
- kn5000-ezo: VGA register documentation
- kn5000-3c5: Framebuffer memory layout
- kn5000-hy8: Pixel format and palette
- kn5000-gln: Drawing primitives

## Success Criteria
- LCD displays boot splash correctly
- UI elements render accurately
- Text/fonts appear correctly

---

#### 🟠 MAME: Spurious button events during boot (voice dialog, transpose B) {#issue-kn5000-0eo}

**ID:** `kn5000-0eo` | **Priority:** High | **Created:** 2026-02-21

**Notes:** Running 'make fsanches_test' outside the VM, after boot sequence completes, some actions happen without user input: a dialog for selecting an instrument voice appears, and the screen shows transposition set to B (half step below default C). This suggests spurious button press events (possibly a 'transpose -' event). The control panel HLE or serial protocol may be generating ghost events. Needs investigation in MAME driver or control panel emulation.

---

#### 🟠 MAME: Update HLE based on audio subsystem findings {#issue-kn5000-0o6}

**ID:** `kn5000-0o6` | **Priority:** High | **Created:** 2026-01-30

**Notes:** The audio subsystem reverse engineering provides new information for MAME HLE:

Key findings for emulation:
1. Command dispatch table with 8 handler ranges
2. Ring buffer at 0x2B0D for MIDI-like commands
3. MIDI status byte parsing (0x80-0xF0)
4. Voice parameter handlers for each message type
5. Control Change handlers including proprietary CCs
6. DSP channel configuration at 0x130000

Update mame_driver/ reference files:
- Document command byte ranges in comments
- Add state machine for MIDI parsing if not present
- Ensure CC handlers match discovered behavior

Reference: audio-subsystem.md, midi-subsystem.md, inter-cpu-protocol.md

---

#### 🟠 Phase 2 Completion: Core functionality working {#issue-kn5000-dnl}

**ID:** `kn5000-dnl` | **Priority:** High | **Created:** 2026-01-31

**Notes:** Meta-issue tracking Phase 2 completion (Core Functionality).

## Phase 2 Goals
User interaction and file I/O fully working in MAME.

## Component Milestones
- kn5000-1vz: Input/Control subsystem emulation
- kn5000-a0k: Storage subsystem emulation

## Key Deliverables
1. **UI/Input** - Font system, widget rendering, control panel HLE
2. **Storage** - FDC working, HDAE5000 detected, custom data accessible

## Depends On
- Phase 1 completion (kn5000-dbi)

## Success Criteria
- [ ] UI navigation works via keyboard/mouse
- [ ] Floppy disk loading functional
- [ ] Custom styles can be loaded/saved
- [ ] All P2 UI/input issues closed
- [ ] All P2 storage issues closed

---

#### 🟠 Table Data: Document ROM internal structure and indexing {#issue-kn5000-d1x}

**ID:** `kn5000-d1x` | **Priority:** High | **Created:** 2026-01-30

**Notes:** Table Data ROM (2MB @ 0x800000) internal organization needs reverse engineering.

**Current state:** 32.42% disassembled, mostly binary assets. Structure unknown.

**Required work:**
- Identify index tables for sound/style/demo data
- Document header formats for embedded assets
- Map data type regions within the ROM
- Create tools to extract and catalog assets

**Phase:** 1 - Foundation (MAME Blockers)
**Blocks:** Full Table Data ROM disassembly, asset loading in emulator
**Dependencies:** None
**Related:** kn5000-hlw (improve match %), kn5000-16s (find images)

---

#### 🟡 Analyze ROTA/ROTB rotary encoder circuit {#issue-kn5000-xhi}

**ID:** `kn5000-xhi` | **Priority:** Medium | **Created:** 2026-01-25

Block diagram shows ROTA and ROTB signals from control panel. Find the encoder circuit in schematics, determine: number of encoders, connection to MCU pins, any conditioning circuitry (pull-ups, filters). This helps understand encoder data format in protocol.

---

#### 🟡 Another World: Complete floppy code injection for KN5000 port {#issue-kn5000-yhj}

**ID:** `kn5000-yhj` | **Priority:** Medium | **Created:** 2026-02-21

---

#### 🟡 Audio: Document Technics SysEx message format {#issue-kn5000-81p}

**ID:** `kn5000-81p` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** The KN5000 likely uses Technics-specific System Exclusive messages for:

1. Bulk data dumps (sounds, sequences, settings)
2. Parameter editing
3. Remote control features
4. Device identification

Need to:
1. Find SysEx handling in Main CPU MIDI code
2. Document manufacturer ID and message structure
3. Catalog known SysEx commands
4. Test with external MIDI tools if possible

Search maincpu for: 0xF0 (SysEx start), 0xF7 (SysEx end), manufacturer ID bytes.

---

#### 🟡 Audio: Document all command byte formats (0x00-0xFF) {#issue-kn5000-x95}

**ID:** `kn5000-x95` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** The Sub CPU CMD_DISPATCH_TABLE routes commands by upper 3 bits:

- 0x00-0x1F: Audio_CmdHandler_00_1F (writes to ring buffer) - DOCUMENTED
- 0x20-0x3F: Audio_CmdHandler_20_3F - needs analysis
- 0x40-0x5F: Audio_CmdHandler_40_5F - needs analysis
- 0x60-0x7F: Audio_CmdHandler_60_7F - needs analysis
- 0x80-0x9F: Serial port setup - partially known
- 0xA0-0xBF: Audio_CmdHandler_A0_BF - needs analysis
- 0xC0-0xFF: Audio_CmdHandler_C0_FF - needs analysis

For each range, document:
1. Expected byte format
2. What parameters are affected
3. Example command sequences

Reference: CMD_DISPATCH_TABLE at line 576 in subcpu/kn5000_subprogram_v142.asm

---

#### 🟡 Audio: Document external MIDI I/O on Main CPU {#issue-kn5000-0vs}

**ID:** `kn5000-0vs` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** The Main CPU handles external MIDI IN/OUT/THRU via serial ports. Need to document:

1. Serial port addresses and configuration
2. MIDI parser routines in maincpu
3. MIDI routing logic (how external MIDI reaches Sub CPU)
4. MIDI OUT generation (keyboard events, sequencer playback)
5. MIDI THRU implementation (hardware vs software)

This complements the internal MIDI processing already documented in midi-subsystem.md.

Search maincpu for: Serial port init, MIDI-related strings, writes to Sub CPU for external events.

---

#### 🟡 Audio: Document proprietary CC handlers (0x97, 0x9B-0x9D) {#issue-kn5000-5ck}

**ID:** `kn5000-5ck` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** The Voice_CtrlChange handler in Sub CPU has handlers for proprietary Control Change numbers:

- Voice_CC_97 at 0x02A496
- Voice_CC_9B at 0x02A4AB  
- Voice_CC_9C at 0x02A4C0
- Voice_CC_9D at 0x02A4D5

These are not standard MIDI CCs. Need to:
1. Trace what parameters they modify
2. Determine if they control effects, filters, or other synthesis parameters
3. Document in midi-subsystem.md

Reference: subcpu/kn5000_subprogram_v142.asm around line 25167-25210

---

#### 🟡 Audio: Document tone generator voice allocation {#issue-kn5000-rlb}

**ID:** `kn5000-rlb` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** The ToneGen_Process_Notes routine manages 16 voice slots at 0x4A4C-0x4A5C. Need to understand:

1. Voice stealing algorithm (what happens when all 16 slots are full)
2. Priority system (which notes get stolen first)
3. How sustain pedal affects voice allocation
4. Relationship between tone generator voices and DSP channels

Key routines:
- ToneGen_Process_Notes at 0x03D01E
- ToneGen_Read_Voice_Data at 0x03D0C5
- Voice slot table at 0x4A4C (16 bytes)

Reference: audio-subsystem.md for current tone generator docs.

---

#### 🟡 Audio: Trace sound category data structures at 0xE023B0 {#issue-kn5000-8dy}

**ID:** `kn5000-8dy` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** The Main CPU has a pointer table at 0xE023B0 with 16 sound categories:

0: PIANO, 1: GUITAR, 2: STRINGS & VOCAL, 3: BRASS, 4: FLUTE,
5: SAX & REED, 6: MALLET & ORCH PERC, 7: WORLD PERC, 8: ORGAN & ACCORDION,
9: ORCHESTRAL PAD, 10: SYNTH, 11: BASS, 12: DIGITAL DRAWBAR,
13: ACCORDION REG., 14: GM SPECIAL, 15: DRUM KITS

Need to:
1. Follow pointers to actual sound data
2. Document sound data format (likely references to waveform ROM)
3. Understand how sound selection maps to Sub CPU synthesis
4. Document relationship to Program Change messages

Reference: SOUND_DATA_SECTION_PTRS at 0xE023B0 in maincpu.

---

#### 🟡 Disassemble TODO routines at F97696-F97D8D range (jump table targets) {#issue-kn5000-kc5}

**ID:** `kn5000-kc5` | **Priority:** Medium | **Created:** 2026-01-26

**Notes:** At address 0xF97D8D there's a jump table that references routines at F97696, F976E4, F97835, F97C21, F97C7C, F96BBF, F96BD0, F97984, F97C4B, F97C54, F97C5B, and F96D95. These routines are currently empty ORG labels. Need to disassemble the code at these addresses. Found via jump table pattern: JP T, XIX + WA with LDA XIX, LABEL_F97D8D.

---

#### 🟡 Document ROM interleaving formats for all ROM chips {#issue-kn5000-67g}

**ID:** `kn5000-67g` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** Different ROM components use different interleaving formats. This caused confusion during table_data bitmap extraction.

**Formats discovered:**

| ROM | Interleaving | Notes |
|-----|--------------|-------|
| Main CPU | None (single chip) | 2MB linear |
| Sub CPU Boot | None (single chip) | 128KB linear |
| Sub CPU Payload | None (sent by maincpu) | 192KB linear |
| Table Data | 16-bit WORD-level | odd.ic1 + even.ic3, alternating 16-bit words |
| HDAE5000 | None (single chip) | 512KB linear |

The table_data ROM is NOT byte-interleaved but WORD-interleaved:
- Correct: even[0:2] + odd[0:2] + even[2:4] + odd[2:4] ...
- Wrong: even[0] + odd[0] + even[1] + odd[1] ...

This should be documented in:
1. CLAUDE.md for developer reference
2. rom-reconstruction.md (partially done)
3. Hardware architecture docs

Reference: kn5000_table_data.rom combination analysis

---

#### 🟡 Document binary include e0176c_e01f7f.bin data structure {#issue-kn5000-jqa}

**ID:** `kn5000-jqa` | **Priority:** Medium | **Created:** 2026-01-26

**Notes:** Binary include at 0xE0176C-0xE01F7F (~2KB). Part of jump table area following large address table at line 36362. Need to analyze structure and determine if this is code, data tables, or other data.

---

#### 🟡 Document binary include e02510_e06baf.bin data structure (~295KB) {#issue-kn5000-c9c}

**ID:** `kn5000-c9c` | **Priority:** Medium | **Created:** 2026-01-26

**Notes:** Large binary include at 0xE02510-0xE06BAF (~295KB). This is one of the largest undocumented blocks in the ROM. Need to analyze structure: could be sound data, lookup tables, compressed assets, or code.

---

#### 🟡 Document binary include e06f30_e0adcf.bin data structure (~254KB) {#issue-kn5000-gqu}

**ID:** `kn5000-gqu` | **Priority:** Medium | **Created:** 2026-01-26

**Notes:** Large binary include at 0xE06F30-0xE0ADCF (~254KB). Need to analyze structure: could be sound data, lookup tables, compressed assets, or code.

---

#### 🟡 Document binary include e0b250_e0ba60.bin data structure (~8KB) {#issue-kn5000-baz}

**ID:** `kn5000-baz` | **Priority:** Medium | **Created:** 2026-01-26

**Notes:** Binary include at 0xE0B250-0xE0BA60 (~8KB). Relatively small block that may be easier to analyze. Check for table structure, code, or known data patterns.

---

#### 🟡 Document binary include e0bb90_e0e974.bin data structure (~46KB) {#issue-kn5000-9os}

**ID:** `kn5000-9os` | **Priority:** Medium | **Created:** 2026-01-26

**Notes:** Binary include at 0xE0BB90-0xE0E974 (~46KB). Medium-sized undocumented block. Check for table structure, code, or known data patterns.

---

#### 🟡 Documentation: Complete all subsystem placeholder pages {#issue-kn5000-8ro}

**ID:** `kn5000-8ro` | **Priority:** Medium | **Created:** 2026-01-31

**Notes:** Track completion of all documentation website subsystem pages.

## Placeholder Pages Needing Content
1. audio-subsystem.md - Sound hardware and protocols
2. display-subsystem.md - LCD and graphics system
3. midi-subsystem.md - MIDI I/O and processing
4. ui-framework.md - Widget system and rendering
5. sequencer.md - Song/sequence playback
6. storage-subsystem.md - Partial, needs completion

## Pages Already Documented
- control-panel-protocol.md ✓
- inter-cpu-protocol.md ✓
- hdae5000-disk-interface.md ✓
- boot-sequence.md ✓
- rom-reconstruction.md ✓

## Success Criteria
- All placeholder pages have substantive content
- Code references link to assembly symbols
- Each page has at least one diagram or table

---

#### 🟡 Input: Document analog controller processing (wheels, pedals) {#issue-kn5000-3c7}

**ID:** `kn5000-3c7` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** Pitch bend wheel, modulation wheel, and expression pedal processing needs documentation.

**Current state:** Encoder IDs known from control panel protocol, processing unknown.

**Required work:**
- Trace A/D conversion routines
- Document wheel position scaling/curves
- Map pedal input handling
- Document velocity/aftertouch processing if applicable

**Phase:** 2 - Core Functionality
**Blocks:** Controller emulation accuracy
**Dependencies:** Control panel protocol (complete)
**Related:** kn5000-unb (encoder data format)

---

#### 🟡 Investigate shared graphics data between maincpu and table_data {#issue-kn5000-0r5}

**ID:** `kn5000-0r5` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** Analysis found ~40KB of shared graphics/image data between ROMs:

| Table Data | Main CPU | Size | Density |
|------------|----------|------|---------|
| 0x91D0EA | 0xE90090 | 13,806 bytes | 100% |
| 0x82CDA4 | 0xE93680 | 7,198 bytes | 100% |
| 0x921176 | 0xE7C8B0 | 9,282 bytes | 83.8% |
| 0x809AD6 | 0xEB8190 | 8,964 bytes | 93.7% |

Tasks:
1. Identify what graphics these regions contain (UI elements? fonts?)
2. Check if they are already documented in maincpu
3. Determine if sharing via binclude is feasible
4. Update image-gallery.md if new images are found

The data appears to be 8-bit indexed color (lots of 0xF7 bytes = likely background color).

Reference: Investigation of ROM word-level interleaving fix

---

#### 🟡 MAME: Input/Control subsystem emulation milestone {#issue-kn5000-1vz}

**ID:** `kn5000-1vz` | **Priority:** Medium | **Created:** 2026-01-31

**Notes:** Track completion of input and control subsystem emulation for MAME.

## Required Components
- [ ] Control panel HLE (MCU ROM not dumped)
- [ ] Button matrix scanning
- [ ] LED control responses
- [ ] Rotary encoder simulation
- [ ] Analog controllers (wheels, pedals)

## Related Issues
- kn5000-9ye: Control panel protocol
- kn5000-qhm: Control panel HLE design
- kn5000-3c7: Analog controllers
- kn5000-j3c: Button index mapping
- kn5000-ljl: LED index mapping
- kn5000-unb: Rotary encoder format

## Success Criteria
- Keyboard input responds to user
- UI navigation works
- LEDs reflect state changes

---

#### 🟡 MAME: Storage subsystem emulation milestone {#issue-kn5000-a0k}

**ID:** `kn5000-a0k` | **Priority:** Medium | **Created:** 2026-01-31

**Notes:** Track completion of storage subsystem emulation for MAME.

## Required Components
- [ ] FDC emulation (floppy disk controller at 0x110000)
- [ ] HDAE5000 expansion interface
- [ ] Custom Data Flash at 0x300000
- [ ] Table Data ROM access

## Related Issues
- kn5000-ima: FDC subsystem symbols
- kn5000-kuu: HDAE5000 ROM disassembly
- kn5000-bqe: Custom Data Flash organization
- kn5000-44c: HDAE5000 filesystem

## Success Criteria
- Floppy disk loading works
- Custom styles/songs can be saved/loaded
- HDAE5000 (if present) is detected

---

#### 🟡 Phase 3 Completion: Full documentation coverage {#issue-kn5000-9m6}

**ID:** `kn5000-9m6` | **Priority:** Medium | **Created:** 2026-01-31

**Notes:** Meta-issue tracking Phase 3 completion (Complete Documentation).

## Phase 3 Goals
All subsystems fully documented in the documentation website.

## Deliverables
- kn5000-8ro: All placeholder pages completed
- Audio details: SysEx format, CC handlers, voice allocation
- Storage details: Custom Data Flash, HDAE5000 filesystem
- Boot/Init: Complete timeline documentation

## Documentation Pages to Complete
1. audio-subsystem.md
2. display-subsystem.md
3. midi-subsystem.md
4. ui-framework.md
5. sequencer.md
6. storage-subsystem.md (expand)

## Depends On
- Phase 2 completion (functional emulation enables testing)

## Success Criteria
- [ ] No placeholder pages remaining
- [ ] All subsystem pages have code references
- [ ] Symbol names in docs match assembly source
- [ ] All P2/P3 documentation issues closed

---

#### 🟡 Storage: Document Custom Data Flash organization at 0x300000 {#issue-kn5000-bqe}

**ID:** `kn5000-bqe` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** Custom Data Flash (1MB @ 0x300000) stores user settings and sequences.

Current state: Address known, internal layout unknown.

Required work:
- Identify file/record structure
- Document user settings storage format
- Map custom sound/style save locations
- Document sequence storage format

Priority: Medium - needed for save/restore functionality
Phase: 3 - Complete Documentation
Dependencies: Sequencer format (for sequence storage)
Related: Storage subsystem documentation

---

#### 🟡 Sub CPU: Complete emulation accuracy documentation {#issue-kn5000-b0h}

**ID:** `kn5000-b0h` | **Priority:** Medium | **Created:** 2026-01-31

**Notes:** Document all requirements for accurate Sub CPU emulation.

## Current Status
- Sub CPU boot ROM: 100% disassembled
- Sub CPU payload: 100% disassembled
- Inter-CPU latch protocol: Documented

## Missing Documentation
- Exact timing requirements for latch communication
- DMA transfer behavior
- Interrupt priority and timing
- Audio output synchronization

## Related Issues
- kn5000-51z: Boot sequence handshake
- kn5000-1ru: Payload memory layout
- kn5000-ayt: Sub CPU type identification

## Hardware Details
- Sub CPU: 65C02 variant at IC27
- Boot ROM: 0xFE0000-0xFFFFFF
- Payload loaded to: 0x000400
- Communication via latch at 0x120000

## Success Criteria
- All timing-critical behaviors documented
- MAME can boot Sub CPU with correct behavior
- Audio output produces correct results

---

#### 🟡 Symbols: Apply semantic naming to FDC subsystem LABEL_* symbols {#issue-kn5000-ima}

**ID:** `kn5000-ima` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** FDC subsystem semantic naming and documentation.

**Current state:** Handler at 0x110000 identified, commands not documented.

**Required work:**
- Rename LABEL_* symbols in FDC code
- Document uPD72068 command sequences
- Trace sector read/write implementation
- Document error handling

**Phase:** 2 - Core Functionality
**Blocks:** Floppy disk emulation
**Dependencies:** None
**Related:** kn5000-70b (FDC during update)

---

#### 🟡 Symbols: Apply semantic naming to UI framework LABEL_* symbols {#issue-kn5000-4bt}

**ID:** `kn5000-4bt` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** Following the successful audio subsystem renaming, apply the same approach to UI framework routines:

1. Identify UI-related LABEL_* symbols (widget handlers, drawing, event dispatch)
2. Analyze each routine's purpose
3. Create semantic names (UI_DrawButton, Widget_HandleClick, etc.)
4. Add documentation headers
5. Update ui-framework.md with code references

Many UI routines already have good names (Display_*, GridCheck_*, ClassProc_*).
Focus on remaining LABEL_* symbols in UI code regions.

Reference: ui-framework.md for existing documentation.

---

#### 🟡 Symbols: Rename remaining LABEL_* in Sub CPU audio code {#issue-kn5000-9jq}

**ID:** `kn5000-9jq` | **Priority:** Medium | **Created:** 2026-01-30

**Notes:** While major audio routines were renamed, many helper labels remain as LABEL_*:

Sub CPU areas needing attention:
- Voice helper routines (LABEL_02C6CD -> Voice_SetPitch, etc.) - some done, verify completeness
- DSP helper routines in 0x035xxx-0x036xxx range
- Ring buffer helper labels
- Audio processing loop internal labels

Approach:
1. Grep for remaining LABEL_02* and LABEL_03* in subcpu asm
2. Analyze context to determine purpose
3. Create meaningful names
4. Add to sed script and apply

Reference: audio_subsystem_rename.sed for pattern.

---

#### 🟡 Update website with service manual findings {#issue-kn5000-8q2}

**ID:** `kn5000-8q2` | **Priority:** Medium | **Created:** 2026-01-25

After extracting info from service manual schematics, update kn5000-docs website: add hardware architecture page, update control-panel-protocol.md with confirmed signals (DATA/BCK/ROTA/ROTB), add IC reference table, include block diagram description.

**Depends on:** [`kn5000-z9k`](#issue-kn5000-z9k)

---

#### ⚪ Docs: Add code reference tables to all subsystem pages {#issue-kn5000-sf8}

**ID:** `kn5000-sf8` | **Priority:** Low | **Created:** 2026-01-30

**Notes:** Following the pattern established in audio-subsystem.md, add Code Reference tables to all subsystem documentation pages:

Pages needing code reference tables:
- fdc-subsystem.md
- display-subsystem.md  
- cpu-subsystem.md
- storage-subsystem.md
- sequencer.md

Each table should include:
- Routine name (with semantic name if available)
- Address
- Brief description
- Link to source file and line number if possible

This makes documentation more useful for MAME development and homebrew.

---

#### ⚪ Docs: Cross-reference Main CPU and Sub CPU symbol names {#issue-kn5000-t2e}

**ID:** `kn5000-t2e` | **Priority:** Low | **Created:** 2026-01-30

**Notes:** Ensure consistent naming between Main CPU and Sub CPU for related functionality:

1. Audio lock routines: Main CPU Audio_Lock_* should match Sub CPU understanding
2. DMA transfer: Main CPU Audio_DMA_Transfer relates to Sub CPU InterCPU_* routines
3. Command dispatch: Document which Main CPU routines send which command ranges

Create a cross-reference table in inter-cpu-protocol.md showing:
- Main CPU routine -> Command sent -> Sub CPU handler

This helps understand the full data flow.

---

#### ⚪ Homebrew: Create SDK documentation and examples {#issue-kn5000-9zb}

**ID:** `kn5000-9zb` | **Priority:** Low | **Created:** 2026-01-30

**Notes:** Enable homebrew development for KN5000 hardware.

**Current state:** Assembly knowledge accumulated, no SDK exists.

**Required work:**
- Create getting-started guide
- Document essential APIs (display, audio, input)
- Provide example programs
- Document memory map for user code
- Create build system templates

**Phase:** 4 - Quality & Polish
**Blocks:** Community homebrew development
**Dependencies:** Complete subsystem documentation
**Related:** All subsystem documentation issues

---

#### ⚪ Homebrew: Development toolkit and SDK planning {#issue-kn5000-5jy}

**ID:** `kn5000-5jy` | **Priority:** Low | **Created:** 2026-01-31

**Notes:** Plan and track homebrew development toolkit creation.

## Toolkit Components

### Assembly Development
- ASL macro library for common patterns
- TMP94C241 instruction reference
- Memory map constants file
- Example programs

### C Development (Long-term)
- LLVM backend for TLCS-900/H2 (tracked in kn5000-raw)
- libc port or minimal runtime
- Hardware abstraction layer

### Tools
- Image converter (bin <-> PNG/BMP)
- MIDI file extractor
- ROM patcher/builder
- Emulator integration

## Documentation Needed
- Getting started guide
- Hardware programming reference
- API documentation
- Example walkthrough

## Related Issues
- kn5000-9zb: SDK documentation and examples
- kn5000-raw: LLVM backend development
- kn5000-pkx: Image converter

## Success Criteria
- Documented build process for homebrew
- At least one working example program
- Community can build and test code

---

#### ⚪ Maintain documentation website {#issue-kn5000-9a0}

**ID:** `kn5000-9a0` | **Priority:** Low | **Created:** 2026-01-25

Keep the kn5000-docs Jekyll website in sync with reverse engineering progress. Update status, add findings, maintain open questions list. Website repo: claude_jail/kn5000-docs/

---

#### ⚪ Phase 4 Completion: Production-ready quality {#issue-kn5000-nca}

**ID:** `kn5000-nca` | **Priority:** Low | **Created:** 2026-01-31

**Notes:** Meta-issue tracking Phase 4 completion (Quality & Polish).

## Phase 4 Goals
Production-ready emulation and homebrew support.

## Deliverables

### Symbol Cleanup
- kn5000-9jq: Sub CPU audio code symbols
- kn5000-4bt: UI framework symbols
- kn5000-aar: Naming convention guide

### Tool Development
- kn5000-waa: Slide viewer/editor
- kn5000-87m: Update file parser
- kn5000-pkx: Image converter
- kn5000-5jy: Homebrew SDK

### Documentation Polish
- kn5000-9a0: Website maintenance
- kn5000-sf8: Code reference tables

### Validation
- kn5000-a8s: Emulation validation procedures

## Depends On
- Phase 3 completion

## Success Criteria
- [ ] All LABEL_* symbols renamed to semantic names
- [ ] Homebrew SDK with working examples
- [ ] MAME driver merged upstream
- [ ] All tools functional and documented

---

#### ⚪ Sequencer: Document event storage format and track organization {#issue-kn5000-wgc}

**ID:** `kn5000-wgc` | **Priority:** Low | **Created:** 2026-01-30

**Notes:** The 16-track MIDI sequencer data format needs reverse engineering.

**Current state:** Basic capability known, internal format undocumented.

**Required work:**
- Locate sequence data in RAM/storage
- Document event record format (note, CC, timing)
- Trace track organization structure
- Document timing resolution and sync

**Phase:** 3 - Complete Documentation
**Blocks:** Sequencer emulation
**Dependencies:** MIDI subsystem
**Related:** Custom Data Flash (kn5000-bqe)

---

#### ⚪ Symbols: Create naming convention guide in CLAUDE.md {#issue-kn5000-aar}

**ID:** `kn5000-aar` | **Priority:** Low | **Created:** 2026-01-30

**Notes:** Document the naming conventions established during audio subsystem renaming:

Prefixes used:
- Audio_* - General audio subsystem routines
- MIDI_* - MIDI message parsing/dispatch
- Voice_* - Voice parameter manipulation
- DSP_* / DSP2_* - DSP hardware control
- RingBuf_* - Ring buffer operations
- InterCPU_* - Inter-CPU communication
- ToneGen_* - Tone generator (keyboard input)
- HDAE5000_* - HDAE5000 expansion board
- TableData_* - Table Data ROM operations
- FDC_* - Floppy disk controller
- UI_* / Widget_* - UI framework
- Display_* - Display/video routines
- CPanel_* - Control panel protocol
- Encoder_* - Rotary encoder handling

Add to CLAUDE.md so future work maintains consistency.

---

#### ⚪ Testing: Establish emulation validation procedures {#issue-kn5000-a8s}

**ID:** `kn5000-a8s` | **Priority:** Low | **Created:** 2026-01-31

**Notes:** Define testing procedures for validating MAME emulation accuracy.

## Testing Categories

### Boot Sequence Validation
- ROM checksum verification
- Peripheral init order matches real hardware
- Sub CPU payload transfer timing

### Display Validation
- Boot splash appearance
- UI element positioning
- Font rendering accuracy
- Color reproduction

### Audio Validation
- Basic tone generation
- MIDI input response
- Effects processing
- Timing/latency

### Input Validation
- Button press response
- Rotary encoder behavior
- Analog controller range

## Test Data Needed
- Screenshots from real hardware
- Audio recordings
- Timing measurements
- Logic analyzer captures

## Success Criteria
- Documented test procedures
- Baseline captures from real hardware
- Automated comparison where possible

---

#### ⚪ LLVM: TLCS-900/H2 backend development tracking {#issue-kn5000-raw}

**ID:** `kn5000-raw` | **Priority:** P4 | **Created:** 2026-01-30

**Notes:** Long-term goal: LLVM compiler backend for TMP94C241F.

**Current state:** Goal documented, no implementation started.

**Required work:**
- Study LLVM backend architecture
- Document TLCS-900/H2 instruction set formally
- Implement register allocation
- Implement instruction selection
- Create C/C++ support

**Phase:** 5 - Future
**Blocks:** High-level language homebrew
**Dependencies:** Complete instruction documentation
**Related:** kn5000-3o6 (ASL macros document encodings)

---

### Sound & Audio {#sound-audio}

#### 🟠 Sound: Document DAC IC310 {#issue-kn5000-xel}

**ID:** `kn5000-xel` | **Priority:** High | **Created:** 2026-01-25

Identify and document the DAC chip (IC310). Find datasheet. Document: resolution (bits), sample rate, number of channels, interface protocol (I2S, parallel), output specifications.

---

#### 🟠 Sound: Document DSP IC311 {#issue-kn5000-xv2}

**ID:** `kn5000-xv2` | **Priority:** High | **Created:** 2026-01-25

Identify and document the DSP chip (IC311). Find datasheet. Document: DSP architecture, instruction set if programmable, effects capabilities (reverb, chorus, EQ), interface to main/sub CPU, audio data format.

---

#### 🟠 Sound: Document Waveform ROM (IC306-307) {#issue-kn5000-d38}

**ID:** `kn5000-d38` | **Priority:** High | **Created:** 2026-01-25

Analyze the waveform ROM chips. Document: total size, data format, sample encoding (PCM bits, compression), how samples are indexed, instrument mapping. These contain the raw sound samples for synthesis.

---

#### 🟡 Sound: Document MIDI implementation {#issue-kn5000-ake}

**ID:** `kn5000-ake` | **Priority:** Medium | **Created:** 2026-01-25

Fully document MIDI capabilities. Trace: MIDI IN/OUT/THRU handling, channel assignments, supported controllers (CC), SysEx commands, GM/GS/XG compatibility, MIDI clock sync, sequencer integration.

---

#### 🟡 Sound: Document audio output path {#issue-kn5000-jy9}

**ID:** `kn5000-jy9` | **Priority:** Medium | **Created:** 2026-01-25

Trace complete audio signal path from DAC to output jacks. Document: analog circuitry, amplifier stages, headphone amp, line out levels, speaker amp (if internal), any analog effects or mixing.

---

#### 🟡 Sound: Document effects processing chain {#issue-kn5000-si0}

**ID:** `kn5000-si0` | **Priority:** Medium | **Created:** 2026-01-25

Trace the audio effects signal path. Document: reverb types and parameters, chorus/flanger, EQ, effects routing (insert vs send), which chip handles each effect (DSP vs sub CPU), effects presets.

---

#### 🟡 Sound: Document rhythm/accompaniment engine {#issue-kn5000-98j}

**ID:** `kn5000-98j` | **Priority:** Medium | **Created:** 2026-01-25

Analyze how auto-accompaniment works. Document: rhythm pattern format, chord detection algorithm, bass/chord/rhythm part generation, style structure (intro/main/fill/ending), variation switching.

---

#### 🟡 Sound: Document synthesis architecture {#issue-kn5000-tvq}

**ID:** `kn5000-tvq` | **Priority:** Medium | **Created:** 2026-01-25

Understand how sounds are generated. Document: oscillator count (polyphony), synthesis method (sample playback, wavetable, FM), envelope generators (ADSR), LFO, filters. Trace sub CPU code for synthesis routines.

---

#### ⚪ Sound: Extract and catalog all instrument patches {#issue-kn5000-cox}

**ID:** `kn5000-cox` | **Priority:** Low | **Created:** 2026-01-25

Extract instrument definitions from ROM. Document: patch names, sample mappings, envelope settings, filter settings, effects assignments. Create patch list matching front panel sound groups.

---

#### ⚪ Sound: Extract and convert waveform samples {#issue-kn5000-mrx}

**ID:** `kn5000-mrx` | **Priority:** Low | **Created:** 2026-01-25

Extract raw waveform data from ROM as playable audio. Convert to WAV format. Catalog samples by instrument type. Document sample rates, loop points, root notes. Useful for MAME sound emulation verification.

---

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-dj3` | Video: Extract and document all fonts | 2026-02-28 |
| `kn5000-nmg` | Video: Document animation and transition effects | 2026-02-28 |
| `kn5000-5dc` | Video: Document UI widget rendering | 2026-02-28 |
| `kn5000-rq0` | Video: Document screen layout and regions | 2026-02-28 |
| `kn5000-kev` | Video: Document font system and text rendering | 2026-02-28 |
| `kn5000-gln` | Video: Reverse engineer drawing primitives | 2026-02-27 |
| `kn5000-t8n` | HDAE5000: Reverse engineer parallel port protocol | 2026-02-27 |
| `kn5000-9bd` | Boot: Document audio subsystem initialization | 2026-02-27 |
| `kn5000-mhj` | Boot: Create complete boot sequence timeline | 2026-02-27 |
| `kn5000-izk` | Boot: Document HDAE5000 detection and init | 2026-02-27 |
| `kn5000-vql` | Boot: Document LCD splash screen sequence | 2026-02-27 |
| `kn5000-bq4` | Boot: Document control panel initialization | 2026-02-27 |
| `kn5000-pkx` | Images: Convert images to viewable formats | 2026-02-27 |
| `kn5000-4rr` | Images: Update assembly sources to include binary images | 2026-02-27 |
| `kn5000-1ru` | SubCPU: Document payload memory layout | 2026-02-27 |
| `kn5000-ayt` | SubCPU: Identify sub CPU type and memory map | 2026-02-27 |
| `kn5000-51z` | SubCPU: Document boot sequence handshake | 2026-02-27 |
| `kn5000-pcq` | Images: Extract all images as binary files | 2026-02-27 |
| `kn5000-36g` | Images: Reverse engineer image format | 2026-02-27 |
| `kn5000-16s` | Images: Find embedded image locations in table data ROM | 2026-02-27 |

*...and 134 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 2 |
| High | 18 |
| Medium | 45 |
| Low | 16 |
| P4 | 1 |

### By Category

| Category | Count |
|----------|-------|
| Feature Demo | 11 |
| Firmware Update | 8 |
| HD-AE5000 Expansion | 2 |
| Other | 51 |
| Sound & Audio | 10 |

---

*Last updated: 2026-02-28 00:49*
