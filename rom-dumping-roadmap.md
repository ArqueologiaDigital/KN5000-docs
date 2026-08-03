---
layout: page
title: ROM Dumping Roadmap
permalink: /rom-dumping-roadmap/
---

# ROM Dumping Roadmap

Where every ROM in the MN10300 family of Technics keyboards stands: what is preserved, what is
not, and — for each device still missing — a concrete proposal for how to obtain it.

*Last reviewed: 2026-08-02. Status is taken from the MAME driver, which is the authoritative
inventory; run `mame -listroms <machine>` to regenerate it.*

---

## 1. Summary

| machine | devices preserved | devices still undumped | missing volume |
|---|---|---|---|
| SX-KN7000 | 4 program/table + 9 custom-flash images | **7** | 80.5 MB |
| SX-KN6000 | 2 program + 1 custom-flash image | **7** | 40 MB |
| SX-KN6500 | 2 program + 1 custom-flash image | **9** | 56 MB |
| SX-KN2400 | 2 program | **3** | 24 MB |
| SX-KN2600 | 2 program (shared with KN2400) | **4** | 24.5 MB |

**30 undumped entries across the five ROM sets, but only 22 distinct physical devices** — five
parts are fitted to both the KN6000 and the KN6500, so one donor instrument serves two machines.

Everything preserved so far was obtained **without opening an instrument**. That is the headline
fact of this roadmap and it shapes every proposal below.

---

## 2. What is sorted out

**Program and table firmware — all five machines.** Extracted from Panasonic's own update disks
(`.SLD` payloads, SLIDE4K LZSS), not from chips. Ten of the eleven images validate against
**Panasonic's own checksum oracles** — the `SMCK*.INF` files shipped alongside them, giving a
32-bit total plus 16-bit sums of every `0x40000` block.

| model | oracle | total | blocks |
|---|---|---|---|
| KN7000 program | `SMCKPR1.INF` | `0x18CE8702` | 16/16 |
| KN7000 table | `SMCKTB1.INF` | `0x13DCD1A3` | 16/16 |
| KN6000 | `SMCKPR1.INF` | `0x166ADB67` | 16/16 |
| KN6500 | `SMCKPV1.INF` | `0x157ED142` | 15/15 |
| KN2400 | `SMCKPR1.INF` | `0x16DA58C4` | 15/15 |

> The KN6000/KN6500/KN2400 oracles sit **inside the self-extracting `.exe`**, not at the top level
> of the `.zip`. They were missed for a long time for exactly that reason — and both this site's
> tooling and its notes carried "no `.INF` oracle shipped" as a statement of fact until 2026-08-02.

**Custom-data flash — KN7000, KN6000, KN6500.** Not chip reads, but the exact bytes the firmware
writes: the Initial Data Disk payload is inflated and written **verbatim to flash offset
`0x20000`**, the top 30 of the 64 KiB sectors of a 16 Mbit bottom-boot device. Nine images are
declared for the KN7000 (factory default plus eight published data sets) and one shared IDD6000
payload for the KN6000 and KN6500. See [Custom Data Flash](/custom-data-flash/) and
[KN7000 Initial Data](/kn7000-initial-data/).

**HD-SX3 expansion firmware.** 768 KiB, decompressed from `EXTAPR.SLD` in 2026-08-02 — the first
time this image had been recovered.

---

## 3. What remains

### SX-KN7000 — 7 devices, 80.5 MB

| device | part | size | type | role |
|---|---|---|---|---|
| IC203 | `C3CBQD000002` | 16 MB | mask ROM | wave, main TG bank Y |
| IC204 | `C3CBQD000001` | 16 MB | mask ROM | wave, main TG bank X |
| IC207 | `C3CBQD000004` | 16 MB | mask ROM | wave, sub TG bank Y |
| IC208 | `C3CBQD000003` | 16 MB | mask ROM | wave, sub TG bank X |
| IC18 | `C3CBND000046` | 8 MB | mask ROM | rhythm (later production) |
| IC19 | `C3CBMD000098` | 8 MB | mask ROM | picture |
| IC414 | `C3FBKD000162` | 512 KB | flash | SD card sub-CPU program |

### SX-KN6000 — 7 devices, 40 MB

| device | part | size | type | role |
|---|---|---|---|---|
| IC13 | `QSIGX3C16008` | 2 MB | mask ROM | table / font |
| IC14 | `QSIGX3C16007` | 2 MB | mask ROM | table / font |
| IC205 · IC206 | `QSIGX3C64004` · `QSIGX3C64005` | 8 MB each | mask ROM | wave |
| IC207 · IC208 | `QSIGX3C64006` · `QSIGX3C64007` | 8 MB each | mask ROM | wave |
| IC15 | `QSIGX3C32021` | 4 MB | mask ROM | rhythm data |

