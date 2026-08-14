---
layout: page
title: Project Roadmap
permalink: /roadmap/
---

# Roadmap — cataloguing and emulating every Technics keyboard

*Assessment date: 2026-08-14. This page supersedes the forward-looking half of the
[KN7000 Roadmap]({{ site.baseurl }}/kn7000-roadmap/) and the
[KN6000 Roadmap]({{ site.baseurl }}/kn6000-roadmap/), which remain as per-model status pages.*

The goal is a museum catalogue: every Technics keyboard documented at IC level, its ROMs preserved
with honest provenance, and — where the silicon allows — a MAME driver that a stranger can run.
Units arrive one at a time, by purchase, so the plan is built around **what can be done at a desk**
with what is already on disk, and a separate lane that waits for hardware.

**Planning constraint:** no hardware bench time is available in the near term. The KN7000 is owned
but not reachable; KN5000 access is uncertain and may not return for a long time. Everything ranked
below Phase 5 assumes zero physical access.

---

## 1. What "done" means

The project has never defined this, which is why "working" has meant different things on different
pages. Four grades, applied per **model × subsystem**:

| grade | criterion |
|---|---|
| **G0 — structural** | Every register and bit the firmware writes is decoded, or explicitly listed as undecoded. A committed script asserts it, with its expected output recorded. |
| **G1 — behavioural** | The firmware cannot tell. It passes **its own factory service diagnostics inside the emulator**, showing the same values a real unit shows. |
| **G2 — signal** | A committed golden capture with a criterion that *can fail*: a positive control that must differ, a null that must not, and a stated tolerance (pitch ±5 cents, envelope times ±10 %). |
| **G3 — provenance** | No `BAD_DUMP`, synthetic, or donor content anywhere in the path being claimed. |

A model is **done** when every subsystem is G2 and G3.

Two consequences worth stating plainly, because they are unwelcome:

- **G2/G3 for every model is not reachable on any horizon we can plan.** Roughly 30 undumped ROM
  entries span 22 distinct devices, and the KN5000's own waveform trio is among them. The
  *reachable* programme goal is **every model at G1, with an honest provenance register** saying
  exactly what is missing.
- **"Perfect KN5000 audio" is structurally blocked.** IC304/305/306 hold about 75 % of what the
  instrument's sounds select; they are not dumps at all but placeholder copies of IC307, and unlike
  the KN7000 there is no CPU-side wave readback port. Ranking KN5000 audio work by "how good will
  it sound" ranks against a ceiling that cannot be reached. The 155 instruments that use **only**
  the genuine IC307 are therefore the declared test corpus.

G1 is the grade this project should chase hardest, and it is nearly free: **every one of these
instruments ships a factory diagnostic suite** — ROM checksum, RAM, DSP, device, disk, panel/LED,
crosstalk, sample play, video out, wave ROM. Roughly seventeen self-tests per machine, with the
manufacturer's own pass criteria, and they run *inside* the emulator against the emulated devices.
Today two of them are ever used. A driver that passes its own factory diagnostics is a far stronger
claim than any bespoke rig.

---

## 2. The catalogue

Effort is **per generation**, not per model: once one member of a silicon generation runs, its
siblings are mostly ROM work.

| gen | years | CPU | members | status |
|---|---|---|---|---|
| **G0** | 1963–83 | none / analogue | SX-601, Technitone organs, SX-U series | out of scope (document only) |
| **G1** | 1982–84 | unknown | SX-K100/K200/K150/K250 | research; analogue solo path makes it poor value |
| **G2** | 1985–86 | **unknown — the one blocker** | SX-K300/K350/K450 | ★ best *new-silicon* target: OKI MSM5232 TG is **already in MAME**; needs one new MSM6202 drum device |
| **G3** | 1987–88 | unknown | SX-K500/K700 | first full-PCM Technics; one manual covers both |
| **G4** | c.1989–95 | **NEC V25 (µPD70325)** | **KN1200 confirmed**; KN2000, KN800/600, KN1000/750, KN901, KN3000? | ★★ **an unexplored third of the line.** V25 core is upstream in MAME already |
| **G5** | 1996–98 | **Toshiba TLCS-900** | KN1500, **KN5000**, **SX-WSA1** | in progress; deepest work |
| **G6** | 1998–2003 | **Matsushita MN10300/AM33** + MILK | KN2400/2600/PR54, KN6000/6500, KN7000/PR804/PR604 | in progress; 6 of 7 drivers |
| **G-ORG** | 1988–95 | unknown | GX/GN/FN3/EN/GA/EA console organs | ★ proven kinship, zero silicon data |
| **G-PIANO** | — | CPU+ROM | SX-PX, SX-PC series | out of scope for drivers; ROM archival only |

