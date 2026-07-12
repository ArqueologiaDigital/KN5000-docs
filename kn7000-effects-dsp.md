---
layout: page
title: KN7000 Effects DSP (ADSP-21065L)
permalink: /kn7000-effects-dsp/
---

# KN7000 Effects DSP (ADSP-21065L)

The KN7000's reverb, chorus, multi-effects and equalizer all run on **IC306**,
an **Analog Devices ADSP-21065L** — a 32-bit floating-point "SHARC" DSP (part
marking `S21065LKS240`, run at 66 MHz), with two 16-Mbit SDRAMs (IC307/IC308) for
delay memory. It sits on the [sound board](/kn7000-sound-subsystem/) between the
tone generators and the main DAC.

The striking result of reverse-engineering it: **the DSP has no boot ROM, and
its programs are embedded in the main firmware.** So the entire effects engine —
kernel and every effect algorithm — was recovered from `kn7000_program.rom`
alone, with no physical chip and no undumped ROM. All 80 programs are
disassembled and documented in the project's disassembly repository; this page
explains how it works.

## Host boot: the CPU loads the DSP

Because the SHARC has no external boot memory, the MN10300 **host-boots** it: it
writes a register index to `0x98000000` and streams program/data words to
`0x9C000000`. The firmware sends a **pool of 80 download records** stored in the
program flash at CPU `0x486BCEC4..0x486CE68D` (≈ 71.6 KB). Each record is a run
of blocks:

```
block  = id 0x2004 | mode (PM=program / DM=data) | target address | length | payload
record = one or more blocks, ended by a zero terminator
```

Program-memory payload is packed as 48-bit SHARC instruction words (the DSP's
native width); data-memory payload as 40-bit words. A small tool walks the pool,
unpacks it, and disassembles every program with `unidasm -arch sharc`. The
unpacking is verified correct because it reproduces the ADSP-2106x **reset and
interrupt vector table** exactly (an `IDLE` at the reset vector, a jump to the
init handler, and RTI-filled interrupt slots).

## The runtime: a 10-slot effect engine (the kernel)

One record is the **resident kernel** — downloaded once at boot; every effect
program then loads *on top of it*. From its disassembly:

- **The reset handler** configures a single interrupt (IRQ0, the per-sample /
  per-frame tick), sets up the serial audio ports (SPORTs) and their DMA, points
  the delay-line circular buffers at the external SDRAM, clears that delay RAM,
  and enters the main loop.
- **The main loop** waits for the IRQ0 tick, then walks a fixed chain of effect
  **units**, each with its own program (loaded at program address `0x8400`), a
  block of working **state**, and a block of tunable **parameters**. Audio
  arrives and leaves over the SPORTs at 44.1 kHz.
- Until a real effect is downloaded into a slot, that slot runs the kernel's own
  7-instruction **passthrough** (read input, write it dry to the outputs).

So the DSP is a **ten-slot insert processor**. The firmware assigns fixed roles
to specific slots — a dedicated reverb unit, a chorus unit, an equalizer unit,
an enhancer unit, and several general "insert" slots — matching the instrument's
Reverb / Chorus / Multi / Sound-DSP / EQ effect structure.

## How the CPU chooses an effect

When you change an effect on a menu, the firmware calls a selector with a
**(unit, type)** pair: *which* of the ten slots, and *which* effect type
(0–0x91). It validates the pair against a per-unit **whitelist** — this is how we
know which slot is which:

| Unit | Role | Accepted effect types |
|---|---|---|
| 0 | Enhancer group | `0x00`, `0x09`, `0x10`–`0x1F` |
| 1–6 | Multi / Sound-DSP insert slots | large shared set |
| 7 | Chorus | `0x00`, `0x58`–`0x5B` |
| 8 | Equalizer (final 5-band bus) | `0x4F` only |
| 9 | Reverb | `0x00`, `0x01`, `0x02`, `0x04`, `0x40`, `0x52` |

An effect **type** is turned into a pool record through a **master table in ROM**
(146 pointers). Decoding that table gives the authoritative type → program map —
this part is *fact*, not inference. The order of programs in the pool is not the
type order; the table remaps it.

## The effect catalogue

Reading the SHARC opcodes identifies what each program computes. The building
blocks are the classic ones of digital audio effects:

- **Delay lines** — a circular buffer in SDRAM, written each sample and read at
  an offset; with feedback this is a **comb filter**, the core of reverb and
  echo.
- **Allpass sections** and **diffusion** — an *allpass* filter passes all
  frequencies at equal level but delays them, and a cascade of allpass sections
  is a **diffuser**: it progressively smears a single sharp echo into a dense,
  smooth tail. Diffusion is the classic reverb-construction technique (the
  Schroeder / Moorer reverberator designs of the 1960s–70s): comb filters set
  the decay time, and allpass diffusers fill in the echo density so the result
  sounds like a real room rather than a series of distinct repeats.
- **Biquads** — two-pole/two-zero filter sections, used for the equalizer and
  for tone shaping inside other effects.
- **LFOs** — a phase accumulator reading a waveform table, modulating a delay
  tap (**chorus / flanger / phaser**) or a gain (**tremolo / auto-pan**).
- **Waveshapers** — a nonlinear transfer function (here a cubic soft-clip with an
  auto-gain front end) for **overdrive / distortion**.
- **Envelope followers + gain** — for **compressors / limiters**.

The 72 effect programs sort into these algorithm classes. Records whose program
code is **byte-identical** are pure preset variants — the same algorithm with
different coefficient values — and this was verified by comparing the extracted
code directly. Examples:

| Group | Programs | Algorithm |
|---|---|---|
| Reverb unit | modulated reverbs + a plate/hall set | comb + allpass diffusion, some with an LFO for movement |
| Chorus unit | 4 distinct programs | allpass-diffusion "ensemble" chorus |
| Enhancer unit | 6 programs (3 distinct + presets) | allpass diffusion network |
| Equalizer | 1 program | cascaded biquad, 5-band |
| Multi / insert | distortion, delay, tremolo, phaser, compressor, pitch-shift, filter… | the full mix of the blocks above |

A per-program table — effect type, target unit/role, algorithm class, preset
family, and confidence — is maintained in the project notes alongside the
disassembly. The **algorithm** of each program is read with high confidence from
the code; the exact **preset names** as they appear on the panel (e.g. which
reverb is "Concert 1" vs "Dark 2") are partly inferred and are being finished by
tracing the menu descriptor tables.

## Two more record kinds

- **SDRAM self-tests (4 records).** Before loading the kernel, the CPU runs four
  short programs that march-test the DSP's external SDRAM — two bit patterns over
  two address regions — and report pass/fail through a host register. They
  contain no audio processing; they are the "DSP alive / DSP RAM OK" power-on
  check.
- **LFO waveform tables (3 records).** Three data-only records hold alternate
  **modulation shapes** — sine, triangle and square — that the CPU can push to
  the DSP to change a modulated effect's LFO on the fly without reloading its
  program.

## Cross-model note

