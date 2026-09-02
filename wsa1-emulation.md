---
layout: page
title: SX-WSA1 Emulation Status
permalink: /wsa1-emulation/
---

# SX-WSA1 / SX-WSA1R — emulation status

Both variants of the [SX-WSA1]({{ site.baseurl }}/wsa1/) are declared in a MAME
driver that boots them to their real `SOUND MODE` screen and takes button
presses. Unusually for this project, **the CPU core was not what was missing**:
both processors are Toshiba TLCS-900/H **TMP95C061** parts and MAME already
implements that device. What was missing was a **clock** and a **memory map**,
and both were recovered from the firmware images rather than from a databook.

> **⚠ Do not read this page as "the machine works."** Both systems are declared
> `MACHINE_NOT_WORKING | MACHINE_NO_SOUND`, and the second flag is the honest
> one: **nothing synthesises**. The tone generator's actual synthesis, the three
> uPD6383GF DSPs and their microcode upload, the flash and MIDI are all absent,
> and **all six wave mask ROMs are undumped** (`NO_DUMP`). The machine draws a UI
> and responds to its panel. That is all.
>
> The modelling window at `0x00104000` has a
> **placeholder device**, `l7a1429_device`. It models the *register
> interface* — an address latch at `+0`, data at `+2`, a saved register file
> numbered `block * 0x40 + channel` — and synthesises nothing. Its value is that
> the register traffic is now captured and inspectable rather than discarded, and
> that its header carries what is established about the device beside what is
> merely inferred.

### What crosses that bus is parameters, not code

Before writing the device, one thing had to be settled, because a program loader
and a register file are different objects: **is the firmware uploading microcode
to the modelling section, or writing registers?**

It is writing registers, and the method is a controlled comparison rather than an
impression — this firmware contains a *known* code-upload path to measure
against, the DSP effect microcode that leaves CPU 2 through port P7 a byte at a
time with strobes and a `0x1F40` timeout poll.

| discriminant | P7 (known code upload) | `0x104000` |
|---|---|---|
| opaque byte stream | yes — `ld (0x0013),(XIZ+d)` | no |
| handshake / strobe / timeout | yes | no |
| micro-DMA ever aimed at it | channel-driven | **no channel, ever** |
| destination addresses | one port, repeatedly | fixed register set |
| register numbering | n/a | `block * 0x40 + channel` |
| values sourced from | a byte buffer | a packed *part record* |

Eight distinct block numbers, every gap exactly `0x40`, and thirteen
`Pack104_SetInputs_*` routines marshalling part records into them. Reproduce with
`wsa1/notes/sound/dev104_payload_class.py` in the disassembly tree (6 checks).

⚠ **The claim is bounded.** No executable payload crosses `0x00104000`. That is
*not* proof the die holds no microcode of its own — a modelling engine with fixed
on-die code exposing only coefficients would produce exactly this traffic.

⚠ **And the device's name is an inference.** The service manual lists **IC3 =
L7A1429, "MODELING LSI"**, so the part is named; what is *not* established is that
`0x104000` decodes to it. What is established: `0x104000` is the only per-channel
synthesis device CPU 2 drives that has no counterpart in the KN5000's PCM
sibling, and its register file is a different shape from the tone generator's
(19 contiguous blocks against 22 sparse). The disassembly still calls it
`Dev104_` for that reason.

## ⚠ The driver is not upstream, and there are deliberately two of it

Upstream MAME has **no `wsa1.cpp` at all**. What exists is:

* a **development driver** in this project's `kn7000_mame` overlay —
  `src/mame/matsushita/wsa1.cpp` (3,399 lines) plus `wsa1_cpanel.{cpp,h}` and
  `src/mame/layout/wsa1r.lay`;
