---
layout: page
title: KN7000 Roadmap
permalink: /kn7000-roadmap/
---

# KN7000 Roadmap — porting the KN5000 effort

This page is a thorough plan of what was accomplished for the
[KN5000](/system-overview/) and how each piece maps onto the
[KN7000](/kn7000/). It exists to guide the KN7000 work and to make the scope of
the preservation project explicit.

**The overarching advantage:** the two firmwares are
[two re-targets of one source tree](/technics-shared-codebase/), so a great deal
of KN5000 *understanding* transfers even though no machine code does. **The
overarching obstacle:** the KN7000's Panasonic **MN10300** CPU replaces the
KN5000's Toshiba TLCS-900, so every tool in the low-level chain (disassembler,
assembler, emulator core, compiler) must target a different ISA.

Legend: ✅ done · 🟡 in progress / partial · ⬜ not started · 🔒 blocked on an
undumped ROM or missing hardware.

## Toolchain — a key difference from the KN5000

For the KN5000 the team had to **build tooling from scratch** for an obscure CPU.
For the MN10300 much of that already exists upstream, which should make the
KN7000 path *shorter* in several places:

| Tool | KN5000 (TLCS-900) | KN7000 (MN10300) |
|------|-------------------|-------------------|
| Disassembler | MAME TLCS-900 dasm | ✅ MAME `unidasm -arch mn10300` already works |
| Assembler | — (LLVM emitted objects) | 🟡 a **purpose-built MN10300 encoder** (`tools/mn10300_asm.py`) round-trips **99.9%** of the ROM's instructions byte-exactly (rest = `udf*` coprocessor ops); GNU binutils also has an upstream `mn10300` target for a full `as`/`ld` |
| C/C++ compiler | 🛠️ custom [LLVM TLCS-900 backend](/rom-reconstruction/) built from scratch (279k instructions) | ⬜ **GCC has an upstream `mn10300`/`am33` backend** — homebrew C could reuse it instead of a new backend |
| Emulator CPU core | ✅ MAME TMP94C241F core written | ⬜ MAME has an mn10300 **disassembler only** — an **execution core must be written** (the dasm is a head start) |

## Extraction & ROM reconstruction

| KN5000 accomplishment | KN7000 status | What remains |
|-----------------------|---------------|--------------|
| Decode the LZSS system-update discs | ✅ [`.SLD` decoded](/kn7000-system-update-discs/), both images extracted & checksum-verified | — |
| Split the Table Data ROM into assets | ✅ [84-segment directory decoded](/kn7000-firmware/); `table_extract.py`; **293 raw UI bitmaps in true colour** (palette @ prog `0x32573C`, `table_bitmaps.py`); **[1,454 sound + 931 style names](/kn7000-sound-names/)** (`table_names.py`/`style_names.py`) | decode the `TCMP`/`TPAD`/"Technics Pads"/"Technics Rhythms" preset-data chunks; sub-tables 1 & 3 |
| Extract embedded images | ✅ [169-image gallery](/kn7000-image-gallery/) | decode any remaining raw/proprietary graphics |
| Buildable disassembly → **100% byte-perfect** ROM rebuild | 🟡 byte-exact; organised by the 443 functions; **first 18 functions converted to real re-assemblable MN10300 assembly** (the 99.9% encoder + `kn7asm` now assemble mnemonics back to exact bytes) | grow the `CONVERT` set to disassemble the rest |
| Name functions from symbol tables | ✅ **444 functions named** from the firmware's own MILK-toolkit reflection tables (same names as the KN5000); `kn7000.sym` / `src/symbols.inc` | extend with the `MT_`/class descriptor tables |

## Firmware & CPU

