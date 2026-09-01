---
layout: page
title: Raw Byte Code Elimination
permalink: /raw-byte-code-elimination/
---

# Raw Byte Code Elimination Plan

**Status: COMPLETE** — All executable code across all 6 ROMs uses native TLCS-900 instructions (0 code `.byte` remaining).
**Goal:** Convert all executable code currently represented as raw `.byte` sequences to native TLCS-900 assembly mnemonics.

## Context

All 6 ROMs achieve 100% byte-perfect match. As of March 2026, all executable code uses native TLCS-900 instructions — the `.byte` code elimination goal is **complete**. The remaining `.byte` directives in the source are exclusively data (tables, strings, padding), not executable code.

> ⚠ **The March 2026 measurement missed real code, and the instrument was the problem.**
> The Sub CPU Payload's "0 code `.byte` remaining" was originally established by checking for
> leftover `.incbin` directives — but a `.byte` run is exactly as undisassembled as an
> `.incbin` and passes that test just as cleanly. A 2026-09-01 audit of the sound subsystem
> (`notes/sound/kn5000_sound_boundary.py`, written up in
> `notes/sound/FINDINGS-kn5000-sound-coverage-2026-09-01.md`) found the v1.42 sub-CPU payload
> still held on the order of 16,000 bytes of `.byte`, including two runs the source itself had
> already annotated *"MISLABELLED, THIS IS CODE"* — roughly 8,500 bytes of that being
> tone-generator/DSP register-write code. All of it has since been converted to native
> instructions and re-verified against the committed MAME `unidasm` listing (10 conversion
> rounds, `--unspellable` and `--misframes` both now 0 in both sub-CPU images). So the *sound
> code* portion of the Sub CPU Payload genuinely reached 0 code `.byte` only on 2026-09-01, not
> in March — directive-counting (no `.incbin` left) is not a completeness proof; only a
> per-byte disassembly attempt (Step 1's actual method, below) is.

> **Second correction, same day.** The scoping above matters: that pass closed the *sound*
> code. A separate falsification pass on 2026-09-01 attacked the payload's remaining 100%
> claim and found **1,230 further bytes of real TLCS-900 code** still spelled `.byte`
> outside the sound path, now converted and each one proved by round trip — disassemble the
> run, re-assemble that exact text, require the original bytes back. **About 976 bytes of
> code-shaped `.byte` remain**, for a named reason rather than for lack of trying: the
> pinned LLVM backend can *decode* some addressing forms it cannot *encode*
> (`DSP_Bytecode_Op01/02/03`, 569 B) and cannot re-parse some spellings its own
> disassembler emits (~407 B in the TaskEvent/FIFO/TaskSched family). So the payload is
> still not at zero, and the honest figure is the one with that remainder in it.
>
> Also worth recording beside the `.incbin` lesson, because it is the same mistake wearing
> different clothes: a lane in the same push converted 153,600 bytes of wallpaper from
> `.incbin` into 9,645 lines of `.byte` and reported the debt falling by that amount — then
> **withdrew it**, on the grounds that a reader understands nothing new afterwards and a
> viewable PNG is the better representation. Counting `.incbin` distorts in both
> directions: it hides real debt written as `.byte`, and it rewards pushing legitimate data
> *into* `.byte`.

**Scope:** `.byte` sequences that encode native TLCS-900 CPU instructions across all 6 ROMs. Data tables, strings, bitmaps, firmware bytecode for software interpreters, and padding are out of scope (correct as-is).

## Current Status

### Completed (March 2026)

All executable code `.byte` sequences have been eliminated from the **Main CPU**, **Sub CPU**, and **Table Data** ROMs:

⚠ The "Sub CPU Payload" row's March 2026 figures were measured by the flawed `.incbin`-absence
test described above; see the warning box for what that method missed and when it was actually
closed out (2026-09-01, for the sound-code portion).

| ROM | Native Instructions | Code .byte Remaining | Status |
|-----|-------------------|---------------------|--------|
| Main CPU | 239,683 | **0** | **Complete** |
| Sub CPU Payload | 35,721 | **0** | **Complete** |
| Sub CPU Boot | 1,357 | **0** | **Complete** |
| Table Data | 1,678 | **0** | **Complete** |
| Custom Data | 0 (data only) | **0** | **Complete** |
| HDAE5000 | 502 | **0** | **Complete** |
| **Total** | **279,441** | **0 code .byte** | **Complete** |

### LLVM Backend Encodings Added

All previously missing instruction encodings have been implemented in the LLVM TLCS-900 backend:

| Category | Prefix | Count Converted | LLVM Status |
|----------|--------|-----------------|-------------|
| JR/JRL/CALR branch instructions | `0x1E` etc. | 1,214 | **Fixed** (label-based) |
| Compact register loads (d8 prefix) | `0xD8-0xEF` | 2,680 reg-reg + 831 ALU/LD/BIT | **Implemented** |
| PrevBank (D7 prefix) | `0xD7` | 147 | **Implemented** |
| Memory R+d8 addressing | various | 3,616 | **Implemented** |
| Compact dst (CALL/JP/CPW/LD) | various | 1,038 | **Implemented** |
| Short LD (compact load) | `0x20-0x3F` | 523 | **Implemented** |
| Compact imm32 loads | various | 684 | **Implemented** |
| ld A, (R+d16) source loads | `0xC3` | ~970 | **Implemented** (Mar 14) |
| ld (R+d16), A stores | `0xF3` | ~400 | **Implemented** |
| Shifts/Rotates/MUL/DIV | various | 246 | **Implemented** |

### HDAE5000: Complete

The HDAE5000 extension ROM's 502 native instructions cover all identified code regions. Remaining `.byte` directives (~15,900 lines) are exclusively **data tables** (custom-filesystem templates — the HD-AE5000 filesystem is *not* FAT16 — string constants, UI bitmaps, etc.) — not executable code.

## Original Audit Results (Historical)

Encoding gaps by category (original counts, now resolved):

## Execution Plan

### Step 1: Precise Automated Audit

Write a Python script (`scripts/audit_byte_code.py`) that:
1. Parses all `.s` files across all ROMs
2. Identifies `.byte` sequences between native instructions (code context)
3. Attempts `llvm-mc --triple=tlcs900 --disassemble` on each sequence
4. Classifies results: (a) already decodable by LLVM → immediate conversion, (b) needs LLVM backend addition, (c) confirmed data
5. Groups code `.byte` by first byte (opcode prefix) to identify LLVM encoding families
6. Outputs a report with: file, line, bytes, category, status

### Step 2: Convert Already-Decodable Instructions

Some `.byte` sequences may already have LLVM support but were written as `.byte` historically. Convert them directly to native mnemonics using the disassembler output.

**Verification:** `make clean && make all` + `compare_roms.py` after each batch.

### Step 3: LLVM Backend — Compact Register Loads

Add encoding support for compact register load instructions:
- `ld wa, 0` (D8 A8), `ld xde, 0` (EA A8), `ld xwa, 1` (E8 A9), etc.
- These are 2-byte compact forms vs the 3-4 byte extended forms

### Step 4: LLVM Backend — Compact Stack Pointer Arithmetic

Add encoding support for:
- `dec N, xsp` (EF 6A/6E) — decrement stack pointer by N
- `inc N, xsp` (EF 62/66) — increment stack pointer by N

### Step 5: LLVM Backend — calr Fix

Fix `calr` with numeric address targets. Currently broken — emits absolute bytes instead of relative offset. Either fix the encoder to compute the relative offset, or add a new mnemonic variant.

### Step 6: LLVM Backend — F2 Immediate-to-Memory Stores

Add encoding support for the F2-prefix `ld (mem), imm` instructions that store immediate values to memory addresses. ~358 occurrences.

### Step 7: LLVM Backend — C3 R+d16 Source Loads

Add encoding support for `ld A, (R+d16)` source addressing (C3 prefix). ~216 occurrences. Note: the D3/E3/F3 destination variants already work; this is the source (load) direction.

### Step 8: LLVM Backend — Remaining D7 Prevbank

Add `cps qiz, 0` and any other prevbank instructions not yet supported (~4 occurrences for cps, ~182 total D7-prefix).

### Step 9: Batch Convert .byte → Native Mnemonics

After each LLVM backend addition (Steps 3-8), convert the corresponding `.byte` sequences in the disassembly to native instructions. Use Python scripts with binary I/O (Latin-1 safety policy). Verify byte match after each batch.

### Step 10: Disassemble FDC Raw Byte Blocks

The FDC routines in `maincpu/storage/fdc_routines.s` contain ~434 lines of raw `.byte` that are actual instruction sequences. These need:
1. Disassembly using `llvm-mc --disassemble` or `llvm-objdump`
2. Analysis of each routine's purpose
3. Semantic labeling (no `LABEL_XXXXXX` allowed)
4. Documentation header comments

### Step 11: Disassemble Flash/Floppy Handler Blocks

`maincpu/storage/flash_floppy_handlers.s` and `maincpu/storage/single_load.s` contain ~2,272 lines of raw byte blocks that need full disassembly, semantic labeling, and documentation.

### Step 12: Iterative Jump/Call Table Discovery & Disassembly

Newly disassembled code may reveal previously unidentified jump tables or call tables. These must be found and their targets disassembled, repeating until exhaustion:

1. **Scan** for undiscovered tables in all newly disassembled code blocks (sequences of `.long` values in ROM range, `lda`+`jp (xwa)` patterns, indexed dispatch)
2. **Verify** table entries are code targets (not already-disassembled or false positives)
3. **Disassemble** newly discovered code targets with semantic labeling and documentation
4. **Recurse** — newly disassembled code may contain more tables
5. **Terminate** when no new tables or code targets are found

**Scope:** All ROMs (maincpu, subcpu, hdae5000, table_data).

### Step 13: Final Verification & Website Sync

1. Full `make clean-all && make all && make asl-all` + `compare_roms.py` (100.00% on all
   fifteen sections — see the note under *Verification* below)
2. Run `scripts/sync_docs_labels.py --apply` to update any new labels on the website
3. Update `rom-reconstruction.md` with the milestone
4. Update issue tracker — edit `kn5000_project/.beads/issues.jsonl` by hand to mark completed issues closed. Do **not** run `bd close` against `kn5000_project` (see `FSanches/beads-usage-policy.md`).

## Ordering & Priorities

**Do first:** Step 1 (audit) — gives precise scope for everything else.
**Then:** Steps 2 (free wins), 3-4 (easy LLVM additions, high impact).
**Then:** Steps 5-8 (harder LLVM work, each unblocks batch conversions).
**Then:** Steps 9-11 (conversion work, depends on LLVM additions).
**Then:** Step 12 (iterative table discovery — feeds back into Steps 9-11).
**Finally:** Step 13 (verification & sync).

Steps 3-8 are independent of each other and can be parallelized.
Step 12 is iterative and may cycle back through Steps 3-11.

## Verification

After each step:
- `cd kn5000-roms-disasm && make clean-all && make all && make asl-all`
- `python3 scripts/build/compare_roms.py` — must show 100.00% on all **fifteen** sections
- LLVM tests: `cd llvm-project && build/bin/llvm-lit llvm/test/CodeGen/TLCS900/`

> **Section count matters more than the percentages.** This page was written in March 2026,
> when the shorter `make clean && make all` was the habit. That form never assembles the six
> ASL mirror sections, and `compare_roms.py` skips a missing section silently — so it prints
> nine sections, all reading `100.00%`, and looks identical to a passing full run. Count the
> sections. See [Disassembly Workflow]({{ site.baseurl }}/disassembly-workflow/).

## Policy Compliance

All newly disassembled code MUST:
1. Have semantic label names (no `LABEL_XXXXXX`)
2. Have documentation header comments explaining what each routine does
3. Be verified with byte-match builds before committing
4. Have website docs updated if labels appear on documentation pages
