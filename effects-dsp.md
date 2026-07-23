---
layout: page
title: Effects DSP (NEC uPD6383GF)
permalink: /effects-dsp/
---

# Effects DSP — NEC uPD6383GF (IC311)

The KN5000's primary effects processor is **IC311**, an **NEC uPD6383GF-3BA** — a
24-bit fixed-point audio DSP with an external delay-DRAM controller. It runs the
reverbs, choruses, delays, EQ and dynamics effects; a second, less-understood chip
(IC310, an MN19413) handles additional effect units.

This page is the reference distillation of the reverse-engineering of that chip. The
narrative — how each result was found — is in the MAME development blog (Parts 78–84);
the conclusions are stated here. Confidence is labelled throughout as **PROVEN /
MEASURED**, **INFERRED**, or **OPEN**, matching the underlying research notes. Where a
claim needs real hardware to settle, it says so plainly.

> **Status.** The host upload path, word format, coefficient format, sample rate,
> memory map, control-flow model and several instruction roles are established, and two
> whole algorithms (the parametric EQ and the reverb diffuser) are decoded to the bit.
> The instruction set as a whole is **not** fully decoded — honest coverage is ~18 % of
> the microcode words. The DSP core is **not** emulated in MAME: the device captures the
> host byte stream, there is no execution and no audio yet.

This page supersedes, in part, the older
[DSP Bytecode Interpreter]({{ site.baseurl }}/dsp-bytecode-interpreter/) page, which was
written before the chip was identified and refers to it by the wrong part number. That
page remains correct about the **Sub CPU-side** bytecode interpreter (the mechanism that
*uploads* configurations); everything it says about the DSP chip's own architecture is
refined here. See also the [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) for how
the Sub CPU reaches the DSP in the first place.

---

## 1. The chip

**NEC uPD6383GF-3BA**, 100-pin QFP, Panasonic service-parts code GGC1163.

For years this part was recorded in the project's notes as *"DS3613GF-3BA, a custom ASIC
with no public documentation."* That was a **transcription error** — the marking is
`uPD6383GF-3BA`. The correct identification came from the **Pioneer CDJ-500 / CDJ-500G
service manual** (order RRV1087), which documents the very same part as **IC302** and
includes a block diagram and a 100-pin description. It is the only substantial public
document for the chip.