Seven MAME drivers exist today — `kn1500`, `kn5000`, `kn6000`, `kn6500`, `kn2400`, `kn2600`,
`kn7000` — all in the fork; **only `kn5000` is upstream**. (The docs have claimed eight models; the
eighth, SX-PR54, is documented but has no driver.)

**Models that do not exist and must not appear in any plan:** KN450 (a confusion with SX-K450),
KN900 (the real number is KN901), KN2100, KN2200, KN4000, KN5500, and **KN8000** — zero hits across
every firmware image, service manual and project note. The SX-KN7000 was the last SX-KN.

---

## 3. The one structural insight: the computer is shared, the audio is not

This reorders everything, and it is now measured rather than assumed.

**The front-panel sub-CPU is the same part across the CPU-architecture change.** Mitsubishi
**M37471M2196S** sits on the TLCS-900 KN5000 *and* on the MN10300 KN2400/KN6500/KN7000, with the
same HD74LS07P buffers beside it, the same two-byte `[ADDR][DATA]` frame, the same "bank bits 7:6
must be 00 or 11" rule, and the *same normalisation formula* `idx = ((ADDR&0xC0)>>1)|(ADDR&0x1F)`
into a 128-entry table — implemented in TLCS-900 machine code on the KN5000 (table `0xEDA03C`) and
in MN10300 machine code on the KN7000 (table `0x486135A0`). Only the table contents differ.

Within G6 the sharing is total: identical `MILK MN10300 Ver1.0R1` banner, identical on-chip I/O map,
and **identical literal-reference counts** across four independently built firmwares (panel RX
`0x34000809` twice in all four; MIDI-2 TX `0x34000828` seven times in all four). That is one
peripheral-driver source recompiled per model.

**And it reaches outside the arranger line entirely.** The SX-WSA1 — an acoustic-modelling synth
with a completely different audio architecture — runs **dual TMP95C061** and shares *three custom
parts* with the KN5000: the M37471M2196S panel MCU, the **TC183C230002 tone generator**, and the
**uPD6383GF-3BA effects DSP**. Its panel is scanned the same way, over the same SIN/SOUT link.

Measured asset sharing (`technics_roms/tools/wsa1_kinship.py`):

| measurement | result | null |
|---|---|---|
| WSA1 16-char tone-name fields also in the KN7000 table ROM | **195 / 252 (77.4 %)** | — |
| KN5000 sub-CPU payload bytes verbatim in the WSA1 | **31,046 B in 588 runs (15.8 %)** | **0 B** on an unrelated ROM |

Where it **breaks down**, and this matters as much: the WSA1 has **no MILK toolkit**, a different
vendor codepage (`¿` = `0xBB` not `0xBF`), a different text engine, an Epson SED1330 mono LCD
instead of the MN89304 VGA controller, and a proprietary disk format. The model is *shared silicon
and shared assets, separate application framework*. The KN1500 sits similarly outside MILK while
still sharing a 1,658-byte Composer data block with the KN5000 — so the **accompaniment data layer
predates the toolkit**.

**Practical consequence:** panel, inter-CPU, storage and asset work should be built as
**cross-model devices and tools from the start**. A parameterised `technics_cpanel_device` would
serve every instrument from 1995 to 2003, including the WSA1.

---

## 4. The programme

### Phase 0 — Custody and truth · *days · do this first*

Nothing else is safe until this is done, because these are the only **unrecoverable** items.

1. **Rescue evidence living outside version control.** `kn7000-emulator/` is not a git repository
   and holds `money.lua` — the reverb/keybed oracle quoted as the regression gate in at least six
   notes — plus the EG sweeps and the DSP unit-role captures. Other load-bearing scripts exist only
   under `KN7000/tmp-dir/`. *(Started: the KN1500 IC15 dump and the WSA1 OS are now in
   `technics_roms`; the rest remains.)*
2. **Decide the fate of the untracked manuals.** `KN7000/service_manual/` (31 MB, 227 files) holds
   the only copies of the KN7000 service manual **and** the complete KN2400/KN2600 manuals with
   schematics. The KN7000 repo has a *public* remote and these are copyrighted Panasonic documents,
   so they need a local, remote-less home — not a push.
