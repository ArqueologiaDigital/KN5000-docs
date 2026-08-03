---
layout: page
title: Shared Codebase Map
permalink: /technics-shared-codebase/
---

# Shared Codebase Map (KN5000 ↔ KN7000)

Many Technics keyboards appear to have had their firmware developed by reusing a
common source codebase. This page maps **where the KN5000 and KN7000 firmwares
match** — which is valuable precisely because the two machines use **different
CPU architectures**, so any similarity must originate above the machine-code
level, in shared *source*.

> **The key constraint:** the [KN5000]({{ site.baseurl }}/cpu-subsystem/) runs a Toshiba
> **TLCS-900/H2**; the [KN7000]({{ site.baseurl }}/kn7000/) runs a Panasonic **MN10300/AM33**.
> Compiled machine code therefore **cannot** be shared. Everything that *does*
> match — identifier names, resource tables, message text, numeric constants —
> is evidence of a shared source tree that was **recompiled** for each target.

## Verdict

The evidence establishes, at high confidence, that the KN5000 and KN7000
firmwares are **two re-targets of one shared application source tree**. The
application layer — an object-oriented UI framework, its localization tables, and
its resource/audio/menu data — was **ported and evolved onto a new CPU and OS**,
while the platform layer (CPU port, RTOS, compression, image pipeline) was
rewritten.

Every match below was located at exact byte offsets in **both** program ROMs
(`kn5000_v10_program.rom` and `kn7000_program.rom`) or table ROMs, and the
headline claims were independently re-verified.

## The smoking gun: a shared misspelling

The single most conclusive proof is an **idiosyncratic spelling error carried
verbatim into both firmwares**: "Comporser" (for "Composer").

| | KN5000 | KN7000 |
|--|--------|--------|
| `ComporserNameBoxProc` | `0x20406` | `0x23D782` |
| `MT_GetComporserName` | `0x20E94` | `0x23D65C` |

A typo cannot arise by coincidence or by convergent naming across two independent
teams targeting two different CPUs. It can only be **inherited from a common
source tree**. (Confirmed present in both program ROMs by direct search.)

## What cannot be shared: machine code

| | KN5000 | KN7000 |
|--|--------|--------|
| Main CPU | Toshiba TLCS-900/H2 (TMP94C241F) | Panasonic MN10300/AM33 |
| Program flash mapping | CPU `0xE00000` | CPU `0x48400000` |
| Instruction encoding | TLCS-900 | MN10300 (byte-aligned CISC) |
| RTOS | custom | named `MILK MN10300 Ver1.0R1` |

Because the instruction sets differ, no byte-run of executable code is common to
the two images. Every match below is therefore source-level reuse, made visible
only because the compiler embeds these strings/tables verbatim regardless of
target CPU.

## What is shared: the MILK UI toolkit

Both ROMs embed the runtime symbol tables of the **same object-oriented,
event-dispatch UI framework** — the "MILK Toolkit" (`MT_` API), named by the
KN7000 kernel banner. These are consumed by the framework's own
class-introspection / RTTI at runtime, so the compiler stores them as literal
strings.

| Framework element | KN5000 | KN7000 | Overlap |
|-------------------|--------|--------|---------|
| `*Proc` class/widget handler names (`ViewableProc`, `InheritedProc`, `DefaultClassProc`, `ObjectProc`, `WindowProc`, `Vw*`/`Ac*`/`Ps*`/`Iv*` taxonomy) | 348 unique, table at `0xB1040`–`0xB15FF` | 537 unique, table at `0x1B3B40`+ | **187 exact-identical** names; same class hierarchy `DefaultClassProc→ClassProc→ObjectProc→ViewableProc` |
| `MT_*` toolkit API (`MT_GetLanguagePtr`, `MT_GetProcedure`, `MT_FLASHWRITE`, `MT_SleepApTask`, `MT_WakeUpApTask`, `MT_IWillWakeUp`, `MT_VST_PST_OK`) | 450 unique | 427 unique | **216 exact-identical**, including highly idiosyncratic names and the cooperative-task API |
| Framework core (`RegisterObjectTable`, `InitializeObjectTable`, `DispatchEvent`, `SendEvent`, `RegisterTitle`, `GetTitleNow`, `CheckViewObject`) | `0xB153E`–`0xB15B4` | `0x1B3B65`–`0x1B406A` | identical names, same contiguous symbol table |
| RTTI / resolution API (`MT_GetProcedure`, `MT_GetModeProc`, `MT_GetTitleProc`, `MT_AreYouClassProc`) | present | `0x1B2A4E`–`0x1B3058` | identical |
| `TT_*` title-tag vocabulary (`TT_SEMENU`, `TT_SEEASY`, `TT_SEDIGEFF`; SE/DK/CM families) | 211 tags (`TT_`) at `0xD588`+ | 375 tags (`_TT_`) at `0x1AEF61`+ | **141 identical** bodies (KN7000 adds a `_` prefix) |
| Symbol-table storage format | NUL-terminated + `0xFF` even-alignment pad (`ALIGNED_STRING`) | same contiguous NUL-terminated table | shared data-format design |
| Developer/system objects | `Panel Simulator for HK`, `PanelSimulator`, `ClipBoard` | `Panel Simulator 2.1` / `for IK`, `ClipBoard`, `DefaultWindow` | same tool, matured (`2.1`) |

