---
layout: page
title: TLCS-900/H Instruction Encoding Reference
permalink: /tlcs900-instruction-encoding/
---

# TLCS-900/H Instruction Encoding Reference

This page documents the instruction encoding format of the Toshiba TLCS-900/H2 CPU (TMP94C241F) as used in the Technics KN5000. This reference was built through systematic reverse engineering of the KN5000 firmware ROMs and verification against both the MAME disassembler (`unidasm`) and our custom LLVM TLCS-900 backend.

## Overview

TLCS-900/H instructions are variable-length (1–7 bytes) using a prefix-based encoding system. The first byte determines the instruction category, operand size, and addressing mode. Subsequent bytes encode the operation (sub-opcode), register operands, displacements, and immediates.

## Register Encoding

All register classes share a consistent 3-bit encoding (0–7):

| Enc | 8-bit | 16-bit | 32-bit (GPR) | Address Reg | Q Reg (PrevBank) |
|-----|-------|--------|--------------|-------------|------------------|
| 0   | W     | WA     | XWA          | XWA         | QWA              |
| 1   | A     | BC     | XBC          | XBC         | QBC              |
| 2   | B     | DE     | XDE          | XDE         | QDE              |
| 3   | C     | HL     | XHL          | XHL         | QHL              |
| 4   | D     | IX     | XIX          | XIX         | QIX              |
| 5   | E     | IY     | XIY          | XIY         | QIY              |
| 6   | H     | IZ     | XIZ          | XIZ         | QIZ              |
| 7   | L     | SP     | XSP          | XSP         | QSP              |

**Note:** SP (enc=7) is not a member of the GR8 or GR16 register classes. Instructions that specify a GR8/GR16 operand cannot use SP/L as the operand.

## Instruction Format Categories

### 1. Compact 32-bit Immediate Loads (0x40–0x47)

5-byte instructions that load a 32-bit immediate into a GPR register.

```
Byte:   [0x40+R] [imm_lo] [imm_b1] [imm_b2] [imm_hi]
```

- `R` = register encoding (0–7)
- Immediate is 32 bits, little-endian

Example: `ld xbc, 0x01E0007F` → `41 7F 00 E0 01`

### 2. Register Source Prefix (0xC8–0xEF)

2-byte minimum instructions where the first byte encodes a source register and operand size, and the second byte is a sub-opcode that determines the operation and destination.

```
Byte:   [prefix] [sub_opc]
```

| Prefix Range | Operand Size | Source Register |
|-------------|-------------|-----------------|
| 0xC8–0xCF   | 8-bit       | R = prefix − 0xC8 |
| 0xD8–0xDF   | 16-bit      | R = prefix − 0xD8 |
| 0xE8–0xEF   | 32-bit      | R = prefix − 0xE8 |

#### Register-to-Register Sub-Opcode Table

The sub-opcode byte encodes both the operation and the destination register:

| Sub-Opc Range | Operation | Format | Direction |
|--------------|-----------|--------|-----------|
| 0x04         | PUSH r    | Unary (16-bit only) | — |
| 0x05         | POP r     | Unary (16-bit only) | — |
| 0x06         | CPL r     | Unary | — |
| 0x07         | NEG r     | Unary | — |
| 0x12         | EXTZ r    | Unary (16-bit only) | — |
| 0x13         | EXTS r    | Unary (16-bit only) | — |
| 0x20+d       | LD d, r   | LD to register | d ← r |
| 0x28+d       | LD r, d   | LD from register (reverse) | r ← d |
| 0x40+d       | MUL d, r  | Multiply (16→32, uses GPR names) | — |
| 0x48+d       | MULS d, r | Multiply signed | — |
| 0x50+d       | DIV d, r  | Divide (32/16, uses GPR names) | — |
| 0x58+d       | DIVS d, r | Divide signed | — |
| 0x60+n       | INC n, r  | Increment by n (1–7) | — |
| 0x68+n       | DEC n, r  | Decrement by n (1–7) | — |
| 0x78+cc      | SCC cc, r | Set if condition code | — |
| 0x80+d       | ADD d, r  | Add | d ← d + r |
| 0x88+d       | LD d, r   | Load (alternate encoding) | d ← r |
| 0x90+d       | ADC d, r  | Add with carry | d ← d + r + C |
| 0x98+d       | LD r, d   | Load reverse | r ← d |
| 0xA0+d       | SUB d, r  | Subtract | d ← d − r |
| 0xA8+n       | LDS r, n  | Load small immediate (0–7) | r ← n |
| 0xB0+d       | SBC d, r  | Subtract with borrow | d ← d − r − C |
| 0xC0+d       | AND d, r  | Bitwise AND | d ← d & r |
| 0xD0+d       | XOR d, r  | Bitwise XOR | d ← d ^ r |
| 0xD8+n       | CPS r, n  | Compare small immediate (0–7) | r − n |
| 0xE0+d       | OR d, r   | Bitwise OR | d ← d \| r |
| 0xF0+d       | CP d, r   | Compare | d − r |

