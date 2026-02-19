---
layout: page
title: "HDAE5000 Homebrew Development"
permalink: /hdae5000-homebrew/
---

# Writing Custom HDAE5000 Extension ROMs

The HD-AE5000 extension slot can run custom code on the KN5000's main CPU. By replacing the HDAE5000 ROM with a custom binary, you can create games, demos, or utilities that run on the keyboard hardware. This page documents the extension ROM protocol, known toolchain bugs, and a working build pipeline.

> **Status**: Boot initialization and frame handler callbacks are working. Handler registration with the firmware's dispatch system is not yet functional (see [Handler Registration](#handler-registration-prerequisites) below).

## Prerequisites

- **LLVM with TLCS-900 backend** -- a custom LLVM build with the TLCS-900 target
- **MAME** with KN5000 driver for testing
- Knowledge of the [HDAE5000 firmware protocol]({{ site.baseurl }}/hdae5000/)

## Extension ROM Protocol

### XAPR Header Format

The KN5000 firmware validates extension ROMs by checking for an "XAPR" magic string at address `0x280000`. The header occupies the first 32 bytes:

```
Offset  Size  Contents              Description
------  ----  --------------------  -----------
0x00    4     "XAPR"                Magic signature
0x04    4     34 A1 2F 00           Version/ID metadata
0x08    4     JP Boot_Init          Entry point 1: boot initialization
0x0C    4     RET + 3x NOP          Padding
0x10    4     JP Frame_Handler      Entry point 2: frame callback
0x14    4     RET + 3x NOP          Padding
0x18    4     RET + 3x NOP          Entry point 3: unused
0x1C    4     RET + 3x NOP          Entry point 4: unused
```

The `JP` instruction (opcode `0x1B`) is followed by a 24-bit little-endian target address.

### Firmware XAPR Validation

The main firmware validates the extension ROM and calls Boot_Init from routine `LABEL_F1E9E0`:

```asm
; At LABEL_F1E9E0 in kn5000_v10_program.rom:
PUSHW 0004h                          ; Compare 4 bytes
PUSHW 00e1h                          ; String compare flags
PUSHW 0ffc6h                         ; Pointer to "XAPR" in firmware ROM
LD    XWA, 00280000h                 ; Extension ROM base address
PUSH  XWA
CALL  String_Compare                 ; Compare first 4 bytes
ADD   XSP, 0000000ah                 ; Clean stack
CP    HL, 0                          ; Match?
JR    NZ, .no_extension              ; Skip if no match

LD    (03DD04h), 001h                ; Set XAPR detection flag

; ... fall through to call Boot_Init ...

LD    XHL, 00280008h                 ; Address of boot init entry point
LDA   XWA, 027ED2h                  ; Workspace pointer = 0x027ED2
CALL  T, XHL                        ; Call Boot_Init(XWA = workspace_ptr)
RET
```

The frame handler dispatcher (`LABEL_F1E9D0`) runs every iteration of the main event loop:

```asm
; Frame handler dispatcher:
CP    (03DD04h), 000h                ; Check XAPR detection flag
RET   Z                              ; Skip if no extension ROM
LD    XHL, 00280010h                 ; Address of frame handler entry point
CALL  T, XHL                        ; Call Frame_Handler()
RET
```

**Key observations:**
- The frame handler is called **unconditionally** every frame -- no registration needed
- The XAPR detection flag at `0x03DD04` is the only gate
- Hardware presence is checked separately via Port E bit 0 (active low)

### Workspace Pointer

The firmware passes `0x027ED2` in XWA to Boot_Init. This is the base address of the firmware's **object table** in main DRAM -- a data structure with 14-byte entries spanning from `0x027ED2` to `0x02BC12` (~1,118 entries).

The workspace provides access to the firmware's callback dispatch system via pointer chains:

```
Workspace (0x027ED2)
    |
    +-- offset +0x0E0A --> Handler Table A pointer
    |                        |
    |                        +-- offset +0x00E4 --> Handler registration function
    |                        +-- offset +0x02C4 --> Callback registration function
    |                        +-- offset +0x0124 --> Display callback function
    |                        +-- offset +0x0244, +0x0248, +0x024C --> UI callbacks
    |
    +-- offset +0x0E88 --> Handler Table B pointer
                             |
                             +-- offset +0x0100 --> Init function 2
                             +-- offset +0x0104 --> Init function 3
                             +-- offset +0x0108 --> Init function 1
```

Both handler tables are in main DRAM (0x000000-0x0FFFFF range). The values at these offsets are function pointers into the firmware ROM.

### Boot_Init Calling Convention

```
Entry:
  XWA = workspace pointer (0x027ED2)

Expected behavior:
  Store workspace pointer for later use
  Perform initialization
  Return (RET) to firmware

Notes:
  Must preserve stack state (firmware continues initialization after return)
  Extension RAM at 0x200000-0x27FFFF is available for variables
  Extension ROM at 0x280000-0x2FFFFF is available for code and data
```

### Frame_Handler Calling Convention

