---
layout: page
title: Raw Byte Code Elimination
permalink: /raw-byte-code-elimination/
---

# Raw Byte Code Elimination Plan

**Status:** In Progress (March 2026)
**Goal:** Convert all executable code currently represented as raw `.byte` sequences to native TLCS-900 assembly mnemonics.

## Context

All 6 ROMs achieve 100% byte-perfect match, but some executable code remains encoded as raw `.byte` sequences rather than native TLCS-900 instructions. The root cause is missing LLVM TLCS-900 backend encodings for certain addressing modes and instruction variants. This is the current major project goal.

**Scope:** `.byte` sequences that encode native TLCS-900 CPU instructions across all 6 ROMs. Data tables, strings, bitmaps, firmware bytecode for software interpreters, and padding are out of scope (correct as-is).

## Audit Results

Encoding gaps by category (approximate counts across all ROMs):

| Category | Prefix | Count | LLVM Status |
|----------|--------|-------|-------------|
| calr with numeric target | `0x1E` | ~655 | Broken (emits absolute bytes) |
| Compact register loads (d8 prefix group) | `0xD8-0xEF` | ~436 | Not implemented |
| F2 immediate-to-memory stores | `0xF2` | ~358 | Not implemented |
| C3 R+d16 loads (source addressing) | `0xC3` | ~216 | Not implemented |
| D7 prevbank instructions | `0xD7` | ~182 | Partially (ld works, cps doesn't) |
| Compact dec/inc xsp | `0xEF 0x6x` | ~37 | Not implemented |
| FDC raw byte blocks | various | ~434 lines | Need full disassembly |
| Flash/floppy handler blocks | various | ~1,399 lines | Need full disassembly |

**Key files with most code .byte:**
- `maincpu/storage/fdc_routines.s` — 434 lines (confirmed code)
- `maincpu/storage/flash_floppy_handlers.s` — 1,399 lines (confirmed code)
- `maincpu/system_handlers.s` — 267 lines
- `maincpu/storage/single_load.s` — 873 lines
- Various sequencer/audio/MIDI files — scattered occurrences

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

1. Full `make clean && make all` + `compare_roms.py` (100% byte match on all 6 ROMs)
2. Run `scripts/sync_docs_labels.py --apply` to update any new labels on the website
3. Update `rom-reconstruction.md` with the milestone
4. Update issue tracker (`bd close` completed issues)

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
- `cd kn5000-roms-disasm && make clean && make all`
- `python scripts/compare_roms.py` — must show 100% match on all 6 ROMs
- LLVM tests: `cd llvm-project && build/bin/llvm-lit llvm/test/CodeGen/TLCS900/`

## Policy Compliance

All newly disassembled code MUST:
1. Have semantic label names (no `LABEL_XXXXXX`)
2. Have documentation header comments explaining what each routine does
3. Be verified with byte-match builds before committing
4. Have website docs updated if labels appear on documentation pages
