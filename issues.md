---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 319 (9 open, 309 closed)

**Quick Links:** 
[Other](#other) (9)

---

## Open Issues

### Other {#other}

#### 🔴 Plan: Long-term project roadmap and phase tracking {#issue-kn5000-3go}

**ID:** `kn5000-3go` | **Priority:** Critical | **Created:** 2026-01-30

**Notes:** Master roadmap for KN5000 reverse engineering project.

## Project Goals
1. **100% ROM Reconstruction** - Byte-accurate rebuilds of all firmware ✅ COMPLETE
2. **MAME Emulation** - Full system emulation for preservation (IN PROGRESS)
3. **Homebrew Development** - Enable custom software creation (App Loader WORKING)
4. **Documentation** - Complete technical reference ✅ COMPLETE

## Phase Structure with Tracking Issues

### Phase 1: Foundation (MAME Blockers) - kn5000-dbi ✅ CLOSED
*Goal: Get basic emulator running with display and sound*
All Phase 1 sub-issues complete. MAME boots with display and audio subsystem traffic logged.

### Phase 2: Core Functionality - kn5000-dnl (OPEN)
*Goal: User interaction and file I/O working*

**UI/Input (kn5000-1vz): ✅ CLOSED**
- All sub-issues complete. UI navigation verified working in MAME.

**Storage (kn5000-a0k): IN PROGRESS**
- FDC fully wired (UPD72067, MSR at 0x110008, FIFO at 0x11000A, DMA at 0x120000)
- HDAE5000 IDE/ATA working — App Loader reads FAT16 from hard disk
- Custom Data Flash: mapped, NVRAM-backed
- Table Data ROM: working (sequencer reads rhythm data)
- Remaining: floppy disk read test (floppy images ready, FDC wired)

### Phase 3: Complete Documentation - kn5000-9m6 ✅ CLOSED
*Goal: All subsystems fully documented*
All subsystem pages documented, no placeholders remain.

### Phase 4: Quality & Polish - kn5000-nca (OPEN)
*Goal: Production-ready emulation and homebrew support*
- Validation test suite: created (boot/menu/display tests)
- SDK documentation: comprehensive (1442 lines, Quick Start guide, Makefile template)

## Recent Milestones (Mar 2026)
- **Tone Generator device (IC303)** — kn5000_tonegen_device added to MAME. 64-voice PCM wavetable with register-indirect interface, waveform ROM reading, stereo 48kHz output. First step toward actual sound.
- **UART mode** — 8-bit UART TX/RX implemented in TMP94C241 serial. Enables MIDI output at 31250 baud.
- **MIDI output** — TX0 wired to midi_port device. MAME emits MIDI.
- **FDC address mapping** — UPD72067 registers properly mapped with PC AT layout + 16-bit bus doubling.
- **R+d16 LLVM addressing** — SRI prefix encoding fixed, 357 .byte→native conversions in roms-disasm.
- **App Loader (HDAE5000)** — Working end-to-end: FAT16 filesystem, menu UI, APP.BIN loading, Mines game launches from disk.
- **ROM reconstruction** — 279,798 native instructions, 0 .byte fallbacks, 100% byte match on all 6 ROMs.

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

#### 🟡 MAME: Tone generator device (IC303) — refine waveform playback {#issue-kn5000-wmfd}

**ID:** `kn5000-wmfd` | **Priority:** Medium | **Created:** 2026-03-14

The kn5000_tonegen_device was created with basic PCM playback. Needs refinement: (1) Pitch control from voice registers — map MIDI note to playback rate, (2) Volume/pan mapping — decode firmware's register encoding more accurately, (3) Waveform index selection — understand how firmware chooses which ROM chip and waveform entry, (4) Envelope support — key-off should have release phase, (5) Loop points — proper loop start/end from parameter records, (6) Voice status readback — return correct 0x8100/0x1200/0x7E00 states matching real hardware timing.

**Depends on:** [`kn5000-u573`](#issue-kn5000-u573)

---

#### 🟡 MAME: Update PR #14558 with accumulated driver fixes {#issue-kn5000-f8gw}

**ID:** `kn5000-f8gw` | **Priority:** Medium | **Created:** 2026-03-10

The MAME upstream PR #14558 was opened with an earlier version of the driver. Since then, many significant fixes have been committed locally: INT0 level-triggered starvation fix, PORT Z MSTAT readback fix, tone generator hold timer, SNS NMI emulation, HDAE5000 IDE/ATA wiring, FDC device instantiation, control panel HLE improvements, DSP device stubs, and more. Need to: (1) rebase kn5000_pr branch onto current MAME master, (2) cherry-pick/squash all relevant fixes, (3) ensure MAME code style compliance (BIT() macros, logmacro.h, no AI attribution), (4) update PR description with current feature list, (5) address any reviewer feedback.

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

#### ⚪ Rename LABEL_XXXXXX placeholders in NAKA ui_widgets files to semantic names {#issue-kn5000-42jw}

**ID:** `kn5000-42jw` | **Priority:** P4 | **Created:** 2026-03-14

With NAKA files identified as UI widget descriptors, the ~9,015 LABEL_XXXXXX placeholders can be renamed to semantic names based on widget type, screen context, and handler function. Start with smaller files. Cross-reference RegisterObjectTable() entries and Proc handler names (Ac*, Iv*, Ps*, Vw* prefixes). Follow-up to kn5000-iueh research.

---

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-yhj` | HDAE5000 Generic Program Loader: FAT filesystem, HD boot,... | 2026-03-14 |
| `kn5000-y7t5` | Trace full code path: Feature Demo selection → FTBMP bitm... | 2026-03-14 |
| `kn5000-ht11` | DSP2: Trace bytecode programs to map registers to effect ... | 2026-03-14 |
| `kn5000-46mu` | Generate synthetic waveform ROMs (IC304, IC305, IC306) fo... | 2026-03-14 |
| `kn5000-cpn5` | Convert 357 R+d16 .byte instructions to native mnemonics | 2026-03-14 |
| `kn5000-iueh` | Disassembly: Semantic analysis of NAKA obfuscated code bl... | 2026-03-14 |
| `kn5000-2w05` | Rename NAKA ui_widgets files to semantic names | 2026-03-14 |
| `kn5000-9qt3` | MAME: Implement MIDI output (TX0) | 2026-03-14 |
| `kn5000-psio` | LLVM: Add R+d16 addressing mode for TLCS-900 backend | 2026-03-14 |
| `kn5000-rqtw` | TMP94C241: Internal RAM range 0xC00-0xFFF missing from ad... | 2026-03-14 |
| `kn5000-umft` | MAME: Complete FDC address mapping at 0x110000-0x12FFFF | 2026-03-14 |
| `kn5000-f8d2` | Fix Unicode box-drawing diagrams in docs website | 2026-03-14 |
| `kn5000-n1lw` | Use symbolic handler references in all C screen data files | 2026-03-14 |
| `kn5000-6rjd` | Phase 5: Build integration for Rhythm/DrumSound dispatch ... | 2026-03-14 |
| `kn5000-rfqe` | Phase 5: Build integration for DrumKit dispatch table (Op... | 2026-03-14 |
| `kn5000-h9ag` | Phase 5: Build integration for accompaniment screen data ... | 2026-03-14 |
| `kn5000-ytw6` | ScreenData C conversion: verification and cleanup | 2026-03-14 |
| `kn5000-3pop` | Sound editor screendata: symbolic SD_PTR cross-references | 2026-03-14 |
| `kn5000-y213` | Sound editor screendata: extract and convert to C | 2026-03-14 |
| `kn5000-620x` | Sound editor screendata: inventory and tooling | 2026-03-14 |

*...and 289 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| High | 2 |
| Medium | 2 |
| Low | 3 |
| P4 | 1 |

### By Category

| Category | Count |
|----------|-------|
| Other | 9 |

---

*Last updated: 2026-03-14 13:02*
