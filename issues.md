---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 292 (7 open, 283 closed)

**Quick Links:** 
[Other](#other) (7)

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

#### 🟠 HDAE5000 Generic Program Loader: FAT filesystem, HD boot, multi-app support {#issue-kn5000-yhj}

**ID:** `kn5000-yhj` | **Priority:** High | **Created:** 2026-02-21

Modified HDAE5000 ROM that implements:
1. FAT filesystem reading from IDE hard disk
2. App Loader menu UI on the KN5000 display with app icons and names
3. Generic program loader that can boot multiple applications
4. Currently supported apps: Mines game, Another World game

Architecture: Only the HDAE5000 ROM is modified. The KN5000 hardware is unmodified. Programs and assets are stored on the hard disk. The loader reads the FAT filesystem, scans for application manifest files, and presents a graphical App Loader menu showing each app's icon and name. Selecting an app loads it into DRAM for execution.

App Manifest: Each application provides a manifest file containing:
- App name (displayed in menu)
- Icon bitmap (displayed in menu)
- Entry point address
- List of asset files to load and their target addresses

This replaces the previous floppy code injection approach. The HD approach solves the 512KB ROM size limit (974KB of Another World resources couldn't fit) and provides a reusable platform for any future homebrew.

Key components:
- FAT16/FAT32 filesystem driver (read-only initially)
- IDE/ATA disk I/O routines (already in HDAE5000 ROM, need adaptation)
- App Loader menu with icon/name display from manifests
- Program loading: read executable + assets from HD into DRAM
- Application launcher: jump to loaded program entry point

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

#### 🟠 Trace full code path: Feature Demo selection → FTBMP bitmap render, identify MAME driver gaps {#issue-kn5000-y7t5}

**ID:** `kn5000-y7t5` | **Priority:** High | **Created:** 2026-03-01

MOTIVATION: The Feature Presentation SSF was confirmed to trigger GroupBoxProc_StartSSFPresentation (9 times), but only the Technics logo was briefly visible and the SSF ran abnormally fast, completing all 9 items in ~5 frames. We need to understand whether all intermediate conditions along the full execution path are satisfied in MAME, or whether some HW emulation gaps prevent the presentation from running correctly (e.g., timing, events not reaching their targets, missing display ownership, etc.).

GOAL: Trace the complete code path from:
  ENTRY: DEMO button pressed in state 0xE4 (GroupBoxProc active)
  → GroupBoxProc event handler for DEMO button
  → GroupBoxProc_StartSSFPresentation (0xF9A273)
  → Sends 0x1C0001C with workspace tag 0xB80A via FA9660 → AcPresentCtrl_CheckSSFStart (0xF84625)
  → Check passes → sends 0x1C00006 → SSF XML parser starts
  → XML parser reads hkst_55.ssf (at 0x88000E), processes each ACT element
  → For each SHOW OBJ='ftdemoXX' → name table lookup → FTDEMO_SCREEN structure
  → FTDEMO_SCREEN.filename_ptr → lookup in file entry index at 0x8CE01C
  → ROM BMP data pointer retrieved
  EXIT: VwUserBitmapByNameProc / DrawBitmapFile renders FTBMP pixel data to VRAM (0x1A0000-0x1DFFFF)

ANALYSIS REQUIRED:
1. Disassemble/trace the GroupBoxProc DEMO button handler (what event code does it use to call StartSSFPresentation?)
2. Confirm how AcPresentCtrl_CheckSSFStart (0xF84625) verifies the workspace tag - is there any timing issue?
3. Trace AcPresentationControlProc (0xF8450B) processing of 0x1C00006 → how does it start the XML parser?
4. Trace the XML parser (AcPresentCtrlProc_ParseSSF or equivalent) - how does it loop through ACT items? What event/callback fires for each SHOW?
5. Identify each FTBMP bitmap load call: VwUserBitmapByNameProc arguments, display ownership required?
6. Check if there's a 'delay' or 'wait for display update' step between frames - does the SSF rely on a hardware vsync or timer that MAME may handle differently?
7. Identify any conditions/guards along the path that might silently abort (e.g., checking GAME_ACTIVE, checking display mode, checking audio ready, etc.)

For each code section that is still in .byte form along this path, create disassembly issues and cross-reference them here.

KEY ADDRESSES ALREADY KNOWN:
- GroupBoxProc: ~0xF998xx (partially decoded in file)
- GroupBoxProc_StartSSFPresentation: 0xF9A273
- AcPresentCtrl_CheckSSFStart: 0xF84625
- AcPresentationControlProc: 0xF8450B (jump table at 0xE9F9B2)
- FA9660: SendEvent (direct)
- FA9945: EventDispatch_Direct (in .byte form - kn5000-84fw)
- FA9D58: BroadcastEvent
- hkst_55.ssf XML: 0x88000E (Table Data ROM)
- File entry index: 0x8CE01C
- FTBMP BMP data: 0x880418 (FTBMP01), 0x89344E (FTBMP02), etc.
- VwUserBitmapByNameProc / DrawBitmapFile: address TBD (find via disasm)

HARDWARE ACCURACY CONSTRAINT: No hacks or shortcuts. All identified gaps must be fixed via accurate hardware emulation in the MAME driver (kn5000.cpp). Document findings on feature-demo.md website page.

---

#### 🟡 TMP94C241: Internal RAM range 0xC00-0xFFF missing from address map {#issue-kn5000-rqtw}

**ID:** `kn5000-rqtw` | **Priority:** Medium | **Created:** 2026-03-09

The TMP94C241 datasheet says internal RAM is 2KB at 0x800-0xFFF. MAME currently maps 0x400-0xBFF as RAM, missing 0xC00-0xFFF. Extending to 0xFFF breaks KN5000 demo timer (0x0D2F) because the KN5000 driver maps external DRAM at 0x000000-0x0FFFFF overlapping internal RAM. Adding internal RAM at 0xC00-0xFFF shadows the DRAM, causing the timer to get stuck. Needs investigation: (1) Are other MAME drivers affected? (2) Should KN5000 driver start DRAM at 0x1000? (3) Do DMA transfers access internal RAM or external bus?

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
| `kn5000-9m6` | Phase 3 Completion: Full documentation coverage | 2026-03-08 |
| `kn5000-n1l2` | DSP1: Investigate algorithm select mechanism (effect name... | 2026-03-08 |
| `kn5000-b0h` | Sub CPU: Complete emulation accuracy documentation | 2026-03-08 |
| `kn5000-8ro` | Documentation: Complete all subsystem placeholder pages | 2026-03-08 |

*...and 263 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| High | 3 |
| Medium | 1 |
| Low | 2 |

### By Category

| Category | Count |
|----------|-------|
| Other | 7 |

---

*Last updated: 2026-03-09 20:14*
