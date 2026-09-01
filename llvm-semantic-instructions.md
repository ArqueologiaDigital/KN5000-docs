---
layout: page
title: "LLVM TLCS-900: Semantic Instruction Migration"
permalink: /llvm-semantic-instructions/
---

# LLVM TLCS-900 Backend: Semantic Instruction Migration

The LLVM TLCS-900 backend originally used 118 custom "wrapper" mnemonics encoding raw addressing mode bytes. This page tracks the ongoing work to replace them with proper semantic instructions.

**Beads issues:** `kn5000-7ubb` (Phase 2), `kn5000-1hqd` (Phase 3), `kn5000-xcuk` (Phase 4), `kn5000-0vbs` (Phase 5)

## Why This Matters

Wrapper mnemonics like `st_dri3b L, 0xfd, 0xb8, 0x01` are unreadable. The same instruction in standard TLCS-900 syntax is `lda xsp, (xsp+440)` — immediately clear that it's deallocating 440 bytes of stack frame. Semantic mnemonics make the disassembly comprehensible and cross-version diffs meaningful.

## Progress Summary

⚠ **Updated 2026-09-01 — all five phases are now complete.** A search of the
current backend and both KN5000 version trees found **zero remaining
occurrences** of every wrapper mnemonic named below (`ld16_24`, `ldto_berp`,
`st_dri3b`, and the rest of the Phase 2-5 lists) — the migration this page
originally tracked as "In progress" / "Planned" has since finished. The
per-phase instance counts below are the historical counts from when each
phase was scoped, kept for context; they were not re-verified against the
current tree, and no page here asserts new counts in their place.

| Phase | Description | Instances (at time of scoping) | Status |
|-------|-------------|-----------|--------|
| Phase 1 | Mnemonic renames (81 mnemonics) | 53,603 | **Complete** |
| Phase 1b | Parenthesized direct addresses | 61,436 | **Complete** |
| Phase 2 | 24-bit addressing semantics | ~1,700 | **Complete** |
| Phase 3 | Extended register pair modes | ~3,300 | **Complete** |
| Phase 4 | SRI/DRI indirect modes | ~3,500 | **Complete** |
| Phase 5 | Miscellaneous | ~700 | **Complete** |

## Completed Work

### Phase 1: Mnemonic Renames (Complete — March 2026)

81 wrapper mnemonics renamed to semantic forms across 53,603 instruction instances:

| Old | New | Category |
|-----|-----|----------|
| `push_sr` | `push sr` | Status register push/pop |
| `pop_sr` | `pop sr` | |
| `ld8_24` | `ldb_da` | Direct address loads |
| `st8_24` | `stb_da` | Direct address stores |
| `sti8_24` | `stib_da` | Direct address immediate stores |
| `ldto_berp` | `stb_erp` | Extended register pair |
| `ldfr_berp` | `ldb_erp` | |
| `st_dri3b` | `stb_dri` | Displacement register indirect |
| ... | ... | (81 total) |

### Phase 1b: Parenthesized Direct Address Syntax (Complete — March 2026)

Added `directaddr` operand class to LLVM backend. All 61,436 direct address operands across 155 `.s` files now use parenthesized syntax:

| Before | After |
|--------|-------|
| `ldb_da a, 0xe12345` | `ldb_da a, (0xe12345)` |
| `stw_da 0xe12345, wa` | `stw_da (0xe12345), wa` |
| `cpw_da 0x3ef50, 0` | `cpw_da (0x3ef50), 0` |
| `incdi8_24 1, 0xcee5` | `incdi8_24 1, (0xcee5)` |
| `bitda_24 3, 0xe12345` | `bitda_24 3, (0xe12345)` |

Changes:
- `TLCS900InstrInfo.td` — 167 instruction definitions updated to use `directaddr` operand class
- `TLCS900AsmParser.cpp` — Added `parseDirectAddrOperand()` for `(expr)` syntax
- `TLCS900InstPrinter.cpp` — Added `printDirectAddr()` to wrap output in parentheses
- Both old (bare) and new (parenthesized) syntax accepted for backward compatibility

