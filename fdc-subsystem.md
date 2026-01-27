---
layout: page
title: FDC Subsystem
permalink: /fdc-subsystem/
---

# Floppy Disk Controller Subsystem

This page documents the FDC (Floppy Disk Controller) handler routines from the KN5000 firmware. The FDC interfaces with a uPD72068GF-3B9 controller at IC208.

**Status:** Many routines are disassembled below but not yet integrated into the assembly source (still stored as raw bytes with EQU labels).

---

## SOME_DELAY Routine (0xF97612) - Timing Delay

The `SOME_DELAY` routine provides millisecond-scale timing delays used throughout FDC operations.

### Disassembly

```asm
SOME_DELAY:                 ; F97612
    SRL 1, WA               ; Divide WA by 2 (logical shift right)
    LD DE, (SYSTEM_TIMESTAMP) ; Snapshot current timestamp
    LD HL, 0                ; Initialize timeout counter
    CP HL, 0ffffh           ; Initial check (always passes)
    RET NC                  ; (never triggers on first pass)

LABEL_F97621:               ; Polling loop
    LD BC, (SYSTEM_TIMESTAMP) ; Read current timestamp
    SUB BC, DE              ; Elapsed = current - start
    CP BC, WA               ; Compare elapsed to target
    RET UGT                 ; Return if elapsed > target (delay complete)
    INC 1, HL               ; Increment timeout counter
    CP HL, 0ffffh           ; Check for timeout (65535 iterations)
    JR C, LABEL_F97621      ; Continue polling
    RET                     ; Timeout exit (safety)
```

### Operation

1. **Input**: WA register contains the delay duration
2. **Division**: WA is divided by 2 (so actual delay is half the input value in ticks)
3. **Timing**: Polls SYSTEM_TIMESTAMP until elapsed time exceeds target
4. **Safety**: Timeout exits after 65535 loop iterations to prevent hangs

### SYSTEM_TIMESTAMP Source

`SYSTEM_TIMESTAMP` (address 0x0409) is a 32-bit counter incremented by the Timer 1 interrupt handler (`INTT1_HANDLER` at 0xEF0BF9). The timer is configured during system initialization:

```asm
; Timer configuration at EF042D
LD (T01MOD), 01dh   ; Timer 0/1 mode: cascade mode, T32 source
LD (TREG0), 00ah    ; Timer 0 reload = 10
LD (TREG1), 010h    ; Timer 1 reload = 16
SET 1, (T8RUN)      ; Start Timer 1
```

Each `SYSTEM_TIMESTAMP` tick represents approximately **1 millisecond** based on the Timer 0/1 cascade configuration with the 20 MHz system clock.

### Delay Formula

```
Actual_delay_ms = WA / 2
```

### Common FDC Delay Values

| WA Value | Effective Delay | Usage Context |
|----------|-----------------|---------------|
| 2        | ~1 ms           | Brief settling (FDC_INIT, FDC_STATUS_HANDLER) |
| 10 (0x0A)| ~5 ms           | Hardware reset settle, FDC_CMD_ENABLE loop |
| 16 (0x10)| ~8 ms           | Status handler secondary delay |
| 200 (0xC8)| ~100 ms        | Motor spin-up, long operations |

### Usage in FDC Code

- **FDC_INIT (0xF96BBF)**: `WA=2` - 1ms delay after register setup
- **FDC_CONFIG_VERIFY**: `WA=2` - Settling delays between operations
- **FDC_STATUS_HANDLER**: `WA=2`, then `WA=0x10` - Status change delays
- **FDC_CMD_ENABLE loop (0xF97C40)**: `WA=0x0A` - 5ms delay per ready-check iteration
- **FDC Reset (0xF97ECF)**: `WA=0x0A` - Reset pulse timing

---

## FDC Memory Map