### SX-KN6500 — 9 devices, 56 MB

**Five are the same parts as the KN6000** (IC205–IC208, IC15) — dump a KN6000 and most of the
KN6500 comes with it. KN6500-only:

| device | part | size | type | role |
|---|---|---|---|---|
| IC13 | `C3FBMD000069` | 2 MB | **flash** | table / font |
| IC14 | `C3FBMD000068` | 2 MB | **flash** | table / font |
| IC209 · IC210 | `QSIGX3C64020` · `QSIGX3C64019` | 8 MB each | mask ROM | wave (extra pair) |

> Note the KN6500 uses **flash** where the KN6000 uses mask ROM for table/font. This site
> previously described both as mask ROM; that was a gap, corrected once the pinout was checked
> (`RESET#`, `RY/BY#`, `VPP` are present).

### SX-KN2400 / SX-KN2600 — 3 and 4 devices, 24 / 24.5 MB

| device | part | size | type | role |
|---|---|---|---|---|
| IC14 | `C3ZBNG000023` | 8 MB | flash | rhythm and other data |
| IC302 | `C3ZBP0000003` | 8 MB | flash | wave bank Y |
| IC303 | `C3ZBP0000004` | 8 MB | flash | wave bank X |
| IC404 | `C3ZBK0000020` | 512 KB | flash | SD sub-CPU (KN2600 only) |

**Everything undumped on these two models is flash, not mask ROM** — the easiest category to read,
and the only family where that is true.

---

## 4. How to dump them

Ranked by risk to the instrument. Prefer the earliest method that can work.

### Method A — find the update files *(zero risk; a search problem, not an engineering one)*

Every image we already hold came this way. Panasonic's own `TECHNICS.HDD` descriptor **enumerates
update payload classes we have never located**, including **Table DATA, Rhythm and
Wave-Expansion**. If those files were ever distributed, they contain the contents of several of the
mask ROMs above without anyone touching hardware.

**Proposal.** Sweep dealer archives, the Wayback Machine, European Technics user groups (the
KN-series had an active German-language community), and collector CD-ROMs for `.SLD`/`.AST` files
whose 8-byte magic is not one we already recognise. The container is documented in
[LZSS Compression](/lzss-compression/); the magic letter is sequential by generation
(KN5000 `H`, KN6000 `I`, KN7000 `J`).

*Applies to:* potentially the table/font and rhythm devices on every model. Not the wave ROMs,
which were almost certainly never updatable.

### Method B — read it with the instrument's own CPU *(no desoldering)*

The main CPU can address several of these devices directly. A small program uploaded over an
existing path can read a ROM and stream it out.

**Proposal.** Establish which regions the CPU can see from the memory map
([Memory Map](/memory-map/)), then use one of the exfiltration routes the firmware already
implements — MIDI system-exclusive dump, the serial port, floppy write, or SD write on models that
have it. This is how homebrew on the HD-AE5000 already works; see
[HD-AE5000 Homebrew](/hdae5000-homebrew/).

*Applies to:* IC18/IC19 on the KN7000, IC15 and the table/font devices on the KN6xxx — anything on
the CPU bus. On the **KN7000 the wave ROMs also qualify** (see Method B′); on the KN5000 they do not.

### Method B′ — read the KN7000 wave ROMs through the tone-generator port *(no desoldering, no harness)*

The KN7000 wave ROMs were long assumed CPU-invisible. They are not: the tone generators expose a
**wave-memory read port**, and the service-mode §8.9 WAVE ROM test already sweeps the full 16 MiB of
each part through it. The read loop (checksum core `0x484839A1`) is simply:

```
  side A (IC203/IC204):  write hi-addr -> 0x98050006 ; write addr -> 0x98050008 ; read WORD <- 0x9805000A
  side B (IC207/IC208):  write hi-addr -> 0x98040006 ; write addr -> 0x98040008 ; read WORD <- 0x9804000A
```

