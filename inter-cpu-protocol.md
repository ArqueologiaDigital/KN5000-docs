---
layout: page
title: Inter-CPU Protocol
permalink: /inter-cpu-protocol/
---

# Inter-CPU Protocol

The KN5000 uses two TMP94C241F CPUs that communicate via a memory-mapped latch at 0x120000. The Main CPU handles UI, MIDI, and control while the Sub CPU handles all audio generation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       MAIN CPU (TMP94C241F)                         │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ Audio_Lock_     │    │ Audio_DMA_      │    │ Audio_Lock_     │ │
│  │ Acquire         │───>│ Transfer        │───>│ Release         │ │
│  │ (0xEF1FEE)      │    │ (0xEF341B)      │    │ (0xEF1F0F)      │ │
│  └─────────────────┘    └────────┬────────┘    └─────────────────┘ │
│                                  │                                  │
│         Lock counter at (0x0532 + lock_index)                       │
│         Linked list of waiting requests at 0x0487                   │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   v
                    ┌──────────────────────────┐
                    │         LATCH            │
                    │       @ 0x120000         │
                    │                          │
                    │  Bidirectional Data      │
                    │  DMA-capable transfer    │
                    └──────────────────────────┘
                                   │
                                   v
┌──────────────────────────────────────────────────────────────────────┐
│                        SUB CPU (TMP94C241F)                          │
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │ InterCPU_Latch_  │    │ MicroDMA CH0/2   │    │ CMD_DISPATCH_  │ │
│  │ Setup (0x020C15) │───>│ Handlers         │───>│ TABLE          │ │
│  └──────────────────┘    └──────────────────┘    └────────────────┘ │
│                                                          │           │
│                          ┌───────────────────────────────┘           │
│                          v                                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    COMMAND HANDLERS                             │ │
│  │                                                                 │ │
│  │  0x00-0x1F: Audio_CmdHandler_00_1F (MIDI/notes → 0x2B0D)       │ │
│  │  0x20-0x3F: Audio_CmdHandler_20_3F (Stub)                      │ │
│  │  0x40-0x5F: Audio_CmdHandler_40_5F (...)                        │ │
│  │  0x60-0x7F: Audio_CmdHandler_60_7F (Audio/DSP → 0x3B60)       │ │
│  │  0x80-0x9F: Serial port setup (38400 baud)                     │ │
│  │  0xA0-0xBF: Audio_CmdHandler_A0_BF (System audio)              │ │
│  │  0xC0-0xFF: Audio_CmdHandler_C0_FF (Extended system)           │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## Main CPU: Sending Commands

### Lock Mechanism

The Main CPU uses a semaphore system to serialize access to the inter-CPU latch:

```asm
; Acquire lock before sending
    LD A, lock_index        ; Lock index 0-7
    CALL Audio_Lock_Acquire ; Decrements counter, waits if busy

; ... send audio commands via DMA ...

; Release lock when done
    LD A, lock_index
    CALL Audio_Lock_Release ; Increments counter, signals waiters
```

**Lock Variables:**
- Counter: `(0x0532 + lock_index)` - Decremented on acquire, incremented on release
- Wait List: `0x0487` - Linked list of pending requests

### DMA Transfer

The `Audio_DMA_Transfer` routine handles bulk data transfer:

```asm
Audio_DMA_Transfer:
    ; Data pointer at 0x05DA
    ; Byte count at 0x05DE
    ; Transfers in chunks to latch at 0x120000
```

**Transfer Variables:**
- Data Pointer: 0x05DA (XWA)
- Byte Count: 0x05DE (16-bit)
- Completion Flag: 0x05E0

## Sub CPU: Receiving Commands

### DMA Configuration

The `InterCPU_Latch_Setup` routine configures the Sub CPU for DMA reception:

1. Sets interrupt priority for DMA channels 0-3
2. Configures MicroDMA source address
3. Initializes `DMA_XFER_STATE` and `CMD_PROCESSING_STATE` to 0

### MicroDMA Handlers

| Handler | Channel | Purpose |
|---------|---------|---------|
| `MICRODMA_CH0_HANDLER` | CH0 | Inter-CPU latch reads |
| `MICRODMA_CH2_HANDLER` | CH2 | Payload data transfers |

### Command Dispatch

Commands are dispatched based on upper 3 bits of the command byte:

```asm
CMD_DISPATCH_TABLE:                         ; Address: 0x00F428
    dd Audio_CmdHandler_00_1F   ; 0x00-0x1F: MIDI/note commands → ring buffer at 0x2B0D
    dd Audio_CmdHandler_20_3F   ; 0x20-0x3F: Stub (returns 0)
    dd Audio_CmdHandler_40_5F   ; 0x40-0x5F: (line 9619)
    dd Audio_CmdHandler_60_7F   ; 0x60-0x7F: Audio/DSP commands → ring buffer at 0x3B60
    dd Serial1_DataTransmit_Loop ; 0x80-0x9F: Serial port 1 data
    dd Audio_CmdHandler_A0_BF   ; 0xA0-0xBF: (line 51502)
    dd Audio_CmdHandler_C0_FF   ; 0xC0-0xDF: (line 10951)
    dd Audio_CmdHandler_C0_FF   ; 0xE0-0xFF: Same as 0xC0-0xDF
```

## Audio Command Format

### Ring Buffer at 0x2B0D (MIDI/Note Commands)

Commands 0x00-0x1F write MIDI-like data to a 4KB ring buffer:

| Variable | Address | Description |
|----------|---------|-------------|
| Write Pointer | 0x2B0D | 12-bit circular index |
| Read Pointer | 0x2B0F | Current read position |
| Byte Count | 0x2B11 | Bytes available |
| Base Address | 0x2B13 | Buffer start |
| Buffer Data | +0x06 | 4KB circular buffer |

### Ring Buffer at 0x3B60 (DSP/Audio Config)

Commands 0x60-0x7F write audio config data to a 2KB ring buffer:

| Variable | Address | Description |
|----------|---------|-------------|
| Write Pointer | 0x3B60 | 11-bit circular index (wraps at 0x800) |
| (reserved) | 0x3B62 | Padding |
| Available Count | 0x3B64 | Bytes queued for processing |
| Buffer Base | 0x3B66 | 3-byte pointer to actual data area |

`Audio_Process_DSP` (called from main loop) reads commands from this buffer. The most important command is **0x2D** (DSP configuration change). See [Audio Subsystem — Command 0x2D Protocol]({{ site.baseurl }}/audio-subsystem/#inter-cpu-command-protocol-command-0x2d--dsp-configuration) for the full 4-layer protocol.

### Command Processing

```asm
Audio_CmdHandler_00_1F:
    ; Entry: XSP+004h = byte count, XSP+006h = data pointer

    Loop:
        ; Read write pointer from 0x2B0D
        ; Mask with 0xFFF (4KB buffer)
        ; Write byte to buffer[write_ptr]
        ; Increment write pointer
        ; Increment byte count at 0x2B11
        ; Repeat for all bytes

    ; Exit: HL = 0 (success)
```

## Sub CPU Response

The Sub CPU can send data back to the Main CPU via `InterCPU_DMA_Send`:

```asm
InterCPU_DMA_Send:
    ; Entry: XDE = source data pointer
    ;        BC = byte count
    ;        A = command/channel identifier

    ; Splits large transfers into 32-byte chunks
    ; Used by tone generator for status responses
```

## Boot Sequence Transfer

During boot, the Main CPU loads the 192KB Sub CPU payload:

1. Main CPU initializes DMA channels via `SubCPU_Init_DMA_Channels`
2. Main CPU writes payload in chunks to latch
3. Sub CPU's MicroDMA handler receives data
4. Sub CPU executes payload from internal RAM
5. Sub CPU enters `Audio_System_Init` and starts processing loop

## Code References

### Main CPU (`maincpu/kn5000_v10_program.asm`)

| Routine | Address | Description |
|---------|---------|-------------|
| `SubCPU_Init_DMA_Channels` | 0xEF329E | Initialize DMA channels for inter-CPU communication |
| `SubCPU_Send_Payload` | 0xEF068A | Transfer 192KB payload to Sub CPU |
| `InterCPU_E1_Bulk_Transfer` | 0xEF3457 | E1 two-phase bulk transfer protocol |
| `InterCPU_E2_Send` | 0xEF33AA | E2 extended transfer command |
| `InterCPU_Send_Data_Block` | 0xEF3345 | Send variable-length data packet |
| `Audio_DMA_Transfer` | 0xEF341B | Core DMA transfer routine |
| `Audio_Lock_Acquire` | 0xEF1FEE | Acquire communication lock |
| `Audio_Lock_Release` | 0xEF1F0F | Release communication lock |

### Sub CPU (`subcpu/kn5000_subprogram_v142.asm`)

| Routine | Address | Description |
|---------|---------|-------------|
| `InterCPU_Latch_Setup` | 0x020C15 | Configure DMA and interrupts |
| `InterCPU_DMA_Send` | 0x020C6B | Send data to Main CPU |
| `Audio_CmdHandler_00_1F` | 0x034D5F | Audio command handler |
| `MICRODMA_CH0_HANDLER` | 0x020F1F | DMA channel 0 interrupt |
| `MICRODMA_CH2_HANDLER` | 0x020F01 | DMA channel 2 interrupt |

## Related Pages

- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) - Sound generation details
- [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) - Both CPU specifications
- [Boot Sequence]({{ site.baseurl }}/boot-sequence/) - Startup process
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Boot ROM Protocol (Sub CPU Side)