| Address | Size | Name | Description |
|---------|------|------|-------------|
| 0x8A10 | 2 | FDC_DRIVE_TYPE | Drive type identifier |
| 0x8A16 | 2 | FDC_STATUS_FLAG | Status/ready flag |
| 0x8A1C | 2 | FDC_SECTOR_COUNT | Sector count register |
| 0x8A1E | 2 | FDC_SECTOR_SIZE | Sector size (0x200 or 0x400) |
| 0x8A20 | 1 | FDC_INIT_FLAG | Initialization flag (0xFF=init done) |
| 0x8A24 | 1 | FDC_ERROR_CODE | Current error code |
| 0x8A26 | 1 | FDC_CACHED_STATUS | Cached status value |
| 0x8A28 | 1 | FDC_COMMAND_REG | Command register |
| 0x8A2B-8A36 | - | FDC_MODE_PARAMS | Mode configuration parameters |
| 0x8A40 | 2 | FDC_HANDLER_INDEX | Handler dispatch index |
| 0x8A44 | 2 | FDC_OUTPUT_MODE | Output control mode |
| 0x8A48 | 2 | FDC_TRACK_NUMBER | Current track number |
| 0x8A4A | 2 | FDC_TRANSFER_PTR | Data transfer pointer |
| 0x8A5C | 4 | FDC_XWA_SAVE | XWA register save area |
| 0x8A68 | 1 | FDC_OPERATION_MODE | Current operation mode |
| 0x8A6A | 1 | FDC_OUTPUT_FLAG | Output enable flag |
| 0x8A6C | 1 | FDC_DRIVE_MODE | Drive mode (0-5) |
| 0x8B00 | 1 | FDC_RESERVED_00 | Reserved |
| 0x8B04 | 1 | FDC_LAST_STATUS | Last known status |
| 0x8B0C | 2 | FDC_MAX_TRACK | Maximum track number |
| 0x8B10 | 2 | FDC_CURRENT_TRACK | Current track cache |

## Routine Addresses

| Address | Name | Description |
|---------|------|-------------|
| 0xF96BBF | FDC_INIT | Basic FDC initialization |
| 0xF96BD0 | FDC_CONFIG_VERIFY | Configuration and status verification |
| 0xF96D95 | FDC_CMD_DISPATCH_SUB | Command handler subroutine |
| 0xF97696 | FDC_STATUS_HANDLER | Status/interrupt handler |
| 0xF976E4 | FDC_CMD_EXEC | Command execution handler |
| 0xF97835 | FDC_SECTOR_XFER | Sector/data transfer handler |
| 0xF97984 | FDC_MODE_CONFIG | Mode configuration (Handler 5) |
| 0xF97C21 | FDC_CMD_ENABLE | Command enable setup |
| 0xF97C4B | FDC_CMD_DISABLE | Command disable |
| 0xF97C54 | FDC_STATUS_COPY | Copy cached status |
| 0xF97C5B | FDC_OUTPUT_CTRL | Output control |
| 0xF97C7C | FDC_INTERRUPT_HANDLER | Main interrupt handler |

## Helper Routine Addresses

| Address | Name | Description | Status |
|---------|------|-------------|--------|
| 0xF97612 | SOME_DELAY | Millisecond delay using SYSTEM_TIMESTAMP | **Documented** |
| 0xF97544 | LABEL_F97544 | FDC drive detection routine | Raw bytes |
| 0xF97592 | LABEL_F97592 | FDC drive status routine | Raw bytes |
| 0xF975AC | LABEL_F975AC | FDC pre-operation check | Raw bytes |
| 0xF975DC | LABEL_F975DC | FDC timing/delay routine | Raw bytes |
| 0xF975E2 | LABEL_F975E2 | FDC post-operation routine | Raw bytes |
| 0xF972F9 | LABEL_F972F9 | FDC command send routine | Raw bytes |
| 0xF974FE | LABEL_F974FE | FDC detection check routine | Raw bytes |

---

## Disassembled Routines

### FDC_INIT (0xF96BBF) - Basic FDC Initialization

Sets up FDC control register to 0xFF.

```asm
FDC_INIT:                   ; F96BBF
    LD WA, 0036h
    CALR LABEL_F96B1F
    LD WA, 2
    CALR SOME_DELAY
    LD (8B04h), 0FFh
    RET
```

### FDC_CONFIG_VERIFY (0xF96BD0) - Configuration/Status Verification

Complex routine that validates FDC status through multiple checks.