| KN5000 | KN7000 status | Notes |
|--------|---------------|-------|
| [Memory map](/memory-map/) | 🟡 [top-level map known](/kn7000/); **112 individual I/O registers recovered** across 5 banks (timers, GPIO, LCD block, dual tone generators) — see the [I/O register map](/kn7000/#io-register-map-from-firmware-analysis) | assign each bank to its peripheral device |
| [Boot sequence](/boot-sequence/) | 🟡 boot header + reset vectors disassembled | trace init once more code is named |
| [CPU subsystem](/cpu-subsystem/) doc | ⬜ | document the MN10300/AM33 core, its I/O, and the panel sub-CPUs (CPL/CPC/CPR/CPSD) |
| Reset vector / version block | 🔒 lives in an **undumped internal boot ROM** at `0x4C000000` / top-of-flash `0x7FFFxx` | needs a hardware dump or an exploit (as the KN5000 sub-CPU boot ROM did) |
| [Test modes](/test-modes/) | 🟡 service-test strings + IC map recovered | document each test screen |
| [Firmware update procedure](/firmware-update-procedure/) & validation | 🟡 container + `.INF` checksums understood | trace the on-device flash-write path |

## Subsystems (transfer via the shared framework)

The KN5000 subsystem docs describe the **same MILK UI toolkit** the KN7000 uses,
so they are the best starting point for each KN7000 equivalent:

| KN5000 subsystem | KN7000 status | Notes |
|------------------|---------------|-------|
| [UI Framework](/ui-framework/) / [widget types](/ui-widget-types/) | 🟡 187 identical `*Proc` handlers, 216 identical `MT_` APIs confirmed | port the KN5000 widget docs; resolve the KN7000 class table |
| [Audio subsystem](/audio-subsystem/) / [tone generator](/tone-generator/) | ⬜ | **dual** tone generators (IC203/204 + IC207/208) — new vs the KN5000 |
| [Display subsystem](/display-subsystem/) | ⬜ | LCD V-RAM IC104; likely a different controller |
| [Keybed scanning](/keybed-scanning/) | ⬜ | |
| [MIDI subsystem](/midi-subsystem/) | ⬜ | |
| [Sequencer](/sequencer/) / [accompaniment engine](/accompaniment-engine/) | ⬜ | style/rhythm taxonomy partially shared |
| [Storage / FDC](/fdc-subsystem/) | ⬜ | adds an **SD-card slot** and USB *Song Manager* (new) |
| [Control panel protocol](/control-panel-protocol/) | ⬜ | four panel sub-CPUs vs the KN5000's arrangement |

## Emulation (MAME)

| KN5000 | KN7000 status | Notes |
|--------|---------------|-------|
| [MAME driver](/mame-pull-requests/) ([PR #14558](https://github.com/mamedev/mame/pull/14558)) | 🟡 **draft started** in the `kn7000_mame` overlay repo: machine driver (memory map, ROM regions, LCD placeholder) + the beginnings of an **MN10300 execution core** (device scaffold + first instruction batch) | not yet build-tested; grow the instruction set, then boot |
| MN10300 CPU core | 🟡 **~99.94% of real instructions implemented** (single-byte group, all common prefixed groups `F0`-`F4`/`F8`/`FA`/`FC`/`FE`, `movm`, and the `setlb`/`Lcc` loop cache); length decoder validated (656k instructions, 0 mismatches); `movm` register mask resolved empirically | build-test, interrupts/exceptions, timing; remaining 0.06% = unused `udf*` coprocessor ops + rare `lra` |
| Peripheral HLE (panel, TG, FDC, display) | ⬜ | reuse KN5000 HLE patterns where the shared design allows |

## Homebrew & higher-level work

| KN5000 | KN7000 status | Notes |
|--------|---------------|-------|
| [Homebrew SDK / app loader](/hdae5000-homebrew/) | ⬜ | a GCC `mn10300` toolchain could shortcut this |
| [Feature-demo / SSF presentation system](/feature-demo/) | 🟡 demo slideshows extracted as JPEGs; `<SLIDESHOW>` markup seen | decode the demo/presentation scripting |
| [Another World VM](/another-world-vm/) style homebrew port | ⬜ | long-term, once a toolchain + emulator exist |
| [Service manual](/) PDF | 🔒 | source a KN7000 service manual for board/IC/pinout ground truth |
| [Cross-version diffs](/cross-version-diff-guidebook/) | 🔒 | only one KN7000 program version (v16 / internal 941) is in hand; more releases needed |

## Suggested order of work

1. **Symbol map** — ✅ largely done: 444 functions recovered and named from the
   firmware's reflection tables, directly reusing KN5000 framework knowledge.
   Remaining: fold in the `MT_` API and class-descriptor tables.
2. **Real assembler** — build a GNU binutils `mn10300` toolchain so the
   disassembly can use a standard `as`/`ld` (with `kn7asm.py` as the zero-dependency
   fallback), and to unblock homebrew.
3. **Grow the disassembly** — convert `.incbin` regions to named MN10300 code and
   typed data, holding the 100% byte-match invariant, starting from the named
   framework entry points.
4. **MN10300 MAME core** — write the execution core (the disassembler is the
   starting point) to enable an emulation driver.
5. **Subsystem docs** — port the KN5000 subsystem pages, adapting for the dual tone
   generators, SD/USB storage, and panel sub-CPUs.
6. **Chase the undumped ROMs** — the boot ROM at `0x4C000000` and the picture flash
   at `0x57800000` will eventually need a hardware dump.
