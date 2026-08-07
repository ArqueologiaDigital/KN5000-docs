---
layout: page
title: Disassembly Workflow
permalink: /disassembly-workflow/
---

# Disassembly Workflow

Between 6 and 7 August 2026 the disassembly repository absorbed twenty-four conversion
packages across four waves — the tone database, the bootloader's FDC and CP-serial
drivers, the Music Stylist and Panel Memory factory data, the fonts and UI bitmaps, the
help databases, the sub-CPU DSP data zones — and the byte-match gate never once dropped
below 100.00%.

That is not luck, and the process is worth writing down because it is reusable. This page
describes it.

## The invariant

> `make all` + `compare_roms.py` at **100.00% byte-match on every section, after every
> merge.**

Everything else in the workflow exists to protect that one line. A package that cannot
demonstrate it does not land — it is reverted, and the reason is recorded rather than
argued away.

## Step 0: audit before touching anything

The waves were scoped by a prior audit rather than by intuition about what looked
interesting. Ten agents — seven scanners and three adversarial verifiers — walked every
`.incbin`/`binclude` directive and every compressed region in the repository.

| Quantity | Result |
|----------|--------|
| Directives inventoried | 598 |
| Honest build products (compiled from C/asm, or generated from documented data) | 505 |
| Findings recorded | 55 |
| Adversarial verdicts | 24 (14 CONFIRMED, 10 REFUTED) |

The output was a machine-readable `findings.json` plus a plan that ordered the remaining
work into waves. Crucially, the audit distinguished *build products* from *undocumented
binaries in disguise* — a `generated/` path is not evidence of anything if the "generator"
is a `dd` that slices the original ROM.

### The evidence standard

"This blob is code" was accepted only after an adversarial pass demanding all four of:

1. a clean decode at the claimed base address;
2. every branch target landing on an instruction boundary;
3. at least one call target coinciding with an independently known label; and
4. **a shifted-decode control** — the same bytes must *not* decode cleanly at base+1.

The fourth condition is the one that does the work. Plausible-looking disassembly is cheap;
disassembly that survives a deliberate attempt to produce it from the wrong offset is not.

### The adversarial pass earned its place

It corrected the scanners repeatedly rather than rubber-stamping them:

- The scan reported 23 `v7_block_*` binaries. The verifier checked all of them and found
  the generator's list contains 138 unique block entries (139 files) — a six-fold
  undercount that would have made Wave 4 unschedulable.
- Ten of the twenty-four verdicts came back **REFUTED**, most of them as *gaps*: whole
  categories the scanners had declared clean and had not actually covered (the maincpu
  inline `.byte` regions, orphaned reference slices, the v1.41 payload with no build
  coverage, binaries under `dsp/` that a "clean sweep" claim had missed).

The waves then refuted two claims the plan itself had carried forward: there is no
"exponential pitch table at 0x13318" (it is the middle of a mixer *gain* curve), and a
banner claiming two 128-byte tables at 0x00FF00/0x00FF80 was retracted — those addresses
are immediate values written to a hardware address latch, not table pointers.

## The wave shape

Each wave is one run with the same three-part structure.

### 1. Parallel read-only workers

N agents draft in parallel into a scratch directory. **No worker ever touches the
repository or git.** Each receives one package — a bounded region and a deliverable — and
returns replacement `.s` text with semantic labels matching house conventions, a module
header, per-table comments, and the evidence behind every label (an xref address or an
observed behaviour).

The part that makes the whole thing work is the **mandatory self-check**: before returning,
a worker assembles its fragment standalone and byte-compares the result against the
original ROM slice, quoting the commands and their output. A fragment that does not match
returns `blocked` or `partial` *with the diff*. It never returns silently.

This pushes verification to where the knowledge is. By the time a package reaches
integration, someone has already proved it reproduces the ROM.

### 2. One integration manager — the only writer

A single agent owns the branch and applies packages **one at a time**. After each package:
a full `make all` and `compare_roms.py`. On 100.00% it commits (one commit per package,
succinct message, toolchain-provenance line). On anything less it reverts — by hand,
surgically, never with `git checkout`/`reset`/`stash`, because those would take
uncommitted work with them.

Serial integration is the expensive-looking part and the reason the gate held. Parallel
drafting is safe because drafts are text in a scratch directory; parallel *merging* would
make a byte mismatch impossible to attribute.

Where packages overlapped — several of the Wave 2 workers touched the same banner comments
in `kn5000_table_data.s` — the manager hand-merged later hunks over earlier text and
re-verified, rather than letting a later package overwrite an earlier one's work.

### 3. Ledger

The manager appends one row per wave to a status file: what launched, what landed, the
commit hashes, what was adapted during integration, and what was deferred. The deferred
list is not a wish list; it is the input to the next wave.

## House constraints that keep the gate honest

Some of these look like bureaucracy until you notice what each one prevents.

- **Blob files that the archived ASL build still `binclude`s stay byte-identical on disk.**
  Conversions slice with `.incbin "file", offset, length` instead of splitting a blob into
  new files. This is why the legacy ASL mirror still builds — and the mirror is six of the
  fifteen verified sections, so it is a real check, not sentiment.
- **Every commit records the exact LLVM toolchain commit** that produced the artifacts
  (`LLVM: <branch>@<hash>`), and LLVM history is immutable once it has produced verified
  ROMs. A byte-match is only meaningful if you can say which assembler produced it.
- **Symbol reference files are uppercase and address-sorted**, so they diff cleanly and
  external tools can bisect them.
- **Documentation commits must build.** A docs change that breaks `jekyll build` is not
  finished.
- **Nothing is pushed** during an autonomous run.

## What went wrong (and what that cost)

Two failures in twenty-four packages, neither of them a byte-match failure:

- One worker stalled and returned nothing. Because workers cannot write to the repository,
  the cost was exactly one package's delay: it was re-run in the next wave and landed.
- A session usage limit interrupted a wave mid-flight, after three workers had finished
  but before the manager ran. Nothing had been integrated, so the repository was untouched;
  the run resumed later, replaying the finished workers from cache and running the rest
  live.

Both failure modes are survivable *because* the only writer is the manager and the only
acceptance criterion is mechanical. There is no state to reconcile if a drafting agent
disappears.

## Why the byte-match never broke

Three properties, in order of importance:

1. **The acceptance criterion cannot be argued with.** 100.00% or revert. No reviewer
   judgement is involved, so no reviewer fatigue can erode it.
2. **Verification happens twice, in different places** — once by the worker against a ROM
   slice, once by the manager against the whole ROM set. The first catches almost
   everything; the second catches interactions between packages.
3. **Serial integration keeps attribution exact.** When something does mismatch, exactly
   one package changed, so the diff points at the cause instead of at a merge.

## Remaining work

Three wave-groups are planned and not started: the HD-AE5000 data slices plus the sub-CPU
boot data blob; the v7 maincpu tree (the largest — its `includes/generated/` directory is
populated at build time by a script that `dd`-slices the v7 ROM, so hundreds of kilobytes
of undocumented binary hide behind a "generated" path); and a closing sweep that includes
the never-classified inline `.byte` regions in the maincpu trees. Current status per ROM
is on the [ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) page.