```asm
FDC_CONFIG_VERIFY:          ; F96BD0
    PUSH XIZ
    CALR LABEL_F975D6
    CALR LABEL_F97544
    CP HL, 0FFFFh
    JR Z, FDC_CONFIG_L1
    CALR LABEL_F97592
    CP HL, 0FFFFh
    JR Z, FDC_CONFIG_L1
    LD (8B04h), 0FFh
FDC_CONFIG_L1:              ; F96BEB
    CP (8A20h), 0FFh
    JRL Z, FDC_CONFIG_EXIT
    LD (8A20h), 0FFh
    LD WA, 0036h
    CALR LABEL_F96B1F
    LD WA, 2
    CALR SOME_DELAY
    CALR LABEL_F97544
    CP HL, 0FFFFh
    JR Z, FDC_CONFIG_L2
    CALR LABEL_F97592
    CP HL, 0FFFFh
    JR Z, FDC_CONFIG_L2
    CALR LABEL_F975D6
    CALR FDC_CMD_DISPATCH_SUB
    CP (8A24h), 0
    JR Z, FDC_CONFIG_L3
    LD (8A20h), 0
    JRL T, FDC_CONFIG_EXIT
FDC_CONFIG_L3:              ; F96C2A
    CALR LABEL_F96B13
    BIT 7, L
    JR NZ, FDC_CONFIG_L4
    LD WA, 0032h
    CALR LABEL_F975AD
    JR T, FDC_CONFIG_L5
FDC_CONFIG_L4:              ; F96C3A
    LD WA, 0031h
    CALR LABEL_F975AD
FDC_CONFIG_L5:              ; F96C3F
    CALR LABEL_F96B13
    BIT 6, L
    JR Z, FDC_CONFIG_L6
    LD WA, 002Fh
    CALR LABEL_F975AD
FDC_CONFIG_L6:              ; F96C4C
    CALR LABEL_F96B13
    CP L, 0FFh
    JR NZ, FDC_CONFIG_L7
    LD WA, 00FCh
    CALR LABEL_F975AD
    JR T, FDC_CONFIG_EXIT
FDC_CONFIG_L7:              ; F96C5C
    LD WA, 0001h
    CALR LABEL_F975AD
    CALR LABEL_F97544
    CP HL, 0FFFFh
    JR Z, FDC_CONFIG_L2
    LD WA, 0001h
    CALR LABEL_F975AD
    CALR LABEL_F97592
    CP HL, 0FFFFh
    JR NZ, FDC_CONFIG_L8
FDC_CONFIG_L2:              ; F96C7B
    LD (8A20h), 0
    LD (8B04h), 0FFh
    JR T, FDC_CONFIG_EXIT
FDC_CONFIG_L8:              ; F96C88
    LD WA, 0036h
    CALR LABEL_F96B1F
    LD WA, 2
    CALR SOME_DELAY
FDC_CONFIG_EXIT:            ; F96D93
    POP XIZ
    RET
```

### FDC_CMD_DISPATCH_SUB (0xF96D95) - Command Handler Subroutine

Primary handler that initializes FDC and returns status.
Called by: FDC_HANDLER_10 (dispatch table entry).

```asm
FDC_CMD_DISPATCH_SUB:       ; F96D95
    LD WA, 0036h
    CALR LABEL_F96B1F
    LD WA, 2
    CALR SOME_DELAY
    CALR LABEL_F96B13
    CP L, 0FFh
    JR NZ, FDC_H10_OK
    LD WA, 00FCh
    CALR LABEL_F975AD
FDC_H10_OK:                 ; F96DAE
    LD HL, 0
    RET
```

### FDC_STATUS_HANDLER (0xF97696) - Status/Interrupt Handler

Checks and updates FDC status, handles interrupts.

```asm
FDC_STATUS_HANDLER:         ; F97696
    LD A, (8A36h)
    CP A, (8B04h)
    RET Z
    LD (8B04h), (8A36h)
    LD WA, 2
    CALR SOME_DELAY
    CALR LABEL_F975DC
    LD WA, 000Fh
    CALR LABEL_F972F9
    CALR LABEL_F975E2
    CP (8A24h), 0
    JR Z, FDC_SH_L1
    LD (8B04h), 0FFh
FDC_SH_L1:                  ; F976C3
    LD WA, 0010h
    JRL T, SOME_DELAY

; Secondary status handler
FDC_STATUS_HANDLER_2:       ; F976C9
    LD (8A28h), 0C6h
    CALR LABEL_F97052
    CALR LABEL_F975DC
    LD WA, 00C6h
    CALR LABEL_F972F9
    CP (8A24h), 0
    RET NZ
    JRL T, LABEL_F975E2
```