Where `d` = destination register encoding (3 bits), `r` = source register from prefix, `n` = small immediate (3 bits), `cc` = condition code (4 bits).

**LD encoding note:** Two encodings exist for register-to-register LD: sub-opcode 0x88+d and 0x20+d (for `LD d, r`), and 0x98+d and 0x28+d (for `LD r, d`). Both forms are semantically identical but produce different byte sequences. The LLVM assembler always uses the 0x88/0x20 forms.

#### Register Prefix + Immediate

When the sub-opcode indicates an immediate operand, additional bytes follow:

```
Byte:   [prefix] [sub_opc] [imm_bytes...]
```

| Sub-Opc | Operation | Imm Size (8-bit/16-bit/32-bit prefix) |
|---------|-----------|--------------------------------------|
| 0x03    | LD r, #imm | 1 / 2 / 4 bytes |
| 0xC8    | ADD r, #imm | 1 / 2 / 4 bytes |
| 0xC9    | ADC r, #imm | 1 / 2 / 4 bytes |
| 0xCA    | SUB r, #imm | 1 / 2 / 4 bytes |
| 0xCB    | SBC r, #imm | 1 / 2 / 4 bytes |
| 0xCC    | AND r, #imm | 1 / 2 / 4 bytes |
| 0xCD    | XOR r, #imm | 1 / 2 / 4 bytes |
| 0xCE    | OR r, #imm | 1 / 2 / 4 bytes |
| 0xCF    | CP r, #imm | 1 / 2 / 4 bytes |

**Shift/rotate sub-opcodes** (1-byte immediate count):

| Sub-Opc | Operation |
|---------|-----------|
| 0xE8    | RLC count, r |
| 0xE9    | RRC count, r |
| 0xEA    | RL count, r |
| 0xEB    | RR count, r |
| 0xEC    | SLA count, r |
| 0xED    | SRA count, r |
| 0xEE    | SLL count, r |
| 0xEF    | SRL count, r |

**BIT operations** (16-bit prefix only, 1-byte bit number):

| Sub-Opc | Operation |
|---------|-----------|
| 0x30    | RES bit, r |
| 0x31    | SET bit, r |
| 0x33    | BIT bit, r |

### 3. Compact Source Addressing Modes (0x80–0xAF)

These prefixes specify a memory source operand with the operand size and addressing mode encoded in the prefix byte:

| Prefix Range | Size | Addressing Mode | Additional Bytes |
|-------------|------|-----------------|-----------------|
| 0x80+R      | 8-bit  | (R) register indirect | sub_opc |
| 0x88+R      | 8-bit  | (R+d8) reg + displacement | d8, sub_opc |
| 0x90+R      | 16-bit | (R) register indirect | sub_opc |
| 0x98+R      | 16-bit | (R+d8) reg + displacement | d8, sub_opc |
| 0xA0+R      | 32-bit | (R) register indirect | sub_opc |
| 0xA8+R      | 32-bit | (R+d8) reg + displacement | d8, sub_opc |
| 0xB0+R      | 32-bit | (R+d16) reg + 16-bit displacement | d16_lo, d16_hi, sub_opc |

