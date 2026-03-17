---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 386 (23 open, 362 closed)

**Quick Links:** 
[Other](#other) (23)

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

#### 🟡 Audit kn5000 MAME driver for upstream code style compliance {#issue-kn5000-mv8f}

**ID:** `kn5000-mv8f` | **Priority:** Medium | **Created:** 2026-03-16

Before PR submission: ensure BIT() macros, logmacro.h LOGMASKED() channels, no AI attribution on PR branch commits, proper MAME conventions.

**Depends on:** [`kn5000-jt0b`](#issue-kn5000-jt0b)

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

#### ⚪ Evaluate LLVM TLCS-900 C compiler output quality for simple functions {#issue-kn5000-s4jr}

**ID:** `kn5000-s4jr` | **Priority:** Low | **Created:** 2026-03-16

Test whether clang -target tlcs900 produces byte-identical output for simple C functions vs hand-written assembly. Try: strlen, memcpy, simple dispatch tables, register manipulation. Document which patterns match and which need __attribute__ hints.

---

#### ⚪ Extract 43 remaining inline data blocks from kn5000_v10_program.s {#issue-kn5000-o97p}

**ID:** `kn5000-o97p` | **Priority:** Low | **Created:** 2026-03-16

43 inline data blocks remain in the main program file (.byte, .zero, .fill, .long, .ascii, aligned_string). These should be moved to dedicated source files or C struct files following the pattern established for NAKA widgets and Voice_FactoryPresetData.

---

#### ⚪ LLVM TLCS-900: Add disassembler round-trip verification tests {#issue-kn5000-xpd2}

**ID:** `kn5000-xpd2` | **Priority:** Low | **Created:** 2026-03-16

The disassembler (TLCS900Disassembler.cpp) should be verified with round-trip tests: assemble -> disassemble -> reassemble -> compare bytes. This catches encoding/decoding mismatches. Create a test that exercises every instruction class.

---

#### ⚪ LLVM TLCS-900: Add missing compact instruction encodings {#issue-kn5000-q5dh}

**ID:** `kn5000-q5dh` | **Priority:** Low | **Created:** 2026-03-16

Several compact TLCS-900 instructions are not in the backend: compact zero-load (d8 a8 = ld wa,0), compact load-1 (e8 a9 = ld xwa,1), compact dec/inc xsp (ef 6a/62), cps qiz (prevbank compact compare). These are used in .byte fallbacks in the ROM disassembly. Adding them would eliminate remaining .byte workarounds.

---

#### ⚪ LLVM TLCS-900: Audit C code generation quality for byte-matching {#issue-kn5000-x1j4}

**ID:** `kn5000-x1j4` | **Priority:** Low | **Created:** 2026-03-16

Evaluate whether clang -target tlcs900 produces byte-identical output for simple C functions vs hand-written assembly. Test: utility functions (strlen, memcpy), dispatch tables, register manipulation. Document which C patterns produce matching code and which need __attribute__ hints. Critical for the C porting path.

---

#### ⚪ LLVM TLCS-900: Fix calr with numeric address targets {#issue-kn5000-cy4r}

**ID:** `kn5000-cy4r` | **Priority:** Low | **Created:** 2026-03-16

calr (relative call with 16-bit offset) with numeric address targets emits absolute bytes instead of computing relative offset. Currently must use labels or .byte fallback. Fix: compute PC-relative offset at emission time.

---

#### ⚪ LLVM TLCS-900: Increase MC test coverage (currently 8 tests) {#issue-kn5000-gyge}

**ID:** `kn5000-gyge` | **Priority:** Low | **Created:** 2026-03-16

Only 8 MC (Machine Code) assembly/disassembly test files exist in llvm/test/MC/TLCS900/. A professional backend needs comprehensive round-trip tests for every instruction encoding. Current CodeGen tests (50 files) test IR lowering but not assembler correctness. Need: (1) test every instruction mnemonic, (2) test all addressing modes, (3) test boundary/edge cases (max displacement, zero operands), (4) test error cases (invalid registers, out-of-range immediates).

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

#### ⚪ Add file header comments to 36 assembly files missing them {#issue-kn5000-4wd3}

**ID:** `kn5000-4wd3` | **Priority:** P4 | **Created:** 2026-03-16

36 of 151 .s files (24%) lack file-level header comments explaining purpose. Mostly data files and auto-generated widget descriptors. Add brief headers following the established pattern.

---

#### ⚪ Convert sepaout_config.s data to C structs {#issue-kn5000-q8tm}

**ID:** `kn5000-q8tm` | **Priority:** P4 | **Created:** 2026-03-16

sepaout_config.s has 105 .byte lines of separator output configuration (layout params, bitmask tables, format strings). Convert to C struct with named config fields.

---

#### ⚪ Convert sound_data_*.s files to C struct arrays {#issue-kn5000-ete6}

**ID:** `kn5000-ete6` | **Priority:** P4 | **Created:** 2026-03-16

7 sound data files (brass, flute, guitar, mallet, organ, sax, world) contain instrument preset parameter tables as .byte data. Convert to typed C struct arrays with named fields for each instrument parameter.

---

#### ⚪ Convert tonegen_param_table.s to C struct {#issue-kn5000-kkwr}

**ID:** `kn5000-kkwr` | **Priority:** P4 | **Created:** 2026-03-16

tonegen_param_table.s has 87 .byte lines of tone generator parameter lookup data. Convert to typed C array with named parameter fields.

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

#### ⚪ LLVM TLCS-900: Add backend documentation (README/architecture doc) {#issue-kn5000-rv4p}

**ID:** `kn5000-rv4p` | **Priority:** P4 | **Created:** 2026-03-16

No documentation exists for the TLCS-900 backend architecture: instruction format encoding scheme, register file layout, addressing mode implementation, custom pass descriptions (BitManipOpt, BitTestOpt, DJNZOpt, BranchShortening, FixLargeDisp, IncDecOpt, RedundantCmpElim). A professional backend needs an architecture document.

---

#### ⚪ LLVM TLCS-900: Add instruction scheduling model {#issue-kn5000-8nkr}

**ID:** `kn5000-8nkr` | **Priority:** P4 | **Created:** 2026-03-16

TLCS900Schedule.td exists but lacks detailed cycle counts. A professional backend should model: memory access latency, multiply/divide throughput, branch prediction miss cost, pipeline stalls. This enables -O2 to make better decisions when compiling C code.

---

#### ⚪ Rename 458 generic .set labels (Data_XXXXXX, PadFF_, etc.) to semantic names {#issue-kn5000-1uiu}

**ID:** `kn5000-1uiu` | **Priority:** P4 | **Created:** 2026-03-16

The LABEL_XXXXXX elimination left 458 .set aliases with auto-generated names like Data_E00800, PadFF_E3DEF1, PtrTable_E1FFB6, etc. These need analysis to determine proper semantic names based on what the data contains.

---

#### ⚪ Suppress ALIGNED_STRING compiler warnings (233 warnings) {#issue-kn5000-ur27}

**ID:** `kn5000-ur27` | **Priority:** P4 | **Created:** 2026-03-16

naka_widget_descriptors.c generates 233 -Wexcess-initializers warnings from ALIGNED_STRING macro expansion. Add #pragma to suppress, or redesign macro to avoid the warning.

---

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-v7cp` | Organize scripts/ into subdirectories (170+ scripts) | 2026-03-17 |
| `kn5000-yclj` | Add pre-commit hook: validate LLVM version in commit message | 2026-03-17 |
| `kn5000-2p4i` | Convert drawbar_panel_ui.s .byte data (1571 lines) | 2026-03-17 |
| `kn5000-e0b6` | Convert widget_dispatch.s .byte data to C structs (4907 .... | 2026-03-17 |
| `kn5000-hjqn` | Disassemble sndparam_routines.s .byte code blocks (616 li... | 2026-03-17 |
| `kn5000-8qpz` | Disassemble dsp_config_sysex.s .byte code blocks (388 lines) | 2026-03-17 |
| `kn5000-2z32` | Disassemble ui_mode_handlers.s .byte code blocks (540 lines) | 2026-03-17 |
| `kn5000-33k0` | Disassemble ui_window_procs.s .byte code blocks (769 lines) | 2026-03-17 |
| `kn5000-r88l` | Disassemble semenu_routines.s .byte code blocks (1599 lines) | 2026-03-17 |
| `kn5000-zhot` | Disassemble note_voice_mapping.s .byte code blocks (1337 ... | 2026-03-17 |
| `kn5000-xxtz` | Convert sound_editor_ui.s .byte data (4673 lines) | 2026-03-17 |
| `kn5000-njrx` | Convert audio_control_engine.s MIDI handler .byte blocks ... | 2026-03-17 |
| `kn5000-dhcw` | Auto-generate NAKA linker scripts from ELF symbol table | 2026-03-17 |
| `kn5000-g7en` | Convert swi 7/nop padding in dispatch files to .fill 0xFF... | 2026-03-17 |
| `kn5000-nr32` | Remove 4 legacy ASL->LLVM TODO comments in smf_playback.s | 2026-03-17 |
| `kn5000-jxhw` | LLVM regression: commit d0fb231 causes 1-byte size change... | 2026-03-17 |
| `kn5000-zvla` | Makefile: Make compare_roms.py failure halt the build | 2026-03-16 |
| `kn5000-e44u` | Makefile: Consolidate 25 NAKA widget build rules into sin... | 2026-03-16 |
| `kn5000-68s7` | Fix unindented .include directives in 5 assembly files | 2026-03-16 |
| `kn5000-rxy9` | Makefile: Add error checking to subcpu ROM extraction dd ... | 2026-03-16 |

*...and 342 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| Medium | 3 |
| Low | 10 |
| P4 | 9 |

### By Category

| Category | Count |
|----------|-------|
| Other | 23 |

---

*Last updated: 2026-03-17 08:32*
