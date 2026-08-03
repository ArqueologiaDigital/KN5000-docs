---
layout: page
title: KN7000 Expansion Bus & Wave-ROM Dump Routes
permalink: /kn7000-expansion-and-wave-dump/
---

# KN7000 Expansion Bus & Wave-ROM Dump Routes

How the SX-KN7000's expansion hardware is wired, what its firmware does with a board plugged in, and
— the practical payoff — **the wave ROMs turn out to be readable by the CPU itself**, through a tone-
generator port the service-mode ROM test already drives.

*Sources: the KN7000 service manual schematic sheets (pages read visually, not via the PDF text
layer) and disassembly of the KN7000 / KN6000 / KN6500 program firmware (MN10300, CPU base
`0x48400000`). Cross-checked against the MAME driver. Last reviewed 2026-08-03.*

---

## Two expansion interfaces, two connector types

The KN7000 has **two** distinct expansion interfaces on separate connectors — a point that is easy to
miss, because both serve the SY-EW01..04 wave-expansion boards:

| interface | connectors (part) | width | carries | read by |
|---|---|---|---|---|
| **CPU peripheral bus** (EXP.CS) | `CN202 CN203 CN205 CN207` (`QJTG02840AA`) | 40-pin | `A(1..19)`, `D(16..31)`, one of `EXP.CS0..3`, `WE2`, `RE` | the **main CPU** |
| **wave bus** | `CN204 CN206` (side A) · `CN208 CN209` (side B) (`K1KA80A00100`) | 80-pin | `WAX(0..16)`, `WAY(0..21)`, `WD(0..15)`, `WOEX`, `WOEY`, `EXCEX0..3`, `EXCEY0..3` | the **tone generators** |

Four 40-pin plus four 80-pin connectors = one CPU connector and one wave connector per SY-EW slot.
The service manual's §8.12 test warns a failure implicates *"the address/data bus as well as the
strobe signal lines"* — because both buses are involved. A SY-EW board is **dual-natured**: the CPU
loads samples into it as *SOUND RAM* over the peripheral bus, and a tone generator plays them back
over the wave bus.

> **Correction to earlier notes:** `CN106` is the **SD-card connector** (`SDCS/SDSO/SDCLK/SDSI`), not
> the expansion/HDD bus. The peripheral EXP.CS bus is the four 40-pin connectors above.

## The four EXP.CS "SOUND RAM" slots

`EXP.CS0..3` are asserted by the system address decoder `IC3` (a `TC74VHC139`, the `PSRT.EXP`
expansion region, decoding `A(23)`/`A(24)`), one strobe per slot. The four CPU windows are:

```
  0x41000000    0x41800000    0x56000000    0x57000000
```

The firmware runs a four-slot detector (the SoundRam probe at `0x48449EF4`) that validates an
**`"Expansion Board KN7000 SOUND RAM"`** signature (ASCII table at `0x485B8518`) at each window. On a
match it walks a **relocatable data structure** the board exports: every pointer is read from the
board header and relocated by the window base. With no board fitted, all four read empty and the
firmware reports **"NO WAVE EXPANSION BOARD"**.

Every board-supplied pointer is dereferenced as **data** (`movbu`/`movhu`/`mov`); the only computed
control transfers are a bounded jump-table switch into firmware (table at `0x486A2D90`, all entries
firmware addresses). **So a KN7000 EW board cannot run code** — it is data-only sound RAM.

## The wave bus is shared with the internal ROMs (buffered)

The internal wave ROMs sit on the raw wave bus:

| chip | part | side | bus |
|---|---|---|---|
| IC203 | `C3CBQD000002` | A (master TG, IC201) | `AWAX/AWAY/AWD` |
| IC204 | `C3CBQD000001` | A | `AWAX/AWAY/AWD` |
| IC207 | `C3CBQD000004` | B (sub TG, IC205) | `BWAX/BWAY/BWD` |
| IC208 | `C3CBQD000003` | B | `BWAX/BWAY/BWD` |

The same buses are branched to the 80-pin expansion connectors, which is why a text search for the
bus names near the connectors finds nothing — **the nets are renamed at a row of buffer resistors:**

- **data** — `BWD(0..15)` → `EXBWD(0..15)` through 47 Ω series packs (`Z242/Z244/Z245/Z246` on side B;
  side A feeds `EXAWD`). The connector's data lines are the ROMs' data lines, buffered.
- **chip-enable** — a demux (`IC202` side A, `IC206` side B, both `TC74VHC139`) decodes the top wave-
  address bits (`AWAX/BWAX 22/23`) into `EXACEX/EXACEY` and `EXBCEX/EXBCEY`, giving expansion samples
  their own enable space.
- the 80-pin connector also carries the wave **address** (`WAX/WAY`) and **output-enables**
  (`WOEX/WOEY`) directly.

A board seated on an 80-pin connector therefore sees every wave-bus transaction, including the tone
generator reading the internal ROMs — a solderless snoop point. But there is a cleaner route.

## ★ The wave ROMs are CPU-readable, through the tone generator