Where `R` = address register encoding (0–7, mapped to XWA–XSP).

The sub-opcode table is the **same** as for register source prefix instructions (0x20+d = LD, 0x80+d = ADD, etc.), except the source is a memory location instead of a register.

### 4. Compact Destination Addressing Mode (0xB8–0xBF)

Encodes stores to memory and LDA (load effective address):

```
Byte:   [0xB8+R] [d8] [sub_opc] [optional_imm...]
```

| Sub-Opc Range | Operation |
|--------------|-----------|
| 0x30+d       | LDA d, (R+d8) — load effective address |
| 0x50+s       | LD (R+d8), reg16 — store 16-bit register |
| 0x60+s       | LD (R+d8), reg32 — store 32-bit register |

### 5. Extended Addressing Modes (0xC0–0xF7)

The first byte encodes both operand size and addressing mode:

| Prefix     | Size   | Mode | Addressing | Bytes After Prefix |
|-----------|--------|------|------------|-------------------|
| 0xC0–0xC7 | 8-bit  | 0–7  | See below  | Varies |
| 0xD0–0xD7 | 16-bit | 0–7  | See below  | Varies |
| 0xE0–0xE7 | 32-bit | 0–7  | See below  | Varies |
| 0xF0–0xF7 | Store  | 0–7  | See below  | Varies |

**Mode encoding (low 3 bits of prefix):**

| Mode | Addressing | Data After Prefix |
|------|-----------|-------------------|
| 0    | (R) register indirect | reg_byte, sub_opc |
| 1    | (R+d8) reg indirect + 8-bit disp | reg_byte, d8, sub_opc |
| 2    | (addr24) direct 24-bit address | addr_lo, addr_mid, addr_hi, sub_opc |
| 3    | (R+d16) reg indirect + 16-bit disp | reg_byte, d16_lo, d16_hi, sub_opc |
| 4    | (−R) predecrement | reg_byte, sub_opc |
| 5    | (R+) postincrement | reg_byte, sub_opc |
| 7    | Previous bank (D7 only) | mode_byte, sub_opc [, imm...] |

**Register byte encoding** (for modes 0, 1, 3, 4, 5):
```
reg_byte = 0xE0 + (register_enc × 4) + inner_mode
```

The `inner_mode` field provides additional addressing information.

### 6. Previous Register Bank (0xD7)

Accesses the previous register bank using Q registers (QWA–QSP):

```
Byte:   0xD7 [mode_byte] [sub_opc] [optional_imm...]
```

Mode byte encoding: `0xE0 + (reg_enc × 4) + 2`

| Mode Byte | Q Register |
|-----------|-----------|
| 0xE2      | QWA       |
| 0xE6      | QBC       |
| 0xEA      | QDE       |
| 0xEE      | QHL       |
| 0xF2      | QIX       |
| 0xF6      | QIY       |
| 0xFA      | QIZ       |
| 0xFE      | QSP       |

Sub-opcode table same as register source prefix, plus additional formats for BIT/SET/RES, LD/CP with word immediate, and LDW/CPW.

## LLVM Backend Support Status

As of February 2026, the following summarizes what the custom LLVM TLCS-900 backend supports for assembly (llvm-mc):

### Fully Supported

| Category | Notes |
|----------|-------|
| Register-to-register ALU | ADD, SUB, ADC, SBC, AND, XOR, OR, CP |
| Register-to-register LD | Both 0x88 and 0x20 forms |
| Register prefix + immediate ALU | ADD/SUB/CP/AND/OR/XOR/ADC/SBC with 8/16/32-bit imm |
| Register prefix + immediate LD | 8-bit and 16-bit (32-bit uses compact form) |
| BIT/SET/RES with 16-bit register | Via register prefix |
| PUSH/POP (16-bit register) | Via register prefix |
| NEG/CPL (16-bit register) | Via register prefix |
| EXTS/EXTZ (16-bit register) | Via register prefix |
| INC/DEC with count (1–7) | Via register prefix |
| MUL/MULS/DIV/DIVS (reg-reg) | Uses GPR (32-bit) register names |
| SCC condition code set | 8-bit and 16-bit |
| Compact 32-bit immediate load | 0x40–0x47 |
| Compact (R) memory indirect | All sizes (8/16/32-bit) |
| Compact (R+d8) memory | All sizes, d8 must be 0–127 |
| LDA (load effective address) | d8 must be 0–127 |
| Memory store (R+d8) | reg16 and reg32, d8 must be 0–127 |
| Extended E2 direct memory load | 32-bit operand, 24-bit address |
| Extended F2 direct memory store | reg16 and reg32 stores |
| Previous bank (D7) operations | Full Q register support |
| LDS/LDS32/LDS8 small immediate | Register prefix form |
| CPS small immediate compare | All sizes |