```
Entry:
  No parameters (called from firmware main loop)

Expected behavior:
  Perform per-frame updates (display, input, etc.)
  Return (RET) to firmware

Notes:
  Called every main loop iteration while XAPR flag (0x03DD04) is set
  Should be fast -- firmware main loop handles other subsystems too
  All registers should be preserved or restored
```

## Handler Registration Prerequisites

The original HDAE5000 firmware performs extensive setup before calling the callback registration function at `workspace[0x0E0A][0x02C4]`:

1. **Clear work buffer** -- 62,762 bytes zeroed at `0x22A000`
2. **Copy init data** -- 3,202 bytes from ROM to `0x23952A`
3. **Register 12 handlers** -- via `workspace[0x0E0A][0x00E4]` (a *different* function than `0x02C4`)
4. **Load VGA palette** -- 256 entries from ROM
5. **Allocate DRAM and copy VRAM** -- 76,800 bytes to display areas
6. *Then* **call `workspace[0x0E0A][0x02C4]`** -- the callback registration function

**Current finding:** Calling `workspace[0x0E0A][0x02C4]` without performing steps 1-5 first causes a crash. The registration function likely depends on state established by the 12-handler registration at offset `0x00E4`. This is an area of ongoing investigation.

For basic operation, handler registration is **not required**. The firmware calls the Frame_Handler entry point every frame regardless. Handler registration is only needed for DISK MENU integration (displaying an icon and responding to user selection).

## LLVM TLCS-900 Assembler Encoding Bugs

The LLVM TLCS-900 assembler backend has several encoding bugs that produce invalid machine code. These affect any project using LLVM to target the TLCS-900 architecture.

### Bug 1: Direct Memory Load Prefix

**Instruction:** `ld reg, (addr)` (load from absolute address)

**Bug:** LLVM uses the `F2` prefix (F0/store group) instead of `E2` (E0/load group). In the F0 sub-opcode table, entry `0x26` is `LDA` (load address), not `LD` (load data) as in the E0 table.

**Workaround:**
```asm
; Instead of: ld xwa, (0x200008)     -- BROKEN
ld   xhl, 0x200008                    ; load address into register
ld   xwa, (xhl)                       ; then dereference
```

### Bug 2: Immediate-to-Memory Store Sub-opcode

**Instruction:** `ld (addr), imm32` (store immediate to absolute address)

**Bug:** LLVM emits sub-opcode `0x08` in the F0 table, which does not exist on the TLCS-900. The hardware only supports `0x00` (byte immediate) and `0x02` (word immediate) -- there is no 32-bit immediate-to-memory store.

**Workaround:**
```asm
; Instead of: ld (0x200000), 0x100   -- BROKEN
ld   xde, 0x200000                    ; load address
ld   xwa, 0x00000100                  ; load value
ld   (xde), xwa                       ; store via register-indirect
```

### Bug 3: Indirect CALL Sub-opcode

**Instruction:** `call (xreg)` (call function at address in register)

**Bug:** LLVM emits sub-opcode `0x1F` in the b0 table, which is undefined on the TLCS-900. The correct encoding for an unconditional call is `0xE8` (CALL T, where T = True = condition code 8). CALL entries occupy `0xE0-0xEF` in the b0 table, one per condition code.

**Workaround:**
```asm
; Instead of: call (xix)             -- BROKEN (emits 0x1F)
.byte 0xB4, 0xE8                      ; B4 = XIX prefix, E8 = CALL T

; Register prefix bytes for indirect CALL:
;   B0 = XWA, B1 = XBC, B2 = XDE, B3 = XHL
;   B4 = XIX, B5 = XIY, B6 = XIZ, B7 = XSP
```

### Bug 4: JP Opcode (Fixed in LLVM Backend)

**Instruction:** `jp target` (unconditional jump)

**Bug:** LLVM originally encoded JP as opcode `0x1C`, which is actually `CALL I16` (call with 16-bit address) on the real hardware. This was fixed in the LLVM backend to use the correct opcode `0x1B` (JP I24, jump with 24-bit address).

### Bug 5: Register+Displacement Loads

**Instruction:** `ld xreg, (xreg + disp)` (load from register + displacement)

**Bug:** LLVM does not support encoding register+displacement loads. This was initially believed to be a hardware limitation, but the original HDAE5000 ROM uses instructions like `ld XWA, (XWA + 0x0E0A)` successfully -- confirming the hardware *does* support this addressing mode. Stores with displacement (`ld (xreg + disp), src`) work correctly in LLVM.

**Workaround:**
```asm
; Instead of: ld xiz, (xiz + 0x0E0A)  -- NOT SUPPORTED
add  xiz, 0x0E0A                       ; modify register (destructive)
ld   xiz, (xiz)                        ; then dereference
```

### TLCS-900 Opcode Reference for Workarounds

Understanding the opcode table structure helps when crafting raw `.byte` workarounds:

| Prefix Range | Table | Purpose |
|-------------|-------|---------|
| A0-A7 | a0/e0 | Source register indirect (loads) |
| B0-B7 | b0 | Destination register indirect (stores, CALL, JP) |
| B8-BF | b0 + 8-bit displacement | Register indirect + displacement |
| E0-E5 | e0 | Direct memory addressing (loads) |
| F0-F5 | f0 | Direct memory addressing (stores) |

Key b0 sub-opcodes:

| Range | Operation |
|-------|-----------|
| 0x40-0x47 | LD (M), C8 -- store 8-bit register |
| 0x50-0x57 | LD (M), C16 -- store 16-bit register |
| 0x60-0x67 | LD (M), C32 -- store 32-bit register |
| 0xD0-0xDF | JP cc, (M) -- conditional jump indirect |
| 0xE0-0xEF | CALL cc, (M) -- conditional call indirect |

Register indices (for prefixes and sub-opcodes):

| Index | 32-bit | 16-bit | 8-bit |
|-------|--------|--------|-------|
| 0 | XWA | WA | A |
| 1 | XBC | BC | C |
| 2 | XDE | DE | E |
| 3 | XHL | HL | L |
| 4 | XIX | IX | - |
| 5 | XIY | IY | - |
| 6 | XIZ | IZ | - |
| 7 | XSP | SP | - |

## Build Pipeline

The build uses a pure LLVM toolchain:

```
C sources --> clang (-emit-llvm) --> .ll files
                                        |
                                        v
                            llvm-link (merge) --> merged.ll
                                                     |
                                                     v
                                    llc (-filetype=obj) --> all_c.o
                                                               |
startup.s --> clang -c --> startup.o                           |
                              |                                |
                              v                                v
                     ld.lld (linker script) --> ELF
                                                |
                                                v
                              llvm-objcopy -O binary --> raw ROM
                                                           |
                                                           v
                                               dd pad --> 512KB ROM
```

### Linker Script

The linker script places code and data in the extension ROM address space:

```
MEMORY {
  ROM (rx)  : ORIGIN = 0x280000, LENGTH = 512K
  RAM (rwx) : ORIGIN = 0x200000, LENGTH = 12K
}
SECTIONS {
  .startup 0x280000 : { startup.o(.startup) } > ROM
  .text             : { all_c.o(.text) } > ROM
  .rodata           : { *(.rodata*) } > ROM
  .data             : { *(.data*) } > RAM AT > ROM
  .bss              : { *(.bss*) } > RAM
}
```

### Minimal Startup Assembly

A minimal working extension ROM needs only a header, Boot_Init, and Frame_Handler:

```asm
.section .startup, "ax", @progbits

; XAPR Header
    .ascii  "XAPR"
    .byte   0x34, 0xA1, 0x2F, 0x00

; Entry Point 1: Boot_Init (offset 0x08)
    jp      Boot_Init
    ret
    .byte   0x00, 0x00, 0x00

; Entry Point 2: Frame_Handler (offset 0x10)
    jp      Frame_Handler
    ret
    .byte   0x00, 0x00, 0x00

; Entry Points 3-4: Unused
    ret
    .byte   0x00, 0x00, 0x00
    ret
    .byte   0x00, 0x00, 0x00

; Boot_Init: called once with XWA = workspace pointer (0x027ED2)
Boot_Init:
    push    xde
    ld      xde, 0x200000           ; extension RAM
    ld      (xde), xwa              ; store workspace pointer
    pop     xde
    ret

; Frame_Handler: called every frame by firmware
Frame_Handler:
    ; Your per-frame code here
    ret
```

## Memory Map for Custom ROMs

| Address Range | Size | Region | Use |
|--------------|------|--------|-----|
| 0x200000-0x27FFFF | 256KB | Extension RAM | Variables, stack, heap |
| 0x280000-0x2FFFFF | 512KB | Extension ROM | Code, read-only data |
| 0x1A0000-0x1DFFFF | 256KB | Video RAM | 320x240 8bpp display |
| 0x1703C8-0x1703C9 | 2B | VGA DAC | Palette index and RGB data |

The KN5000's LCD is 320x240 pixels at 8 bits per pixel (256-color indexed palette). VRAM starts at `0x1A0000` with a linear framebuffer layout (row-major, 320 bytes per row).

## Testing with MAME

Install your ROM as the HDAE5000 extension:

```bash
# Copy to MAME ROM set
cp your_rom.bin rompath/kn5000/hd-ae5000_v2_06i.ic4

# Run with extension enabled
mame kn5000 -rompath rompath -extension hdae5000 -window -oslog
```

The `-oslog` flag captures debug output, including any invalid instruction reports from the TLCS-900 CPU emulation.

## Related Pages

- [HDAE5000 Hard Disk Expansion]({{ site.baseurl }}/hdae5000/) -- Original firmware documentation
- [Memory Map]({{ site.baseurl }}/memory-map/) -- Full system address space
- [Boot Sequence]({{ site.baseurl }}/boot-sequence/) -- System startup and XAPR validation
- [Another World VM]({{ site.baseurl }}/another-world-vm/) -- Another homebrew project for the KN5000