### FDC_CMD_EXEC (0xF976E4) - Command Execution Handler

Handles FDC command execution with detection and validation.

```asm
FDC_CMD_EXEC:               ; F976E4
    PUSH IZ
    CALR LABEL_F974FE
    CP HL, 0
    JR Z, FDC_CE_L1
    LD (8A68h), 001h
    JRL T, FDC_CE_DISPATCH  ; 0xF9782A
FDC_CE_L1:                  ; F976F4
    CALR LABEL_F97544
    CP HL, 0
    JR NZ, FDC_CE_L2
    LD (8A68h), 008h
    JRL T, FDC_CE_DISPATCH
FDC_CE_L2:                  ; F97703
    LD (8A68h), 001h
    JRL T, FDC_CE_DISPATCH

FDC_CE_PROCESS:             ; F9770B
    LD (8A24h), 0
    CALR FDC_STATUS_HANDLER
    CP (8A24h), 0
    JR Z, FDC_CE_L3
    LD A, (8A24h)
    LD IZL, A
    EXTS IZ
    CALR FDC_CONFIG_VERIFY
    LD A, IZL
    LD (8A24h), A
    JRL T, FDC_CE_EXIT      ; 0xF97833
FDC_CE_L3:                  ; F97730
    LD WA, (8A48h)
    CP WA, (8B0Ch)
    JR ULE, FDC_CE_L4
    LD (8A48h), 0001h
FDC_CE_L4:                  ; F97740
    LDW (8B10h), (8A48h)
    LD (001Ch), 0
    ; ... continues with more sector handling
```

### FDC_MODE_CONFIG (0xF97984) - Mode Configuration (Handler 5)

Configures FDC for different operating modes (0-5).

```asm
FDC_MODE_CONFIG:            ; F97984
    CALR LABEL_F975AC
    CP (8A24h), 0
    JRL NZ, FDC_MC_EXIT     ; 0xF97A3C
    CALR FDC_INTERRUPT_HANDLER
    CP (8A24h), 0
    JRL NZ, FDC_MC_EXIT
    CALR LABEL_F97652
    CP (8A24h), 0
    JRL NZ, FDC_MC_EXIT
    LD A, (8A6Ch)           ; Load FDC mode
    CP A, 2
    JR Z, FDC_MC_MODE2
    CP A, 3
    JR Z, FDC_MC_MODE3
    CP A, 5
    JR Z, FDC_MC_MODE045
    CP A, 4
    JR Z, FDC_MC_MODE045
    CP A, 0
    JR NZ, FDC_MC_COMMON
FDC_MC_MODE045:             ; F979BD - Mode 0, 4, 5
    LD (8A2Eh), 002h
    LD (8A33h), 050h
    JR T, FDC_MC_COMMON
FDC_MC_MODE3:               ; F979C9
    LD (8A2Eh), 002h
    LD (8A33h), 06Ch
    JR T, FDC_MC_COMMON
FDC_MC_MODE2:               ; F979D5
    LD (8A2Eh), 003h
    LD (8A33h), 074h
FDC_MC_COMMON:              ; F979DF
    LD (8A36h), 0
    LD (8A2Bh), 0
    LD (8A34h), 0E5h
    LD (8A2Ch), 0
    LD (8A29h), 0
    ; ... continues
```

### FDC_CMD_ENABLE (0xF97C21) - Command Enable Setup

Sets bit 3 at 0x28, waits for FDC ready.

```asm
FDC_CMD_ENABLE:             ; F97C21
    PUSH IZ
    SET 3, (28h)
    LD WA, 00FEh
    CALR LABEL_F972F9
    CP (8A24h), 0
    JR Z, FDC_CE_READY
    LD WA, 0031h
    CALR LABEL_F975AD
    JR T, FDC_CE_DONE
FDC_CE_READY:               ; F97C3A
    LD IZ, 1
    CP IZ, 0
    JR Z, FDC_CE_DONE
FDC_CE_LOOP:                ; F97C40
    LD WA, 000Ah
    CALR SOME_DELAY
    DJNZ IZ, FDC_CE_LOOP
FDC_CE_DONE:                ; F97C49
    POP IZ
    RET
```

