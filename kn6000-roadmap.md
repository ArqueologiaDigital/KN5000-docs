---
layout: page
title: KN6000 / KN6500 Roadmap
permalink: /kn6000-roadmap/
---

# KN6000 / KN6500 — preservation plan

Goal: reproduce, for the Technics **SX-KN6000** and **SX-KN6500**, everything the
project achieved for the [KN5000](/system-overview/) and
[KN7000](/kn7000-roadmap/) — extraction, ROM reconstruction, a byte-exact
disassembly, symbol recovery, table-ROM asset decoding, and a MAME driver with an
MN10300 CPU core.

The IC-level **[hardware architecture](/kn6000-hardware/)** has been recovered from
the *Technics SX-KN6000* (89-page) and *SX-KN6500* (142-page) service manuals —
main CPU **MN10300** (`MN103002A`), program flash `IC11/IC12`, custom-data flash
`IC18` (defaulted from the Initial Data Disk), tone-generator LSI, DSP, four 64 Mbit
wave ROMs, and 8-bit panel sub-CPUs (CPL/CPC/CPR).

## The key discovery: four re-targets of one source tree

Reconnaissance of `~/compartilhado/KN6000/ca_software_files` (downloaded from the
same ca-software.com source as the KN7000 files) establishes the decisive facts:

| Property | KN5000 | KN6000 | KN6500 | KN7000 |
|----------|--------|--------|--------|--------|
| CPU | Toshiba **TLCS-900** | **MN10300** ✅ | **MN10300** ✅ | **MN10300** |
| Application framework | **MILK toolkit** | **MILK toolkit** ✅ | **MILK toolkit** ✅ | **MILK toolkit** |
| Firmware container | LZSS `SLIDE4K` | **LZSS `.SLD` (`IKPRG4K`)** ✅ | **LZSS `.SLD` (`IKPRG4K`)** ✅ | LZSS `.SLD` (`JKPRG4K`) |
| Initial-data disk | — | **`idd6000` = same files as `idd7000`** ✅ | (same family) | `idd7000` |

Verified this tick:

- **CPU = MN10300**, same as KN7000. The KN6000 program ROM disassembles as clean,
  coherent MN10300 code (`movm` prologues, `ret [regs],size`, `cd/dd` calls — the
  same idioms as KN7000). So the KN6000/KN6500 are the **MN10300 siblings of the
  KN7000, not of the TLCS-900 KN5000.**
- **Same MILK toolkit**: `DefaultClassProc`, `MT_GetModeProc`, `MT_AreYouClassProc`,
  `ObjectProc`, `InheritedProc`, `ResourceProc`, `ResBitmapProc`, … are all present
  — the same reflection-table framework whose `*Proc`/`*Func` tables gave us all
  2,302 KN7000 function names.
- **~85 % source-level reuse with KN7000**: 4,479 of the KN6000's 5,234 distinct
  ≥8-char strings also appear verbatim in the KN7000 ROM (internal symbol names,
  resource names, `MT_*`, `_TT_SDMIXER`, `ConvertStringsEx`, …). But **0 % of the
  compiled code is byte-identical** — exactly the KN5000↔KN7000 relationship: *a
  great deal of understanding transfers even though no machine code does.*

**Consequence:** almost the entire KN7000 toolchain applies to KN6000/KN6500
directly, and a **four-way comparison** becomes a force-multiplier (below).

## What we have (the files)

`~/compartilhado/KN6000/ca_software_files/` (self-extracting archives, same layout
as the KN7000 download):

| File | Contents | Role |
|------|----------|------|
| `kn6-71.zip` | → `kn6-v7-1a.exe` / `-1b.exe` → **`IK1.SLD` / `IK2.SLD`** | **KN6000 firmware v7.1** — program flash (0x200000) + table flash (0x1F7A31) |
| `kn65-13.zip` | → `kn65_v1-3a/b.exe` → **`IKV1.SLD` / `IKV2.SLD`** | **KN6500 firmware v1.3** — program (0x200000) + table (0x181691) |
| `idd6000.exe` | `01ctmini.ast`, `03favini.fav`, `02umdini.md`, `04hpgini.hmp` | Initial-Data disk — **identical file set to `idd7000`** |
| `ca6001-ca6010`, `ca6000p/s`, `scd6000` | style / sound / CA-software modules | user-content packs (decode later) |
| `ca6tm01/02` | test-mode | service data |
| `ca6fp01-04`, `ca6dim` | JPEG slideshows | marketing (not firmware) |

Extraction is **already proven**: `kn7000_extraction`'s `lzss` + `kn7000_extract.py`
decoded all four `IK*.SLD` images with the magic `IKPRG4K` unmodified.

## The four-way code-reuse strategy (the force-multiplier)

Because KN5000/6000/6500/7000 are re-targets of **one evolving source tree**, treat
them as a parallel corpus and cross-reference constantly:

1. **Symbol "Rosetta stone".** A function named in KN7000 (from its MILK reflection
   tables) has a counterpart in KN6000/6500 — found not by byte-matching (compiled
   code differs) but by **string/structure matching**: the `*Proc`/`*Func` reflection
   tables exist in every model, so re-run the KN7000 symbol-recovery generically on
   each ROM, then align by name. Names recovered in *any* model propagate to all.
2. **Shared data formats, decode once.** `.SLD`/LZSS, the Initial-Data disk, the
   table-ROM directory, UI bitmaps (palette + `table_bitmaps.py`), the sound/style
   name tables, PAD phrase presets — all are MILK formats. The KN7000 decoders
   (`table_extract.py`, `table_names.py`, `style_names.py`, `pad_names.py`,
   `table_bitmaps.py`) should run on the KN6000/6500 table ROMs with, at most, offset
   tweaks.
