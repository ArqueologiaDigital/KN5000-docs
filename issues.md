---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 422 (20 open, 401 closed)

**Quick Links:** 
[Other](#other) (20)

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

#### 🟡 Data wheel (Program encoder) delivery mechanism unsolved {#issue-kn5000-wa40}

**ID:** `kn5000-wa40` | **Priority:** Medium | **Created:** 2026-03-18

The steady-state mechanism for how the data wheel (jog dial) rotation reaches the firmware UI is not yet understood. Boot-time detection via segment 0x0B works but only runs during init. The Type 2 encoder system handles analog controllers only. The UI event chain requires SwbtWr type 0x21 at DRAM[0xC07D] → CtrlPanel_HandleSerialPort → event 0x1C0001F, but nothing produces type 0x21 during normal operation. Research branches: kn5000_research_encoder, kn5000_research_encoder_v2. Full documentation in control-panel-protocol.md Data Wheel section. Next step: MAME debugger execution trace while pressing UP/DOWN LCD buttons to find the event code path for value changes.

---

#### 🟡 Dump encoder scan table (0x8E78) via MAME debugger {#issue-kn5000-bey1}

**ID:** `kn5000-bey1` | **Priority:** Medium | **Created:** 2026-03-18

After boot completes, dump DRAM 0x8E78 region in MAME debugger: d 0x8E78,0x30. Shows what encoder entries are active. Requires human interaction with MAME debugger.

---

#### 🟡 LLVM semantic instruction migration Phase 2: 24-bit addressing {#issue-kn5000-7ubb}

**ID:** `kn5000-7ubb` | **Priority:** Medium | **Created:** 2026-03-25

Replace ~1,700 wrapper mnemonics for 24-bit addressing modes (ld16_24, ld32_24, st16_24, st32_24, sti16_24, cpi8_24, cpdi16_24) with semantic TLCS-900 syntax. Requires changes to TLCS900InstrInfo.td, AsmParser, Disassembler, and all .s files.

---

#### 🟡 LLVM semantic instruction migration Phase 3: Extended register pair modes {#issue-kn5000-1hqd}

**ID:** `kn5000-1hqd` | **Priority:** Medium | **Created:** 2026-03-25

Replace ~3,300 wrapper mnemonics for extended register pair modes (ldto_berp, ldfr_berp, ldto_werp, ldfr_werp, ldi_berp, ldi_werp, push/pop_werp, cpi_berp/werp, inc1_berp/werp, cp_werp). Requires LLVM backend changes.

**Depends on:** [`kn5000-7ubb`](#issue-kn5000-7ubb)

---

#### 🟡 LLVM semantic instruction migration Phase 4: SRI/DRI indirect modes {#issue-kn5000-xcuk}

**ID:** `kn5000-xcuk` | **Priority:** Medium | **Created:** 2026-03-25

Replace ~3,500 wrapper mnemonics for SRI/DRI indirect addressing modes (st_dri3b/w/l, ld_srib3/sriw3, lda_dri3, lda_dpi, ld_spib, jp_dri, stib_dri/dpi, stiw_dri, bit_dri). Largest phase. Requires LLVM backend changes.

**Depends on:** [`kn5000-1hqd`](#issue-kn5000-1hqd)

---

#### 🟡 LLVM semantic instruction migration Phase 5: Miscellaneous {#issue-kn5000-0vbs}

**ID:** `kn5000-0vbs` | **Priority:** Medium | **Created:** 2026-03-25

Replace ~700 remaining wrapper mnemonics (ld_srib/sriw, mrid2, ldada/ldda8/stda8, addm32_24/addmi16). Final cleanup phase.

**Depends on:** [`kn5000-xcuk`](#issue-kn5000-xcuk)

---

#### 🟡 MAME PR5 rebase on upstream/master {#issue-kn5000-fc48}

**ID:** `kn5000-fc48` | **Priority:** Medium | **Created:** 2026-03-25

Rebase kn5000_pr5_driver_v2 branch on latest upstream/master from mamedev/mame. Verify splash screen, control panel, and boot sequence still work after rebase.

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

#### 🟡 Set watchpoint on encoder state area 0x8E78 {#issue-kn5000-s2wv}

**ID:** `kn5000-s2wv` | **Priority:** Medium | **Created:** 2026-03-18

In MAME debugger: wpset 8e78,30,w then interact with emulator. See what writes to encoder scan table and from which PC addresses. Requires human interaction.

---

#### 🟡 Test encoder ID candidates with MAME debugger watchpoint on 0xC07D {#issue-kn5000-o1k9}

**ID:** `kn5000-o1k9` | **Priority:** Medium | **Created:** 2026-03-18

After identifying candidate encoder IDs from ROM table analysis, modify HLE to send Type 2 packets with those IDs. Test with MAME debugger watchpoint on 0xC07D for SwbtWr type 0x21. Requires human interaction.

---

#### 🟡 Verify CPanel_InitButtonState runs in steady state {#issue-kn5000-4tgy}

**ID:** `kn5000-4tgy` | **Priority:** Medium | **Created:** 2026-03-18

Set breakpoint on CPanel_InitButtonState in MAME debugger and wait 30+ seconds. If it never triggers, the 4th-cycle counter is broken and button/encoder state never refreshes after boot. Requires human interaction.

---

#### ⚪ MAME keybed test mode activation {#issue-kn5000-gvcz}

**ID:** `kn5000-gvcz` | **Priority:** Low | **Created:** 2026-03-25

Implement keybed service test mode activation in MAME. Requires HLE for checking devices MCU responses to B3+B4 combo and mode codes 0xF5-0xFC.

---

#### ⚪ NAKA widget bytecode reverse engineering {#issue-kn5000-xz6f}

**ID:** `kn5000-xz6f` | **Priority:** Low | **Created:** 2026-03-25

Deep analysis of NAKA widget bytecode interpreter. 28 files, ~80K lines, ~9015 labels defining UI widget hierarchies. Continue semantic label renaming and document bytecode opcodes.

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

#### ⚪ v141 subcpu disassembly (29% diff from v142) {#issue-kn5000-q8nv}

**ID:** `kn5000-q8nv` | **Priority:** Low | **Created:** 2026-03-25

Create v141/subcpu source tree. 56,018 bytes differ (29.2% of 192KB). Significant effort required - many code changes between versions.

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

#### ⚪ Remaining firmware versions (v7, v6, v5) disassembly {#issue-kn5000-2kwt}

**ID:** `kn5000-2kwt` | **Priority:** P4 | **Created:** 2026-03-25

Create source trees for older firmware versions v7, v6, v5. Deferred until v9 and v141 are stable. Diff sizes unknown - need ROM dumps.

---

#### ⚪ v8 maincpu disassembly (1 byte diff from v9) {#issue-kn5000-5vpa}

**ID:** `kn5000-5vpa` | **Priority:** P4 | **Created:** 2026-03-25

v8 firmware differs from v9 by only 1 byte (version number). Create v8/maincpu source tree. Trivial once v9 is complete.

**Depends on:** [`kn5000-q8nv`](#issue-kn5000-q8nv)

---

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-5m2t` | LLVM TLCS-900 backend: add semantic instruction definitio... | 2026-03-25 |
| `kn5000-5p9k` | Replace unresolved ROM hex addresses with positional .set... | 2026-03-24 |
| `kn5000-eu8c` | Replace hex ROM addresses with symbolic labels in disasse... | 2026-03-24 |
| `kn5000-mpyg` | Multi-version ROM disassembly: restructure for v9+v141 | 2026-03-23 |
| `kn5000-n05c` | MAME: Connect DSP1 ready signal to SubCPU Port H bit 0 | 2026-03-17 |
| `kn5000-7c0w` | Trace SSF event 0x1C00038 routing path in MAME | 2026-03-17 |
| `kn5000-jbhk` | MAME: Feature Demo SSF visual presentation | 2026-03-17 |
| `kn5000-ur11` | Document SSF (Sound Slide Film) presentation system | 2026-03-17 |
| `kn5000-bock` | MAME: Research MN89304 VGA controller and A18 banking signal | 2026-03-17 |
| `kn5000-a254` | MAME: Route ATA INTRQ from HDAE5000 extension slot to CPU... | 2026-03-17 |
| `kn5000-j60k` | Convert widget_dispatch.s large data blocks to C structs | 2026-03-17 |
| `kn5000-pq05` | Convert gui_display_struct_data.s to C struct (17 x 34-by... | 2026-03-17 |
| `kn5000-9n3o` | Suppress _start linker warnings in ROM .ld files | 2026-03-17 |
| `kn5000-8nkr` | LLVM TLCS-900: Add instruction scheduling model | 2026-03-17 |
| `kn5000-9a0` | Maintain documentation website | 2026-03-17 |
| `kn5000-ejyx` | LLVM TLCS-900: Implement jump table lowering (BR_JT) | 2026-03-17 |
| `kn5000-riek` | LLVM TLCS-900: Add auto-increment addressing mode for CP | 2026-03-17 |
| `kn5000-cy4r` | LLVM TLCS-900: Fix calr with numeric address targets | 2026-03-17 |
| `kn5000-jd8s` | LLVM TLCS-900: Add 8-bit direct addressing mode (F0 prefix) | 2026-03-17 |
| `kn5000-205q` | LLVM TLCS-900: Fix R+d16 addressing in disassembler (SRI ... | 2026-03-17 |

*...and 381 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| Medium | 12 |
| Low | 4 |
| P4 | 3 |

### By Category

| Category | Count |
|----------|-------|
| Other | 20 |

---

*Last updated: 2026-03-25 10:05*
