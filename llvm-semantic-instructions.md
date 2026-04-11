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

| Phase | Description | Instances | Status |
|-------|-------------|-----------|--------|
| Phase 1 | Mnemonic renames (81 mnemonics) | 53,603 | **Complete** |
| Phase 1b | Parenthesized direct addresses | 61,436 | **Complete** |
| Phase 2 | 24-bit addressing semantics | ~1,700 | In progress |
| Phase 3 | Extended register pair modes | ~3,300 | Planned |
| Phase 4 | SRI/DRI indirect modes | ~3,500 | Planned |
| Phase 5 | Miscellaneous | ~700 | Planned |

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

## Remaining Phases

### Phase 2: 24-bit Addressing Mode Semantics (~1,700 instances)

| Current | Semantic | Count | Status |
|---------|----------|-------|--------|
| `ld16_24 reg, addr` | `ld reg, (addr24)` | 645 | Pending |
| `ld32_24 reg, addr` | `ld reg, (addr24)` | 161 | Pending |
| `st16_24 addr, reg` | `ld (addr24), reg` | 252 | Pending |
| `st32_24 addr, reg` | `ld (addr24), reg` | 139 | Pending |
| `sti16_24 addr, imm` | `ld (addr24), imm16` | 209 | Pending |
| `cpi8_24 addr, imm` | `cp (addr24), imm8` | 63 | Pending |
| `cpdi16_24 addr, imm` | `cp (addr24), imm16` | 120 | Pending |

### Phase 3: Extended Register Pair Modes (~3,300 instances)

| Current | Semantic | Count | Status |
|---------|----------|-------|--------|
| `ldto_berp` | `ld (erp+off), val` | 1,251 | Pending |
| `ldfr_berp` | `ld val, (erp+off)` | 597 | Pending |
| `ldto_werp` | `ld (erp+off), val` | 459 | Pending |
| `ldfr_werp` | `ld val, (erp+off)` | 221 | Pending |
| `ldi_berp` | `ld (erp+off), imm` | 316 | Pending |
| `ldi_werp` | `ld (erp+off), imm` | 281 | Pending |
| `push_werp` / `pop_werp` | `push (erp)` / `pop (erp)` | 325 | Pending |
| `cpi_berp` / `cpi_werp` | `cp (erp+off), imm` | 260 | Pending |
| `inc1_berp` / `inc1_werp` | `inc 1, (erp+off)` | 281 | Pending |
| `cp_werp` / `cp_srib_im` | `cp (erp), val` | 184 | Pending |

### Phase 4: SRI/DRI Indirect Modes (~3,500 instances)

| Current | Semantic | Count | Status |
|---------|----------|-------|--------|
| `st_dri3b/w/l` | `ld (reg+d16), val` | 2,105 | Pending |
| `ld_srib3` / `ld_sriw3` | `ld val, (reg+d16)` | 1,073 | Pending |
| `lda_dri3` | `lda reg, (reg+d16)` | 396 | Pending |
| `lda_dpi` | `lda reg, (reg+d16)` | 164 | Pending |
| `ld_spib` | `ld val, (xsp+d8)` | 129 | Pending |
| `jp_dri` | `jp (reg+d16)` | 240 | Pending |
| `stib_dri` / `stib_dpi` | `ld (reg+d16), imm` | 326 | Pending |
| `st_dpiw` / `stiw_dri` | `ld (reg+d16), imm16` | 120 | Pending |
| `bit_dri` | `bit n, (reg+d16)` | 68 | Pending |

### Phase 5: Miscellaneous (~700 instances)

| Current | Semantic | Count | Status |
|---------|----------|-------|--------|
| `ld_srib` / `ld_sriw` | `ld val, (reg)` | 341 | Pending |
| `mrid2` | Various | 48 | Pending |
| `ldada` / `ldda8` / `stda8` | `ld` with direct addressing | ~200 | Pending |
| `addm32_24` / `addmi16` / etc. | `add (addr), imm` | ~100 | Pending |

## Architecture

The LLVM TLCS-900 backend lives at `/home/fsanches/compartilhado/llvm-project/llvm/lib/Target/TLCS900/`.

**Key files:**
- `TLCS900InstrFormats.td` — 79 instruction format class definitions
- `TLCS900InstrInfo.td` — ~5000 lines of instruction definitions
- `TLCS900BaseInfo.h` — TSFlags bit-field definitions
- `MCTargetDesc/TLCS900MCCodeEmitter.cpp` — 1500+ lines, manual encoding
- `Disassembler/TLCS900Disassembler.cpp` — 1000+ lines, manual decoding

**Encoding strategy:** The backend uses manual encoding via a giant `switch(Format)` in `MCCodeEmitter::encodeInstruction()`, NOT auto-generated TableGen encoding. Each of the 79 format classes has a dedicated switch case that emits bytes using TSFlags metadata.

**TSFlags layout (32 bits):**
```
[6:0]   InstFormat  — selects encoding strategy (79 values)
[14:7]  Opcode      — primary prefix/opcode byte
[16:15] OpSize      — 0=8-bit, 1=16-bit, 2=32-bit
[17]    AddrWidth   — 0=16-bit addr, 1=24-bit addr
[20:18] RegIdx      — block transfer register index
[28:21] SubOpcode   — secondary operation byte
[31:29] NumPreOps   — pre-SubOpcode operand count
```

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
