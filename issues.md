---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 304 (13 open, 287 closed)

**Quick Links:** 
[Other](#other) (13)

---

## Open Issues

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

### Phase 1: Foundation (MAME Blockers) - kn5000-dbi ✅ CLOSED
*Goal: Get basic emulator running with display and sound*
All Phase 1 sub-issues complete. MAME boots with display and audio subsystem traffic logged.

### Phase 2: Core Functionality - kn5000-dnl (OPEN)
*Goal: User interaction and file I/O working*

**UI/Input (kn5000-1vz): ✅ CLOSED**
- All sub-issues complete. UI navigation verified working in MAME.

**Storage (kn5000-a0k): IN PROGRESS**
- FDC documentation complete. Floppy image creation in progress.
- HDAE5000 ROM: complete. IDE/ATA wiring in progress (kn5000-492z).
- Custom Data Flash: mapped, NVRAM-backed.
- Table Data ROM: working (sequencer reads rhythm data).

### Phase 3: Complete Documentation - kn5000-9m6 ✅ CLOSED
*Goal: All subsystems fully documented*
All subsystem pages documented, no placeholders remain.

### Phase 4: Quality & Polish - kn5000-nca (OPEN)
*Goal: Production-ready emulation and homebrew support*
- Validation test suite: created (boot/menu/display tests)
- SDK documentation: comprehensive (1442 lines, Quick Start guide, Makefile template)
- Homebrew toolkit: documented (kn5000-5jy closed)

## Active Unblocking Work (Mar 8)
Three parallel efforts to resolve blockers:
1. **Tone generator timing fix** — Add voice hold time in tc183c230002.cpp to fix Feature Demo speed (kn5000-y7t5)
2. **Floppy disk images** — Create test FAT12 images for MAME FDC testing (kn5000-a0k)
3. **HDAE5000 IDE wiring** — Connect ata_interface_device in hdae5000.cpp (kn5000-492z)

## Current Status (Mar 2026)
- **ROM reconstruction: ALL 6 ROMs 100% byte-perfect match**
  - Total: 279,441 native instructions, zero .byte fallbacks
- **Build system:** LLVM with custom TLCS-900 backend (authoritative)
- **Issue tracker:** 284 issues (276 closed, 8 open)
- **DSP research:** 16 effect types traced, 10 distinct algorithms, chip mapping documented
- **Homebrew SDK:** Complete docs with Quick Start, API reference, Makefile templates
- **MAME:** Boots with display, audio/DSP logging. Phase 2 storage testing in progress.
- **Proactive unblocking policy:** Added as strict policy (Mar 8)

## Success Criteria
- [x] All ROMs 100% byte-matching
- [ ] MAME driver merged upstream
- [x] All subsystems documented (Phase 3 closed)
- [x] Homebrew SDK available (kn5000-9zb, kn5000-5jy closed)

## Phase Tracking Issues
- Phase 1: kn5000-dbi (P0 - ✅ CLOSED)
- Phase 2: kn5000-dnl (P1 - Storage in progress, Input done)
- Phase 3: kn5000-9m6 (P2 - ✅ CLOSED)
- Phase 4: kn5000-nca (P3 - Open)

---

#### 🟠 MAME: Complete FDC address mapping at 0x110000-0x12FFFF {#issue-kn5000-umft}

**ID:** `kn5000-umft` | **Priority:** High | **Created:** 2026-03-10

The UPD72067 FDC device is instantiated and interrupt routing (INT4/INT5) is wired, but the actual address mapping at 0x110000-0x11FFFF (FDC registers) and 0x120000-0x12FFFF (DMA ACK) is commented out with FIXME. Also PORT D bit 6 (FD.I/O input) is marked TODO. Uncommenting and completing this mapping should enable floppy disk read/write operations. This is the last gap preventing Phase 2 closure (kn5000-dnl). Test with kn5000_v10_disk.mfi image already available.

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

#### 🟠 Waveform ROM investigation: dump IC304-IC306 or create approximations {#issue-kn5000-u573}

**ID:** `kn5000-u573` | **Priority:** High | **Created:** 2026-03-10

THE single biggest blocker across the project. Waveform ROMs IC304-IC306 (1.2MB of 1.6MB total) are NO_DUMP. Only IC307 is dumped. Without waveforms: no actual sound synthesis, Feature Demo stuck (sequencer never completes), tone generator HLE is timing-only. Paths forward: (1) Attempt to dump from physical hardware (requires chip desoldering or in-circuit reading), (2) Analyze IC307 format to understand waveform structure, (3) Create synthetic approximations using IC307 as template, (4) Check if other Technics keyboards (KN6000, KN7000) share compatible waveform chips. This is prerequisite for any real audio progress.

---

#### 🟡 Decode all style_ui_paramblock_*.s files {#issue-kn5000-5uor}

**ID:** `kn5000-5uor` | **Priority:** Medium | **Created:** 2026-03-13

Annotate all 12 paramblock .s files with decoded ScreenData bytecode commands (172 total commands)

---

#### 🟡 MAME: Implement MIDI output (TX0) {#issue-kn5000-9qt3}

**ID:** `kn5000-9qt3` | **Priority:** Medium | **Created:** 2026-03-10

Currently only MIDI RX0 is connected in the MAME driver. TX0 (MIDI output) is marked TODO at line 834 of kn5000.cpp. The KN5000 can output MIDI from its sequencer, accompaniment engine, and keyboard. Implementing MIDI output would make the emulator useful as a virtual MIDI instrument. Need to: (1) wire TX0 serial output to a midi_port device, (2) configure baud rate (31250 standard MIDI), (3) test with a MIDI monitor to verify note output from keybed.

---

#### 🟡 MAME: Update PR #14558 with accumulated driver fixes {#issue-kn5000-f8gw}

**ID:** `kn5000-f8gw` | **Priority:** Medium | **Created:** 2026-03-10

The MAME upstream PR #14558 was opened with an earlier version of the driver. Since then, many significant fixes have been committed locally: INT0 level-triggered starvation fix, PORT Z MSTAT readback fix, tone generator hold timer, SNS NMI emulation, HDAE5000 IDE/ATA wiring, FDC device instantiation, control panel HLE improvements, DSP device stubs, and more. Need to: (1) rebase kn5000_pr branch onto current MAME master, (2) cherry-pick/squash all relevant fixes, (3) ensure MAME code style compliance (BIT() macros, logmacro.h, no AI attribution), (4) update PR description with current feature list, (5) address any reviewer feedback.

---

#### 🟡 TMP94C241: Internal RAM range 0xC00-0xFFF missing from address map {#issue-kn5000-rqtw}

**ID:** `kn5000-rqtw` | **Priority:** Medium | **Created:** 2026-03-09

The TMP94C241 datasheet says internal RAM is 2KB at 0x800-0xFFF. MAME currently maps 0x400-0xBFF as RAM, missing 0xC00-0xFFF. Extending to 0xFFF breaks KN5000 demo timer (0x0D2F) because the KN5000 driver maps external DRAM at 0x000000-0x0FFFFF overlapping internal RAM. Adding internal RAM at 0xC00-0xFFF shadows the DRAM, causing the timer to get stuck. Needs investigation: (1) Are other MAME drivers affected? (2) Should KN5000 driver start DRAM at 0x1000? (3) Do DMA transfers access internal RAM or external bus?

---

#### ⚪ Disassembly: Semantic analysis of NAKA obfuscated code blocks {#issue-kn5000-iueh}

**ID:** `kn5000-iueh` | **Priority:** Low | **Created:** 2026-03-10

18 NAKA files in maincpu/ contain ~41,000 lines with ~9,109 LABEL_XXXXXX placeholder names. These are deliberately obfuscated code blocks (likely style/rhythm/accompaniment-related proprietary algorithms). Semantic analysis would: (1) identify callers from dispatch tables, (2) trace register usage and memory access patterns, (3) cross-reference with known subsystems (sequencer, tone gen, accompaniment engine), (4) assign meaningful labels. This is the largest remaining chunk of unanalyzed code. Start with smaller NAKA files (86-683 lines) before tackling the large ones (5,000-8,000 lines).

---

#### ⚪ LLVM: Add R+d16 addressing mode for TLCS-900 backend {#issue-kn5000-psio}

**ID:** `kn5000-psio` | **Priority:** Low | **Created:** 2026-03-10

The LLVM TLCS-900 backend lacks support for register+16-bit-displacement addressing mode (R+d16, C3 prefix encoding). This prevents ~970 .byte instructions in HDAE5000 from being converted to native mnemonics. Also blocks ~470 16-bit direct addressing and ~210 8-bit direct addressing conversions. The load direction (ld A, (R+d16)) is known broken ('displacement too large' error) while the store direction (ld (R+d16), A) works via F3 prefix. Need to fix the C3 prefix load encoding and add the missing addressing mode patterns.

---

#### ⚪ MAME: Implement VRAM A18 banking (VGA display modes) {#issue-kn5000-0vuo}

**ID:** `kn5000-0vuo` | **Priority:** Low | **Created:** 2026-03-10

The VGA.A18 signal from the main CPU through a T7W139F decoder is not emulated (marked TODO at line 927 of kn5000.cpp). This controls VRAM bank selection, potentially affecting full-screen graphics, palette switching, and extended display modes. The display currently works for the main UI but some rendering modes (e.g., Feature Demo FTBMP bitmaps, full-screen splash screens) may depend on correct A18 banking. Need to: (1) trace the T7W139F decoder logic from the service manual schematic, (2) identify which firmware writes control the banking, (3) implement the bank switching in the VGA read/write handlers.

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

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-jyo7` | MAME: Build and test TMP94C241 16-bit timer interrupt fix | 2026-03-13 |
| `kn5000-xpkj` | Annotate all StyleUI screendata bytecode files | 2026-03-13 |
| `kn5000-hkeq` | Decode style_ui_screendata_main.s bytecode format | 2026-03-13 |
| `kn5000-ko7x` | Document all dispatch/jump tables in ROM disassembly | 2026-03-09 |
| `kn5000-3sar` | Fix cpanel HLE for Feature Demo navigation without breaki... | 2026-03-09 |
| `kn5000-tgd6` | MAME: TMP94C241 timer output callbacks fire unconditional... | 2026-03-09 |
| `kn5000-u6du` | MAME: Fresh NVRAM boot shows ERROR in CPU data transmission | 2026-03-09 |
| `kn5000-asm6` | LLVM TLCS-900: LDA with displacement > d8 generates inval... | 2026-03-08 |
| `kn5000-8gqi` | LLVM TLCS-900: Variable shift SLA Rx,Ry generates wrong e... | 2026-03-08 |
| `kn5000-m7iu` | MAME: Implement TMP94C241 timer output callbacks and wire... | 2026-03-08 |
| `kn5000-492z` | MAME: Wire HDAE5000 IDE/ATA interface using MAME ata_inte... | 2026-03-08 |
| `kn5000-qnf` | HDAE5000: Analyze HD-TechManager5000 software | 2026-03-08 |
| `kn5000-0bx2` | HDAE5000: Document hard disk control protocol (low-level ... | 2026-03-08 |
| `kn5000-4qqo` | HDAE5000: Full ROM disassembly with semantic labels and d... | 2026-03-08 |
| `kn5000-5jy` | Homebrew: Development toolkit and SDK planning | 2026-03-08 |
| `kn5000-9zb` | Homebrew: Create SDK documentation and examples | 2026-03-08 |
| `kn5000-a8s` | Testing: Establish emulation validation procedures | 2026-03-08 |
| `kn5000-gkpv` | DSP2 (MN19413): Map register functions from boot-time writes | 2026-03-08 |
| `kn5000-1vz` | MAME: Input/Control subsystem emulation milestone | 2026-03-08 |
| `kn5000-0eo` | MAME: Spurious button events during boot (voice dialog, t... | 2026-03-08 |

*...and 267 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| High | 3 |
| Medium | 4 |
| Low | 5 |

### By Category

| Category | Count |
|----------|-------|
| Other | 13 |

---

*Last updated: 2026-03-14 00:23*