3. **Bug/behaviour triangulation.** Open questions on one model (e.g. the KN7000
   rhythm-name resolution, the library-ROM self-load, the panel board-decode) can be
   cross-checked against the other three: where three agree and one differs, the
   difference localises the model-specific code.
4. **MN10300 trio first.** For 6000/6500 use **KN7000 as the primary reference**
   (same CPU, same era, closest strings); fall back to KN5000 only for
   framework-level concepts that predate the MN10300 port.

## Transfer table — KN7000 accomplishment → KN6000/6500 plan

| KN7000 accomplishment | Reuse for KN6000/6500 | Work remaining |
|-----------------------|------------------------|----------------|
| `.SLD`/LZSS decode → flash images | ✅ **works unmodified** (magic `IKPRG4K`) | checksum-verify (`@XXXX`/`#XXXXXXXX` sums in the `SMCK*.INF`) |
| Split table ROM → 84-segment directory + 293 bitmaps + sound/style names + PAD presets | 🟢 same MILK formats; reuse `table_*.py` | re-point offsets; regenerate galleries |
| MN10300 disassembler (`unidasm -arch mn10300`) | ✅ **works** (verified on KN6000 code) | — |
| MN10300 **execution core** (`mn10300.cpp`, incl. `udf00`/`udf07`, interrupts) | ✅ **reuse the KN7000 core verbatim** | none for the ISA; only device wiring |
| MAME driver (`kn7000.cpp`) | 🟢 **fork → `kn6000.cpp` / `kn6500.cpp`** | new memory map / base address, panel wiring, ROM regions |
| Self-loaded library ROM (`0x4C000000`) | 🟢 likely the same mechanism | find the copy routine + source offset per model |
| Byte-exact buildable disassembly + `mn10300_asm.py` | 🟢 transfers | regenerate per ROM |
| 2,302 functions named from MILK reflection tables | 🟢 **rerun generically per ROM**, then four-way align | — |
| Subsystem docs (memory map, boot, panel, test modes) | 🟢 port + diff | model-specific deltas |

## Phased plan

**Phase 0 — repos & scaffolding.** Mirror the KN7000 layout: a `kn6000_extraction`
(SLD/table decoders), a `kn6000_mame` overlay repo (fork `kn7000_mame`: reuse
`src/devices/cpu/mn10300/*` verbatim, add `src/mame/matsushita/kn6000.cpp` +
`kn6500.cpp`), a `kn6000_disassembly`, and KN6000/6500 pages on this docs site. Keep
`make verify` byte-exact and Jekyll building, as for KN7000.

**Phase 1 — extraction & ROM reconstruction.** Decode `IK*.SLD`/`IKV*.SLD`
(done → 4 flash images); verify the `SMCK*.INF` block checksums; run the table-ROM
splitter + `table_names.py`/`style_names.py`/`table_bitmaps.py`/`pad_names.py`;
decode `idd6000` (`01ctmini.ast` is raw DEFLATE, same as `idd7000`). Publish the
sound/style-name lists and image gallery.

**Phase 2 — boots in MAME.** Find each model's **reset vector / base address**
(KN7000 = `0x48400000`) and I/O map by disassembly; fork the KN7000 driver, drop in
the MN10300 core, and iterate to first boot (hardware init → BSS → MILK kernel →
self-loaded library ROM), reusing the KN7000 interrupt/timer findings.

**Phase 3 — symbol recovery & disassembly.** Run the generic MILK
reflection-table walker to name functions; build the byte-exact disassembly;
recover `CL_*`/`VF_*`/`BD_*` constants. Then **four-way align** names across models.

**Phase 4 — the four-way diff.** Build a cross-model symbol/behaviour map; use it to
resolve each model's open questions and to back-fill KN5000/KN7000 gaps (e.g. the
rhythm-name resolution, panel board-decode). Document the shared framework once, with
per-model deltas.

## Status & next steps (updated 2026-07-07)

**Done:** firmware extracted (all four `IK*/IKV*.SLD` images); [hardware mapped from
the service manuals](/kn6000-hardware/); **draft MAME drivers built** — `kn6000` and
`kn6500` are registered in the shared `kn7000_mame` tree (reusing `kn7000_state` and
the KN7000 machine config, same verified `0x48400000` program base), build into the
one binary alongside `kn7000`, pass `-verifyroms`, and run their MN10300 firmware at
~140 % speed with no fatal error. **[Table-ROM name inventories extracted](/kn6000-names/)**:
KN6000 4,440 strings (1,963 internal MILK GUI symbol names + user-facing style/sound
names), KN6500 4,189 (2,006 symbols) — via the new NUL-walk `name_extract_nul.py`.

**Next:** exploit the recovered **MILK symbol names** for cross-model symbol recovery
(align KN6000/KN6500/KN7000 GUI-resource identifiers → propagate function names); tune
each model's memory map / peripheral wiring for a full boot; decode the remaining
table-ROM assets (bitmaps, PAD presets); add `kn5000` to the same binary (blocked on a
MAME genie/`SOURCES` link quirk — see memory).

## More Technics models incoming

The user is supplying more devices for the same consolidated treatment
(`~/compartilhado/KN2400_KN2600_KN7000`): **KN2400** (`kn24-11.zip`), **KN2600**
(`kn26-11.zip` + `KN2600_CD-Rom.zip`), a **PR804** CD-ROM, and additional KN7000
material (`kn7-14`/`kn7-16` firmware, `KN7000_CD-Rom.zip`, `scd7000`, `idd7000`,
`ca7001`, `custom1/2`). Triage next: extract each `.SLD`, confirm CPU + MILK
framework, and fold into what is becoming an N-way family comparison.
