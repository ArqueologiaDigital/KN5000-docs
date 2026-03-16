---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 340 (4 open, 335 closed)

**Quick Links:** 
[Other](#other) (4)

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

### Phase 2: Core Functionality - kn5000-dnl ✅ CLOSED
*Goal: User interaction and file I/O working*

**UI/Input (kn5000-1vz): ✅ CLOSED**
- All sub-issues complete. UI navigation verified working in MAME.

**Storage (kn5000-a0k): ✅ CLOSED**
- FDC fully wired (UPD72067, MSR at 0x110008, FIFO at 0x11000A, DMA at 0x120000)
- HDAE5000 IDE/ATA working — App Loader reads FAT16 from hard disk
- Custom Data Flash: mapped, NVRAM-backed
- Table Data ROM: working (sequencer reads rhythm data)
- Floppy disk testing: separate issue kn5000-bxwb still open

### Phase 3: Complete Documentation - kn5000-9m6 ✅ CLOSED
*Goal: All subsystems fully documented*
All subsystem pages documented, no placeholders remain.

### Phase 4: Quality & Polish - kn5000-nca (OPEN)
*Goal: Production-ready emulation and homebrew support*
- Validation test suite: created (boot/menu/display tests)
- SDK documentation: comprehensive (1442 lines, Quick Start guide, Makefile template)
- MAME PR update pending (kn5000-f8gw): accumulated driver fixes need to be pushed upstream
- Quality audit: NAKA C file struct conversion in progress (kn5000-vc1b)
- Playing-games tutorial: added to docs website

## Current Stats (Mar 16, 2026)
- **Total issues:** 334 (328 closed, 6 open)
- **ROM reconstruction:** 279,441 native instructions, 0 .byte fallbacks, 100% byte match on all 6 ROMs
- **.byte code elimination:** ✅ COMPLETE — all executable code is native TLCS-900 instructions
- **Data reversion fix:** 25 data regions across 10 files reverted from bogus instruction mnemonics back to .byte data
- **LABEL_XXXXXX elimination:** ✅ COMPLETE (0 remaining across all ROMs)

## Recent Milestones (Mar 2026)
- **Phase 2 CLOSED** — All core functionality sub-issues resolved.
- **.byte code elimination COMPLETE** — Zero remaining .byte code fallbacks. 279,441 native instructions across all 6 ROMs.
- **Data reversion fix** — 25 data regions across 10 files that had been incorrectly converted to instruction mnemonics were reverted to proper .byte data sequences.
- **Playing-games tutorial** — New tutorial page added to the documentation website explaining how to play homebrew games on the KN5000 via MAME.
- **Tone Generator device (IC303)** — kn5000_tonegen_device added to MAME. 64-voice PCM wavetable with register-indirect interface, waveform ROM reading, stereo 48kHz output.
- **UART mode** — 8-bit UART TX/RX implemented in TMP94C241 serial. Enables MIDI output at 31250 baud.
- **MIDI output** — TX0 wired to midi_port device. MAME emits MIDI.
- **FDC address mapping** — UPD72067 registers properly mapped with PC AT layout + 16-bit bus doubling.
- **R+d16 LLVM addressing** — SRI prefix encoding fixed, 357 .byte→native conversions in roms-disasm.
- **App Loader (HDAE5000)** — Working end-to-end: FAT16 filesystem, menu UI, APP.BIN loading, Mines game launches from disk.

## Success Criteria
1. ✅ All 6 ROMs 100% byte-match reconstruction
2. ✅ All subsystems documented (no placeholder pages)
3. ✅ Homebrew SDK functional (App Loader + Mines game working)
4. ⬜ MAME driver merged upstream (PR update pending — kn5000-f8gw)

---

#### 🟡 MAME: Update PR #14558 with accumulated driver fixes {#issue-kn5000-f8gw}

**ID:** `kn5000-f8gw` | **Priority:** Medium | **Created:** 2026-03-10

Create a new MAME upstream PR (PR5) for accumulated driver fixes on kn5000_pr5_driver branch. This includes: tone generator device (IC303 with PCM playback, pitch, pan, volume), FDC wiring and dskchg polarity fix, HDAE5000 IDE/ATA, control panel HLE improvements, DSP device stubs. Must: (1) rebase onto current MAME master, (2) squash into logical commits, (3) ensure MAME code style (BIT macros, logmacro.h), (4) NO AI attribution on PR commits, (5) create PR with feature list.

---

#### ⚪ MAME: Feature Demo SSF visual presentation {#issue-kn5000-jbhk}

**ID:** `kn5000-jbhk` | **Priority:** Low | **Created:** 2026-03-16

The Feature Demo button sequence (DEMO → LEFT 4 → LEFT 2) plays demo songs correctly but the visual SSF presentation never renders. The FTBMP bitmaps don't appear because demo_state at DRAM 0x0251D8 stays 0x0000. Root cause is event routing — SSF event 0x1C00038 doesn't reach GroupBoxProc_StartSSFPresentation. Investigate and fix the event dispatch path.

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
| `kn5000-v0uv` | MAME: Decode voice parameter template (ROM 0x12115, 34 by... | 2026-03-16 |
| `kn5000-kdis` | MAME: Wire FDC Terminal Count (TC) signal from TMP94C241 ... | 2026-03-16 |
| `kn5000-vc1b` | NAKA C files: Convert remaining raw byte arrays to structs | 2026-03-16 |
| `kn5000-u4k7` | Add MAME screenshots to playing-games tutorial | 2026-03-16 |
| `kn5000-bxwb` | Test floppy disk I/O in MAME | 2026-03-16 |
| `kn5000-vpmb` | Disassembly quality audit: verify code vs data classifica... | 2026-03-16 |
| `kn5000-hrtz` | Update project roadmap with current status | 2026-03-16 |
| `kn5000-rtru` | Raw Byte Code Elimination: Audit all .byte sequences | 2026-03-16 |
| `kn5000-sitw` | Write user-facing tutorial: Running games on MAME | 2026-03-16 |
| `kn5000-7geb` | Revert bogus instruction mnemonics in data regions back t... | 2026-03-16 |
| `kn5000-pn28` | Convert NAKA widget descriptors to C structs | 2026-03-15 |
| `kn5000-j8pz` | Phase 4: Continue LABEL_XXXXXX semantic renaming | 2026-03-14 |
| `kn5000-2wj1` | Rename all LABEL_ in extension_data.s to semantic names | 2026-03-14 |
| `kn5000-3j4z` | Rename LABEL_ in performance_style_screens.s | 2026-03-14 |
| `kn5000-zi7j` | Rename all LABEL_ in scoop_display.s to semantic names | 2026-03-14 |
| `kn5000-u8fl` | MAME: DSP device stubs for IC310 (MN19413) and IC311 (DS3... | 2026-03-14 |
| `kn5000-wmfd` | MAME: Tone generator device (IC303) — refine waveform pla... | 2026-03-14 |
| `kn5000-02h7` | Rename LABEL_ placeholders in note_voice_mapping.s | 2026-03-14 |
| `kn5000-h1d0` | Rename LABEL_XXXXXX to semantic names in audio_control_en... | 2026-03-14 |
| `kn5000-xm8x` | MAME: Fix FDC disk detection (dskchg polarity) | 2026-03-14 |

*...and 315 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| Medium | 1 |
| Low | 2 |

### By Category

| Category | Count |
|----------|-------|
| Other | 4 |

---

*Last updated: 2026-03-16 06:11*