During boot, the Sub CPU boot ROM implements a DMA-based protocol for receiving the 192KB payload from the Main CPU.

### Boot ROM INT0 Handler (0xFF881F)

The Sub CPU boot ROM's INT0 handler processes commands from the latch:

```asm
InterCPU_RX_Handler:           ; 0xFF881F
    push XWA
    bit  2, (0x34)             ; Check busy flag
    jr   NZ, .exit
    ld   A, (0x120000)         ; Read command from latch
    ld   (0x051A), A           ; Store for processing
    cp   A, 0xE1               ; E1 command?
    jr   NZ, .check_e2
    ; ... set up DMA for 6-byte header ...
    jr   .done

.check_e2:
    cp   A, 0xE2               ; E2 command?
    jr   NZ, .check_e3
    ; ... set up DMA for 10-byte header ...
    jr   .done

.check_e3:
    cp   A, 0xE3               ; E3 command? (CRITICAL!)
    jr   NZ, .data_packet
    set  6, (0x04FE)           ; SET PAYLOAD_LOADED_FLAG bit 6!
    jr   .cleanup

.data_packet:
    ; Handle variable-length data packet
    ...

.cleanup:
    res  1, (0x34)             ; Clear handshake flag
.exit:
    pop  XWA
    reti
```

### E1/E2/E3 Command Protocol

| Command | Byte | Action | Data Size |
|---------|------|--------|-----------|
| E1 | 0xE1 | Bulk data transfer header | 6 bytes (dest addr + count) |
| E2 | 0xE2 | Extended transfer header | 10 bytes |
| E3 | 0xE3 | **Payload complete signal** | 0 bytes |
| Data | 0x00-0xDF | Data packet | Low 5 bits + 1 |

### PAYLOAD_LOADED_FLAG (0x04FE)

| Bit | Meaning |
|-----|---------|
| 6 | Payload ready - triggers `call 0x000400` in boot ROM main loop |
| 7 | Transfer active flag |

### Boot ROM Main Loop (0xFF8410)

```asm
Boot_Main_Loop:                ; 0xFF840C
    res  6, (0x04FE)           ; Clear payload-ready flag
.poll:
    bit  6, (0x04FE)           ; Check if payload ready
    jr   Z, .check_status
    ei   6                     ; Enable interrupts level 6
    call 0x000400              ; CALL PAYLOAD ENTRY POINT!
.check_status:
    ; Update SSTAT signals based on MSTAT
    ldcf 1, (0x30)             ; Read Port D bit 1
    ; ... process and update Port D ...
    jr   T, .poll              ; Loop forever
```

## Main CPU Payload Transfer

### SubCPU_Init_DMA_Channels (0xEF329E)

Configures MicroDMA channels for inter-CPU communication:

```asm
SubCPU_Init_DMA_Channels:      ; 0xEF329E
    ; Configure interrupt priorities
    AND  (INTET23), 0xF8
    RES  2, (T8RUN)
    ; ... more interrupt config ...

    ; Set DMA destination 2 to latch address
    LDA  XWA, INTER_CPU_COMM_LATCHES   ; 0x140000
    LDC_DMAD2_XWA

    ; Set DMA source 0 to latch address
    LDA  XWA, INTER_CPU_COMM_LATCHES
    LDC_DMAS0_XWA

    ; Clear state variables
    LD   (0x05E0), 0x00
    LD   (0x05E2), 0x00
    RET
```

### SubCPU_Send_Payload (0xEF068A)

Sends the 192KB payload to Sub CPU in chunks. This is the core routine for loading the Sub CPU firmware during boot.

