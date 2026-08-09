---
layout: page
title: Firmware Robustness & ROM Archival
permalink: /kn7000-firmware-security/
---

# Firmware Robustness & ROM Archival

Two questions about the KN7000's main‑CPU firmware, answered by static reverse engineering of the
program ROM:

1. **Can data from outside the instrument make the CPU run code?** — the expansion connector and the
   SD card are the two places an outside party supplies bytes. Could either one seat a ROM, or a
   crafted file, that the firmware would *execute*?
2. **Can the instrument non‑destructively archive its own firmware?** — some KN7000 units carry an
   **undocumented earlier program‑ROM revision** that deserves preservation. What can the machine's own
   diagnostics tell us, and hand us, without desoldering a chip?

The short answers: **no, external data cannot run code** on the KN7000 (by construction, on both
surfaces); and the instrument can **identify** its firmware revision non‑destructively but **cannot
hand over its contents** — a full dump needs a hardware read or a code‑execution route. The detail is
below. All of it is ordinary preservation reverse engineering; nothing here is an attack recipe, and
the one memory‑safety wrinkle it turns up is something a faithful emulator should *reproduce*, not fix.

---

## 1. The two external surfaces, and the pattern that closes the door

Bytes reach the KN7000 from outside through exactly two channels:

- the **CN106 expansion connector** (the SY‑EW wave bus / SOUND‑RAM windows — see
  [Expansion Bus & Wave‑ROM Dump]({{ site.baseurl }}/kn7000-expansion-and-wave-dump/)), and
- the **SD card** (and its sibling floppy — see [Storage & File System]({{ site.baseurl }}/kn7000-storage-subsystem/)).

Both are handled by the same shape of code, and it is that shape that makes code execution
impossible. The firmware never takes an address *from the data* and jumps to it. Instead it **matches**
the data against fixed tables to derive a small **bounded index**, and calls a **fixed handler** baked
into the ROM. The outside bytes choose *which* of a fixed set of routines runs; they never supply the
routine's *address*.

For the SD card this is the disk‑file dispatcher at `0x4852B6B0`: it matches a file's tag/extension
against the string tables `DiskFileTagTable` (`0x48664090`) and `DiskFileExtTable` (`0x48664438`),
turns the match into an index (`asl 3` / `mulu 0xc`), and calls a fixed PC‑relative handler. A scan of
the whole dispatcher finds **zero** register‑indirect calls or jumps that take their target from file
data. The expansion connector's board‑probe path has the identical property.

---

## 2. The expansion connector — a capability that was removed

The older SX‑KN6000 / KN6500 firmware *did* have a way for an expansion board to run code: a routine
that memory‑compares an `XAPR` signature on the board window and then calls vectors read from the
board. On the KN7000, **that facility was excised.** The only trace left is a dead checksum stub at
`0x4849FD9E` that nothing reaches. The `XAPR` and `HD‑SX3` markers that look like support on the
KN7000 are shared‑codebase residue — the KN2400, which has *no expansion connector at all*, shows the
same singletons.

Three independent reverse‑engineering passes (~0.97 confidence) confirmed there is **no native
code‑execution vector** and **no memory‑corruption path to the program counter** from the expansion
board. What a malformed board *can* do is bounded to an **arbitrary read** (information disclosure back
into the instrument) and a **denial of service** (a hang/crash). Board content that the firmware does
copy lands in **fixed** work‑RAM buffers (the copy base is a compile‑time constant, `*(0x501496B8) =
0x840327E8`), never a pointer that is later called.

---

## 3. SD media — seven parsers, five clean, two that overflow

Every SD file format was reverse‑engineered and classified on two axes: does any file byte become a
control‑transfer target or store base (control‑flow), and is any copy sized by a file‑supplied number
into an unbounded buffer (memory‑safety)?

