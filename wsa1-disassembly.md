---
layout: page
title: SX-WSA1 Disassembly
permalink: /wsa1-disassembly/
---

# SX-WSA1R — the byte-exact disassembly

All four of the [SX-WSA1]({{ site.baseurl }}/wsa1/)'s EPROM images — 2,097,152
bytes in total — are being converted to TLCS-900 assembly source that
**reassembles to the original bytes**. The project is the sibling of the
[KN5000 ROM reconstruction]({{ site.baseurl }}/rom-reconstruction/) and follows
the same practices, including the same
[LLVM TLCS-900 backend](https://github.com/felipesanches/llvm-project/tree/tlcs900_backend).

> **Status: the reachability coverage goal has been met.** A further wave, run
> after the wave-6 pause, converted every reachable code path that has start
> evidence: recursive descent over the three code images now finds only
> **STRONG 17 bytes** still reachable-and-unconverted (all formally refused —
> see below), down from 17,558 at that goal's start. Raw substantive coverage —
> which counts territory, not reachability, and so is a smaller number by
> design — stands at **1,575,648 bytes — 75.1 %.**

## The gate is the only thing that certifies this tree

```
python3 scripts/analysis/assert_byte_identical.py
```

It must print `PASS: every rebuilt ROM is byte-identical.` after **every** edit
and at **every** commit. It rebuilds first and compares bytes.

Never substitute a similarity percentage, and never use `--no-build` unless you
have just built — **both shortcuts have already cost the sibling project real
retractions**, and the reasons are written into the script's own docstring.
Commits additionally carry an `LLVM: <branch>@<short> (<full>)` line, enforced by
a commit hook; the current pin is `tlcs900_backend @ dbb72df07371`. The same
backend assembles the KN5000 tree.

## ⚠ The rule the gate cannot enforce

**The gate is blind to names and comments. A confidently wrong routine header
passes for ever.** Every error in the list below was gate-clean:

* eight KN5000 label transplants naming the wrong object (a spliced-ROM offset
  bug, off by `0xEB00`);
* a "zero exceptions" that had 341 exceptions;
* a "243 of 244" reproduced by no committed script;
* a handler count of 35 that was 34;
* a "byte for byte" for a match that was 170 of 204 bytes;
* a routine **80 of 81 bytes identical** to the KN5000's where the one differing
  byte was the peripheral base;
* about 20 call sites cited one byte past the instruction, systematically;
* "no references" and "no site found" asserted without running the census — they
  had references;
* a findings title claiming producers were "named" when they were only "located";
* the system-clock note's lever B (see the
  [retraction]({{ site.baseurl }}/wsa1/#the-clock-fc--28-mhz-and-the-firmware-is-what-says-so)).

Hence the working rules: every semantic name needs an `Evidence:` line; every
quantified claim needs a committed script, tested on the **last** element as well
as the first; every borrowed name needs a byte diff with the differing count
stated. **Prefer `sub_XXXXXX` plus a stated gap over a plausible guess.**

## Coverage — and why the headline number is the smaller one

Regenerate with `python3 scripts/analysis/source_coverage.py`; never retype it.

| source | image | substantive | verified filler | still `.incbin` | spans |
|---|---|---:|---:|---:|---:|
| `prom_a` | `wsa1_prom_a.ic12` | 429,545 | 48,437 | 46,306 | 84 |
| `prom_b` | `wsa1_prom_b.ic13` | 420,510 | 62,966 | 40,812 | 417 |
| `prom_c` | `wsa1_prom_c.ic28` | 395,072 | 129,216 | **0** | 32 |
| `prom_d` | `wsa1_prom_d.bin` | 330,521 | 193,767 | **0** | 0 |
| **total** | | **1,575,648 (75.1 %)** | 434,386 | 87,118 | |

*(Re-run 2026-09-01, after the reachability goal below was met — prom_a and
prom_b both moved substantially, and `prom_b`'s span count went up because the
remaining `.incbin` fragmented into more, smaller gaps as reachable code was
carved out of it.)*

⚠ **Quote the substantive column, not the 95.8 % total.** Wave 3 converted
123,151 bytes of prom_c of which **118,298 were a verified run of `0x0E` pad
emitted as `.fill`** — that moved the headline from 4.3 % to 27.7 % while adding
under 5 KB of decoded content. The pad is real and checked rather than sampled,
so it belongs in the source; but a number that treats it as equal to decoded code
flatters. **Coverage measures territory, not understanding.**

⚠ The table is generated for a reason: the hand-typed version went **stale within
one commit** — it still claimed 4,639 bytes after four agents had converted
604,523 — because it sat outside every lane. Three of the four lanes noticed and
none edited it.

## ★★ The reachability goal: met

A goal distinct from raw coverage — *convert every reachable code path that has
start evidence* — has been completed. `notes/reachability.py` walks the CPU
vector table, the 1,910-slot routine directory, framed pointer tables, branch
targets in converted code and 32-bit immediates, and grades every seed:
**STRONG** (a directory slot, a decoded branch, a hardware vector — convert on
this column) versus **WEAK** (a `.long` entry or a raw immediate, which is a
pointer and as likely to name a table as a routine).

| | at goal start | now |
|---|---:|---:|
| STRONG reachable-and-unconverted | 17,558 bytes | **17 bytes** |
| `prom_b` STRONG remaining | — | **0** |
| `prom_c` STRONG remaining | — | **0** |
| ANY (STRONG+WEAK) reachable-and-unconverted | — | 1,702 bytes, 17 spans |

The 17 remaining STRONG bytes (`0xFA369A-0xFA36AB` in `prom_a`) are a walk
artefact and are **formally refused**: read straight out of the ROM they spell
`"D GROUP NAMING"`, the tail of a UI string reached only because the walk
decoded its way into it — no seed of any grade names that address, and no
converted instruction falls through into it. The walk reached a **fixpoint**:
round 1 revealed 499 bytes, round 2 revealed 38, and converting those 38
revealed nothing further.

This did **not** touch semantics — every label the goal added is a bare
`sub_XXXXXX` with a start-evidence line, no claim about behaviour — and it left
existing prose untouched (verified by diff, not assumed). What is left for a
future goal: 180 bytes with no start evidence at all (refuse unless evidence
appears), ~1,702 reachable bytes that are WEAK-seed-only pointer-table
artefacts needing a byte-level audit before conversion, and ~105,000 bytes of
`.incbin` that nothing reaches (data — converting it adds territory, not
coverage).

### ★ The number that measures meaning, and it keeps going up

`sub_XXXXXX` — the count of routines that are converted but **unnamed** — stood
at about 4,998 after wave 6 and has continued to climb since, to about
**5,014**. Newly converted code brings in unnamed routines faster than naming
retires them.

> *Coverage measures territory; this number measures meaning, which is the half
> of the goal that is furthest from done.*

Alongside it, re-derived 2026-09-01: **7,557 routine headers with
`Evidence:` lines** (`grep -rh 'Evidence:' prom_*/*.s | wc -l`), **105 notes
documents** of which 78 are `FINDINGS-*` (`git ls-files 'notes/*.md'`), **360
committed Python analysis scripts** (`git ls-files '*.py'`), and about **5,014**
routines still named only `sub_XXXXXX` — the last of those is the number worth
watching, because it measures meaning rather than territory.

⚠ These move with every wave. Re-derive them with the commands above rather than
quoting this paragraph; a label count in particular depends on whether you count
compiler-local `.L` labels, so no single figure is quoted here.

## ★★ ONE KERNEL, FOUR PROCESSORS, TWO PRODUCTS

The result below stands and has since been carried two steps further.

**Step one — the two WSA1R processors now share ONE SOURCE.** `wsa1/kernel/kernel.s`
plus `kernel_maincpu.inc` / `kernel_subcpu.inc` assembles **twice**: into 2,180
bytes of `prom_a` and 2,180 bytes of `prom_c`, both byte-identical to the EPROMs.
That dual build is the proof — one wrong constant and one of the two images stops
matching. Over the union of 941 instruction slots, 735 needed no reconciliation,
129 differed only in house style, and **81 carry a per-CPU value — which turned
out to be 21 constants**, not 81 patches (twelve RAM addresses, six array sizes,
three ROM pointers). There is no `.if`/`.else` in the file.

**Step two — the same kernel is in BOTH of the KN5000's processors**, in its
sub-CPU payload and, as a separate build rather than a copy, in its main program
ROM. One kernel, four processors, two products.

⚠ **Byte identity is the wrong instrument for that second question.** Zero
routines match byte-for-byte across the 41 KN5000 images — true about bytes and
irrelevant to the question, for the reason step one measures: two processors in the same product, from the
same build, running the same source, still differ in 81 of 941 slots.

### A second shared source: the DSP channel-register driver

The kernel is not the only source both processors share. `dsp/dsp_channel_regs.s` — four routines, 234 bytes, of which **231 are
byte-identical between the two CPUs** — is now a single file included by both
roots. Everything that differs is one equate:

| CPU | `DSP_REGS_BASE` |
|---|---|
| CPU 1 (`prom_a`) | `0x007F0000` |
| CPU 2 (`prom_c`) | `0x00E00000` |

Three use sites, and **no conditional assembly anywhere in the body**. The
byte-identity gate covers it: 13 images rebuild identically (9 KN5000 + 4
WSA1R), and the negative control — setting the sub-CPU equate wrong — fails
`prom_c` at exactly three bytes while leaving `prom_a` green, so the gate is
demonstrably load-bearing here.

⚠ **The merge produced a finding, not just a tidier tree.** With both files'
call-site annotations on one page, they disagree twice, in opposite directions:

| routine | CPU 1 | CPU 2 |
|---|---|---|
| `DSP_ChannelRegs_Init` | no call site found | called at boot from `0xF98B95` |
| `DSP_WriteAllChannelRegs` | published via `prom_b` thunk `0xF42DE4` | not traced |

Identical bytes, different reachability per processor — each one uses the
routine the other does not. This is **unexplained**. In either file alone an
untraced routine reads as ordinary coverage debt; only the merge makes it an
asymmetry.

The control that decides it is a **foil** — the identical search run over WSA1R
code that is *not* the kernel:

| | n | max | median | ≥ 0.70 |
|---|---:|---:|---:|---:|
| kernel routines (≥ 20 instr) | 20 | 1.000 | **0.909** | **20** |
| non-kernel foils, same lengths | 26 | **0.333** | 0.212 | **0** |

No overlap, a gap of 0.41. `prom_b` — same product, same compiler, no kernel —
tops out at 0.28, so it is not measuring the compiler; shuffling the query's
token order collapses the score, so it is measuring *order*, not vocabulary. Two
threshold-free instruments agree: the 26 sites appear in ROM order as a **21-long
increasing run** (200,000 permutations never exceeded 14), and the recovered RAM
map is **monotone** across all three processors.

**Not established:** who wrote it, or that the sources are identical —
`Kernel_Dispatch` scores 0.742, the KN5000 version having no tick-drain loop and
its lock depth moved out of a control register the TMP94C241 does not have.

---

## ★ The two processors run the same kernel — 35 of 36 routines identical to the byte

The strongest structural result in the tree is about the machine's relationship
to *itself*. `notes/prom_c_prom_a_routine_diff.py` aligns two routines
instruction by instruction and separates *different mnemonic* (structural) from
*same mnemonic, different operand* (a substituted address):

| | |
|---|---:|
| routine pairs | **36** (35 in the block, plus `INTT3_KernelTick`) |
| pairs whose prom_c length equals their prom_a length | **36 of 36** |
| pairs with **zero** structural differences | **35 of 36** |
| the exception | `Kernel_InitRam`, with **2** — both inside an 8-byte inline data block |

The routine boundaries are **checked, not asserted**: `notes/prom_c_kernel_map.py --pairs`
verifies that each
routine ends exactly where the next begins **in both images**, and fails
otherwise. *36 boundaries agreeing to the byte across two independently compiled
images is not something a wrong split survives.* `Kernel_ResumeTask` is the
extreme case — all nine bytes identical, with no operand to substitute.

**Every one of the ~120 operand differences is a RAM address, a ROM table
address, a loop bound or a branch target. The two images differ in their RAM map
and in nothing else.** CPU 1 publishes the kernel through two runs of prom_b
thunks (a register-argument face and a stack-argument face); prom_c has **no
thunk table** — the same routines at the same relative offsets, with the same
nine stack faces falling through into the register face.

### The kernel's RAM map is a proof, not a reading

`Kernel_InitRam` (prom_c `0xF9816B`) writes nine arrays with literal bases and
literal counts. `prom_c_kernel_map.py --map` reads all eighteen numbers out of the
**instruction bytes**:

```
base     n  stride  end      what
0x0100   3   12    0x0124   task control blocks
0x0124   2    4    0x012C   ready-queue heads
0x012C   4    4    0x013C   semaphore wait queues
0x013C   4    1    0x0140   semaphore counts
0x0140   2    4    0x0148   message WAIT queues
0x0148   2    4    0x0150   MESSAGE queues
0x0150   4    8    0x0170   free nodes
0x0170   1    4    0x0174   free-list head
0x0174   2    8    0x0184   software timers
```

**The nine arrays tile `0x0100`–`0x0183` with no gap and no overlap.** A wrong
count anywhere in that chain leaves a hole or an overlap — so "three tasks, two
priority levels, four semaphores, two message queues, four free nodes, two
software timers" is each pinned **twice**: by a literal loop count, and by the
array that starts where the previous one ends.

## ★ Shared code with the KN5000 — measured, with a null

Because **both machines are TLCS-900**, code can cross between them as literal
bytes. `scripts/analysis/kn5000_shared_runs.py` finds every maximal run of ≥ 16
bytes shared between the WSA1 images and the KN5000 sub-CPU payload, and grades
each one:

| | |
|---|---:|
| kept (survived the entropy guard) | **32,795 B** |
| rejected as low-entropy fill | 291,802 B |
| **shuffle null** (same byte histogram, sequence destroyed) | **0 B** |
| signal-to-null | **32,795×** |
| of the kept mass, held in **prom_c** | **28,916 B** |

*(Re-run 2026-08-26; the figures above are that run's output.)*

**The entropy guard is the whole script.** Without it, the "shared" mass is nine
parts erase-fill and padding. Runs are rejected when fewer than 12 distinct byte
values appear, when the modal byte is more than 60 % of the run, or when the run
is a repeating period of ≤ 4 bytes — and the rejected set is **printed, not
silently dropped**, because "the kinship is entirely in padding" is an outcome
this script exists to be able to report.

That **28,916 of 32,795 land in prom_c** is the structural finding: the KN5000
sub-CPU is *its* tone-generator controller, so **WSA1 CPU 2 and the KN5000
sub-CPU are the same design.** The data format follows the controller — prom_d's
81-byte per-element voice-parameter block is the KN5000's too, measured against
byte-shift and rotation nulls.

⚠ **Two different numbers exist and must not be conflated.** A separate,
earlier script — `technics_roms/tools/wsa1_kinship.py` — reports **31,046 B in
588 runs (15.8 %)** with a null of 0 B against an unrelated Technics ROM. It is a
different script over a different corpus, with no entropy guard and the WSA1
images concatenated. **Pick one and name its script.** Do not average them.

⚠ A provenance caveat on the 32,795 figure: `kn5000_shared_runs.py` matches
against `kn5000_subprogram_v142.rom`, which the sibling Makefile builds as a
**spliced** image. The de-splicing was applied to the label transplanter, not to
this script. The count of WSA1 bytes is unaffected, but **payload offsets from
this script are not directly comparable to KN5000 addresses**.

### The label transplant, and the retraction that shaped it

`transplant_kn5000_labels.py` proposes KN5000 sub-CPU routine names for WSA1
addresses **by byte identity**, and currently emits **105 proposals, 0 dropped**.

⚠ **An earlier version advertised eight proposals, and all eight named the wrong
object** — the script matched against the spliced image, so every offset past the
first 256 bytes was short by 60,160 = `0xEB00`. `EGEnv_ValueCurve_Simple` landed
inside the keybed *touch* curve. **The names were thematically plausible, which is
why eye-checking did not catch them**, and two independent lanes found the bug.

Two changes so it cannot recur: the splice is out of the pipeline, and **every
proposal is byte-verified at emission** and dropped if the bytes disagree. The
original failure would now emit zero rows rather than eight wrong ones.

⚠ Byte identity establishes that the *code* is the same, not that the surrounding
machine is. Of the 105, exactly **one** (`Int_SignedDiv` / `FP_UnsignedDiv` at
prom_a `0xFE68F3`) has been converted and read; the other 104 are **proposals,
not renames.**

## What is left

`prom_c` and `prom_d` have **zero `.incbin`** — they are territorially complete.
All remaining conversion is in prom_a (106,585 B) and prom_b (159,459 B).

* **prom_a** — `0xFE8000-0xFEB330` (13,104 B) and `0xFEF746-0xFF3800` (16,570 B),
  the code halves of the sequencer/UI module. Deferred because about **15 string
  constants sit inside the instruction stream** (`SEQUENCER`, `NOTE EDIT`,
  `DRUM EDIT`, an 838-byte effect-name table at `0xFF047F`); their bounds must be
  pinned first or the linear decode desynchronises. **That bounding is the next
  pass's first job.**
* **prom_b** — the top span is `0xF067A6-0xF0D79B` (28,662 B).
* **prom_c** — `0xFCD0F7-0xFDD2AA` (65,972 B) is a byte-code/command stream left
  **whole**, because the existing 16-bit big-endian framing desynchronises at the
  fifth record. It needs its interpreter found first: *guessing a stride is this
  project's known failure mode.*

## ⚠ Tools that mislead, named as such

* **`prom_c_frontier.py`: 132 of its 135 targets are phantoms**, produced by
  linearly disassembling ASCII descriptor strings and data zones. Wave 5 ignored
  it and was right to.
* **`prom_b_span_frontier.py`'s `proven 0` is not evidence of data.** Its
  call-site scanner only recognises one calling idiom, so a well-evidenced region
  reached another way scores 0. Wave 6's best target scored worst.
* **A frontier count that does not fall after converting a data span is correct,
  not a failure** — data retires no call target. Do not quote a drop that did not
  happen.

There is a matching trap in the code tracer. A straight linear sweep of these
images is worthless for a memory map: prom_c holds an IEEE-754 double table at
file `0x4B27E` (the bytes at its head are π) which linearly disassembles into a
tidy stride-4 register file **that does not exist** — 280 phantom "registers" came
out of that before the recursive-descent walker was written. Even the walker's
heuristic seeds drag data in as code, and three known false positives are named
in its README. Recursive descent currently reaches **36.7 %** of CPU 1's two
EPROMs and **42.6 %** of CPU 2's, so a device touched only from unreached code
would still be missing from the
[memory map]({{ site.baseurl }}/wsa1/#memory-maps).

## Related

| Page | Description |
|------|-------------|
| [SX-WSA1 / SX-WSA1R Overview]({{ site.baseurl }}/wsa1/) | The machine, the hardware, the memory maps, the model strap |
| [Emulation Status]({{ site.baseurl }}/wsa1-emulation/) | The MAME driver the disassembly feeds, and which feeds it back |
| [Shared Codebase Map]({{ site.baseurl }}/technics-shared-codebase/) | Where this machine's code meets the KN5000's and the KN7000's |
| [KN5000 ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) | The sibling project, and where these practices come from |