## Phases 2-5 (Complete)

These tables record the mnemonics as originally scoped. Every wrapper
mnemonic listed in them has zero occurrences left in the KN5000 or SX-WSA1R
trees; the semantic replacement shapes were not individually re-audited
here, so read these as "what was migrated away from," not as a live
inventory of current mnemonics.

### Phase 2: 24-bit Addressing Mode Semantics (~1,700 instances)

| Current | Semantic | Count | Status |
|---------|----------|-------|--------|
| `ld16_24 reg, addr` | `ld reg, (addr24)` | 645 | Complete |
| `ld32_24 reg, addr` | `ld reg, (addr24)` | 161 | Complete |
| `st16_24 addr, reg` | `ld (addr24), reg` | 252 | Complete |
| `st32_24 addr, reg` | `ld (addr24), reg` | 139 | Complete |
| `sti16_24 addr, imm` | `ld (addr24), imm16` | 209 | Complete |
| `cpi8_24 addr, imm` | `cp (addr24), imm8` | 63 | Complete |
| `cpdi16_24 addr, imm` | `cp (addr24), imm16` | 120 | Complete |

### Phase 3: Extended Register Pair Modes (~3,300 instances)

| Current | Semantic | Count | Status |
|---------|----------|-------|--------|
| `ldto_berp` | `ld (erp+off), val` | 1,251 | Complete |
| `ldfr_berp` | `ld val, (erp+off)` | 597 | Complete |
| `ldto_werp` | `ld (erp+off), val` | 459 | Complete |
| `ldfr_werp` | `ld val, (erp+off)` | 221 | Complete |
| `ldi_berp` | `ld (erp+off), imm` | 316 | Complete |
| `ldi_werp` | `ld (erp+off), imm` | 281 | Complete |
| `push_werp` / `pop_werp` | `push (erp)` / `pop (erp)` | 325 | Complete |
| `cpi_berp` / `cpi_werp` | `cp (erp+off), imm` | 260 | Complete |
| `inc1_berp` / `inc1_werp` | `inc 1, (erp+off)` | 281 | Complete |
| `cp_werp` / `cp_srib_im` | `cp (erp), val` | 184 | Complete |

### Phase 4: SRI/DRI Indirect Modes (~3,500 instances)

| Current | Semantic | Count | Status |
|---------|----------|-------|--------|
| `st_dri3b/w/l` | `ld (reg+d16), val` | 2,105 | Complete |
| `ld_srib3` / `ld_sriw3` | `ld val, (reg+d16)` | 1,073 | Complete |
| `lda_dri3` | `lda reg, (reg+d16)` | 396 | Complete |
| `lda_dpi` | `lda reg, (reg+d16)` | 164 | Complete |
| `ld_spib` | `ld val, (xsp+d8)` | 129 | Complete |
| `jp_dri` | `jp (reg+d16)` | 240 | Complete |
| `stib_dri` / `stib_dpi` | `ld (reg+d16), imm` | 326 | Complete |
| `st_dpiw` / `stiw_dri` | `ld (reg+d16), imm16` | 120 | Complete |
| `bit_dri` | `bit n, (reg+d16)` | 68 | Complete |

### Phase 5: Miscellaneous (~700 instances)

| Current | Semantic | Count | Status |
|---------|----------|-------|--------|
| `ld_srib` / `ld_sriw` | `ld val, (reg)` | 341 | Complete |
| `mrid2` | Various | 48 | Complete |
| `ldada` / `ldda8` / `stda8` | `ld` with direct addressing | ~200 | Complete |
| `addm32_24` / `addmi16` / etc. | `add (addr), imm` | ~100 | Complete |

## Architecture

The LLVM TLCS-900 backend lives at `/home/fsanches/compartilhado/llvm-project/llvm/lib/Target/TLCS900/`.