| Format (extension) | Control‑flow | Memory‑safety | Notes |
|---|---|---|---|
| `.AST` custom data (zlib) | fixed‑table | **safe** | zlib 1.0.4 streaming inflate into a fixed scratch cap, then a fixed flash region; the claimed decompressed size is range‑checked, never trusted as a copy count |
| SMF `.MID` / `.SEQ` / `.SQF` | fixed‑table | **safe** | table‑driven MIDI state machine; SysEx/meta lengths streamed‑and‑discarded, not trusted to size a copy |
| `.ACT` demo script | fixed‑table | **safe** | a *text/markup* interpreter dispatched through a fixed handler table keyed by a string‑matched token |
| `.FAV` / `.MD` / `.HMP` → SRAM | fixed‑table | **safe** | compile‑time‑fixed byte counts into fixed SRAM; no file‑supplied count governs any copy |
| SD µ‑COM transport | fixed‑table | **safe** | every SD byte consumed as data; no execute‑from‑SD, no SD firmware update; the runtime library loads from **program flash**, not the card |
| **`.JPG` (JFIF/JPEG)** | fixed‑table | **⚠ unbounded write** | §3.1 |
| **`.HMP` embedded BMP** | fixed‑table | **⚠ unbounded write** | §3.2 |

There is no execute‑from‑SD path of any kind — no overlay loader, no plug‑in, no firmware update from
the card. Five of the seven parsers are also cleanly bounded. The two exceptions are the image
decoders, and they fail the same way.

### 3.1 JPEG

`.JPG` is a genuine SD file type (the picture/wallpaper feature). The SOF0 marker parser reads the
declared height and width and checks **only that they are positive** — it never compares them against
the fixed **640×240** display plane (`0x500D4080` / `0x500F9880`) they are about to fill, and it
decodes *before* it asks how big the image is. The pixel writer computes its destination as
`base + (y_origin + row)·640 + x_origin + col` with **no clamp against the plane**. A well‑formed JPEG
declaring, say, 640×480 is decoded at full size and the writer walks off the bottom of the buffer,
laying file‑derived pixels into the RAM that follows.

### 3.2 BMP

The BMP header validation is otherwise careful (signature, header size, bit depth, compression,
palette) but **never validates the width**. Height is clipped to the 240 rows; width is not. Each row
is copied with a length taken straight from the file into a buffer with a fixed 640‑pixel stride, so a
wide enough BMP overruns it. Because the home‑page code *centres* the picture with
`X = (screen − width)/2`, an oversized width wraps `X` to a huge unsigned value and the destination
wanders.

### 3.3 What it is — and what it is not

In both cases **control‑flow stays safe**: the file controls the *length* and *offset* of a write, not
a pointer that is loaded and called. This is memory corruption, not a jump to attacker code — and
whether it could be steered all the way to the program counter is **unproven** (the writes land in
work RAM ahead of the display plane, not on the stack). It is the same open residual the expansion
board leaves.

For emulation this is reassuring rather than alarming: MAME runs the instrument's *real* decoder on the
real CPU core over RAM the memory map keeps bounded, so the host is never wild‑written and the emulated
instrument corrupts its own RAM exactly as hardware would. **Faithfulness means not adding the bounds
check the firmware never had.**

---

## 4. Archiving the firmware — what the instrument will and won't give up

The second question is preservation: a KN7000 with an undocumented early program‑ROM revision. The
firmware's own diagnostics were mapped to see how far they get.

### 4.1 It tells you its version (the easy, zero‑risk win)

The KN7000 has a built‑in **SOFTWARE VERSION** screen. Each firmware component prints a decimal number
via a `%4d` format string — `PROGRAM : %4d` (`0x485D67E0`), `TABLE : %4d`, `RHYTHM : %4d`,
`PICTURE : %4d`, under the header `--- SOFTWARE VERSION ---` (`0x485D5D9C`). The **PROGRAM** number is a
single 16‑bit build stamp read straight out of program flash:

```
mov   (0x4873660C), d0        ; the PROGRAM build stamp, in flash at file offset 0x33660C
movhu d0, (0x50007DC4)        ; -> formatted as "PROGRAM : %4d"
```