The KN6000 and KN6500 use the **same** ADSP-21065L and carry a **byte-identical**
program pool to one another; compared with the KN7000, the kernel's data tables
match while the program code is a slightly older build. One DSP model and one
effect analysis therefore serve all three instruments — see the
[KN6000/KN6500 notes](/kn6000-hardware/). (The KN5000 is different: its effects
run on two fixed-function ASICs with undumped internal ROM, so its effect
algorithms are *not* recoverable the way the KN7000's are.)

## Why this matters for emulation

Unlike the tone-generator side — which is blocked by the
[undumped wave ROMs](/kn7000-sound-subsystem/) — the effects DSP is **fully
recoverable from data we already have**. Both the DSP core and its programs
exist, and the integration path is now completely mapped out:

- **The DSP core is already in MAME.** MAME emulates the ADSP-2106x SHARC family
  (the `ADSP21062`/`ADSP21060` devices) — the same instruction set the 21065L
  uses — with a mature interpreter, a recompiler and a disassembler proven in
  shipping arcade drivers. No instruction-level work is needed.
- **The programs are recovered** — all 80 records, kernel and effects, extracted
  and disassembled from the firmware (above).
- **The 21065L's memory personality has been reverse-engineered from the program
  itself.** The public summary datasheet doesn't give the internal-memory or I/O
  register map, so it was *derived from what the program actually uses*: its code
  lives at program address `0x8000`–`0x8Dxx`, its data at `0x9800`–`0x9Cxx` and
  `0xC000`–`0xC3xx`, its delay buffers in external SDRAM from `0x80000`, and it
  touches a specific, now-enumerated set of on-chip I/O registers (serial-port,
  SDRAM-controller and DMA control blocks). That is exactly what a MAME
  `adsp21065l` device variant needs.

What remains is genuine but well-scoped device work: add that 21065L variant to
MAME's SHARC core, wire the host-boot upload (the `0x98000000`/`0x9C000000` port)
so the firmware loads the DSP as it does on hardware, and — the one piece with no
MAME precedent — model the serial-audio ports so sound flows tone-generators →
DSP → DAC. The first milestone is simply proving the recovered programs *run* on
MAME's SHARC core, which would independently validate the whole disassembly. It is
the most complete part of the KN7000 sound story, and the best-understood path
forward.

## 2026-07 update: it works — the emulated DSP now plays real effects

Everything above became a working emulation in July 2026: the MAME driver
host-boots the recovered kernel, uploads the firmware's effect chain, and a
piano note with reverb ON is clean audio with a naturally decaying tail. The
route there uncovered hardware truths that were not visible from the static
program alone; they are recorded here because they *are* the KN7000's design.

### The runtime topology: a TDM patchbay into the tone generator

The DSP's serial outputs feed **no DAC**. All four SPORT transmit pins loop
back into the tone generator (`DT0A/DT0B/DT1A/DT1B → TG SDIE0-3`), and the DSP's
TX stream is a time-multiplexed **per-unit patchbay**: each of the kernel's 10
effect units owns a stereo *return* pair in the frame, and reads its *input*
from the matching slot 0x20 above it:

| unit | program | return (L/R) | input |
|---|---|---|---|
| 0 (panel REVERB) | selected type | `0xC342/43` | `0xC362/63` |
| 1..5 | per-part inserts | `0xC344/45` .. `0xC34C/4D` | +0x20 each |
| 6 | chorus-class insert | `0xC358/59` | `0xC378/79` |
| 7 (CHORUS) | rec58-family | `0xC350/51` | +0x20 |
| 8 (EQ) | rec34 | `0xC352/53` | +0x20 |
| 9 | rec49-family | `0xC356/57` | +0x20 |

The **tone generator** performs the final mix: its output-bus registers
(group 0x20) crossfade each DAC channel between the TG's direct sound and the
DSP *returns* — the panel REVERB button toggles exactly that crossfade
(`0x803A = 007F/7F00`), and REVERB TOTAL DEPTH is the return level
(`0x8338 = 0x8500|depth`). The DSP send enters at unit 0's input slots.

### Hardware truths required for a faithful emulation

- **MODE1 ALUSAT is load-bearing.** The kernel's only mode write
  (`BIT SET MODE1 0x3000`) enables integer *saturation*; the effects' triangle
  LFOs are saturate-then-reflect generators. An emulator that wraps integer
  adds turns every such LFO into a permanent ±2³¹ two-sample oscillation — the
  signature is an input-independent, never-decaying full-scale wash.
- **SPORT data is sign-extended** (`DTYPE=01`, right-justified): 24-bit samples
  must be delivered sign-extended into 32-bit words. Zero-padding turns every
  negative sample into ≈ +2× full scale (a rectified pedestal that rails every
  unit's output limiter).
- **The host interface is the stock ADSP-2106x IOP-register protocol** — the
  "index" written to `0x98000000` is literally the SHARC IOP register address
  (IIEP0/IMEP0/CEP0/DMAC-EP0/EPB0...). All runtime parameter and level traffic
  travels as ordinary framed DM/PM uploads; there are no hidden level registers.
- **The DSP runs at 66 MHz** and completes exactly 44,100 effect frames per
  second; per-frame the kernel walks the unit CALL chain (slots at PM
  `0x8080-0x80A0`, patched to relocated programs at `0x8400 + unit×0x100`).

### Fix catalogue contributed to MAME's SHARC core

Emulating this machine surfaced core bugs relevant to every SHARC system:
missing ALUSAT in the recompiler's entire fixed-point ALU family (add/sub,
carry forms, negate, inc/dec, dual add/sub — the interpreter had it), a
circular-buffer wrap off-by-one (`> B+L` vs `≥ B+L`), pre-modify addressing
never applying circular wrap, fixed-point AVG truncating where the TRM
specifies round-to-nearest, unrounded SSFR multiplier forms, and FIX-overflow
undefined behavior. A **performance** gap too: the recompiler translated *no*
fixed-point multiplier at all — the entire single-function multiply / MAC family
fell back to the interpreter. Measuring the fallback path showed the KN7000
effects kernel hits it ~66 million times per second of audio; giving those a
native code path (verified bit-identical) removes 96 % of all interpreter
fallbacks during a reverb. The 21065L personality (vector base, host boot, memory
map, IOP set) lives in the project's SHARC fork pending upstreaming.

### Emulation status: which effects are audible (2026-07)

The MAME bridge carries tone-generator audio through the DSP. The boot-default
**reverb executes on unit 0** and is fully audible and faithful (clean, decaying,
robust under dense input). **Chorus is also audible** (July 2026): it runs on
unit 4 (a non-flag-gated modulated-delay program), and the bridge now feeds that
unit its send (the low byte of sub-TG reg `0x8198`, tracking the on-screen CHORUS
DEPTH) and sums its return as an independent wet — verified as a real chorus
(LFO comb modulation, not a doubled note), with the reverb output kept
bit-identical when chorus is off.

**SOUND DSP** (unit 9, rec49) and **MULTI** (unit 1, rec15) are also audible
(July 2026): each is fed from its send register (SOUND DSP `0x8098`, MULTI
`0x8298` — both low bytes track the on-screen DEPTH) and summed as its own
independent wet. MULTI's unit was pinned by diffing the coefficient blocks
between two of its *types* (a delay vs a distortion) so the shared effect-bus
refresh cancels — unit 1 rewrote 43 words while the rest moved 1–2. **Four
effects are now audible** (reverb, chorus, SOUND DSP, MULTI), verified coexisting
with no clipping. The remaining **EQ** (unit 8) is a master/insert (a different
integration) and is a follow-up. All ten effect
programs are loaded and run every frame; the silent ones were simply never fed
(the bridge historically filled only unit 0's input slot). A special case: four
of the seventy-two effect programs (a pitch-shifter + three specialty reverbs)
gate on the SHARC **FLAG3** input pin, which is part of the DSP's double-buffered
frame handshake; those need the faithful frame model, not just an input feed.

**Divergence sweep (July 2026): every effect type validated.** The reverb-rail
bug was root-caused to the recompiler missing the SHARC's fixed-point saturation
mode (a triangle LFO wrapped instead of clipping, and the feedback loop turned
that into a permanent full-scale buzz). To prove the fix held for *all* ~200
effect programs — not just the reverb — a harness walked every effect type on all
four screens (**241 selections**), reprogrammed each unit, played a note, and
watched two independent alarms: a 60 Hz sampler on the DSP's own output slots
(rail = 94 % of full scale, catches self-excitation even over silence) and a DAC
clip check (catches anything audible, by a separate path). Result: **zero rails,
zero clips**; the loudest was the Concert reverb at ≈12 % of full scale, over 8×
below the rail. The load-bearing cases are the LFO-driven flanger, phaser and
rotary programs — built on the same clip-and-fold arithmetic that sank the reverb
— which all pass at ≈5 %. The fix generalizes to the whole class. (Scope: the
non-reverb units mostly ran over near-silence during selection, so this proves no
program *self-excites* to the rail — the input-independent failure that actually
occurred; heavy per-effect drive is a separate follow-up.)

On real hardware the TG routes each part to multiple effect units through its
per-channel output-bus / effect-send matrix (sub-TG register group `0x20`, 64
channels × `0x10`) and sums all four returns into the DAC. Each effect has both a
**send** (reg 8, how much signal enters the effect) and its own **return** (reg
0xA low byte, how much of the effect's output reaches the DAC).

**Per-effect returns (July 2026).** A live per-effect toggle capture pinned each
effect's own return register — REVERB = ch03 (`0x803A`), SOUND DSP = ch09
(`0x809A`), MULTI = ch06 (`0x806A`) — and proved the returns are **independent**:
pressing REVERB moves only ch03's return and leaves the others untouched. (CHORUS
is the exception: toggling it moves only its send `0x8198`; it has no separate
return register, so its wet is send-driven.) The emulation now scales each
effect's wet by its own return, so **turning reverb off no longer mutes chorus,
sound-DSP or multi** — they were previously (incorrectly) scaled by the reverb
return. Verified: the reverb-only output is bit-identical before/after, and with
reverb off the sound-DSP unit's output now reaches the DAC through ch09's return.
