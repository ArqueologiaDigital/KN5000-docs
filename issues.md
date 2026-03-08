---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 282 (10 open, 271 closed)

**Quick Links:** 
[HD-AE5000 Expansion](#hd-ae5000-expansion) (1) · [Other](#other) (9)

---

## Open Issues

### HD-AE5000 Expansion {#hd-ae5000-expansion}

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

### Phase 1: Foundation (MAME Blockers) - kn5000-dbi ✅ CLOSED
*Goal: Get basic emulator running with display and sound*
All Phase 1 sub-issues complete. MAME boots with display and audio subsystem traffic logged.

### Phase 2: Core Functionality - kn5000-dnl (OPEN)
*Goal: User interaction and file I/O working*

**UI/Input (kn5000-1vz):**
- kn5000-kev: Font system [P2]
- kn5000-5dc: Widget rendering [P2]
- kn5000-qhm: Control panel HLE [P2]
- kn5000-3c7: Analog controllers [P2]

**Storage (kn5000-a0k):**
- kn5000-ima: FDC subsystem [P2]
- kn5000-kuu: HDAE5000 ROM [P1]

### Phase 3: Complete Documentation - kn5000-9m6 (OPEN)
*Goal: All subsystems fully documented*

### Phase 4: Quality & Polish - kn5000-nca (OPEN)
*Goal: Production-ready emulation and homebrew support*

## Current Status (Mar 2026)
- **ROM reconstruction: ALL 6 ROMs 100% byte-perfect match**
  - Main CPU: 100% (239,683 native instructions, 15,683 symbolic .long)
  - Sub CPU boot: 100% (1,357 native instructions)
  - Sub CPU payload: 100% (35,721 native instructions)
  - Table Data: 100% (1,678 native instructions)
  - HDAE5000: 100% (502 native instructions)
  - Custom Data: 100% (data-only)
  - Total: 279,441 native instructions, zero .byte fallbacks (except HDAE5000 ~4,663)
- **Build system:** LLVM with custom TLCS-900 backend (authoritative)
- **Issue tracker:** 280 issues (265 closed, 13 open, 2 in progress)
- **Documentation:** cpu-subsystem, audio-subsystem, midi-subsystem, inter-cpu-protocol all updated
- **MAME:** Boots with display, audio/DSP logging. Phase 2 input/storage work remains.

## Success Criteria
- [x] All ROMs 100% byte-matching
- [ ] MAME driver merged upstream
- [ ] All subsystems documented
- [ ] Homebrew SDK available

## Phase Tracking Issues
- Phase 1: kn5000-dbi (P0 - ✅ CLOSED)
- Phase 2: kn5000-dnl (P1 - Current Focus)
- Phase 3: kn5000-9m6 (P2)
- Phase 4: kn5000-nca (P3)

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

#### ⚪ DSP2: Trace bytecode programs to map registers to effect parameters {#issue-kn5000-ht11}

**ID:** `kn5000-ht11` | **Priority:** Low | **Created:** 2026-03-08

With the DSP2 register map established (112 addresses), the next step is to trace through the firmware's bytecode programs (at ROM 0x14777) entry-by-entry to understand which registers correspond to which effect parameters (reverb time, chorus depth, etc). This requires decoding the 6 bytecode handler types and their data operands. Cross-reference with DSP1's known coefficient addresses.

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

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-a8s` | Testing: Establish emulation validation procedures | 2026-03-08 |
| `kn5000-gkpv` | DSP2 (MN19413): Map register functions from boot-time writes | 2026-03-08 |
| `kn5000-1vz` | MAME: Input/Control subsystem emulation milestone | 2026-03-08 |
| `kn5000-0eo` | MAME: Spurious button events during boot (voice dialog, t... | 2026-03-08 |
| `kn5000-9m6` | Phase 3 Completion: Full documentation coverage | 2026-03-08 |
| `kn5000-n1l2` | DSP1: Investigate algorithm select mechanism (effect name... | 2026-03-08 |
| `kn5000-b0h` | Sub CPU: Complete emulation accuracy documentation | 2026-03-08 |
| `kn5000-8ro` | Documentation: Complete all subsystem placeholder pages | 2026-03-08 |
| `kn5000-0o6` | MAME: Update HLE based on audio subsystem findings | 2026-03-08 |
| `kn5000-1oy` | Audio: Analyze DSP effects processing algorithms | 2026-03-08 |
| `kn5000-cox` | Sound: Extract and catalog all instrument patches | 2026-03-07 |
| `kn5000-imt3` | Disasm: Extract more include files for major functional a... | 2026-03-07 |
| `kn5000-wgc` | Sequencer: Document event storage format and track organi... | 2026-03-07 |
| `kn5000-9gom` | Docs: Document registration memory save/recall system | 2026-03-07 |
| `kn5000-mzz` | HDAE5000: Document interface cable pinout | 2026-03-07 |
| `kn5000-8q2` | Update website with service manual findings | 2026-03-07 |
| `kn5000-dbi` | Phase 1 Completion: All MAME blockers resolved | 2026-03-07 |
| `kn5000-y18` | MAME: Audio subsystem emulation milestone | 2026-03-07 |
| `kn5000-8z5` | MAME: Display subsystem emulation milestone | 2026-03-07 |
| `kn5000-8jn0` | Disasm: Systematic semantic labeling of high-reference-co... | 2026-03-07 |

*...and 251 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| High | 1 |
| Medium | 2 |
| Low | 6 |

### By Category

| Category | Count |
|----------|-------|
| HD-AE5000 Expansion | 1 |
| Other | 9 |

---

*Last updated: 2026-03-08 01:34*
