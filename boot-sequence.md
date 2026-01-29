---
layout: page
title: Boot Sequence
permalink: /boot-sequence/
---

# KN5000 Boot Sequence

This page documents the complete boot sequence of the Technics KN5000, from power-on to a fully functional system. The KN5000 uses a dual-CPU architecture where the Main CPU orchestrates startup and loads firmware to the Sub CPU.

## Overview

```
Power On
    │
    ▼
┌─────────────────┐     ┌─────────────────┐
│   Main CPU      │     │    Sub CPU      │
│  TMP94C241F     │     │   TMP94C241F    │
│  (IC10)         │     │   (IC27)        │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │  1. Reset vector      │  1. Reset vector
         │     0xFFFEE0          │     0xFFFEE0
         │                       │
         ▼                       ▼
    Init Hardware           Init Hardware
    Load Sub CPU            Wait for payload
    Payload (192KB)         at 0x0400
         │                       │
         │   ◄─── DMA ───►       │
         │   (0x120000 latch)    │
         │                       │
         ▼                       ▼
    Start Subsystems        Execute Payload
    (UI, MIDI, FDC...)      (Audio Engine)
         │                       │
         ▼                       ▼
    ┌─────────────────────────────┐
    │     System Ready            │
    └─────────────────────────────┘
```

## Main CPU Boot Sequence

### 1. Reset Vector (0xFFFEE0)

The TMP94C241F CPU fetches its reset vector from address `0xFFFEE0`. This points to `RESET_HANDLER` in the main program ROM.

### 2. Hardware Initialization

The reset handler performs essential hardware setup:

| Step | Description | Key Registers |
|------|-------------|---------------|
| 1 | Disable watchdog | WDMOD, WDCR |
| 2 | Configure clock | CLKMOD |
| 3 | Initialize ports | P0-PZ, PxCR, PxFC |
| 4 | Set up memory controller | MSARx, MAMRx, BxCS |
| 5 | Initialize DRAM | DREFCR, DMEMCR |
| 6 | Configure timers | T01MOD, T4MOD, etc. |
| 7 | Initialize stack | XSP = stack address |

### 3. Sub CPU Payload Loading

After hardware initialization, the main CPU loads a 192KB firmware payload to the sub CPU via DMA through the inter-CPU latch at `0x120000`.

**Protocol:**
1. Main CPU sends command byte with data length
2. Sub CPU receives interrupt, sets up DMA
3. Data transfers via latch
4. Handshake via `INTERCPU_STATUS` register
5. Repeat until 192KB transferred
6. Send E3 command to signal completion