### Not Supported (require .byte fallback)

| Category | Count in HDAE5000 | Notes |
|----------|------------------|-------|
| (R+d16) 16-bit displacement | ~1,100 | "Displacement too large" error |
| d8 range 128–255 | ~500 | LLVM treats displacement as signed |
| 16-bit direct memory load | ~474 | "Byte/word direct memory load not encodable" |
| Conditional call via register | ~516 | `call T, XHL` not supported |
| CALR (relative call) | ~355 | Requires label infrastructure |
| Shift/rotate operations | ~200 | SRL, SLA, SRA, RL, RR, RLC, RRC, SLL |
| MUL/DIV with immediate | ~18 | Not supported with immediate operand |
| MUL/DIV with memory operand | varies | Not supported |
| INC/DEC with memory operand | varies | Not supported |
| PUSH/POP with memory operand | varies | Not supported |
| LD (addr), #imm16 via F2 | ~422 | LLVM uses wrong sub-opcode (0x00 vs 0x02) |
| 8-bit/16-bit direct CP | varies | "Not encodable" |

### Known Encoding Issues

1. **Displacement is signed:** The 8-bit displacement in `(R+d8)` addressing modes is **signed** (range −128 to +127). This is confirmed by MAME's TLCS-900 emulator (`(int8_t)m_op` cast in `900tbl.hxx`). The LLVM backend correctly handles both positive and negative displacements. Example: `ld wa, (xsp-56)` produces byte `0xC8` for the displacement (−56 in two's complement).

2. **d8=0 optimization:** When displacement is 0, LLVM optimizes `(R+0)` to the shorter `(R)` form, producing different byte sequences than the firmware which uses explicit `(R+0)`.

3. **LD immediate to memory sub-opcode:** LLVM uses sub-opcode 0x00 for `LD (addr), #imm16` but the hardware encoding uses 0x02. This produces incorrect bytes.

4. **32-bit LD immediate always compact:** `LD XWA, #imm32` always uses the compact 5-byte form (0x40+R) rather than the 6-byte prefix form (E8+R, 0x03, imm32). Cannot reproduce the prefix form.

## Condition Codes

Used with SCC, JP, CALL, and other conditional instructions:

| Code | Value | Condition |
|------|-------|-----------|
| F    | 0     | False (never) |
| LT   | 1     | Less than (signed) |
| LE   | 2     | Less than or equal (signed) |
| ULE  | 3     | Unsigned less than or equal |
| OV   | 4     | Overflow |
| MI   | 5     | Minus (negative) |
| Z    | 6     | Zero |
| C    | 7     | Carry |
| T    | 8     | True (always) |
| GE   | 9     | Greater than or equal (signed) |
| GT   | 10    | Greater than (signed) |
| UGT  | 11    | Unsigned greater than |
| NOV  | 12    | No overflow |
| PL   | 13    | Plus (positive) |
| NZ   | 14    | Not zero |
| NC   | 15    | No carry |

## References

- [TMP94C241F Datasheet (Toshiba)](https://archive.org/details/tmp94c241f)
- [TLCS-900 Programming Manual](https://archive.org/details/tlcs900programmingmanual)
- [MAME TLCS-900 CPU core](https://github.com/mamedev/mame/tree/master/src/devices/cpu/tlcs900)
- [LLVM TLCS-900 Backend (custom)](https://github.com/ArqueologiaDigital/llvm-project)