3. **Fix provenance lies.** Three fabricated files ship under real chip filenames
   (`kn5000_waveform_rom.ic304/305/306`, a pure sine); `technics_roms/README.md` calls them genuine
   dumps; the KN6000/KN6500 drivers declare the **KN7000's** table ROM as `BAD_DUMP` when the
   honest flag is `NO_DUMP` — `BAD_DUMP` asserts "this chip, read badly", not "a different chip".
   Rename, re-flag, and make `publish-binary.sh` refuse to publish anything matching `*_rom.ic*`
   that is not in the verified manifest.
4. **Correct false completeness claims** on the three pages a newcomer reads first. `help-wanted.md`
   states all `.byte` code is eliminated (507 `.byte` lines still carry instruction comments, one of
   them a called function) and all `LABEL_*` symbols are replaced (35,924 of 39,451 rows are still
   `LABEL_*`). `issues.md` was last built **2026-03-27**.
5. **Fix the two standing autonomous authorisations**, which are steering on bad inputs *right now*:
   `coverage_score.py` over-reports KN7000 source coverage as 18.03 % when it is **3.64 %**, and the
   cron loop's handoff file stops at a July tick, so it re-derives a month-old world state every run.

**Exit:** no quoted number in the project has an untracked producer; no file misrepresents what it is.

### Phase 1 — Instrumentation · *2–3 weeks*

Build the things that make every later phase checkable. The project's leading cause of retraction is
rig error, and every hard-won rule currently lives as prose in a different file, enforced by nothing.

- **`tools/gate.sh`** — per model: `-validate`, `-listxml`, `-verifyroms`, a headless timed boot
  asserting a liveness signal, and the audio oracle hash. There is no CI in any of the seven repos.
- **`tools/rig.sh` + `rig_lib.lua`** — encode every hazard once: explicit cfg directory with a loud
  banner, NVRAM handling, timeout wrapper, visible video, correct skip flag, Lua taps held in
  globals, and a run manifest recording binary mtime, git HEAD and ROM hashes.
- **The service-diagnostic suite** — one Lua driver per model that walks all ~17 factory tests and
  records the firmware's own verdict. Expect and document honest failures: WAVE ROM will report NG
  on the KN7000 (synthetic waves) and the KN5000. That is the point — it converts "which parts are
  honestly emulated" into a per-subsystem verdict the manufacturer defined.
- **A reference-audio oracle** — the single largest untapped hardware-free ground truth. The KN5000
  Feature Presentation demo and the KN7000 factory styles are extensively recorded in public, and
  the emulator renders the *same named songs*. An onset-aligned comparison can settle pan polarity,
  gain reference and EG decay law — all currently parked as "needs hardware". It cannot settle
  waveform identity; say so up front.
- **Save states** — `kn7000_tonegen.cpp` has *zero* `save_item` calls. This is both an upstream gate
  and 25 seconds of boot removed from every experiment.

**Exit:** a red gate is a bug, not a mystery; a measurement can be repeated by a command.

### Phase 2 — KN5000 audio, root-cause first · *3–5 weeks*

`detect_period()` is the root node and is now fully unblocked. It gates the hand-off decode (which
silences 738 of 1,762 organ note-ons), the P10 octave error, `compute_loop()`, the IC307 chunk
catalogue, and the shared wave helper the KN7000/KN6000 will reuse. Strict order:

1. Build a period oracle from the firmware's own multisample zone table — **not** YIN, which breaks
   the circularity that stopped the last attempt. Use it as acceptance only, never as a fitting target.
2. Rewrite `detect_period()`, dropping the `peak >= 0.5` gate that rejects a real period at 0.436.
3. Fix the aperiodic fallback and `compute_loop()` (a one-shot currently repeats ~90 times).
4. Flip the hand-off default; re-run the demo captures.
5. **Only then** re-open P10 (the octave error) and P9 (the stall at 58 % of the song).

Deprioritise anything whose acceptance test needs the missing wave banks, and say why in the docs so
an outside reader is not misled.

### Phase 3 — KN7000 desk work · *3–4 weeks, parallel to Phase 2*

- **Felipe's own SD card is banked hardware ground truth needing no hardware.** It holds effect,
  sound, panel-memory, composer and sequencer data written by the real instrument. Load it, read
  back the live parameter blocks, diff against the file bytes — the closest thing to a G1 test the
  KN7000 sound domain can build now. *(Contains personal data — never share the image.)*
