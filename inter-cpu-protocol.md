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
│  │ Acquire         │───►│ Transfer        │───►│ Release         │ │
│  │ (0xEF1FEE)      │    │ (0xEF341B)      │    │ (0xEF1F0F)      │ │
│  └─────────────────┘    └────────┬────────┘    └─────────────────┘ │
│                                  │                                  │
│         Lock counter at (0x0532 + lock_index)                       │
│         Linked list of waiting requests at 0x0487                   │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │         LATCH            │
                    │       @ 0x120000         │
                    │                          │
                    │  Bidirectional Data      │
                    │  DMA-capable transfer    │
                    └──────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        SUB CPU (TMP94C241F)                          │
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │ InterCPU_Latch_  │    │ MicroDMA CH0/2   │    │ CMD_DISPATCH_  │ │
│  │ Setup (0x020C15) │───►│ Handlers         │───►│ TABLE          │ │
│  └──────────────────┘    └──────────────────┘    └────────────────┘ │
│                                                          │           │
│                          ┌───────────────────────────────┘           │
│                          ▼                                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    COMMAND HANDLERS                             │ │
│  │                                                                 │ │
│  │  0x00-0x1F: Audio_CmdHandler_00_1F (DSP/audio control)         │ │
│  │  0x20-0x3F: Audio_CmdHandler_20_3F (Extended audio)            │ │
│  │  0x40-0x5F: Audio_CmdHandler_40_5F (Audio parameters)          │ │
│  │  0x60-0x7F: Audio_CmdHandler_60_7F (Voice/DSP config)          │ │
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
CMD_DISPATCH_TABLE:
    dd Audio_CmdHandler_00_1F   ; 0x00-0x1F: DSP/audio control
    dd Audio_CmdHandler_20_3F   ; 0x20-0x3F: Extended audio
    dd Audio_CmdHandler_40_5F   ; 0x40-0x5F: Audio parameters
    dd Audio_CmdHandler_60_7F   ; 0x60-0x7F: Voice/DSP config
    dd LABEL_01F890             ; 0x80-0x9F: Serial port setup
    dd Audio_CmdHandler_A0_BF   ; 0xA0-0xBF: System audio
    dd Audio_CmdHandler_C0_FF   ; 0xC0-0xDF: Extended system
    dd Audio_CmdHandler_C0_FF   ; 0xE0-0xFF: Extended system (shared)
```

## Audio Command Format

Commands 0x00-0x1F write MIDI-like data to a 4KB ring buffer:

### Ring Buffer Structure

| Variable | Address | Description |
|----------|---------|-------------|
| Write Pointer | 0x2B0D | 12-bit circular index |
| Read Pointer | 0x2B0F | Current read position |
| Byte Count | 0x2B11 | Bytes available |
| Base Address | 0x2B13 | Buffer start |
| Buffer Data | +0x06 | 4KB circular buffer |

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

1. Main CPU initializes DMA channels via `Audio_InitDMAChannels`
2. Main CPU writes payload in chunks to latch
3. Sub CPU's MicroDMA handler receives data
4. Sub CPU executes payload from internal RAM
5. Sub CPU enters `Audio_System_Init` and starts processing loop

## Code References

### Main CPU (`maincpu/kn5000_v10_program.asm`)

| Routine | Address | Description |
|---------|---------|-------------|
| `Audio_Lock_Acquire` | 0xEF1FEE | Acquire communication lock |
| `Audio_Lock_Release` | 0xEF1F0F | Release communication lock |
| `Audio_DMA_Transfer` | 0xEF341B | Core DMA transfer routine |
| `Audio_InitDMAChannels` | 0xEF329E | Initialize DMA channels |

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

## Research Needed

- [ ] Document exact latch register bit layout
- [ ] Analyze handshaking timing requirements
- [ ] Document all command byte formats for each handler
- [ ] Map status response message formats