* a deliberately **smaller submission candidate** on the branch `technics-wsa1`
  of a separate MAME checkout — 610 lines carrying only the two processors, the
  clock, and the part of the memory map that is evidence-complete enough to
  offer. Five prep commits (a ROM record; instantiating both TMP95C061s with a
  partial map; mapping the tone bank at `0xf00000` on CPU 2; naming the floppy
  controller and the model strap; and correcting CPU 1's static RAM to reach
  `0x7fff`, not `0x51ff`) sit on that branch **unmerged**.

**The two files will diverge, and that is intentional.** Everything in the
overlay beyond the submission copy is work in progress, and several pieces rest
on inferences a MAME reviewer would rightly refuse until a schematic or a real
machine confirms them. Do not describe one as the other, and do not "sync" them
mechanically.

## Two systems, one ROM set

```
SYST(1995, wsa1r, 0,     0, wsa1r, wsa1r, wsa1_state, init_wsa1r, "Technics", "SX-WSA1R", MACHINE_NOT_WORKING|MACHINE_NO_SOUND)
SYST(1995, wsa1,  wsa1r, 0, wsa1,  wsa1,  wsa1_state, init_wsa1,  "Technics", "SX-WSA1",  MACHINE_NOT_WORKING|MACHINE_NO_SOUND)
```

`wsa1` is declared a **clone of `wsa1r`** and shares its ROM definitions verbatim
— *not because the rack matters more*, but because **every document the driver
rests on is the rack's**: the service manual is SX-WSA1R only, and the
redistributed image set is *said* by its uploader to have been read from a
rack. (That is testimony, not something this project verified.)

The *emulated machine configuration* is identical between the two, because
everything the driver models is shared: one ROM set, the same pair of
TMP95C061s, the same panel link, the same LCD.

