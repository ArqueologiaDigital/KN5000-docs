---
layout: page
title: Shared Codebase Map
permalink: /technics-shared-codebase/
---

# Shared Codebase Map (KN5000 ↔ KN7000)

Many Technics keyboards appear to have had their firmware developed by reusing a
common source codebase, or at least significant portions of it. This page maps
**where the KN5000 and KN7000 firmwares match** — which is valuable precisely
because the two machines use **different CPU architectures**, so any similarity
must originate above the machine-code level, in shared *source*.

> **The key constraint:** the [KN5000](/cpu-subsystem/) runs a Toshiba
> **TLCS-900/H2**; the [KN7000](/kn7000/) runs a Panasonic **MN10300/AM33**.
> Compiled machine code therefore **cannot** be shared between them. Everything
> that *does* match — file formats, symbol-naming conventions, resource tables,
> message text, numeric constants — is evidence of a shared source lineage that
> was **recompiled** for each target.

## What cannot be shared: machine code

| | KN5000 | KN7000 |
|--|--------|--------|
| Main CPU | Toshiba TLCS-900/H2 (TMP94C241F) | Panasonic MN10300/AM33 |
| Program flash mapping | CPU `0xE00000` | CPU `0x48400000` |
| Instruction encoding | TLCS-900 | MN10300 (byte-aligned CISC) |
| Toolchain | [LLVM TLCS-900 backend](/rom-reconstruction/) | MAME `unidasm -arch mn10300` |

Because the instruction sets differ, no byte-run of executable code is common to
the two images. This rules out binary reuse and makes the *non-code* matches
below all the more telling.

## What is shared: the update-disc container

The clearest shared component is the firmware-update container, documented for
both models:

| Aspect | KN5000 ([SLIDE4K](/system-update-discs/)) | KN7000 ([`.SLD`](/kn7000-system-update-discs/)) |
|--------|-------------------------------------------|-------------------------------------------------|
| Magic | `SLIDE4K\0` | `JKPRG4K\0` / `JKTB14K\0` / `JKTB24K\0` |
| Size field | 24-bit **big-endian** decompressed size | identical |
| Compression | [LZSS](/lzss-compression/), 4 KB window, zero-initialized | identical scheme |
| Checksum sidecar | 32-bit total + per-block 16-bit sums | identical (`SMCK*.INF`) |

The `4K` window size, the big-endian size field in an otherwise little-endian
system, and the LZSS bit layout are all shared — the KN5000's own header bytes
are only fully explained *by* the KN7000's size-field discovery. This is the same
update subsystem, carried forward.

## What is shared: firmware design and resources

The KN7000 program image carries the same developer symbol-naming conventions and
UI-framework vocabulary seen throughout the KN5000
([UI Framework](/ui-framework/), [UI Widget Types](/ui-widget-types/)):

- **`PanelSimulator`** — the KN5000's on-screen panel-simulation concept recurs
  by name in the KN7000.
- **`_TT_*`** tag-name tables, **`*Proc`** window-procedure names, and **`MT_*`**
  API names — the same identifier scheme in both firmwares.
- **Version screen** strings (`SOFT VERSION`, `--- SOFTWARE VERSION ---`,
  `PROGRAM : %4d`) appear in both.
- **Model-compatibility lists** — the KN7000 enumerates
  `KN6000 / KN5000 / KN3000 / KN2000 / KN1600 SOUND RAM`, explicitly reaching back
  across the product line to load older models' sound-RAM data.
- The **table/resource ROM** is an offset-directory archive in both machines.

## Detailed match table

*A dimension-by-dimension comparison (UI symbols, container formats, string /
message content, numeric tables and audio data) with exact strings and file
offsets on both sides is being compiled from a direct byte-level comparison of
the two ROM sets. It will be published here.*

## Why this matters

Mapping the shared portions lets discoveries transfer between models: a data
format decoded on the well-documented KN5000 gives a decoding head-start on the
KN7000 (and vice-versa), and the naming conventions let KN5000 symbol knowledge
seed the KN7000 disassembly. Over the whole Technics keyboard line, this reuse
map is a route to understanding the family as a single evolving system rather
than a set of unrelated instruments.
