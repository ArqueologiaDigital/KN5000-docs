---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 271 (44 open, 226 closed)

**Quick Links:** 
[HD-AE5000 Expansion](#hd-ae5000-expansion) (2) · [Other](#other) (41) · [Sound & Audio](#sound-audio) (1)

---

## Open Issues

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

#### 🟡 Update website with service manual findings {#issue-kn5000-8q2}

**ID:** `kn5000-8q2` | **Priority:** Medium | **Created:** 2026-01-25

After extracting info from service manual schematics, update kn5000-docs website: add hardware architecture page, update control-panel-protocol.md with confirmed signals (DATA/BCK/ROTA/ROTB), add IC reference table, include block diagram description.

**Depends on:** [`kn5000-z9k`](#issue-kn5000-z9k)

---

#### ⚪ DSP1: Investigate algorithm select mechanism (effect name tracking) {#issue-kn5000-n1l2}

**ID:** `kn5000-n1l2` | **Priority:** Low | **Created:** 2026-03-03

DSP1 (DS3613GF-3BA) never receives CMD 0x30 (algorithm select). The SubCPU's LABEL_038439 path (wa==1) never triggers for DSP1, so m_channel_algo is never populated and all effect names show 'NO OPERATION'. The algo select may be: (1) embedded in VOICE DATA bulk writes (CMD 0x01 data[0]=0x00), (2) managed purely by SubCPU voice slot allocation (0x041368), or (3) implicit in the coefficient structure. Need to trace SubCPU DSP_ParameterWriteEngine bytecode dispatch to understand when wa==1 occurs.

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

#### ⚪ Sound: Extract and catalog all instrument patches {#issue-kn5000-cox}

**ID:** `kn5000-cox` | **Priority:** Low | **Created:** 2026-01-25

Extract instrument definitions from ROM. Document: patch names, sample mappings, envelope settings, filter settings, effects assignments. Create patch list matching front panel sound groups.

---

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-87m` | Update: Create update file parser tool | 2026-03-07 |
| `kn5000-jqa` | Document binary include e0176c_e01f7f.bin data structure | 2026-03-07 |
| `kn5000-7v8` | Update: Document complete update procedure for users | 2026-03-07 |
| `kn5000-e7f` | Update: Document HDAE5000 update procedure | 2026-03-07 |
| `kn5000-acu` | Update: Document validation and error handling | 2026-03-07 |
| `kn5000-6f7` | Update: Document update progress display | 2026-03-07 |
| `kn5000-koom` | Systematic .byte block decoding to native LLVM instructions | 2026-03-07 |
| `kn5000-4bt` | Symbols: Apply semantic naming to UI framework LABEL_* sy... | 2026-03-07 |
| `kn5000-aksz` | Semantic labeling: rename top-20 most-referenced LABEL_* ... | 2026-03-07 |
| `kn5000-9jq` | Symbols: Rename remaining LABEL_* in Sub CPU audio code | 2026-03-03 |
| `kn5000-ima` | Symbols: Apply semantic naming to FDC subsystem LABEL_* s... | 2026-03-03 |
| `kn5000-kc5` | Disassemble TODO routines at F97696-F97D8D range (jump ta... | 2026-03-03 |
| `kn5000-bntj` | Document data blocks with comments and NAKA macros | 2026-03-03 |
| `kn5000-n8u2` | Disassemble and document GroupBoxProc state table interac... | 2026-03-03 |
| `kn5000-84fw` | Disassemble and document FA9945 (EventDispatch_Direct) | 2026-03-03 |
| `kn5000-lb2x` | Disassemble and document F98697 (KeyPress_StateDispatch) | 2026-03-03 |
| `kn5000-4m2r` | DS3613GF-3BA: false ALGO SELECT from alt param write format | 2026-03-03 |
| `kn5000-dvwg` | DSP1 standalone coefficient sub-packets produce garbage a... | 2026-03-03 |
| `kn5000-tyjr` | DSP1 parallel port cmd 0x01 protocol decoding wrong | 2026-03-03 |
| `kn5000-8eg2` | DSP param name off-by-one fixed | 2026-03-03 |

*...and 206 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 2 |
| High | 9 |
| Medium | 20 |
| Low | 12 |
| P4 | 1 |

### By Category

| Category | Count |
|----------|-------|
| HD-AE5000 Expansion | 2 |
| Other | 41 |
| Sound & Audio | 1 |

---

*Last updated: 2026-03-07 07:36*