The `Panel Simulator for <model-code>` template (HK on the KN5000, IK on the
KN7000) and the whole class-introspection table survive the CPU change intact —
the shared code is the entire event-dispatch + object-registration core, not just
leaf widgets.

### Framework internals: the dispatch & object model

Decoding the KN7000 tables reveals *how* this shared toolkit works internally —
mechanism that transfers to the KN5000 too:

* **A unified 32-bit message-id space, partitioned by category** (the high 16
  bits). The same encoding recurs everywhere: `0x0002_xxxx` toolkit opcodes,
  `0x0004_xxxx` / `0x0008_xxxx` `MT_` method selectors, `0x0005_xxxx` UI events,
  `0x0006_xxxx` system/task messages. `SleepMainTask`, for instance, sends
  opcode `0x00020009` with message id `0x0006009D`.
* **The `MT_` dispatch table** (KN7000 name array at `0x326CE4`, 241 entries) is
  *heterogeneous*: each method resolves to **either** a direct code pointer
  (≈29, e.g. `MT_GetProcedure` itself), a **selector** id (`0x0004_xxxx`, routed
  through the kernel), or a pointer into the **class-descriptor region** — i.e.
  the toolkit mixes direct calls, late-bound message dispatch and RTTI in one
  table.
* **An object property/class metadata region** (KN7000 ≈`0x1B1000`+): class
  descriptors delimited by `0xFFFFFF00`, carrying property lists whose names
  (`parent`, `top`, `super`, `fontcolor`, `pagemax`, `editsw`, …) are what the
  `MT_GetPropName`/`MT_GetPropData`/`MT_GetClass`/`MT_GetParentClass` RTTI reads.
* **A named-constant table** for the property values — recovered by
  `kn7000_disassembly/tools/gen_constants.py`: `VF_*` view flags, `CL_*` palette
  colours, `BD_*` border styles, and part/track/step enums. These cross-check the
  rest of the reverse engineering exactly — `VF_Invisible=1`, `VF_Change=4`,
  `VF_Const=8` are precisely the object flag bits the KN7000's `SetVisible` /
  `SetChange` / `SetConst` test with `btst`, and `CL_Transparent=0xF7` names the
  transparent palette index used by both machines' sprite blitters.

## What is shared: localization & resource tables

| Element | KN5000 | KN7000 |
|---------|--------|--------|
| Multi-language dialog blocks (`ATTENTION!` / `ACHTUNG !` / `Perhatian !`; `Sind Sie sicher ?`; Indonesian `Apakah yakin akan dihapus ?`) in identical EN/DE/FR/ES/Indonesian order | `0x1E4D0`+ (repeats `0x25884`, `0x3382C`, …) | `0x2276B8`+ (repeats `0x261E6C`, `0x2AE468`) |
| Vendor-custom 8-bit codepage — `¿Está seguro?` = bytes `BF 45 73 74 E1 …` (¿=`0xBF`, á=`0xE1`, û=`0xFB`), **not** Latin-1 | `0x1E55E` | `0x227BFF` (byte-for-byte identical) |
| Private engineering test-menu selector (~90 bytes: `\|-\|SAVE REMINDER\|'COMPLETED' MESSAGE\|ARE YOU SURE?\|…\|EASY SETTING`) | `0xD4D5A` | `0x20E735` (byte-identical) |
| User prompt `Please Insert the Style Convert Disk!` | `0x1EE44` | `0x207124` |

A non-user-facing engineering test-menu string present verbatim in both is a
direct fingerprint of a shared source/asset tree; the identical vendor codepage
implies shared font and string tooling.

## What is shared: audio & menu data tables

