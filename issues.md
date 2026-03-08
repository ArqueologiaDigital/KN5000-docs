---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 280 (23 open, 255 closed)

**Quick Links:** 
[HD-AE5000 Expansion](#hd-ae5000-expansion) (2) · [Other](#other) (20) · [Sound & Audio](#sound-audio) (1)

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

#### 🟡 Another World: Complete floppy code injection for KN5000 port {#issue-kn5000-yhj}

**ID:** `kn5000-yhj` | **Priority:** Medium | **Created:** 2026-02-21

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

**Depends on:** [`kn5000-gexo`](#issue-kn5000-gexo)

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

#### ⚪ Disasm: Extract more include files for major functional areas {#issue-kn5000-imt3}

**ID:** `kn5000-imt3` | **Priority:** Low | **Created:** 2026-03-07

The main CPU program (360K lines) has 16 include files covering well-understood subsystems. Many more functional areas could be extracted to improve organization. Candidates: sequencer routines, display/paint routines, accompaniment processing, registration memory, flash programming, boot sequence, interrupt handlers, timer handlers, DMA routines. Each extraction should group related routines into a themed .s file with documentation headers.

---

#### ⚪ Docs: Document registration memory save/recall system {#issue-kn5000-9gom}

**ID:** `kn5000-9gom` | **Priority:** Low | **Created:** 2026-03-07

Registration memory allows saving/recalling complete instrument setups (sound, style, tempo, split points, effects). The Custom Data Flash page documents the storage format, but the firmware routines for saving, recalling, and managing registration banks are undocumented. Trace the registration save/load code and document the parameter set that gets saved/restored.

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

### Sound & Audio {#sound-audio}

#### ⚪ Sound: Extract and catalog all instrument patches {#issue-kn5000-cox}

**ID:** `kn5000-cox` | **Priority:** Low | **Created:** 2026-01-25

Extract instrument definitions from ROM. Document: patch names, sample mappings, envelope settings, filter settings, effects assignments. Create patch list matching front panel sound groups.

---

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-dbi` | Phase 1 Completion: All MAME blockers resolved | 2026-03-07 |
| `kn5000-y18` | MAME: Audio subsystem emulation milestone | 2026-03-07 |
| `kn5000-8z5` | MAME: Display subsystem emulation milestone | 2026-03-07 |
| `kn5000-8jn0` | Disasm: Systematic semantic labeling of high-reference-co... | 2026-03-07 |
| `kn5000-zfxb` | Docs: Document accompaniment/style playback engine | 2026-03-07 |
| `kn5000-d12s` | Docs: Document display subsystem paint/draw primitives | 2026-03-07 |
| `kn5000-5msx` | MAME: Trace and document tone generator register interface | 2026-03-07 |
| `kn5000-gexo` | Disasm: Document main loop structure and top-level dispatch | 2026-03-07 |
| `kn5000-gmcc` | Disasm: Convert 5,936 numeric call targets to symbolic la... | 2026-03-07 |
| `kn5000-raw` | LLVM: TLCS-900/H2 backend development tracking | 2026-03-07 |
| `kn5000-3c7` | Input: Document analog controller processing (wheels, ped... | 2026-03-07 |
| `kn5000-fs3i` | Semantic labeling: rename top-30 most-referenced LABEL_ r... | 2026-03-07 |
| `kn5000-bqe` | Storage: Document Custom Data Flash organization at 0x300000 | 2026-03-07 |
| `kn5000-d1x` | Table Data: Document ROM internal structure and indexing | 2026-03-07 |
| `kn5000-6je` | Document jump tables in maincpu ROM | 2026-03-07 |
| `kn5000-ezo` | Display: Document VGA register set for MN89304 controller | 2026-03-07 |
| `kn5000-aar` | Symbols: Create naming convention guide in CLAUDE.md | 2026-03-07 |
| `kn5000-67g` | Document ROM interleaving formats for all ROM chips | 2026-03-07 |
| `kn5000-0r5` | Investigate shared graphics data between maincpu and tabl... | 2026-03-07 |
| `kn5000-8dy` | Audio: Trace sound category data structures at 0xE023B0 | 2026-03-07 |

*...and 235 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| High | 3 |
| Medium | 8 |
| Low | 11 |

### By Category

| Category | Count |
|----------|-------|
| HD-AE5000 Expansion | 2 |
| Other | 20 |
| Sound & Audio | 1 |

---

*Last updated: 2026-03-08 00:03*