**Proposal.** Upload a small routine over an existing exfil path (MIDI sysex / SD) that drives that
port across the whole address space and streams the words out. Verify against the firmware's own
[golden checksums](#5-verifying-a-dump). This reaches all four KN7000 wave ROMs (64 MB) with no
hardware work at all. Full write-up: [KN7000 Expansion Bus & Wave-ROM Dump Routes](/kn7000-expansion-and-wave-dump/).

*Applies to:* KN7000 IC203/204/207/208 only. **The KN5000's IC303 has no equivalent read port** — its
Wave ROM Check is an acoustic (listen-for-distortion) test — so its wave ROMs still need Method C or D.

### Method C — in-circuit read on the tone-generator bus *(no desoldering, needs a harness)*

For the machines with **no** CPU-side wave read (the KN5000, and if Method B′'s port arithmetic cannot
be pinned down) the wave ROMs are the bulk of what is missing and must be read on their own bus.

**Proposal.** Hold the tone generator in reset so it stops driving its bus, then clip onto the ROM
and drive address lines from an external microcontroller, reading data back. Practical notes: these
are TSOP packages, so a purpose-made clip or a set of tack-soldered wires to the address/data lines
is required; verify the TG is genuinely tri-stated before driving anything; and read each device
twice with different address orderings to catch a floating line.

*Applies to:* all wave ROMs — KN7000 IC203/204/207/208, KN6xxx IC205–IC210, KN2400 IC302/303.

### Method D — desolder and read on a programmer *(highest risk, highest certainty)*

Hot-air rework, TSOP adapter socket, universal programmer.

**Proposal of last resort.** These parts are irreplaceable and the boards are thirty-year-old
consumer instruments; lifting a pad ends that instrument. Reserve for a machine that is already
beyond repair — a water-damaged or otherwise dead unit is the ideal donor and is far cheaper to
acquire than a working one. **Prefer a dead donor over a working instrument in every case.**

*Applies to:* any device, but should only ever be needed for the mask ROMs.

### Method E — sub-CPU flash over the inter-CPU protocol

`IC414` (KN7000) and `IC404` (KN2600) are the SD-card sub-CPU's own program flash.

**Proposal.** The inter-CPU protocol is already documented for this family
([Inter-CPU Protocol](/inter-cpu-protocol/), [Sub-CPU Command Format](/subcpu-command-format/)).
Check whether the sub-CPU implements a memory-read or firmware-verify command; the main CPU has to
be able to validate a sub-CPU update somehow, and whatever mechanism does that is likely readable.
This is a firmware reverse-engineering task, not a hardware one, and costs nothing to attempt.

---

## 5. Verifying a dump

Any dump obtained by any method above can be checked **against the instrument itself**, which is
better than checking it against our own expectations.

**The ROM DEVICE TEST.** These machines have a service-mode self-test that computes and displays
checksums per device — the KN7000 firmware contains display strings of the form
`CUSTOM FLASH:     IC21 =`. Entering that mode on a real instrument and photographing the values
gives an oracle for every device it covers. See [Test Modes](/test-modes/).

> **This is the single highest-value thing an owner can contribute without any disassembly**:
> enter the ROM device test and photograph the screen. It costs nothing, risks nothing, and turns
> every future dump from "plausible" into "verified".

**The KN7000 wave-ROM golden checksums** are already extracted from the firmware (table `0x485CFD18`),
so a Method B′ dump of those four parts can be verified with no instrument at all. The value is
Σ(hi+lo) over every 16-bit word of the device:

| device | expected checksum |
|---|---|
| IC203 | `0x8164C77C` |
| IC204 | `0x815CFC83` |
| IC207 | `0x8331EF0B` |
| IC208 | `0x83254F9D` |

**The `.INF` oracles**, where an update disk exists for that device, as in §2.

**Cross-model agreement.** Five KN6000 parts are fitted to the KN6500. Dumps from two different
instruments that agree byte-for-byte are strong evidence against a bad read.

---

## 6. Priorities

1. **Method A sweep** — free, non-invasive, and could resolve several devices at once.
2. **ROM DEVICE TEST photographs** from any owner of any model — free, and makes everything else
   verifiable.
3. **Method E** on the sub-CPU flash — pure firmware work, no hardware access needed.
4. **A dead donor KN6000** — five of its devices also serve the KN6500, the best ratio available.
5. **Wave ROMs** — the bulk of the missing data, and the only category with no non-invasive route.

---

## See also

- [MAME Pull Requests](/mame-pull-requests/) — how these declarations reach upstream
- [Custom Data Flash](/custom-data-flash/) · [KN7000 Initial Data](/kn7000-initial-data/)
- [ROM Reconstruction](/rom-reconstruction/) · [LZSS Compression](/lzss-compression/)
- [Flash Programming](/flash-programming/) · [Test Modes](/test-modes/)