**Key files** (line counts re-checked 2026-09-01):
- `TLCS900InstrFormats.td` — 83 instruction format class definitions (1,093 lines; was 79 formats when this page was first written)
- `TLCS900InstrInfo.td` — 5,521 lines of instruction definitions
- `TLCS900BaseInfo.h` — TSFlags bit-field definitions (283 lines)
- `AsmParser/TLCS900AsmParser.cpp` — 569 lines, including the direct-address width-request parser (see below)
- `MCTargetDesc/TLCS900MCCodeEmitter.cpp` — 1,631 lines, manual encoding
- `Disassembler/TLCS900Disassembler.cpp` — 2,459 lines, manual decoding

**Encoding strategy:** The backend uses manual encoding via a giant `switch(Format)` in `MCCodeEmitter::encodeInstruction()`, NOT auto-generated TableGen encoding. Each of the 83 format classes has a dedicated switch case that emits bytes using TSFlags metadata.

**TSFlags layout (32 bits, unchanged since this page was written):**
```
[6:0]   InstFormat  — selects encoding strategy (83 values in use; field holds up to 128)
[14:7]  Opcode      — primary prefix/opcode byte
[16:15] OpSize      — 0=8-bit, 1=16-bit, 2=32-bit
[17]    AddrWidth   — 0=16-bit addr, 1=24-bit addr
[20:18] RegIdx      — block transfer register index
[28:21] SubOpcode   — secondary operation byte
[31:29] NumPreOps   — pre-SubOpcode operand count
```

## Direct-address width-request syntax (new since this page's last major revision)

A direct-address operand now takes an optional explicit width suffix —
`(0x8a:8)`, `(0x2075:16)`, `(0x8a:24)` — parsed by
`parseDirectAddrOperand()` in `AsmParser/TLCS900AsmParser.cpp`. The TLCS-900
has three direct-address widths and picks between them in the prefix byte, so
the width is a spelling choice the source has to make: this firmware writes
`set 7,(0x00008a)` as `F2 8A 00 00 BF` for an address that fits in eight
bits, so the width is **not derivable from the address value alone**. An
operand with no suffix keeps the 24-bit default, which is why code that
already assembled before the suffix existed did not need to change.

## Silent miscompiles found and fixed in this backend

Three encodings assembled to the **wrong bytes with no diagnostic** before
being caught and fixed (LLVM `tlcs900_backend`, commits `e7a43c67fdca` and
`95f7f2d40428`, both 2026-09-01):

- `push (0x1234)` emitted `09 34` — the address silently truncated to 8 bits.
- `mul WA,(0x1234)` emitted `d8 08 34 12` — a multiply by the *address*, not
  the memory operand, because neither mnemonic had a memory form and the
  parenthesised address was parsed as an immediate.
- The 8-bit **INDEX register**'s file address was emitted with its high/low
  halves swapped (`A=0xE1` instead of the correct `A=0xE0`). The byte gate
  had stayed green because all four call sites in the KN5000/WSA1 trees
  happened to name the wrong register to get the right byte.

All three are now diagnosed or fixed rather than silently mis-encoded; see
`llvm-project`'s `TOOLCHAIN_VERSION` file (UPDATE 8/9) for the full writeups
and verification (`make gate-all` across the KN5000 and SX-WSA1R ROM sets).

## Process for Each Phase

1. **Define new instruction in `.td`** with semantic mnemonic and proper operand types
2. **Add encoding case** in `MCCodeEmitter.cpp` (or reuse existing format)
3. **Add decoding case** in `TLCS900Disassembler.cpp` to emit semantic mnemonic
4. **Build LLVM:** `ninja -C /home/fsanches/compartilhado/llvm-project/build llc llvm-mc`
5. **Update all `.s` files** in both v9 and v10 (Python script with binary I/O)
6. **Rebuild ROMs:** verify 100% byte-match
7. **Run LLVM tests:** `build/bin/llvm-lit llvm/test/CodeGen/TLCS900/`

## See Also

- [TLCS-900 Instruction Encoding]({{ site.baseurl }}/tlcs900-instruction-encoding/) — Hardware instruction format reference
- [ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) — Disassembly progress
- [Source Code Map]({{ site.baseurl }}/source-map/) — Guide to every source file