- **Decode the user-data formats** (`.SEQ .SQF .CMP .TM .LSW .MSP .PMT .EFC .ACT .SQT`) by reading
  the firmware's own serialisers, not by guessing at bytes. Seven real 1999–2000 user disks sit in
  `floppy-archive/` as loose files. Then close the loop: play a real 1999 song and diff the note-on
  stream against the file's event list — a full-stack test of FDC, filesystem, sequencer and TG.
- **Simulate composite video.** The ROM screen-scraper reads 99.87 % on emulator frames and commits
  **zero bytes** on real captures — because it has never seen an NTSC-encoded signal, only a clean
  progressive LCD. Encode, degrade, decode, and find the operating point *before* the instrument is
  reachable. Two calibration pages with fully known answers are already on disk.
- **Build the feature matrix** from the user manual's table of contents: one row per user-facing
  feature (Composer, sequencer record, Music Stylist, One Touch Play, Technichord, Registration,
  pedals, SysEx, GM, metronome), graded per model with the evidence named. Nothing on the site
  currently answers "how much of this instrument works".

### Phase 4 — Upstreaming, continuous · *runs from week 1*

Small, independently-correct PRs beat one large one. Order:

1. **Push the rebased PR #15878** — it is 4 commits ahead / 149 behind origin, so a maintainer sees
   a stale base with no CI signal. **First resolve the IC14 filename collision**: the fork expects
   `76d11a5e` and de-scrambles at load; the PR expects a flat `aa4917ce`. Both call the file
   `kn5000_rhythm_data_rom.ic14`, so no single romset satisfies both.
2. The one-character `mn10300` disassembler fix — costs nothing, starts the relationship.
3. `spi_sdcard` CRC16 init-0.
4. **Promote `mn89304_vga_device`** out of `kn5000.cpp`, where it hides as a driver-local class with
   a live `emu_fatalerror`. It is documented, self-contained and upstream has nothing like it.
5. **Software lists** — `hash/kn5000_flop.xml` and friends. No Technics machine has one, and real
   media sits unpreserved. Reconstructed disk images must be labelled reconstructions, never dumps.
6. Ask mamedev the policy question about declaring update-disk payloads — **concurrently**, since it
   gates the ROM-record PR.

Gate PR 8a/8b (tone generator) on a written verdict for each of the 27 `getenv` switches. One of
them deletes held notes; per the project's own RULE 20 a diagnostic of exactly that kind cost a day
of contradicting the owner about organ sustain.

### Phase 5 — Siblings and the nearly-free models · *2–3 weeks*

Build the **cross-model code aligner** first — relocation-tolerant byte-pattern matching across N
program images, emitting an address-correspondence table. Four separate lanes describe this same
technique as their method, and it is the highest-leverage cross-model artefact available.

Then: **SX-PR54** (a clone of kn2400; its firmware *is* the KN2400 image, selector documented), and
**SX-PR604/PR804** once the KN7000's selector RAM address is located. Caveat: the cabinets genuinely
differ — 88 weighted keys, different panel, video out on the PR804 — so a clone entry that silently
reuses the KN keybed would be a cosmetic lie even though the ROM sharing is real.

### Phase 6 — Opening the NEC generation · *months*

The V25 era is a third of the product line and nobody has touched it. The CPU core is **already
upstream in MAME**; the uPD72068 FDC is a uPD765 relative. The whole cost is the **uPD93083 tone
generator**, which has no datasheet and must be reverse-engineered from firmware register writes —
exactly as was done for the MN10300 line. The KN1200's service manual is free and complete, and its
self-diagnostic makes the wave ROM emit a **sine wave**: a built-in audio oracle.

Two service-manual purchases resolve the entire generation boundary: **KN3000** (which is the
KN5000's direct firmware ancestor — untranslated `KN3000` strings survive in the KN5000's Spanish,
German and French catalogues where the English reads KN5000) and **KN2000**.

### Phase 7 — WSA1, and the organs · *months, gated on research*

The WSA1 is now the best-prepared unstarted target in the project: its **full 2 MB v2.0 OS is in
hand** and verified, its service manual is free, its CPU is one we already emulate, and three of its
custom chips are parts we have already reverse-engineered. Budget it as a new *application*, not a
new architecture. MAME already has a SED1330 device for its display.

★ **The WSA1 may also unblock the KN5000's DSP.** It drives the same uPD6383 and names real effects
— SLOW ATTACKER, PITCH SHIFTER, PEDAL WAH, ROTARY SPEAKER — that the KN5000 ships as programs
byte-identical to NO OPERATION. The link is **not yet demonstrated**: the test is to find the WSA1's
DSP upload routine and check whether its tables parse under the documented KN5000 grammar.