> **See Also:**
> - [Boot Sequence: SubCPU_Send_Payload Details]({{ site.baseurl }}/boot-sequence/#subcpu_send_payload-details) - Transfer sequence table, timing, error handling
> - [LZSS Compression]({{ site.baseurl }}/lzss-compression/) - Optional preset data decompression

**Source:** `maincpu/kn5000_v10_program.asm:134212`

```asm
SubCPU_Send_Payload:           ; 0xEF068A
    PUSH XIZ
    CP   (0xFFFEEF), 0xFF      ; Check transfer enable flag
    JRL  NZ, .skip_transfer

    ; Initial timing delay (0x2000 iterations)
    LD   XIZ, 0
.delay_loop:
    INC  1, XIZ
    CP   XIZ, 0x2000
    JR   C, .delay_loop

    ; Send 64KB chunks from Table Data ROM (0x830000-0x870000)
    LD   XWA, 0x830000         ; Source: table_data + 0x30000
    LD   XBC, 0x10000          ; Count: 64KB
    LD   XDE, 0x050000         ; Dest: Sub CPU RAM
    CALL InterCPU_E1_Bulk_Transfer

    LD   XWA, 0x840000         ; Next 64KB
    LD   XBC, 0x10000
    LD   XDE, 0x060000
    CALL InterCPU_E1_Bulk_Transfer

    ; ... 3 more 64KB chunks (0x850000, 0x860000, 0x870000) ...

    ; Optional LZSS decompression from 0x3E0000
    CP   (0xFFFEED), 0xFF      ; Check decompression flag
    JR   Z, .skip_decompress
    CALL LABEL_EF41E3          ; Decompress SLIDE4K data
    ; ... copy decompressed data to Sub CPU ...

.skip_transfer:
    POP  XIZ
    RET
```

**Transfer Summary:**

| Chunk | Source | Sub CPU Dest | Size |
|-------|--------|--------------|------|
| 1-5 | 0x830000-0x870000 | 0x050000-0x090000 | 5 × 64KB |
| 6-8 | Decompressed/Fallback | 0x00F000-0x02F000 | 3 × 64KB |
| 9 | Buffer | 0x000400 | 256 bytes |

### InterCPU_E1_Bulk_Transfer (0xEF3457)

Implements the E1 two-phase transfer protocol:

```asm
InterCPU_E1_Bulk_Transfer:     ; 0xEF3457
    PUSH IZ
    ; Wait for previous transfer to complete
    ...

.wait_ready:
    BIT  3, (PZ)               ; Check SSTAT1 (Sub CPU ready)
    JRL  Z, .timeout

    ; Send E1 command
    RES  0, (PZ)               ; Clear MSTAT0
    LD   (0x05E0), 0x02        ; Set state = 2 (two-phase)
    LD   (INTER_CPU_COMM_LATCHES), 0xE1  ; Send E1 command!

.wait_ack:
    BIT  3, (PZ)               ; Wait for Sub CPU response
    JRL  NZ, .ack_timeout
    SET  0, (PZ)               ; Set MSTAT0

    ; Send 6-byte header (dest addr + byte count)
    LDA  XHL, 0x0608
    LD   (XHL), XWA            ; Store dest address
    LDA  XWA, 0x05D0
    LD   (XWA), XDE            ; Store source address
    LD   (XHL+4), BC           ; Store count
    LD   (XWA+4), BC
    LD   (0x05DA), XWA         ; Setup for Audio_DMA_Transfer
    LDW  (0x05DE), 0x0006      ; 6 bytes for header
    CALR Audio_DMA_Transfer    ; Send header

    ; Wait for phase 1 complete, then send actual data
    ...
    CALR Audio_DMA_Transfer    ; Send data

    POP  IZ
    RET
```

## Research Needed

- [x] Document exact latch register bit layout - See Boot ROM Protocol above
- [x] Analyze handshaking timing requirements - Uses 60,000 iteration timeout (~300ms)
- [x] Document command 0x2D (DSP configuration) format — Complete: 4-layer protocol fully traced
- [x] Document two ring buffers (0x2B0D for MIDI, 0x3B60 for DSP) — Complete
- [ ] Document remaining ring buffer command formats (other than 0x2D)
- [ ] Document handlers 2 (0x40-0x5F), 5 (0xA0-0xBF), 6-7 (0xC0-0xFF)
- [ ] Map status response message formats
- [ ] Determine actual subprogram storage location (table_data vs custom_data flash)