| Element | KN5000 (table ROM) | KN7000 (table ROM) |
|---------|--------------------|--------------------|
| Tone-name inventory in 16/17-char centered fields (`SymphonicStrings `, `Concert Strings  `, `CupMuteTrombone  `, ` Bottle Marimba `, ` Country Fiddle  `) — byte-identical incl. padding | `SymphonicStrings` @ `0x36DD6` | @ `0xA2266` |
| Easy-Setting / Music-Stylist genre menu (`     8 Beat     `, `16 Beat`, `Dance Pop`, `Jazz Fusion`, …) — 10 labels, identical centered padding | `0x1DEFC` (prog) | `0x1CCF2C` (prog); only traversal order differs |

## Evolved, but recognizably the same lineage

Some elements were carried forward with modifications — the signature of a shared
codebase that kept developing:

- **Version screen**: both share the `SOFT VERSION` caption and the internal
  `MPVersion` symbol; the KN7000 added `RHYTHM`/`PICTURE` rows and dropped the
  MAIN/SUB split (reflecting its single-CPU design).
- **`<model> SOUND RAM` convention**: the KN7000 extends it to a predecessor list
  at `0x1B8517` — `KN6000 / KN5000 / KN3000 / KN2000 / KN1600 SOUND RAM` — i.e. it
  explicitly reaches back to import the **KN5000's own** sound-RAM data format.
- **Sound-group / style categories**: `DIGITAL DRAWBAR`, `DRUM KITS`,
  `JAZZ COMBO`, `MARCH & WALTZ`, `COUNTRY`, `CUSTOM` carry over exactly; others
  are reorganized or spelled out (`ACCORDION REG.` → `ACCORDION REGISTER`).

## The divergence boundary (what was rewritten)

Shared reuse stops cleanly at the application layer:

| Layer | KN5000 | KN7000 |
|-------|--------|--------|
| RTOS/kernel | custom (no banner) | `MILK MN10300 Ver1.0R1` @ `0x3B8AAC` |
| Compression | [LZSS]({{ site.baseurl }}/lzss-compression/) | LZSS **and** zlib/deflate 1.0.4 @ `0x3B8604` |
| Photo/demo images | headerless 8bpp bitmaps | *adds* JPEG (Adobe Photoshop) + Windows BMP |
| Tone-init helper | `SwbtWr` @ `0x1F410` | absent (sound-init layer reworked) |
| Version widgets | — | KN7000-only `AcProgVerBoxProc`, `IvMpVerWinProc`, `DefaultWindow` (same naming grammar) |

The KN7000-only additions follow the **same framework naming grammar**
(`Ac*BoxProc`, `Iv*WinProc`), exactly what you expect from new features authored
downstream in a shared codebase.

Note that the image *divergence* is only partial: the KN7000 **adds** JPEG for
photos and demo art but still stores its **UI icons as headerless
palette-indexed bitmaps reached through a `{width, height, pointer}` descriptor
hierarchy — the same design as the KN5000** (293 such bitmaps, including a 240
sprite icon set; see the [KN7000 image gallery]({{ site.baseurl }}/kn7000-image-gallery/#raw-ui-bitmaps-table-rom)).
So even the graphics pipeline is shared at the UI layer; only the photo/demo
asset format was modernised.

## The update-disc container is shared too

Independently of the firmware, the update subsystem is the same across models —
same `.SLD` container, same 24-bit big-endian size field, same 4 KB
[LZSS]({{ site.baseurl }}/lzss-compression/), same `.INF` checksum sidecar — only the magic string
differs (`SLIDE4K` → `JKPRG4K`/`JKTB14K`/`JKTB24K`). See
[KN7000 System Update Discs]({{ site.baseurl }}/kn7000-system-update-discs/) and the KN5000's
[System Update Discs]({{ site.baseurl }}/system-update-discs/).

## Why this matters

Mapping the shared portions lets discoveries transfer between models: a data
format decoded on the well-documented KN5000 gives a decoding head-start on the
KN7000, and the shared `MT_`/`*Proc` symbol tables let KN5000 symbol knowledge
seed the KN7000 disassembly directly. Across the whole Technics keyboard line,
this reuse map is a route to understanding the family as a **single evolving
system** rather than a set of unrelated instruments.

## Method note

Matches were found by intersecting whole-token string inventories of the two
program ROMs and comparing the table ROMs field-by-field, then verifying exact
byte offsets on both sides. Counts (e.g. "187 identical `*Proc` names") are
whole-string set intersections; "byte-identical" means an exact byte-run match
including padding. The comparison covered UI-framework symbols, container/file
formats, localized string tables, and numeric/audio data tables.
