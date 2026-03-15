---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 330 (5 open, 325 closed)

**Quick Links:** 
[Other](#other) (5)

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

#### 🟡 MAME: Update PR #14558 with accumulated driver fixes {#issue-kn5000-f8gw}

**ID:** `kn5000-f8gw` | **Priority:** Medium | **Created:** 2026-03-10

Create a new MAME upstream PR (PR5) for accumulated driver fixes on kn5000_pr5_driver branch. This includes: tone generator device (IC303 with PCM playback, pitch, pan, volume), FDC wiring and dskchg polarity fix, HDAE5000 IDE/ATA, control panel HLE improvements, DSP device stubs. Must: (1) rebase onto current MAME master, (2) squash into logical commits, (3) ensure MAME code style (BIT macros, logmacro.h), (4) NO AI attribution on PR commits, (5) create PR with feature list.

---

#### ⚪ MAME: Decode voice parameter template (ROM 0x12115, 34 bytes) {#issue-kn5000-v0uv}

**ID:** `kn5000-v0uv` | **Priority:** Low | **Created:** 2026-03-14

The 34-byte voice parameter template at SubCPU ROM 0x12115 contains default register values for all tone gen registers. Decoding this would improve waveform selection accuracy — currently the mapping from register values to waveform ROM addresses is unknown. Tasks: (1) Extract the template bytes from the SubCPU ROM. (2) Map each byte pair to the corresponding tone gen register. (3) Understand what default waveform, pitch, and volume values are set.

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
| `kn5000-qkdr` | Rename LABEL_XXXXXX to semantic names in accompaniment_en... | 2026-03-14 |
| `kn5000-dnl` | Phase 2 Completion: Core functionality working | 2026-03-14 |
| `kn5000-a0k` | MAME: Storage subsystem emulation milestone | 2026-03-14 |
| `kn5000-42jw` | Rename LABEL_XXXXXX placeholders in NAKA ui_widgets files... | 2026-03-14 |
| `kn5000-0vuo` | MAME: Implement VRAM A18 banking (VGA display modes) | 2026-03-14 |
| `kn5000-u573` | Waveform ROM investigation: dump IC304-IC306 or create ap... | 2026-03-14 |
| `kn5000-yhj` | HDAE5000 Generic Program Loader: FAT filesystem, HD boot,... | 2026-03-14 |
| `kn5000-y7t5` | Trace full code path: Feature Demo selection → FTBMP bitm... | 2026-03-14 |
| `kn5000-ht11` | DSP2: Trace bytecode programs to map registers to effect ... | 2026-03-14 |
| `kn5000-46mu` | Generate synthetic waveform ROMs (IC304, IC305, IC306) fo... | 2026-03-14 |

*...and 305 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| Medium | 1 |
| Low | 3 |

### By Category

| Category | Count |
|----------|-------|
| Other | 5 |

---

*Last updated: 2026-03-15 09:30*