No datasheet, databook page or programming manual for the uPD6383 exists on the public
web (**verified** exhaustively: it is absent from every NEC databook and from NEC's own
October 1996 selection guide, and even distinctive strings from its CDJ pin table return
zero hits worldwide). It was a set-maker ASSP, sold direct and never catalogued. Its
documented sibling, the **uPD6380** (used in NEC's own PC-98GS / PC-9801-73 sound board),
was likewise never published and never reverse-engineered. **The instruction set has had
to be inferred from the microcode itself.**

### Architecture (from the CDJ-500 block diagram — PROVEN for the block level)

| Block | Detail |
|---|---|
| Instruction RAM (I-RAM) | **384 words × 36 bits**, uploaded by the host; both effect units resident at once |
| Coefficient / data RAM | Two **256 × 24-bit** internal spaces (C-RAM and D-RAM) plus a bank register |
| Multiplier | **24 × 24** fixed-point |
| ALU | **44-bit**, with two accumulators (**ACCA / ACCB**) and two shifters |
| Delay memory | On-chip controller for **external DRAM**; ring-buffer address generation (echo / reverb-A / reverb-B regions) |
| Audio I/O | Serial audio in/out (DI / DO), three ports; this board uses one stereo pair |

### Board facts (verified on the KN5000 by Felipe)

* **25 MHz** master clock on IC311.
* Delay DRAM = **M5M44260AJ** (IC309), the external reverb/delay memory.
* **Sample rate = 44,100 Hz** — **PROVEN three independent ways**:
  1. the firmware's own millisecond→samples conversion `ms × 0xAC44 / 0x3E8`;
  2. a ROM `double` constant equal to `pi / 44100` (`0x012F57`), used by the biquad
     designer;
  3. the LFO rate constants — nine effect defaults decode to round numbers of Hz
     (0.2, 0.4, 0.6, 1.2, 3.0, 4.0, 5.2, 7.4, 1000 Hz) only under 44,100 Hz, and miss a
     0.1 Hz grid by up to 8.7 % at 48,000 Hz.

---

## 2. How programs reach the chip

The Sub CPU (TMP94C241F) is the host. It reaches the DSP through a **parallel
microcontroller interface** — port **PZ** carries an 8-bit data byte, and port 7 supplies
the strobes: command/data select (C/D), write (`/WR`), read (`/RD`) and chip select
(`/CS`). Status bits (ready, read-busy, I-RAM-modify, GF, OVF) are polled back. This is
the physical layer documented on the
[Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) page.

Above that sits the Sub CPU's **bytecode interpreter**
([its own page]({{ site.baseurl }}/dsp-bytecode-interpreter/)): compact ROM-resident
programs that expand into the sequences of register writes which upload a microprogram
and stream its coefficients. A **36-bit instruction word is packed into 5 bytes**
(right-aligned big-endian; bits 36–39 are always zero). A **coefficient is 3 bytes**,
signed **Q0.23** for static program constants (the value `0x517CC1 = 2/π` recurs 53
times). Parameter-path biquad coefficients are written per-word as Q1.22 or Q0.23 instead.

There are **~40 distinct microprograms serving ~100 effects** — "one algorithm, many
coefficient banks." The Sub CPU holds a 100-slot algorithm-pointer table and a matching
parameter-pointer table (see the [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/)
tables at `0x1ED7C` / `0x1EF0C`).

---

## 3. The instruction word

Each 36-bit word divides into four fields (**MEASURED**):

```
   hi12[35:24] . class4[23:20] . addr8[19:12] . lo12[11:0]
```

* **`hi12` is not an opcode — it is a horizontal microword of independent enable bits**
  (**MEASURED**: values one bit apart recur far more than an enumerated field would
  allow, `z = +7.9`). Three of its twelve bits have assigned meanings:
  * **bit 4 = write the accumulator to `mem[ptr]`** (a store);
  * **bit 10 = end of block** (with bit 11 clear); the terminating instruction still does
    its datapath work — it is a modifier, not a halt code;
  * **bit 11 = format escape** (selects a second word format used by host-poke and
    DRAM-bracket words).
  Bits [9:8] and [3:1] are proven to be *fields* but their meaning is **OPEN**; the rest
  are unassigned.
* **`class4` = a cursor-fetch enable (bit 23) plus a 3-bit `MODE = class4 & 7`.** Bit 23
  was **corrected**: it is *not* a multiply-enable (eighteen phaser all-pass sections
  multiply with no class-A word), but a **cursor-fetch** enable — a class-A word pulls the
  next coefficient from the implicit cursor.
* **`addr8`** is, in the addressing modes (`class4 & 7 == 2`), a **signed post-increment**
  applied to an 8-bit data pointer that **wraps mod 256** (INFERRED, with a measured
  floor). In other modes it is frozen to a constant or is a table selector.
* **`lo12`** carries operand routing and some ALU-step identity (e.g. `0x647`/`0x687` =
  latch-store steps, `0x44C` = apply modulation offset).

Two implicit cursors run alongside the word stream: the **coefficient cursor** (+1 per
class-A word, reset by `801.0.00.021`) and the **data pointer** just described.

**What is OPEN.** The **absolute origin** of the data pointer cannot be pinned from the
ROM — the per-unit base is reset by the header to a value the instruction stream never
names (unit 0 = `0x70`, unit 1 = `0x50`, loaded via register `0x821`), and every static
falsifier is a *difference*, hence origin-free. The **audio-input** instruction, the
meaning of most individual arithmetic words, and the `COND`/`BRAKST` control fields named
in the CDJ pin table are all unidentified. **Honest coverage is ~18 %** (545 of 2974
microcode words) — the structural results are worth far more than that number, but the
number is reported straight.

### Control flow (PROVEN BY CONSTRUCTION)

The program is **restarted by the sample clock** — there is no software frame loop. Per
sample, the PC is reset to 0; a 60-word **common header** runs the input stage, LFOs and
mixes, then **calls unit 0's body and, on return, unit 1's body**, using a shared
call/return encoding (`class4==1 && addr8 ∈ {0x0E, 0x0F}`, the unit tag) on a two-level
stack; a 23-word epilogue does the output/effect-return stage and waits for the next
sample edge. The effect **bodies are straight-line and hand-unrolled** — there is no loop
in a body, which is why an exhaustive search for a branch instruction found none. The
per-frame instruction budget (~286–326 slots) fits comfortably inside the 25 MHz clock at
44.1 kHz.

---

## 4. The algorithms solved to the bit

### Parametric EQ — a bilinear-transform biquad (PROVEN BY CONSTRUCTION)

The `PARAMETRIC EQ` effect (5 bands × 2 channels) is fully decoded. Each band is a
second-order section whose coefficients are computed at run time — not tabulated — by a
software floating-point **biquad designer** in the Sub CPU (`LABEL_03A933`, reached by
parameter opcode `0x70`). It:

* reads the three user values as **frequency in Hz** (ISO ⅓-octave table, 40 Hz…16 kHz),
  **Q** (0.1…20), and **gain in dB** (−12…+12 in 0.5 dB steps);
* computes `K = tan(pi·f0 / 44100)` in IEEE double, then the classic
  `a0 = 1 + K/Q + K²`, `a1 = 2(K²−1)`, `a2 = 1 − K/Q + K²`;
* emits **five** coefficients — `b1, b0, b2, −a1/a0, −a2/a0` — the recursive pair stored
  **negated** so the DSP runs a pure multiply-accumulate. (A "sixth coefficient" in an
  earlier note was **falsified**: it is padding.)
* implements *cut* by reciprocating the whole section, not by inverting the poles.

The DSP-side realisation is **Direct Form I** with four state cells `{x₁, x₂, v₁, v₂}`,
recovered by an exhaustive constraint search (19,674,720 candidate assignments → one
dataflow). Two of the four state writes are folded into multiply instructions, which is
why the topology "refused every textbook form" for so long. Running the recovered
semantics as an interpreter against the transfer function computed from the same ROM
words gives **`max|err| = 0.000e+00`** (bit-identical) on nine real coefficient blocks,
and the full 42,336-preset design grid is **0 unstable**, with f0/Q/gain recovered to
~1e-10.

### Reverb — pre-delay into all-pass diffuser ladders (MEASURED counts / INFERRED dataflow)

The reverb (the corpus's only unit-1 program) is a pre-delay feeding **nine first-order
all-pass diffusers arranged in two descending-gain ladders** (five + four; gains read
live from `CONCERT REVERB 1` as `0x98…0x9C | 0xA1…0xA4`), plus damping filters and
recirculation. The 8-word all-pass motif matches the **only** first-order all-pass
realisable with a single multiply, on instruction *count and position*, not by fitting.
With the ROM's own gains and delay lengths every stage is a **true all-pass** to nine
digits (impulse energy 1.000000000) and the nine-stage cascade is a dense, colourless
diffuser (28 taps/ms). Its decay comes from the damping filters and recirculation
*outside* the motif — the diffuser alone is loss-less by construction, so "does it decay
like a reverb" is **not** answered by the diffuser and is flagged as such.

---

## 5. The complete effect + parameter catalogue

This is the newest and most complete result: **50 distinct effect algorithms**, each with
its ordered, named, unit-tagged parameter list — **read live from Sub CPU RAM** while the
edit page was on screen in MAME, and **pixel-verified against the LCD**. The binding
mechanism (a per-effect array of name indices at RAM `0x29AC` into an 85-name table in the
main-CPU program) is confirmed end-to-end.

Two universal tails recur: every DSP-effect list ends with **VOLUME** then **REV SEND**
(the send to the reverb bus); the standalone reverbs drop REV SEND (a reverb *is* the
bus). Parameter names bind to the actual DSP writes — **HIGH DAMP GAIN** appears only on
reverbs and delays, **THRESHOLD / RATIO** only on the compressor, **LFO SPEED / LFO
WAVEFORM** only on LFO effects, and the EQ's five **BAND EMPHASIS FC/Q/G** triples are
exactly the solved biquad's five bands.

### DSP EFFECT page (38 effects, in TYPE-selector order)

| # | Effect | Parameters (in order) |
|---|--------|-----------------------|
| 0 | CHORUS | DEPTH, LFO SPEED, LFO WAVEFORM, VOLUME, REV SEND |
| 1 | MODULATED CHORUS | DEPTH, SLOW LFO SPEED, FAST LFO SPEED, FAST LFO BALANCE, LFO WAVEFORM, VOLUME, REV SEND |
| 2 | ENHANCER | MANUAL, LOW MIX, HIGH MIX, DELAY L, DELAY R, VOLUME, REV SEND |
| 3 | FLANGER | DEPTH, LFO SPEED, RESONANCE, MANUAL, PHASE, LFO WAVEFORM, VOLUME, REV SEND |
| 4 | PHASER | DEPTH, LFO SPEED, RESONANCE, MANUAL, PHASE, LFO WAVEFORM, VOLUME, REV SEND |
| 5 | ENSEMBLE | DEPTH, LFO SPEED, LFO WAVEFORM, VOLUME, REV SEND |
| 6 | GATED REVERB | GATE TIME, HIGH DAMP GAIN, THRESHOLD, MASK TIME, VOLUME, REV SEND |
| 7 | SINGLE DELAY | DELAY L, DELAY R, FEEDBACK L, FEEDBACK R, HIGH DAMP GAIN, VOLUME, REV SEND |
| 8 | MULTI TAP DELAY | DELAY 1–4, PAN 1–4, FEEDBACK, HIGH DAMP GAIN, VOLUME, REV SEND |
| 9 | DISTORTION | DRIVE, ADJUST, VOLUME, REV SEND |
| 10 | OVERDRIVE | DRIVE, ADJUST, VOLUME, REV SEND |
| 11 | FUZZ | DRIVE, ADJUST, VOLUME, REV SEND |
| 12 | EXCITER | DRIVE, ADJUST, HIGH EMPHASIS FC, EMPHASIS GAIN, VOLUME, REV SEND |
| 13 | COMPRESSOR | THRESHOLD, RATIO, ATTACK SENS., RELEASE SENS., VOLUME, REV SEND |
| 14 | SLOW ATTACKER | THRESHOLD, ATTACK RATE, RELEASE RATE, VOLUME, REV SEND |
| 15 | PARAMETRIC EQ | (BAND EMPHASIS FC / Q / G) × 5 bands, VOLUME, REV SEND |
| 16 | AUTO PAN | DEPTH, LFO SPEED, PHASE, LFO WAVEFORM, VOLUME, REV SEND |
| 17 | VIBRATO | DEPTH, LFO SPEED, PHASE, LFO WAVEFORM, VOLUME, REV SEND |
| 18 | AUTO WAH | RESONANCE, MANUAL, SWEEP RANGE, VOLUME, REV SEND |
| 19 | ROTARY SPEAKER | DRIVE, VOLUME ADJUST, TREBLE DEPTH, TREBLE FAST, TREBLE SLOW, TREBLE WIND UP/DOWN, BASS DEPTH, BASS FAST, BASS SLOW, BASS WIND UP/DOWN, VOLUME, SLOW/FAST, REV SEND |
| 20 | ROCK ROTARY | (identical to ROTARY SPEAKER) |
| 21 | RING MODULATOR | OSC SPEED, PHASE, LFO WAVEFORM, VOLUME, REV SEND |
| 22 | MIX UP | DEPTH, SLOW LFO SPEED, FAST LFO SPEED L, FAST LFO SPEED R, PHASE, LFO WAVEFORM, VOLUME, REV SEND |
| 23 | S. DELAY + CHORUS | DELAY DRY/WET, DELAY L/R, FEEDBACK L/R, CHORUS DRY/WET, DEPTH, LFO SPEED, LFO WAVEFORM, VOLUME, REV SEND |
| 24 | S. DELAY + S. DELAY | (two single-delay blocks) VOLUME, REV SEND |
| 25 | S. DELAY + FLANGER | delay block + FLANGER block, VOLUME, REV SEND |
| 26 | S. DELAY + VIBRATO | delay block + VIBRATO block, VOLUME, REV SEND |
| 27 | S. DELAY + PHASER | delay block + PHASER block, VOLUME, REV SEND |
| 28 | AUTO WAH + S. DELAY | RESONANCE, MANUAL, SWEEP RANGE, delay block, VOLUME, REV SEND |
| 29 | PEQ + CHORUS | BAND EMPHASIS FC/Q/G, CHORUS DRY/WET, DEPTH, LFO SPEED, LFO WAVEFORM, VOLUME, REV SEND |
| 30 | PEQ + S. DELAY | BAND EMPHASIS FC/Q/G, delay block, VOLUME, REV SEND |
| 31 | PEQ + FLANGER | BAND EMPHASIS FC/Q/G, FLANGER block, VOLUME, REV SEND |
| 32 | PEQ + VIBRATO | BAND EMPHASIS FC/Q/G, VIBRATO block, VOLUME, REV SEND |
| 33 | PEQ + COMPRESSOR | BAND EMPHASIS FC/Q/G, THRESHOLD, RATIO, ATTACK/RELEASE SENS., VOLUME, REV SEND |
| 34 | PEQ + COMPR + DIST | PEQ + compressor + DRIVE/ADJUST, VOLUME, REV SEND |
| 35 | PEQ + COMPR + OVERDR | (identical to PEQ + COMPR + DIST) |
| 36 | PEQ + DIST + DELAY | PEQ + DRIVE/ADJUST + delay block, VOLUME, REV SEND |
| 37 | PEQ + OVERDR + DELAY | (identical to PEQ + DIST + DELAY) |

`S. DELAY` = SINGLE DELAY; `PEQ` = PARAMETRIC EQ; a "delay block" = DELAY DRY/WET, DELAY
L/R, FEEDBACK L/R. Effects sharing an identical parameter list (FLANGER ≡ PHASER in UI,
DISTORTION ≡ OVERDRIVE ≡ FUZZ, ROTARY ≡ ROCK ROTARY) differ only in DSP coefficients, not
in the exposed parameter set.

### DIGITAL REVERB page (12 reverbs + 2 delays)

All twelve standalone reverbs share **one** parameter list:

| Effect(s) | Parameters |
|---|---|
| ROOM 1/2, PLATE 1/2, CONCERT 1/2, DARK 1/2, BRIGHT 1/2, WAVE 1/2 | REVERB TIME, PRE DELAY, HIGH DAMP GAIN, ER. LEVEL, VOLUME |
| SINGLE DELAY (reverb page) | DELAY L, DELAY R, FEEDBACK L, FEEDBACK R, HIGH DAMP GAIN, VOLUME |
| MULTI TAP DELAY (reverb page) | DELAY 1–4, PAN 1–4, FEEDBACK, HIGH DAMP GAIN, VOLUME |

The **EQUALIZER** (master 4-band) and **ACOUSTIC ILLUSION** pages use fixed hard-coded
layouts rather than this array and are outside the 50-effect catalogue.

---

## 6. What still needs real hardware

The reverse engineering is entirely **static** — nothing above was executed on the chip or
in an emulator. Four things need a running core (a real uPD6383 or a MAME core, once one
exists) and are honestly OPEN:

1. **The absolute pointer origin** — a single address-bus read on the first data access
   after the header would convert every `addr8` in the corpus into a real address.
2. **The audio-input instruction** — the input stage is *located* (header blocks 0–1) but
   no word is decoded.
3. **Direct confirmation of the mod-256 pointer wrap** (INFERRED from a measured floor).
4. **Validation of the whole chain against a real impulse response** — the biquad and
   diffuser are proven against the firmware's own arithmetic, which is strong but is not
   the same as measuring the physical chip.

A datasheet would retire most of the remaining inference in one stroke; none has been
found, and the search is documented as exhausted.

---

## Related pages

- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) — the Sub CPU audio firmware and
  the parallel host interface that reaches this chip.
- [DSP Bytecode Interpreter]({{ site.baseurl }}/dsp-bytecode-interpreter/) — the Sub
  CPU-side interpreter that uploads microprograms and streams coefficients (partly
  superseded here regarding the DSP chip itself).
- [Tone Generator]({{ site.baseurl }}/tone-generator/) — IC303, the wavetable voice engine
  upstream of the effects.