### FDC_CMD_DISABLE (0xF97C4B) - Command Disable

Clears bit 3 at 0x28.

```asm
FDC_CMD_DISABLE:            ; F97C4B
    RES 3, (28h)
    LD WA, 000Eh
    JRL T, LABEL_F972F9
```

### FDC_STATUS_COPY (0xF97C54) - Copy Cached Status

Simple 2-instruction routine.

```asm
FDC_STATUS_COPY:            ; F97C54
    LD (8A24h), (8A26h)
    RET
```

### FDC_OUTPUT_CTRL (0xF97C5B) - Output Control

Controls FDC output based on value in 0x8A44.

```asm
FDC_OUTPUT_CTRL:            ; F97C5B
    LD WA, (8A44h)
    CP WA, 1
    JR Z, FDC_OC_ENABLE
    CP WA, 0
    JR NZ, FDC_OC_OTHER
    JR T, FDC_OC_DISABLE
FDC_OC_OTHER:               ; F97C69
    LD WA, 00FEh
    CALR LABEL_F975AD
    RET
FDC_OC_ENABLE:              ; F97C70
    LD (8A6Ah), 0FFh
    RET
FDC_OC_DISABLE:             ; F97C76
    LD (8A6Ah), 0
    RET
```

### FDC_INTERRUPT_HANDLER (0xF97C7C) - Main Interrupt Handler

Checks status and dispatches to appropriate handlers.

```asm
FDC_INTERRUPT_HANDLER:      ; F97C7C
    PUSH QIZ
    CP (8A24h), 0
    JR NZ, FDC_IH_EXIT
    LD WA, 4
    CALR LABEL_F972F9
    CP (8A24h), 0
    JR NZ, FDC_IH_EXIT
    CALR LABEL_F970C9
    CP (8A24h), 0
    JR NZ, FDC_IH_EXIT
    CALR LABEL_F96B19
    LD QIZH, L
    BIT 7, QIZH
    JR Z, FDC_IH_L1
    LD WA, 0032h
    CALR LABEL_F975AD
FDC_IH_L1:                  ; F97CAE
    BIT 5, QIZH
    JR NZ, FDC_IH_L2
    LD WA, 0031h
    CALR LABEL_F975AD
FDC_IH_L2:                  ; F97CBA
    BIT 6, QIZH
    JR Z, FDC_IH_EXIT
    LD WA, 002Fh
    CALR LABEL_F975AD
FDC_IH_EXIT:                ; F97CC6
    POP QIZ
    RET
```

---

## Handler Dispatch Table (0xF97D8D)

The FDC uses a handler dispatch table starting at 0xF97D8D:

| Index | Address | Handler Name | Description |
|-------|---------|--------------|-------------|
| 0 | F97D8D | DISPATCH_BASE | Basic handler (calls F97639) |
| 1 | F97D93 | HANDLER_01 | CMD_ENABLE + LABEL_F97652 |
| 2 | F97D99 | HANDLER_02 | CMD_ENABLE + STATUS_HANDLER |
| 3 | F97D9F | HANDLER_03 | CMD_ENABLE + CMD_EXEC |
| 4 | F97DA5 | HANDLER_04 | CMD_ENABLE + SECTOR_XFER |
| 5 | F97DAB | HANDLER_05 | CMD_ENABLE + MODE_CONFIG |
| 6 | F97DB1 | HANDLER_06 | CMD_ENABLE only |
| 7 | F97DB5 | HANDLER_07 | CMD_DISABLE |
| 8 | F97DB9 | HANDLER_08 | STATUS_COPY |
| 9 | F97DBD | HANDLER_09 | OUTPUT_CTRL |
| 10 | F97DC1 | HANDLER_10 | CMD_DISPATCH_SUB |
| 11 | F97DC5 | HANDLER_11 | CMD_ENABLE + INTERRUPT_HANDLER |

All handlers end by jumping to LABEL_F97DE1 which sets the status flag and returns.

---

*Last updated: January 2026*