The wave ROMs were long assumed CPU-invisible (on the TG's private bus). They are not. The service
manual's **§8.9 WAVE ROM test** returns OK/NG in ≤30 s, and in the firmware it is a full digital
read:

- `MainWaveRomTestFunc` (`0x484A2E3A`) runs the test for indices 0..3 = the four ROMs, calling a per-
  ROM checksum helper (`0x48483B63`) and OR-ing an error bit per ROM.
- The helper sets a length of **`0x00FFFFFF`** — the entire 16 MiB (128 Mbit) of each part, a
  **complete sweep** — and calls the checksum core `0x484839A1`.
- The core is a plain read loop over a tone-generator **wave-memory read port**:

  ```
    side A (IC203/IC204):  write hi-addr -> 0x98050006 ; write addr -> 0x98050008 ; read WORD <- 0x9805000A
    side B (IC207/IC208):  write hi-addr -> 0x98040006 ; write addr -> 0x98040008 ; read WORD <- 0x9804000A
    checksum += (word>>8) + (word & 0xFF)   for every 16-bit word across 0x00FFFFFF
  ```

**The CPU reads every raw sample word itself.** So the wave ROMs — 64 MB, the bulk of what is missing
— have a fully *software* dump route: walk `0x9804/0x9805 0006/08 → 000A` across the address space and
stream the words out over MIDI or SD, exactly like any CPU-visible ROM. No bus snoop, no tri-stating,
no soldering.

**Golden checksums** (the firmware's own expected values, table `0x485CFD18`, = Σ(hi+lo) over all
words) verify any dump before the chips are ever in hand:

```
  IC203 = 0x8164C77C    IC204 = 0x815CFC83    IC207 = 0x8331EF0B    IC208 = 0x83254F9D
```

*Still to pin down:* the exact (side, chip, address) → byte mapping inside the port (bank base
`0x8000` plus the running hi/lo latches, and whether the two ROMs per side are a 32-bit-wide pair or a
hi/lo bank). Enough is known to write the dumper loop; confirm the arithmetic against `0x484839A1`
before trusting byte order. The port is **not yet modelled** in MAME, so the software readout runs on
real hardware today; emulating it would need the tone-generator device to answer `0x9804/0x9805
0006/08/0A`.

## Running code from a board — the KN6000/KN6500 XAPR route

The KN7000 EW slots are data-only (above), but its siblings keep the HD-SX3 support the KN7000
dropped, and that path **does** run board code. On the KN6000/KN6500 the board sits at `0x97800000`
with the signature **`"XAPR\0"`**, and once it validates:

```
  0x48572A15  memcmp(0x97800000, "XAPR", 4)          -> sets a present flag
  0x48572A6F  mov (0x9780000C), a0 ; calls (a0)      <- board entry vector +0x0C
  0x48572A8C  mov (0x97800008), a1 ; calls (a1)      <- board entry vector +0x08
  0x48572AAF  mov (0x97800010), a0 ; calls (a0)      <- board entry vector +0x10
```

`calls (aN)` is the MN10300 indirect subroutine call. The `XAPR` header is an **export table of
function pointers the firmware jumps into**. Present a board mapped there with the signature and valid
vectors and the host CPU executes your code — over the firmware's existing MIDI/SD/floppy paths. Both
machines' program ROMs are already dumped, so the value is the confirmed *mechanism*.

## Does the KN5000 have the same wave-read port? No.

The KN5000 is architecturally different, and the answer matters because its IC304–IC306 are currently
only **BAD_DUMP copies of IC307** — a real read-out would fix them.

- Its tone generator **IC303** (`TC183C230002`) is driven by a **Sub CPU** via a register-indirect
  interface. The CPU-facing ports are a register-address latch / voice-status read (`0x100000`), a
  register **data** port (`0x100002`, "voice status readback"), and a keybed-event queue
  (`0x110000`). **None is a wave-memory read port** — nothing lets the CPU address a wave-ROM location
  and read the sample word back, the way the KN7000's `0x9805000A` does.
- Consistent with that, the KN5000's **Wave ROM Check (Test 6)** is an **acoustic** test: the ROMs are
  made to output sine waves as keys are pressed and the technician listens for distortion (C keys →
  IC304 & IC305, C#–B → IC306 & IC307). Disassembling its handler confirms it: `TEST6FUNC`
  (`0xFB7E0E` → core `0xFB7C8F`) sends a single command byte (`0x0003`) toward the tone-generator sub-
  CPU and polls a **status byte** (`(0x8A24) == 0xFC`), then reports OK/NG. There is **no read loop**
  — nothing like the KN7000's 8-million-iteration sweep of `0x9805000A`. The main CPU never sees a
  sample word; it triggers the sine-wave diagnostic and waits for a pass/fail.

So the clean software route does **not** transfer to the KN5000. Its wave ROMs remain reachable only
by an in-circuit snoop of IC303's bus while it plays, or by desoldering — see the
[ROM Dumping Roadmap](/rom-dumping-roadmap/), Methods C and D. (See also
[Tone Generator (IC303)](/tone-generator/).)

## MAME status

The four EXP.CS windows are modelled as empty SY-EW slots — open bus, read-zero, writes dropped —
replacing an earlier 24 MiB RAM placeholder (the firmware only ever *reads* these windows; there is
not a single store to any of the four bases). The machine boots to the play screen and reports "NO
WAVE EXPANSION BOARD", the way real empty hardware does. The tone-generator wave-read port is not yet
modelled.

## See also

- [ROM Dumping Roadmap](/rom-dumping-roadmap/) — where these routes sit in the overall plan
- [KN7000 Sound Subsystem](/kn7000-sound-subsystem/)
- [Tone Generator (IC303)](/tone-generator/) — the KN5000 side
- [Memory Map](/memory-map/)