In the reference firmware image this cell reads **941** (`0x03AD`, verified). An earlier revision will
show a *smaller* integer — and **that integer is the revision identifier.** The owner opens the Version
screen and reads it off the LCD; no tools, no risk, no disassembly. Once a unit is dumped by any means,
the same `u16` at the equivalent of `0x4873660C` re‑identifies the build.

This has already found an unpreserved firmware: a real instrument reports `PROGRAM : 893`
and `TABLE : 80`. For where each of the four numbers comes from — only PROGRAM is a
compiled-in constant; TABLE, RHYTHM and PICTURE are parsed as ASCII decimal out of their
own flash devices — see the [SOFT VERSION screen]({{ site.baseurl }}/kn7000-soft-version/).

### 4.2 The ROM device test checks integrity, but shows no fingerprint

Service diagnostic **§8.1 "ROM device test"** (`MainRomTestFunc` `0x4849FDF8`, reached by holding
**C#3 + D#3 + C#4** at power‑on, then PAGE to the item and **EXECUTE**) sweeps the full 8 MB flash
window `0x48000000`–`0x487FFFFF` — table ROM plus the program flash (IC16) — as interleaved halfwords,
accumulating two 32‑bit additive sums. But it runs the sweep **twice and compares the two sums for
self‑consistency** (its golden‑value seed table is all zeros in this build), and reports only **OK / NG**
on the LCD. No number is shown; the sums are discarded. So the test confirms the flash *reads back
cleanly* but **cannot fingerprint a revision** on‑screen. Usefully, its algorithm is now fully
specified, so a unique fingerprint can be computed **offline** from any dump: two 32‑bit additive
halfword sums over `0x48000000`–`0x487FFFFF`.

### 4.3 No firmware‑mediated byte dump exists

The decisive negative: **no KN7000 diagnostic ever emits program‑flash bytes** to MIDI, serial, or
disk. The ROM test posts only UI OK/NG events; the firmware‑update path is strictly **write‑only**
(disk → flash); and there is no CPU‑observable program‑flash read port analogous to the tone‑generator
[wave‑ROM read port]({{ site.baseurl }}/kn7000-expansion-and-wave-dump/) that made the wave ROMs
dumpable. The firmware can **identify** the revision but not **reproduce** it.

### 4.4 So how do you get the contents?

| Route | Non‑destructive? | Status |
|---|---|---|
| **SOFTWARE VERSION screen** | yes — read `PROGRAM : NNNN` off the LCD | ✅ identifies the revision now, zero risk |
| **§8.1 ROM device test** | yes — OK/NG integrity | ✅ confirms the flash reads cleanly |
| **In‑circuit clip read of IC16** (CPU held in reset) | yes — reading doesn't modify the chip | pragmatic path to full contents; extends the [ROM‑dumping roadmap]({{ site.baseurl }}/rom-dumping-roadmap/) |
| **Code‑execution dumper** (CPU runs a small flash reader → observable port) | yes | the only *firmware‑only* route to full contents; uncertain — no proven corruption→PC path exists |
| **Desolder + programmer** | no (risks the part) | the route this whole investigation exists to avoid |

The first step costs nothing and should be done first: photograph the Version screen and record the
§8.1 result. The full dump then follows by clip read (recommended) or, if a path is ever found, by a
firmware‑only dumper.

---

## Sources & related pages

- [ROM Dumping Roadmap]({{ site.baseurl }}/rom-dumping-roadmap/) · [Wave‑ROM Dump Tutorial]({{ site.baseurl }}/kn7000-wave-rom-dump/)
- [Expansion Bus & Wave‑ROM Dump]({{ site.baseurl }}/kn7000-expansion-and-wave-dump/) · [Storage & File System]({{ site.baseurl }}/kn7000-storage-subsystem/)
- Findings notes (project repo): `FINDINGS-expansion-buses-and-code-exec.md`,
  `FINDINGS-sd-media-codeexec-and-parsers.md`, `FINDINGS-program-rom-version-and-dump-paths.md`.

*This page is preservation reverse engineering of hardware the project maintains. The memory‑safety
observations are documented so that emulation stays faithful; they are not exploitation instructions.*
