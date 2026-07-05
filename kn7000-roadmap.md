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
| Split the Table Data ROM into assets | ✅ [84-segment directory decoded](/kn7000-firmware/); `table_extract.py`; **293 raw UI bitmaps in true colour** (palette @ prog `0x32573C`, `table_bitmaps.py`); **[1,454 sound + 931 style names](/kn7000-sound-names/)** (`table_names.py`/`style_names.py`); **[120 PAD phrase presets](/kn7000-sound-names/#sound-arranger-pad-presets)** decoded as 0xF5-delimited MIDI phrases (`pad_names.py`) | decode the `TCMP`/"Technics Rhythms" style/rhythm pattern data; sub-tables 1 & 3 |
| Extract embedded images | ✅ [169-image gallery](/kn7000-image-gallery/) | decode any remaining raw/proprietary graphics |
| Buildable disassembly → **100% byte-perfect** ROM rebuild | 🟡 byte-exact; organised by the **2,302 functions**; **66 functions converted to real re-assemblable MN10300 assembly**, with call targets resolved to labels (recovered names, else synthetic `func_<ADDR>` — 140/181 call sites named) so the source reads normally | grow the `CONVERT` set to more subsystems |
| Name functions from symbol tables | ✅ **2,302 functions named** from the firmware's own MILK-toolkit reflection tables — all ~114 widget/handler tables discovered generically (518 `*Proc` + 353 `*Func`); plus **191 named constants** recovered (`tools/gen_constants.py`: `CL_*` palette colours, `VF_*` view flags, `BD_*` styles, part/track enums); `kn7000.sym` / `src/symbols.inc` / `src/constants.inc` | the `MT_` table decodes as a mixed code-ptr / selector / class-descriptor dispatch table |

## Firmware & CPU

| KN5000 | KN7000 status | Notes |
|--------|---------------|-------|
| [Memory map](/memory-map/) | 🟡 [top-level map known](/kn7000/); **112 individual I/O registers recovered** across 5 banks (timers, GPIO, LCD block, dual tone generators) — see the [I/O register map](/kn7000/#io-register-map-from-firmware-analysis) | assign each bank to its peripheral device |
| [Boot sequence](/boot-sequence/) | 🟢 runs in MAME through hardware init, BSS, the MILK kernel and the self-loaded library ROM. **MN10300 interrupts now implemented and FIRING** (INTC `0x34000100` + system-tick timer → maskable vector `0x4C03DDA0`; the library handler runs and returns via `rti`). Boot still parks in a task-ready poll (`0x4C03DCF3`): the tick fires but doesn't yet wake a task | advance the scheduler — likely implement the handler's AM33 `udf*`/extended ops + confirm the IAGR index |
| [CPU subsystem](/cpu-subsystem/) doc | ⬜ | document the MN10300/AM33 core, its I/O, and the panel sub-CPUs (CPL/CPC/CPR/CPSD) |
| Reset vector / version block | 🔒 lives in an **undumped internal boot ROM** at `0x4C000000` / top-of-flash `0x7FFFxx` | needs a hardware dump or an exploit (as the KN5000 sub-CPU boot ROM did) |
| **Library / kernel ROM** at `0x4C000000` | 🟢 **NOT undumped — self-loaded from the program flash at runtime**: `InitializeBlock27` (`0x484D7BBD`) copies ~253 KB from prog-ROM `0x487B8FD1` into `0x4C000000`, which the copy loop aliases to `0x8C000000` (adds `0x40000000`). All 298 entry points (C runtime + MILK kernel: printf `0x4C001A48`, …) are inside that block. In MAME, aliasing `0x4C`↔`0x8C` to one RAM makes the boot run the real library code — no dump, no HLE. See `kn7000_mame/notes/library-rom-loading.md` | (was wrongly thought to need a hardware dump) |
| [Test modes](/test-modes/) | 🟡 service-test strings + IC map recovered | document each test screen |
| [Firmware update procedure](/firmware-update-procedure/) & validation | 🟡 container + `.INF` checksums understood | trace the on-device flash-write path |

## Subsystems (transfer via the shared framework)

The KN5000 subsystem docs describe the **same MILK UI toolkit** the KN7000 uses,
so they are the best starting point for each KN7000 equivalent:

| KN5000 subsystem | KN7000 status | Notes |
|------------------|---------------|-------|
| [UI Framework](/ui-framework/) / [widget types](/ui-widget-types/) | 🟡 **518 `*Proc` window-procedures + 353 `*Func` handlers named**; the runtime core is documented from the disassembly — [Event & Dispatch](/kn7000-event-system/) (60 `EV_*` codes, object table @`0x5000757C`) and [Tasks & Scheduler](/kn7000-task-scheduler/) (main/AP tasks, sleep/wake message API) | port the remaining KN5000 widget docs; the `MT_` method-selector table |
| [Audio subsystem](/audio-subsystem/) / [tone generator](/tone-generator/) | ⬜ | **dual** tone generators (IC203/204 + IC207/208) — new vs the KN5000 |
| [Display subsystem](/display-subsystem/) | 🟡 **[documented](/kn7000-display-subsystem/)** from the disassembly: panel-type detection (colour / 2-bit), per-depth bitmap blitters (4/16/256), CLUT @`0x32573C`, font table, LCD I/O `0x34000000` + framebuffer `0x90000000` | trace the exact pixel path to V-RAM |
| [Keybed scanning](/keybed-scanning/) | ⬜ | |
| [MIDI subsystem](/midi-subsystem/) | 🟡 two ports identified (SIO ch 1&2 @ `0x34000810`/`0x34000820`, ISRs `0x484B1E86`/`0x484B2037`, 31250 8N1) and **declared in the MAME driver**; ch2's differing config (`0x1181`) may be a computer/TO-HOST link | trace the MIDI parser + confirm ch2's role |
| [Sequencer](/sequencer/) / [accompaniment engine](/accompaniment-engine/) | 🟡 **[sequencer documented](/kn7000-sequencer/)**: `MT_Seq_*` engine API, `EV_SEQ_*` events, record/play + SMF, Seq→Composer/Pad copy | accompaniment/style engine still ⬜; style/rhythm taxonomy partially shared |
| [Storage / FDC](/fdc-subsystem/) | 🟡 **[documented](/kn7000-storage-subsystem/)**: three media (floppy FAT12/16, SD card, USB Song Manager) via the shared `Fmm*` File Management Mode; file types `.MID`/`.CST`/Composer/Playlist/…; rich `Sdc*` handler set | trace the SD/FDC media I/O drivers |
| [Control panel protocol](/control-panel-protocol/) | 🟢 **[documented](/kn7000-control-panel/) + serial framing fully reverse-engineered + HLE'd in MAME**: four panel sub-CPUs scan switches + drive LEDs over a 3-channel SIO ASIC; the 2-byte `[ADDR][DATA]` switch/LED frame formats are decoded (e.g. START/STOP press = `C0 10`) and modelled in the driver | deliver switch reports to firmware once the CPU takes SIO interrupts |

## Emulation (MAME)

| KN5000 | KN7000 status | Notes |
|--------|---------------|-------|
| [MAME driver](/mame-pull-requests/) ([PR #14558](https://github.com/mamedev/mame/pull/14558)) | 🟢 **builds, passes `-validate`, and RUNS** (`build.sh` in the overlay repo): boots the real firmware headless, **self-loads the library ROM** and runs deep init; has the SIO/panel HLE, two MIDI ports, a clickable `.lay`, and a real 640×240 8bpp `screen_update` (framebuffer `0x500D4080`, CLUT `0x50031490`) | **MN10300 interrupts** (so the scheduler runs → UI draws + panel/MIDI RX); then model the remaining peripherals |
| MN10300 CPU core | 🟢🎉 **THE KN7000 DRAWS ITS SCREEN IN MAME** (2026-07-05): full AM33 core (incl. the DSP MAC ops, imm8-total call/ret, level-triggered interrupts) + a 2-level INTC with per-level vectors; the MILK RTOS multitasks correctly (the 1kHz tick -- deliberately the LOWEST-priority interrupt -- vectors to the scheduler entry `0x4C03DE26`, which switches task stacks; quick vector `0x4C03DDA0` for device levels) and the firmware renders its panel-diagnostic UI: all 640x240 pixels, real fonts/CLUT (screenshot in `kn7000_mame/notes/images/`). Boot I/O trace remains byte-identical to the Python interpreter. Full spec + war story in `kn7000_mame/notes/interrupt-mechanism.md` + blog part 2 | panel handshake IN PROGRESS: full protocol chain reversed (EXTMD 0x34000280 confirmed; TX state machine grp 0x11; 2-edge ATN pulse grp 0x1A; reply-per-byte grp 0x10 into ring 0x5006BDB4; success = ring head moved) and the ATN/reply model implemented; presence line 0x36008084 found+fixed, FIRST real command byte transmitted ([00 00 1F], state 3 reached); per-data-write transfer trigger confirmed (state-2 writes data with no bit15); three INTC/panel mechanisms committed (IAGR latch-on-accept, per-data-write completion, unserviced re-delivery — all measurement-backed); wire format decoded (syncs interleave payloads); next: single-attempt forensics on the state-2-exit crash → normal UI → panel keys/MIDI RX → .lay layout |
| Peripheral HLE (panel, TG, FDC, display) | 🟡 **control panel + MIDI modelled**: the driver has a 3-channel SIO ASIC model (`0x34000800`), a control-panel HLE (LED-command decode on TX, 250 Hz button scan → switch-report frames on RX) and **two MIDI ports** (byte↔bit UART bridges → MAME `midi_port`), plus a **clickable `.lay`** (184 buttons + LED strips). TG/FDC/display still ⬜ | deliver panel RX + MIDI IN to firmware once the CPU takes SIO interrupts; then TG/FDC/display |
| MIDI ports | 🟡 **declared in the driver**: SIO channels 1 & 2 (`0x34000810`/`0x34000820`) each wired to a MIDI IN + MIDI OUT port; TX path functional, RX awaits CPU interrupts | verify against real MIDI traffic once interrupts land |

## Homebrew & higher-level work

| KN5000 | KN7000 status | Notes |
|--------|---------------|-------|
| [Homebrew SDK / app loader](/hdae5000-homebrew/) | ⬜ | a GCC `mn10300` toolchain could shortcut this |
| [Feature-demo / SSF presentation system](/feature-demo/) | 🟡 demo slideshows extracted as JPEGs; `<SLIDESHOW>` markup seen | decode the demo/presentation scripting |
| [Another World VM](/another-world-vm/) style homebrew port | ⬜ | long-term, once a toolchain + emulator exist |
| [Service manual](/) PDF | 🔒 | source a KN7000 service manual for board/IC/pinout ground truth |
| [Cross-version diffs](/cross-version-diff-guidebook/) | 🔒 | only one KN7000 program version (v16 / internal 941) is in hand; more releases needed |

## Suggested order of work

1. **Symbol map** — ✅ largely done: **2,302 functions** recovered and named from
   the firmware's ~114 reflection tables, directly reusing KN5000 framework
   knowledge. Remaining: the `MT_` method-selector table (selectors, not code).
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