See [Inter-CPU Protocol](#inter-cpu-communication-protocol) for details.

### 4. Subsystem Initialization

After the sub CPU payload is loaded:

| Subsystem | Description |
|-----------|-------------|
| Display | VGA-compatible LCD controller at 0x1A0000 |
| Control Panel | Serial communication with MCU (SC1, 250kHz) |
| FDC | Floppy disk controller at 0x110000 |
| MIDI | External MIDI I/O |
| HDAE5000 | Hard disk expansion (if present) at 0x160000 |

### 5. Main Loop

The main CPU enters its event loop, handling:
- User interface events
- Control panel button/encoder input
- MIDI I/O
- Disk operations
- Display updates

---

## Sub CPU Boot Sequence

The sub CPU has a dedicated 128KB boot ROM (`kn5000_subcpu_boot.ic30`) that initializes hardware and waits for the payload.

### 1. Reset Vector (0xFFFEE0)

The sub CPU's reset vector jumps to `BOOT_INIT` at `0xFF8290`.

### 2. Hardware Initialization (BOOT_INIT)

```
Address: 0xFF8290
Size: ~400 bytes
```

**Initialization steps:**

| Step | Registers | Values | Purpose |
|------|-----------|--------|---------|
| 1 | WDMOD_REAL | 0x00 | Disable watchdog |
| 2 | INT_CTRL | 0x04 | Configure interrupts |
| 3 | P0FC-P2FC | 0xFF | Port 0-2 all function mode |
| 4 | P7, P7FC, P7CR | Various | Port 7 configuration |
| 5 | P8, P8FC, P8CR | Various | Port 8 (chip select) |
| 6 | PA, PAFC, PB, PBFC | Various | DRAM signals |
| 7 | INTTC01 | 0x03 | Timer interrupt control |
| 8 | SC0/SC1 registers | Various | Serial configuration |
| 9 | T01MOD, T23MOD | Various | Timer modes |
| 10 | MSARx, MAMRx | Various | Memory controller |
| 11 | SER0/SER1 | Various | Serial channels |
| 12 | DRAM_* | Various | DRAM refresh/timing |
| 13 | BxCSL, BxCSH | Various | Bus chip select |

### 3. Copy Interrupt Vectors (COPY_VECTORS)

```
Address: 0xFF846D
Source: 0xFF8F6C (ROM)
Destination: 0x0400 (RAM)
Size: 225 bytes (45 handlers × 5 bytes)
```

The boot ROM copies 45 interrupt vector trampolines from ROM to RAM. Each trampoline is a 5-byte `JP` instruction that initially points back to the boot ROM's default handlers, but will be overwritten by the payload.

### 4. Enable Interrupts

```asm
ei 0    ; Enable interrupts at level 0
```

### 5. Initialization Routines

| Routine | Address | Size | Purpose |
|---------|---------|------|---------|
| INIT_MEMORY_TEST | 0xFF8956 | ~300B | RAM test, ROM checksum |
| INIT_DMA_SERIAL | 0xFF85AE | ~90B | DMA and serial setup |
| INIT_TONE_GEN | 0xFF84A8 | ~70B | Tone generator at 0x130000 |

### 6. Main Loop (Wait for Payload)

```
Address: 0xFF8405
```

The sub CPU enters a loop waiting for the payload ready flag:

```asm
MAIN_LOOP:
    res  6, (SUBCPU_STATUS_FLAGS)    ; Clear ready flag
.wait_loop:
    bit  6, (SUBCPU_STATUS_FLAGS)    ; Check if payload ready
    jr   Z, .check_status
    ei   6                            ; Enable interrupt level 6
    call PAYLOAD_ENTRY               ; Call payload at 0x0400
.check_status:
    ; Update serial status
    jr   .wait_loop
```

### 7. Payload Execution

Once `PAYLOAD_LOADED_FLAG` bit 6 is set (by E3 command), the sub CPU jumps to the payload entry point at `0x0400`. The payload takes over audio synthesis and tone generation duties.

---

## Inter-CPU Communication Protocol

The main CPU and sub CPU communicate via a single-byte latch at `0x120000`.

### Command Format

| Command | Description | Data Size | Buffer |
|---------|-------------|-----------|--------|
| 0x00-0x1F | Variable-length data | Low 5 bits + 1 | CMD_DATA_BUFFER |
| 0xE1 | Two-phase transfer setup | 6 bytes | CMD_E1_BUFFER |
| 0xE2 | Parameter block | 10 bytes | CMD_E2_BUFFER |
| 0xE3 | Payload complete | 0 bytes | - |

### Variable-Length Commands (0x00-0x1F)

```
Bits 7-5: Handler index (0-7) from jump table at 0xFF8000
Bits 4-0: Data length - 1 (so 0x00 = 1 byte, 0x1F = 32 bytes)
```

### Handshaking Signals (INTERCPU_STATUS at 0x34)

| Bit | Direction | Meaning |
|-----|-----------|---------|
| 0 | Sub → Main | Sub CPU ready flag |
| 1 | Internal | Completion signal from interrupt |
| 2 | Internal | Gate for command processing |
| 4 | Main → Sub | Main CPU ready flag |

### DMA State Machine (DMA_XFER_STATE at 0x0516)

| State | Meaning |
|-------|---------|
| 0 | Idle - no transfer in progress |
| 1 | Single transfer - waiting for completion |
| 2 | Two-phase transfer - phase 1 done, phase 2 pending |

### Transfer Flow

```
Main CPU                          Sub CPU
   │                                 │
   │  1. Write command to latch      │
   │  ─────────────────────────────► │
   │                                 │  2. InterCPU_RX_Handler
   │                                 │     triggered
   │                                 │
   │  3. Wait for sub ready          │  4. Set up DMA
   │  ◄───────────────────────────── │     destination
   │                                 │
   │  5. Send data bytes             │
   │  ─────────────────────────────► │  6. DMA receives data
   │                                 │
   │  7. Check completion            │  8. DMA_Complete_Handler
   │  ◄───────────────────────────── │     clears state
   │                                 │
```

---

## Boot ROM Routines Reference

### DMA Transfer Routines (0xFF8604-0xFF881E)

| Routine | Address | Size | Description |
|---------|---------|------|-------------|
| SendData_Chunked | 0xFF8604 | 69B | Break large transfers into 32-byte chunks |
| SendData_Block | 0xFF8649 | 99B | Send single block with handshaking |
| SendCmd_E3 | 0xFF86AC | 48B | Signal payload complete |
| SendParams_E2 | 0xFF86DC | 112B | Send E2 parameter block |
| TwoPhase_Transfer | 0xFF874C | 211B | Execute E1 two-phase sequence |

### Interrupt Handlers

| Handler | Address | Description |
|---------|---------|-------------|
| InterCPU_RX_Handler | 0xFF881F | Receives commands from main CPU |
| DMA_Complete_Handler | 0xFF889A | Advances DMA state machine |
| CMD_Dispatch_Handler | 0xFF88B8 | Processes received commands |
| DEFAULT_HANDLER | 0xFF8432 | Default handler (just RETI) |

### Utility Routines

| Routine | Address | Description |
|---------|---------|-------------|
| COPY_VECTORS | 0xFF846D | Copy interrupt trampolines to RAM |
| INIT_TONE_GEN | 0xFF84A8 | Initialize tone generator |
| TONE_GEN_WRITE | 0xFF84F1 | Write to tone generator registers |
| CHECKSUM_CALC | 0xFF859B | Calculate memory checksum |
| MEM_TEST_ROUTINE | 0xFF89FC | RAM test with patterns |
| ROM_CHECKSUM | 0xFF8AB4 | Verify boot ROM integrity |

---

## Memory Map During Boot

### Sub CPU RAM Layout

| Address | Size | Symbol | Description |
|---------|------|--------|-------------|
| 0x0400 | 225B | PAYLOAD_ENTRY | Interrupt vector trampolines |
| 0x04FE | 1B | PAYLOAD_LOADED_FLAG | Payload ready flags |
| 0x0502 | 10B | DMA_SETUP_PARAMS | DMA parameter block |
| 0x050C | 6B | E1_XFER_PARAMS | E1 command parameters |
| 0x0512 | 4B | DMA_TARGET_ADDR | Current DMA destination |
| 0x0516 | 2B | DMA_XFER_STATE | DMA state machine |
| 0x0518 | 2B | CMD_PROCESSING_STATE | Command processing phase |
| 0x051A | 1B | LAST_CMD_BYTE | Last received command |
| 0x051E | 32B | CMD_DATA_BUFFER | Variable-length command data |
| 0x053E | 10B | E2_XFER_PARAMS | E2 command parameters |
| 0x0544 | 6B | CMD_E1_BUFFER | E1 command buffer |
| 0x054A | 10B | CMD_E2_BUFFER | E2 command buffer |
| 0x0556 | 1B | MEMTEST_RESULT | Memory test result |
| 0x0558 | 8B | SERIAL_STATUS | Serial status bytes |
| 0x05A2 | - | STACK_INIT | Initial stack pointer |

### Hardware Addresses

| Address | Description |
|---------|-------------|
| 0x100000 | Audio hardware registers (DSP/DAC) |
| 0x110000 | Keyboard/control panel latches |
| 0x120000 | Inter-CPU communication latch |
| 0x130000 | Tone generator registers |

---

## Timing Considerations

### Boot Time Estimates

| Phase | Duration | Notes |
|-------|----------|-------|
| Hardware init | ~1ms | SFR configuration |
| Memory test | ~10ms | RAM pattern test |
| ROM checksum | ~5ms | 4KB verification |
| Tone gen init | ~1ms | 4 channel setup |
| Payload load | ~100ms | 192KB via DMA |
| **Total** | **~120ms** | To payload execution |

### DMA Transfer Rates

- Latch clock: Tied to timer frequency
- Typical chunk size: 32 bytes
- Timeout: 60,000 iterations (~300ms at 20MHz)

---

## Error Handling

### Memory Test Errors (MEMTEST_RESULT)

| Bit | Meaning |
|-----|---------|
| 0-1 | Low word RAM errors |
| 2-3 | High word RAM errors |
| 3 | ROM checksum mismatch |

### DMA Timeouts

All DMA routines have 60,000 iteration timeouts (~300ms). On timeout:
- Transfer is abandoned
- Ready flag is set
- Control returns to caller

### HALT_LOOP (0xFF8490)

Fatal error handler that disables serial and halts the CPU:

```asm
HALT_LOOP:
    res  0, (SC0MOD)    ; Disable serial
.halt:
    halt                ; Halt CPU
    jr   T, .halt       ; Loop forever
```

---

## See Also

- [Memory Map]({{ site.baseurl }}/memory-map/) - Complete address space documentation
- [Reverse Engineering]({{ site.baseurl }}/reverse-engineering/) - Technical details
- [ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) - Build status and known issues