The console organs (GN7/GN9/FN3) cannot be emulated — no CPU, no dumps, 100 kg instruments — but a
**format-analysis pass is possible today with zero new material**, because the KN keyboards
hard-code the organs' sequencer capacity limits in a string both the KN5000 and KN7000 carry.

---

## 5. The parked-hardware lane

About twenty items need physical access, currently scattered across nine documents in inconsistent
formats — at least one with a defect that would void the take. **Write
`notes/HARDWARE-VISIT-PROTOCOL.md` now, not when access returns**, one file per instrument, ordered
by what each item unblocks, each with: exact setup, exact takes *including the mandatory negative
control*, the pre-registered prediction with the artefact that computed it, and the acceptance
criterion that would make the take void.

Highest-value parked items: re-dump **IC14** (should hash to `aa4917ce`); dump **IC304/305/306**
(~75 % of KN5000 sounds, the largest single audible defect); re-read **KN1500 IC15** (lane census
shows 8.5 % vs 54.3 % `0xFF` — against 0.8 %/1.9 % on the known-good IC307); the KN7000 build-893
camera sweep; and the KN5000 sub-CPU boot ROM's two undumped ranges.

**Cheapest acquisitions, ranked by information per euro:** the KN3000 service manual; the KN2000
service manual; the combined SX-K300/K350/K450 manual (the one missing part number for the best
new-silicon target); a **SY-EW65NX** board — the retail KN6000→KN6500 upgrade kit, which likely
carries the KN6500-only wave pair on a bench-readable PCB instead of requiring a donor instrument;
and any gen-03 PR update disk, which would settle a whole generation by checking for the MILK banner.

---

## 6. What we ask of other owners

Every terminal blocker is somebody else's chip, and no one has written the ask. Four contributions
cost a stranger minutes and are worth months here:

1. **A photograph of the service-mode ROM DEVICE TEST screen** — a free per-device checksum oracle
   for any model, including ones nobody here owns.
2. **Raw images of original Panasonic disks** (a PC task, not bench time).
3. **Any unrecognised `.SLD`/`.AST` payload** from a dealer CD. The container magic is sequential by
   generation — KN5000 `H`, KN6000 `I`, KN7000 `J`, KN2400 `L` — so an unfamiliar magic is a
   fingerprint of a model we have not catalogued.
4. **A TMP94C241F hardware manual**, and any datasheet for the uPD6383 or uPD93083.

Panasonic's own `TECHNICS.HDD` enumerates twelve KN6000 update payload classes, and **six are types
we have never located** — Table, Rhythm and Wave-Expansion among them. Panasonic itself says those
were field-distributable: a zero-risk software route to several currently "undumped" mask ROMs.

---

## 7. Dead ends — do not retry

- **The uPD6383 decode campaign must not be on the critical path.** Parked since 2026-08-01 at
  38.53 % ALU decode with an honest ceiling near 45–50 %; the device is *compiled out by default*
  and runtime-gated off; `run_frame()` discards every frame unless decode is total; 44 filed dead
  ends; the output stage is a proven null — "not starved, not connected". Even a perfect IC311 is
  capped, because **IC310 (MN19413), which the entire main mix passes through, is not emulated at
  all**. Keep the cheap hygiene items and the never-run acceptance test T5; drop the SRC 0x00
  adjudication, the kernel-A forward-gain hunt and the base-0x90 falsifier. Redirect that budget to
  IC310, where a few days of desk work buys a first-order gain on the whole mix.
- **The "~93.3 % decode ceiling"** is a misread of a stale diagnostic line. It is not a real number.
- **The PR804 CD-ROM** contains no firmware — PC drivers, an MSI and 100 score PDFs. Closed.
- **The `EA5` string** in our firmware is an interleaving artefact; zero hits in any merged image.
  Likewise the apparent `WSA` hits in KN ROMs are coincidence — the real WSA1 kinship was found by
  other means.
- **Never scan split even/odd ROM halves with `strings`.** It shreds every string and returns a
  confident-looking negative. This produced the false claim that the KN6000/KN6500 lack the MILK
  banner — it is present at `0x487F77E8` / `0x48781448`.

---

## 8. Maintaining this page

Every numeric claim here should carry the command that produced it. Where this page and a
measurement disagree, the measurement wins and this page gets corrected in the same commit —
including in the direction that makes the project look less finished. The three most valuable
things published in the last month were retractions.