⚠ That is a statement about the driver, **not** about the two products. Their
control panels are genuinely different boards — the firmware gives the keyboard
two extra scan columns and three extra pots (see
[the panel page]({{ site.baseurl }}/wsa1-panel/)) — and no SX-WSA1 document
exists anywhere, so nothing about the keyboard's panel is corroborated by paper.
The driver's configurations match because the parts it currently models happen
to be the shared ones. The difference lives where it actually is — in the
[strap value]({{ site.baseurl }}/wsa1/#two-products-one-rom-set-one-strap-bit)
each `init_` sets (`m_model` = 1 keyboard, 2 rack) and in which inputs the box
physically has. **The default is the rack, deliberately:** it is what the dumped
set was read from, and it is what the machine already did before the strap was
modelled at all, since MAME's unbound port read returns 0 and PB bit 0 therefore
read low.

## Both variants reach a real UI — and they draw different screens

<figure style="margin:1.5rem 0;text-align:center;"><img src="{{ "/assets/images/wsa1/wsa1r_layout_t45_sound_mode.png" | relative_url }}" alt="SX-WSA1R front panel with SOUND MODE on the LCD" style="max-width:100%;border:1px solid #ccc;border-radius:3px;"><figcaption style="font-size:0.8rem;color:#777;">The SX-WSA1R at t = 45 s, on <code>SOUND MODE</code> with its parameter row (OCT / LVL / PAN / EFF1 / EFF2 / REV / INT / MIDI), reached without any input.</figcaption></figure>

<div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;margin:1.5rem 0;">
<figure style="margin:0;text-align:center;"><img src="{{ "/assets/images/wsa1/wsa1r_intnest_implemented_sound_mode.png" | relative_url }}" alt="SX-WSA1R SOUND MODE, one parameter pane" style="image-rendering:pixelated;width:320px;max-width:100%;border:1px solid #ccc;border-radius:3px;"><figcaption style="font-size:0.8rem;color:#777;"><strong>SX-WSA1R</strong> (rack) — one parameter pane</figcaption></figure>
<figure style="margin:0;text-align:center;"><img src="{{ "/assets/images/wsa1/wsa1_intnest_sound_mode.png" | relative_url }}" alt="SX-WSA1 SOUND MODE, two parameter panes" style="image-rendering:pixelated;width:320px;max-width:100%;border:1px solid #ccc;border-radius:3px;"><figcaption style="font-size:0.8rem;color:#777;"><strong>SX-WSA1</strong> (keyboard) — <strong>two</strong> panes side by side</figcaption></figure>
</div>

The keyboard variant draws **two** parameter panes where the rack draws one.
That is the **first screen-level confirmation that the two systems really are
different machines and not a cosmetic split** — the strap is doing visible work.

⚠ The colours are a **driver choice**, not a measurement (see `palette_init()`).
Only the glyphs are evidence.

## The boot, milestone by milestone

Each line below was produced by a named probe in
`kn7000_mame/notes/wsa1-probes/`, and each probe states the question it answers.

| t | what happens |
|---|---|
| 0.00 s | RESET at `0xF826A9` — watchdog off, ports, timers, chip selects, RAM cleared, then into prom_b through the thunk table |
| 0.00 s | the 488 Hz timer tick at RAM `0x0080` starts counting |
| 0.013 s | the **battery-RAM checksum pair** at `0xF82C80` runs: `0x100` words summed from `0x007620` against `(0x007FD2)`, then from `0x617800` against `(0x007FD4)` |
| 5.01 s | the SC1 module opens the control-panel link, and the panel answers |
| 7.21 s | the SED1330 is initialised, from `0xF8E822` in `LCD_Init_SED1330` |
| 70.5 s | CPU 2 reaches MAIN and its key scanner goes live |
| 75 s | the panel carries drawn text and stops changing, while CPU 1 keeps running ordinary code across prom_a and prom_b — **a live system sitting on a screen, not a hang** |

⚠ **This walkthrough was measured on an older build, and two later fixes move
it.** The absolute times predate the timer corrections below: with the timers
right the same milestones arrive about **4× sooner** — the SED1330's first write
moves from t = 7.21 s to **t = 0.50 s**, and SWI7 text drawing from t = 72.24 s
to **t = 19.62 s**. And the screen the last row settles on was
`ALL INITIAL SETTING!` on that build; once control register `0x3C` existed, the
draw task runs and both variants go on to `SOUND MODE`.

**Both checksums FAIL, and that is the right answer.** The helper at `0xF82CD3`
returns carry *clear* on a match and its callers only `set` a verdict bit on that
path, so in `(0x007FD1)` a **set bit means PASS**; the measured value is `0x00`.
For a machine with no battery-backed contents, failing is correct.

> ★ **A teaching anecdote this project keeps on purpose.** An earlier revision of
> the probe notes reported *"0 LCD accesses, the boot never reaches the display"*
> and called a blank window the expected state. That came from a **six-second
> run** on a machine that takes ~90 emulated seconds to boot. It was a
> measurement artefact, corrected in place. **On this machine, a null result from
> a short run is not a null result.**

## Four defects in MAME's TLCS-900, found by this machine

All four are in `src/devices/cpu/tlcs900/`, and every one of them was found
because this firmware depends on it:

1. **The 8-bit prescaler taps were 16× too slow** — `m_timer_pre >> 15` instead
   of the databook's φT1 = 8/fc, φT4 = 32/fc, φT16 = 128/fc, φT256 = 2048/fc
   (Toshiba *TLCS-900 Series CMOS 16-bit Microcontrollers TMP95C061*,
   Table 3.8 (1) p. 81).
2. **The 16-bit timers 4–7 were never counted at all** — `m_t16_reg` was written
   by `treg45_w` / `treg67_w` and read by nothing, and nothing set `INTET54`. So
   `INTTR4`, *this machine's musical clock* (vector `0x50` → `0xF82EA2`), could
   not fire.
3. **Control register `0x3C`, INTNEST, did not exist** — the `p_CR16` decode sent
   it to `m_dummy`. This is what blocked the UI; see below.
4. **P6 was mapped with `port_w<PORT_7>`**, so every write to P6 was delivered to
   PORT_7.

Plus, in the overlay's `tmp95c061`, a **serial engine on channel 1** and **INT6 /
INT7 in `execute_set_input()`**, both of which upstream lacks entirely.

### What fixing the timers changed, measured

`notes/wsa1-probes/tlcs900_timer_control.sh` switches between the two builds:

| | reverted | fixed |
|---|---|---|
| INTT1 (the RAM `0x0080` tick) | 30.5 Hz | **488.3 Hz** (the firmware wants 488.28) |
| INTTR4 (vector `0x50`) | never fired | **192.0 Hz** |
| SED1330 first write | t = 7.21 s | **t = 0.50 s** |
| SWI7 text drawing | t = 72.24 s | **t = 19.62 s** |

Boot to a drawn screen is ~4× quicker in emulated time, and **the machine's
musical clock exists at all for the first time.**

### ★ Control register 0x3C is what stood between two screens

`IRQ_Epilogue` (prom_a `0xF857B7`) reads control register **`0x3C`** and enters
the kernel only if it reads exactly 1; `Kernel_Dispatch` (`0xF85715`) reads it
again and refuses to reschedule unless it is 0. MAME had no such register and
nothing incremented it on interrupt acceptance or decremented it on `RETI`. Both
CPUs' kernels use it — 10 accesses in prom_a, 9 in prom_c.

Implemented for real in the shared CPU core, and measured against a control build
with no register at all:

| | no register | implemented |
|---|---|---|
| pending-tick counter `(0xBE)` | wraps at 253 Hz, never drained | `00` |
| semaphore 1 | count `02`, wait queue **empty** | count `00`, queue **occupied** |
| task 2 | state `04`, never runs | state `03`, blocked |
| callback ring | rd `0000`, wr `0008` | rd = wr = `0008` |
| LCD writes | 33,623, frozen from t = 20 | **80,460** ⚠ |
| screen | `ALL INITIAL SETTING!` | **`SOUND MODE`** |

⚠ **The LCD-writes row does not discriminate and is kept only for completeness.**
A control build with INTNEST implemented *also* ends at 33,623 LCD writes, so
both explanations produce that number. The other five rows do discriminate.


<figure style="margin:1.5rem 0;text-align:center;"><img src="{{ "/assets/images/wsa1/wsa1r_intnest_before_all_initial_setting.png" | relative_url }}" alt="ALL INITIAL SETTING! — the screen before the INTNEST register existed" style="image-rendering:pixelated;width:320px;max-width:100%;border:1px solid #ccc;border-radius:3px;"><figcaption style="font-size:0.8rem;color:#777;">The null: with no INTNEST register the scheduler is never entered, the draw task never dequeues, and the machine sits here for ever.</figcaption></figure>

⚠ **The KN5000 is not affected, and that is a measurement rather than a symmetry
argument.** `tlcs900_intnest_evidence.py` scans every `ldc` in all four SX-WSA1R
images and in the KN5000's: the WSA1 uses cr `0x3C` and never `0x7C`, while the
KN5000 uses `0x7C` and **never reads it back** — it keeps the nesting depth in a
RAM word at `(1475)` and only *mirrors* it into the register. So the same RTOS,
adapted to two family members. *(The same scan shows the
[SX-KN1500]({{ site.baseurl }}/kn1500/)'s IC15 reading cr `0x3C` with the same
4-read / 5-write shape — an observation, not yet a claim about its kernel.)*

### The regression gate that had to pass

Those files are shared by every `tlcs900` driver in MAME, so the standing gate was
re-run on the built binary: **17 passed, 0 failed, 1 skipped**, every liveness
figure equal to its recorded 2026-08-14 value, and — the one that matters — the
**KN5000 demo-audio capture byte-identical to its pinned baseline**. That is 90
emulated seconds of the tone generator playing, i.e. tens of thousands of
interrupts and `RETI`s on the sibling TMP94C241, producing exactly the same WAV
as before.

## What is modelled

| device | how |
|---|---|
| both TMP95C061s | MAME's `tmp95c061`, at fc = 28 MHz |
| the 320 × 240 LCD | a real `sed1330_device` + screen. The geometry is the firmware's own SYSTEM SET, written identically three times (`30 07 00 27 35 EF 28 00`), and two unrelated pieces of code agree with it — the coordinate clamps are 319/239 and the pixel plotter forms `Y·AP + X/8` |
| the inter-processor link | byte port, strobe/busy handshake, micro-DMA channels 2 and 3 |
| the 61-key keybed scanner | `0x108000`, with a touch-time adjuster |
| the panel microcontroller | HLE'd on serial channel 1, in `wsa1_cpanel.cpp` |
| the touch-calibration EEPROM | a 93C46-class serial part |
| the floppy controller | a real `upd765a_device` with a 3.5″ drive and PC formats |
| the `0x7F0000` register file | modelled as the 4 × 32 file its driver shape says it is, **without a part name** |
| the service CHECKING DEVICE | a switch plus a `check_led` output |

**The control panel is wired, and it works in both directions.** CPU 1 clocks out
exactly the seven command frames the disassembly says the SC1 module sends first,
in ROM order; the panel answers each; and since the receive-ring phase bug was
found and fixed, pressing MENU DISK through the rack layout's own binding opens
the DISK menu and lights the DISK lamp. All 58 rack switches and 14 of its 18
lamps are bound. The full account — the schematic trace, the second witness in
the ROM, and the bug — is on the
[Control Panel]({{ site.baseurl }}/wsa1-panel/) page.

The SED1330's two runtime services differ in **layer count, not geometry**:
service `0x10` rebuilds the boot layout (three layers, `OV = 1`), service `0x0F`
sets up two layers and clears exactly `0x6580` bytes = `SAD2 + 240 × AP`. The
overlay's `sed1330_device` was changed to gate layer 3 on `OV`.

⚠ The SED1330's **clock is deliberately 0**: its oscillator is a part this scan
does not resolve, and the device only uses `clock()` to re-derive the frame rate.
Leaving it at 0 keeps the screen's nominal 60 Hz rather than deriving a refresh
rate from a crystal nobody has read.

### The floppy controller is a `upd765a_device`, and here is why

`Dev7A_StartDma` (prom_a `0xFE596A`) selects on **ten command bytes, and every one
is a legal uPD765 command carrying exactly the MT/MFM flags that command may
carry**: `0x4D` FORMAT|MFM, `0xC5`/`0xC9` WRITE / WRITE-DELETED|MT|MFM,
`0xC6`/`0xCC` READ / READ-DELETED|MT|MFM, `0x42` READ TRACK|MFM, `0x4A` READ
ID|MFM, `0xD1`/`0xD9`/`0xDD` SCAN EQ/LE/HE|MT|MFM. **Only 59 of the 256 byte
values are legal uPD765 commands**, so ten arbitrary bytes all landing legal has
probability ≈ 4.2 × 10⁻⁷. The post-reset drain at `0xFE6891` is the textbook
SENSE INTERRUPT STATUS. The parts list has a **uPD72070GF3BE**, which has no MAME
device of its own; the family does.

⚠ 10/10 on the opcodes, but **7/10 on the direction**: the three SCAN commands
need a CPU→FDC data phase and sit in the device→RAM group. Recorded, not
explained.

## ★ The fake that was deliberately not enabled

CPU 2's uPD6383GF microcode upload polls the DSP's READY line on **P9 bit 3**
(`0xF9A19F`: `ld C,(0x19) / and C,0x08`) at **eighteen sites**. MAME's unbound
port read returns 0, so every byte of the upload burns the poll's full `0x1F40`
iteration bound and sets the firmware's timeout flag. Measured: in a six-second
run, CPU 2's program counter is concentrated in `0xF9A347-0xF9A399`, inside
exactly that loop. **That is where its boot time goes.**

One line would make the handshake complete instantly:

```cpp
m_cpu2->port9_read().set_constant(0x08);
```

**It is not enabled, because it is a fake.** No schematic net has been read for
that pin, and the poll is bounded, so nothing hangs without it — it is only slow.
*Turning a measured stall into a fabricated ready signal would buy speed with a
claim about the hardware that nobody has checked.*

*(P5 bit 4 used to be on that same list and is not any more: it is the service
CHECKING DEVICE's switch, and the manual says so in as many words.)*

## The keybed scanner works; the link does not carry the note

These are two different claims and the driver states them separately.

* **The scanner works.** Press C4 after t = 71 s and prom_c reads `0x5C98` off
  `0x108000`, and `0x5C18` on release — touch `0x5C`, key 24, bit 7 for down —
  which is byte for byte what the driver queued.
* **The link does not carry it.** CPU 2 → CPU 1 sends exactly one packet per boot
  and then wedges on a handshake line CPU 1 never releases, so
  `KeyEvents_ToLink`'s channel-5 packet is dropped.

So no note reaches the tone generator — and nothing would make a sound if it did.

## Findings flow in both directions

This machine is the clearest case on the site of a disassembly and an emulator
feeding each other:

* **the disassembly predicted `cr 0x3C`**, and the emulator confirmed it was what
  blocked the UI;
* **the emulator found the consumer of prom_c's key-state bitmap** at
  `0x0000FFF0` — which the disassembly tree had looked for in prom_c and not
  found, because it is **on the other processor**.

`kn7000_mame/notes/WSA1-EMULATION-DISASM-GAPS.md` is the formal version of that
traffic: a ranked **request list** of about 95 entries from the emulator to the
disassembly, lettered A–Y plus MAME-side items, each naming a question, what the
driver does instead today, and where to start looking. Gaps B, C, E, F, L and Y
are closed; gap O is closed for the rack; gap G is half closed — the link wedge
it was blamed for turned out to be gap G's DSP-ready handshake, not the link
itself.

## What is still missing

| gap | state |
|---|---|
| **Sound of any kind** | nothing synthesises. The tone generator, the three DSPs, the modelling LSI and the wave ROMs are all absent or undumped |
| **The six wave mask ROMs** | `NO_DUMP`. The manual gives their capacity (16 Mbit each) but not their organisation, and the scan does not resolve which sits on which of the tone generator's address buses — so each gets its own region rather than being concatenated |
| **The AM29F400T flash** | not modelled; its data-poll and erase-verify loops are unbounded and will spin if reached |
| **MIDI** | MAME's `tmp95c061` has no serial engine on channel 0 at all, so there is nothing to connect a `midiin`/`midiout` to |
| **The panel MCU's mask ROM** | not dumped, and no ROM region is declared for it — the manual does not give its capacity, and guessing one would be worse than leaving it out |
| **`0x104000` and `0x10C000`** | shapes established, **roles not**. The labels deliberately read `Dev104_` and `Dev10C_` rather than anything that would imply a function |
| **The drive motor line** | the firmware **does** drive CPU 1's PA bit 3 — four writes, the only bit of PA it changes after RESET, and it *clears* the bit (`res 3,(0x1E)` at `0xFE18EF`) before a 307 ms spin-up delay. ⚠ An earlier note claimed the firmware never writes that pin and called it a hardware question; **that is retracted at the source**. The driver still declines to wire it to the drive's motor, because *what the pin does* is not claimed — a drive-motor or drive-select line is only the obvious reading. The consequence is stated rather than papered over: with no motor modelled, an attached image never becomes READY, and a read reports the firmware's own error `0x31`, drive not ready |

## Reproducing any of this

Every measurement on this page comes from a committed probe in
`kn7000_mame/notes/wsa1-probes/`, and the directory's README carries the run
recipe and two traps worth repeating:

* **MAME's Lua GC silently collects a tap or notifier not held in a global.**
  Every script there keeps its handles in `_G`.
* **Taps on these 16-bit spaces must start on a word boundary.** A tap on an odd
  single byte throws; cover the containing word and select the half with a mask.
