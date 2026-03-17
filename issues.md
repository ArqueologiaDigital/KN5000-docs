---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 395 (8 open, 387 closed)

**Quick Links:** 
[Other](#other) (8)

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

**Depends on:** [`kn5000-jt0b`](#issue-kn5000-jt0b), [`kn5000-mv8f`](#issue-kn5000-mv8f)

---

#### 🟡 Rebase kn5000_pr5_driver branch onto current MAME master {#issue-kn5000-jt0b}

**ID:** `kn5000-jt0b` | **Priority:** Medium | **Created:** 2026-03-16

The kn5000_pr5_driver branch needs rebasing onto current upstream MAME master before creating PR. Check for conflicts with recent MAME changes.

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

#### ⚪ Trace SSF event 0x1C00038 routing path in MAME {#issue-kn5000-7c0w}

**ID:** `kn5000-7c0w` | **Priority:** Low | **Created:** 2026-03-16

The Feature Demo SSF visual presentation doesn't work because event 0x1C00038 never reaches GroupBoxProc_StartSSFPresentation. Add MAME logging to trace where the event gets lost in the dispatch chain.

**Depends on:** [`kn5000-jbhk`](#issue-kn5000-jbhk)

---

#### ⚪ EPIC: Path to full C port of ROM firmware {#issue-kn5000-4sry}

**ID:** `kn5000-4sry` | **Priority:** P4 | **Created:** 2026-03-16

Long-term goal: port the entire KN5000 firmware from assembly to C while maintaining 100% byte-matching output. This enables:
- Readable, maintainable firmware understanding
- Potential recompilation for other targets
- Professional documentation quality

Phases:
1. Convert all remaining data tables to C structs (sound_data_*.s, sepaout, etc.)
2. Convert simple leaf functions to C (utility functions, string handlers)
3. Convert medium-complexity routines (MIDI handlers, parameter dispatch)
4. Convert major subsystems (sequencer engine, accompaniment engine, UI framework)
5. Final: boot code, interrupt handlers, hardware init

Each phase maintains 100% byte match via LLVM TLCS-900 backend compilation.

Prerequisites:
- All .byte code blocks disassembled to native instructions first
- LLVM C compiler must produce identical code for each converted function
- Regression testing on every conversion

---

#### ⚪ LLVM TLCS-900: Add instruction scheduling model {#issue-kn5000-8nkr}

**ID:** `kn5000-8nkr` | **Priority:** P4 | **Created:** 2026-03-16

TLCS900Schedule.td exists but lacks detailed cycle counts. A professional backend should model: memory access latency, multiply/divide throughput, branch prediction miss cost, pipeline stalls. This enables -O2 to make better decisions when compiling C code.

---

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-9a0` | Maintain documentation website | 2026-03-17 |
| `kn5000-ejyx` | LLVM TLCS-900: Implement jump table lowering (BR_JT) | 2026-03-17 |
| `kn5000-riek` | LLVM TLCS-900: Add auto-increment addressing mode for CP | 2026-03-17 |
| `kn5000-cy4r` | LLVM TLCS-900: Fix calr with numeric address targets | 2026-03-17 |
| `kn5000-jd8s` | LLVM TLCS-900: Add 8-bit direct addressing mode (F0 prefix) | 2026-03-17 |
| `kn5000-205q` | LLVM TLCS-900: Fix R+d16 addressing in disassembler (SRI ... | 2026-03-17 |
| `kn5000-rv4p` | LLVM TLCS-900: Add backend documentation (README/architec... | 2026-03-17 |
| `kn5000-mv8f` | Audit kn5000 MAME driver for upstream code style compliance | 2026-03-17 |
| `kn5000-h5ci` | LLVM TLCS-900: Fix D7 prevbank prefix in disassembler | 2026-03-17 |
| `kn5000-ete6` | Convert sound_data_*.s files to C struct arrays | 2026-03-17 |
| `kn5000-q8tm` | Convert sepaout_config.s data to C structs | 2026-03-17 |
| `kn5000-kkwr` | Convert tonegen_param_table.s to C struct | 2026-03-17 |
| `kn5000-xpd2` | LLVM TLCS-900: Add disassembler round-trip verification t... | 2026-03-17 |
| `kn5000-ka1c` | LLVM TLCS-900: Add .word/.hword assembler directive support | 2026-03-17 |
| `kn5000-1uiu` | Rename 458 generic .set labels (Data_XXXXXX, PadFF_, etc.... | 2026-03-17 |
| `kn5000-noum` | LLVM TLCS-900: Override allowsMisalignedMemoryAccesses fo... | 2026-03-17 |
| `kn5000-x1j4` | LLVM TLCS-900: Audit C code generation quality for byte-m... | 2026-03-17 |
| `kn5000-s4jr` | Evaluate LLVM TLCS-900 C compiler output quality for simp... | 2026-03-17 |
| `kn5000-ur27` | Suppress ALIGNED_STRING compiler warnings (233 warnings) | 2026-03-17 |
| `kn5000-4wd3` | Add file header comments to 36 assembly files missing them | 2026-03-17 |

*...and 367 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| Medium | 2 |
| Low | 3 |
| P4 | 2 |

### By Category

| Category | Count |
|----------|-------|
| Other | 8 |

---

*Last updated: 2026-03-17 14:07*
